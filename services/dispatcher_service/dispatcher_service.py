from dotenv import load_dotenv
import os
import asyncio
import aiohttp
from fastapi import FastAPI
import pika
from utils import calculate_manhattan_distance

app = FastAPI()

# Load environment variables
load_dotenv()

# RabbitMQ configuration
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))

# RabbitMQ connection
connection_params = pika.ConnectionParameters(
    host=RABBITMQ_HOST,
    port=RABBITMQ_PORT,
    credentials=pika.PlainCredentials('guest', 'guest'),
    heartbeat=60,
    blocked_connection_timeout=300
)

try:
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    channel.queue_declare(queue="ride_requests")
    print("✅ Successfully connected to RabbitMQ")
except Exception as e:
    print("❌ RabbitMQ connection failed:", e)

async def fetch_taxis():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://taxi_service:8003/taxis/") as response:
                response.raise_for_status()
                return await response.json()
    except aiohttp.ClientError as e:
        print(f"Error fetching taxis: {e}")
        return []

async def update_taxi(taxi_id, location_x, location_y, available):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"http://taxi_service:8003/taxis/update/",
                params={
                    "taxi_id": taxi_id,
                    "location_x": location_x,
                    "location_y": location_y,
                    "available": available
                }
            ) as response:
                response.raise_for_status()
    except aiohttp.ClientError as e:
        print(f"Error updating taxi {taxi_id}: {e}")

async def process_request(ride_request, method_frame, fetch_taxis, update_taxi, channel):
    """
    Processes a single ride request: allocates a taxi or leaves it in the queue.
    """
    # Fetch all taxis from Taxi Service asynchronously
    taxis = await fetch_taxis()

    # Find the nearest taxi
    nearest_taxi = min(
        (taxi for taxi in taxis if taxi['available']),
        key=lambda t: calculate_manhattan_distance(
            t['location_x'], t['location_y'],
            ride_request['start']['x'], ride_request['start']['y']
        ),
        default=None
    )

    if nearest_taxi:
        # Update taxi state via Taxi Service asynchronously
        await update_taxi(
            nearest_taxi['id'], 
            ride_request['end']['x'], 
            ride_request['end']['y'], 
            False
        )
        # Acknowledge the ride request in RabbitMQ
        channel.basic_ack(method_frame.delivery_tag)
        return {"ride_request": ride_request, "taxi_id": nearest_taxi['id']}
    else:
        # No available taxis; keep the ride request in the queue
        return {"ride_request": ride_request, "message": "No available taxis"}


@app.get("/dispatcher/assign/")
async def assign_taxi():
    """
    Assigns the nearest available taxi to all ride requests in the queue.
    """
    results = []

    # List of async tasks to process all ride requests
    tasks = []
    while True:
        try:
            # Fetch the next ride request from RabbitMQ queue
            method_frame, _, body = channel.basic_get(queue="ride_requests")
            if not body:
                # No more ride requests in the queue
                break

            ride_request = eval(body)
            tasks.append(process_request(ride_request, method_frame, fetch_taxis, update_taxi, channel))
        except pika.exceptions.AMQPError as e:
            print(f"Error accessing RabbitMQ: {e}")
            break

    # Run all tasks concurrently
    if tasks:
        results = await asyncio.gather(*tasks)

    return {"results": results}
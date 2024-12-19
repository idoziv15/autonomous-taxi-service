import asyncio
import aiohttp
from fastapi import FastAPI
import pika
from utils import calculate_manhattan_distance

app = FastAPI()

connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()
channel.queue_declare(queue="ride_requests")

async def fetch_taxis():
    async with aiohttp.ClientSession() as session:
        async with session.get("http://taxi_service:8003/taxis/") as response:
            return await response.json()

async def update_taxi(taxi_id, location_x, location_y, available):
    async with aiohttp.ClientSession() as session:
        await session.post(
            f"http://taxi_service:8003/taxis/update/",
            params={
                "taxi_id": taxi_id,
                "location_x": location_x,
                "location_y": location_y,
                "available": available
            }
        )

@app.get("/assign/")
async def assign_taxi():
    """
    Assigns the nearest available taxi to a ride request.
    """
    # Fetch the next ride request from RabbitMQ
    method_frame, _, body = channel.basic_get(queue="ride_requests")
    if not body:
        return {"message": "No ride requests"}

    ride_request = eval(body)

    # Fetch all taxis from Taxi Service asynchronously
    taxis = await fetch_taxis()

    # Find the nearest taxi
    nearest_taxi = min(
        (taxi for taxi in taxis if taxi['available']),
        key=lambda t: calculate_manhattan_distance(
            t['location']['x'], t['location']['y'],
            ride_request['start']['x'], ride_request['start']['y']
        ),
        default=None
    )

    if nearest_taxi:
        # Update taxi state via Taxi Service asynchronously
        await update_taxi(nearest_taxi['id'], ride_request['end']['x'], ride_request['end']['y'], False)

        # Acknowledge the ride request in RabbitMQ
        channel.basic_ack(method_frame.delivery_tag)

        return {"message": "Taxi assigned", "taxi_id": nearest_taxi['id']}
    
    return {"message": "No available taxis"}

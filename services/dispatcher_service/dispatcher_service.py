import asyncio
import aiohttp
from fastapi import FastAPI
from utils import calculate_manhattan_distance
from shared.rabbitmq_utils import RabbitMQConnection

app = FastAPI()
rabbitmq = RabbitMQConnection(queue='ride_requests')

# Initialize RabbitMQ connection at startup
@app.on_event("startup")
def startup_event():
    rabbitmq.connect()


# Safely close RabbitMQ connection at shutdown
@app.on_event("shutdown")
def shutdown_event():
    try:
        if rabbitmq.connection and not rabbitmq.connection.is_closed:
            rabbitmq.close()
            print("✅ RabbitMQ connection closed gracefully.")
        else:
            print("ℹ️ RabbitMQ connection was already closed.")
    except Exception as e:
        print(f"❌ Error during RabbitMQ shutdown: {e}")



# Async helper functions for interacting with Taxi Service
async def fetch_taxis():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://taxi_service:8003/taxis/") as response:
                response.raise_for_status()
                return await response.json()
    except aiohttp.ClientError as e:
        print(f"❌ Error fetching taxis: {e}")
        return []


async def update_taxi(taxi_id, location_x, location_y, available, dest_x, dest_y):
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "id": taxi_id,
                "location_x": location_x,
                "location_y": location_y,
                "available": available,
            }

            if dest_x is not None and dest_y is not None:
                payload["destination_x"] = dest_x
                payload["destination_y"] = dest_y

            async with session.post(
                f"http://taxi_service:8003/taxis/update/",
                json=payload
            ) as response:
                response.raise_for_status()
                print(f"✅ Taxi {taxi_id} updated successfully.")
    except aiohttp.ClientResponseError as e:
        print(f"❌ Error updating taxi {taxi_id}: {e.status}, message='{str(e.message)}', url='{e.request_info.url}'")
    except aiohttp.ClientError as e:
        print(f"❌ Error updating taxi {taxi_id}: {e}")


async def process_request(ride_request, method_frame):
    """
    Processes a single ride request: allocates a taxi or leaves it in the queue.
    """
    try:
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
                ride_request['start']['x'],
                ride_request['start']['y'],
                False,
                ride_request['end']['x'],
                ride_request['end']['y'],
            )
            # Acknowledge the ride request in RabbitMQ
            rabbitmq.channel.basic_ack(method_frame.delivery_tag)

            return {"ride_request": ride_request, "taxi_id": nearest_taxi['id']}
        else:
            # No available taxis; keep the ride request in the queue
            return {"ride_request": ride_request, "message": "No available taxis"}
    except Exception as e:
        print(f"❌ Unexpected error during processing: {e}")
        return {"error": "An unexpected error occurred"}


@app.get("/dispatcher/assign/")
async def assign_taxi():
    """
    Assigns the nearest available taxi to all ride requests in the queue.
    """
    # List of async tasks to process all ride requests
    tasks = []

    while True:
        try:
            # Fetch the next ride request from RabbitMQ queue
            method_frame, _, body = rabbitmq.channel.basic_get(queue="ride_requests")
            if not body:
                # No more ride requests in the queue
                break

            ride_request = eval(body)
            tasks.append(process_request(ride_request, method_frame))
        except Exception as e:
            print(f"❌ Error accessing RabbitMQ: {e}")
            break

    # Run all tasks concurrently
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)

    return {"message": "Finished assigning taxis to rides."}

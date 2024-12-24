import asyncio
import aiohttp
import json
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

def find_nearest_taxi(taxis, ride_request, seen):
    nearest_taxi = min(
        (taxi for taxi in taxis if taxi['available'] and taxi['id'] not in seen),
        key=lambda t: calculate_manhattan_distance(
            t['location_x'], t['location_y'],
            ride_request['start']['x'], ride_request['start']['y']
        ),
        default=None
    )
    return nearest_taxi

async def process_request(ride_request, method_frame, taxis):
    """
    Processes a single ride request: allocates a taxi or leaves it in the queue.
    """
    try:
        if not taxis:
            print("❌ No taxis available for processing the ride request.")
            return {"error": "No taxis available"}

        attempted_taxis = set()

        while len(attempted_taxis) < len(taxis):
            nearest_taxi = find_nearest_taxi(taxis, ride_request, attempted_taxis)

            if not nearest_taxi:
                print(f"🚫 No available taxis left for ride request: {ride_request}")
                return {"ride_request": ride_request, "message": "No available taxis"}

            response = await update_taxi(
                nearest_taxi['id'],
                ride_request['start']['x'],
                ride_request['start']['y'],
                False,
                ride_request['end']['x'],
                ride_request['end']['y']
            )

            if "error" in response:
                print(f"❌ Taxi {nearest_taxi['id']} is occupied, trying next closest taxi.")
                attempted_taxis.add(nearest_taxi['id'])
                continue

            rabbitmq.channel.basic_ack(method_frame.delivery_tag)
            print(f"✅ Taxi {nearest_taxi['id']} successfully assigned to ride request.")
            return {"ride_request": ride_request, "taxi_id": nearest_taxi['id']}

        print(f"🚫 All taxis occupied. Ride request remains in the queue.")
        return {"ride_request": ride_request, "message": "No available taxis"}
    
    except Exception as e:
        print(f"❌ Unexpected error during processing: {e}")
        return {"error": "An unexpected error occurred"}


@app.get("/dispatcher/assign/")
async def assign_taxi():
    """
    Assigns the nearest available taxi to all ride requests in the queue.
    """
    # Fetch all taxis from Taxi Service asynchronously
    taxis = await fetch_taxis()
    if not taxis:
        print("❌ No taxis fetched. Cannot assign rides.")
        return {"message": "No taxis available for assignment."}

    # List of async tasks to process all ride requests
    tasks = []

    while True:
        try:
            # Fetch the next ride request from RabbitMQ queue
            method_frame, _, body = rabbitmq.channel.basic_get(queue="ride_requests")
            if not body:
                # No more ride requests in the queue
                break

            ride_request = json.loads(body.decode('utf-8'))
            tasks.append(asyncio.create_task(process_request(ride_request, method_frame, taxis)))
        except Exception as e:
            print(f"❌ Error accessing RabbitMQ: {e}")
            break

    # Run all tasks concurrently
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)

    return {"message": "Finished assigning taxis to rides."}

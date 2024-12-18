import pika
import requests
from shared.utils import calculate_manhattan_distance
from fastapi import FastAPI

app = FastAPI()

connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()
channel.queue_declare(queue="ride_requests")

@app.get("/assign/")
def assign_taxi():
    """
    Assigns the nearest available taxi to a ride request.
    """
    # Fetch the next ride request from RabbitMQ
    method_frame, _, body = channel.basic_get(queue="ride_requests")
    if not body:
        return {"message": "No ride requests"}

    ride_request = eval(body)

    # Fetch all taxis from Taxi Service
    response = requests.get("http://taxi_service:8003/taxis/")
    taxis = response.json()

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
        # Update taxi state via Taxi Service
        requests.post(
            "http://taxi_service:8003/taxis/update/",
            params={
                "taxi_id": nearest_taxi['id'],
                "location_x": ride_request['end']['x'],
                "location_y": ride_request['end']['y'],
                "available": False
            }
        )
        channel.basic_ack(method_frame.delivery_tag)
        return {"message": "Taxi assigned", "taxi_id": nearest_taxi['id']}
    
    return {"message": "No available taxis"}

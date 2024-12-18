import pika
from fastapi import FastAPI
from shared.models import RideRequestModel

app = FastAPI()

# RabbitMQ Connection
connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()
channel.queue_declare(queue="ride_requests")

@app.post("/ride-request/")
def add_ride_request(request: RideRequestModel):
    channel.basic_publish(
        exchange="",
        routing_key="ride_requests",
        body=str(request.dict())
    )
    return {"message": "Ride request added to the queue"}

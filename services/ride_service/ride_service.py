from dotenv import load_dotenv
import os
import pika
from fastapi import FastAPI
from shared.models import RideRequestModel

app = FastAPI()

# Load environment variables
load_dotenv()

# RabbitMQ configuration
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))

# RabbitMQ connection
connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT))
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

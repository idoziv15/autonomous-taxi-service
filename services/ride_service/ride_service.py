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

@app.post("/ride-request/")
def add_ride_request(request: RideRequestModel):
    try:
        channel.basic_publish(
            exchange="",
            routing_key="ride_requests",
            body=request.json()
        )
        return {"message": "Ride request added to the queue"}
    except pika.exceptions.AMQPError as e:
        print(f"Error publishing to RabbitMQ: {e}")
        return {"error": "Failed to add ride request"}

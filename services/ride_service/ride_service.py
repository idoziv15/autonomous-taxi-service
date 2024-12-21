from dotenv import load_dotenv
import os
import pika
from fastapi import FastAPI, HTTPException
from shared.models import RideRequestModel

app = FastAPI()

# Load environment variables
load_dotenv()

# RabbitMQ configuration
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))

# Global RabbitMQ connection and channel variables
connection = None
channel = None


def create_rabbitmq_connection():
    global connection, channel
    try:
        connection_params = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=pika.PlainCredentials('guest', 'guest'),
            heartbeat=60,  # Keep the heartbeat interval short
            blocked_connection_timeout=300  # Prevent indefinite blocking
        )
        connection = pika.BlockingConnection(connection_params)
        channel = connection.channel()
        channel.queue_declare(queue="ride_requests")
        print("✅ Successfully connected to RabbitMQ")
    except pika.exceptions.AMQPError as e:
        print(f"❌ Failed to connect to RabbitMQ: {e}")
        connection = None
        channel = None
        raise HTTPException(status_code=500, detail="Failed to connect to RabbitMQ")


# Initialize RabbitMQ connection at startup
@app.on_event("startup")
def startup_event():
    create_rabbitmq_connection()


# Safely close RabbitMQ connection at shutdown
@app.on_event("shutdown")
def shutdown_event():
    global connection
    if connection and not connection.is_closed:
        connection.close()
        print("✅ RabbitMQ connection closed.")


@app.post("/ride-request/")
def add_ride_request(request: RideRequestModel):
    global connection, channel
    if connection is None or connection.is_closed:
        print("❌ Connection is closed. Reconnecting...")
        create_rabbitmq_connection()

    if channel is None or channel.is_closed:
        print("❌ Channel is closed. Reconnecting...")
        channel = connection.channel()
        channel.queue_declare(queue="ride_requests")

    try:
        channel.basic_publish(
            exchange='',
            routing_key='ride_requests',
            body=request.json()
        )
        print("✅ Message published successfully")
        return {"message": "Ride request added to the queue"}
    except pika.exceptions.AMQPError as e:
        print(f"❌ Error publishing to RabbitMQ: {e}")
        return {"error": "Failed to add ride request"}
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return {"error": "An unexpected error occurred"}

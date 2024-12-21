from dotenv import load_dotenv
import os
import pika

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
def establish_connection():
    try:
        connection = pika.BlockingConnection(connection_params)
        channel = connection.channel()
        channel.queue_declare(queue="ride_requests")
        print("✅ Successfully connected to RabbitMQ")
        return channel
    except Exception as e:
        print("❌ RabbitMQ connection failed:", e)
        return e
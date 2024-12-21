from dotenv import load_dotenv
import os
import pika
from fastapi import HTTPException

# Load environment variables
load_dotenv()

# RabbitMQ configuration
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_QUEUE = "ride_requests"
RABBITMQ_HEARTBEAT = 60
RABBITMQ_BLOCK_TIMEOUT = 300

class RabbitMQConnection:
    def __init__(self, host=RABBITMQ_HOST, port=RABBITMQ_PORT, queue=RABBITMQ_QUEUE):
        self.host = host
        self.port = port
        self.queue = queue
        self.connection = None
        self.channel = None

    def connect(self):
        try:
            connection_params = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=pika.PlainCredentials('guest', 'guest'),
                heartbeat=RABBITMQ_HEARTBEAT,
                blocked_connection_timeout=RABBITMQ_BLOCK_TIMEOUT
            )
            self.connection = pika.BlockingConnection(connection_params)
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=self.queue)
            print(f"✅ Successfully Connected to RabbitMQ. Queue: {self.queue}")
        except pika.exceptions.AMQPError as e:
            print(f"❌ RabbitMQ connection failed: {e}")
            raise HTTPException(status_code=500, detail="Failed to connect to RabbitMQ")

    def publish_message(self, message):
        if not self.channel or self.channel.is_closed:
            self.connect()
        try:
            self.channel.basic_publish(
                exchange='',
                routing_key=self.queue,
                body=message
            )
            print("✅ Message published successfully")
        except pika.exceptions.AMQPError as e:
            print(f"❌ Error publishing to RabbitMQ: {e}")
            raise HTTPException(status_code=500, detail="Failed to publish message")

    def consume_message(self):
        if not self.channel or self.channel.is_closed:
            self.connect()
        try:
            method_frame, _, body = self.channel.basic_get(queue=self.queue)
            if method_frame:
                self.channel.basic_ack(method_frame.delivery_tag)
                return body
            return None
        except pika.exceptions.AMQPError as e:
            print(f"❌ Error consuming from RabbitMQ: {e}")
            raise HTTPException(status_code=500, detail="Failed to consume message")

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            print("✅ RabbitMQ connection closed.")

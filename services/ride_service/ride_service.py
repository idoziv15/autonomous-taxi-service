from fastapi import FastAPI
from shared.models import RideRequestModel
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
    rabbitmq.close()

@app.post("/ride-request/")
def add_ride_request(request: RideRequestModel):
    try:
        rabbitmq.publish_message(request.json())
        print("✅ Message published successfully")
        return {"message": "Ride request added to the queue"}
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return {"error": "An unexpected error occurred"}

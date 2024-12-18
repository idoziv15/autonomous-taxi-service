from fastapi import FastAPI
import requests

app = FastAPI()

# Route to Ride Request Service
@app.post("/ride-request/")
def send_ride_request(request: dict):
    response = requests.post("http://ride_request_service:8001/ride-request/", json=request)
    return response.json()

# Route to Dispatcher Service
@app.get("/dispatcher/assign")
def assign_taxi():
    response = requests.get("http://dispatcher_service:8002/assign")
    return response.json()

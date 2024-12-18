from fastapi import FastAPI
import requests

app = FastAPI()

# Forward request to Ride Request Service
@app.post("/ride-request/")
def send_ride_request(request: dict):
    response = requests.post("http://ride_request_service:8001/ride-request/", json=request)
    return response.json()

# Forward request to Taxi Service
@app.get("/taxis/")
def get_all_taxis():
    response = requests.get("http://taxi_service:8003/taxis/")
    return response.json()

@app.get("/taxis/{taxi_id}")
def get_taxi(taxi_id: int):
    response = requests.get(f"http://taxi_service:8003/taxis/{taxi_id}")
    return response.json()

# Forward request to Dispatcher Service
@app.get("/dispatcher/assign/")
def assign_taxi():
    response = requests.get("http://dispatcher_service:8002/assign/")
    return response.json()

# Forward taxi initialization to Taxi Service
@app.post("/taxis/init/")
def initialize_taxis():
    response = requests.post("http://taxi_service:8003/init-taxis/")
    return response.json()
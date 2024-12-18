import requests
import time
import random

RIDES = 10
AWAIT_TIME = 20

# Initialize taxis with random locations
response = requests.post("http://api_gateway:8000/taxis/init")
print(response.json())

for i in range(RIDES):
    ride_request = {
        "start": {"x": random.randint(0, 20000), "y": random.randint(0, 20000)},
        "end": {"x": random.randint(0, 20000), "y": random.randint(0, 20000)}
    }
    response = requests.post("http://api_gateway:8000/ride-request/", json=ride_request)
    print(f"Request {i+1}: {response.json()}")
    time.sleep(AWAIT_TIME)
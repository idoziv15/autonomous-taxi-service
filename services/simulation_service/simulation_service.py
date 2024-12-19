import requests
import random
import time

# Constants
CITY_SIZE = 20000 
TAXIS = 10
SIMULATION_DURATION = 300
INTERVAL = 20

# Initialize taxis with random locations
response = requests.post("http://localhost:8000/taxis/init/")
print(response.json())

# Run the simulation
for t in range(0, SIMULATION_DURATION, INTERVAL):
    print(f"\n=== Time: {t} seconds ===")

    # Add a new ride request
    ride_request = {
        "start": {"x": random.randint(0, CITY_SIZE), "y": random.randint(0, CITY_SIZE)},
        "end": {"x": random.randint(0, CITY_SIZE), "y": random.randint(0, CITY_SIZE)}
    }
    ride_response = requests.post("http://localhost:8000/ride-request/", json=ride_request)
    print(f"Added ride request: {ride_response.json()}")

    # Update taxi locations
    response = requests.post("http://localhost:8000/taxis/update-locations/")
    print(response.json())

    # Get the state of all taxis
    taxi_response = requests.get("http://localhost:8000/taxis/")
    taxis = taxi_response.json()
    print("Taxis:")
    for taxi in taxis:
        availability = 'standing' if taxi['available'] else 'driving'
        print(f"  Taxi-{taxi['id']}: Location: {taxi['location']} ({availability})")

    # Try to allocate a taxi for each ride request
    assign_response = requests.get("http://localhost:8000/dispatcher/assign/")
    print(assign_response.json())

    time.sleep(INTERVAL)

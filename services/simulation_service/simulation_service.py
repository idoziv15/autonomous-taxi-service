import requests
import random
import time

# Constants
CITY_SIZE = 20000 
TAXIS = 10
SIMULATION_DURATION = 300
INTERVAL = 20

def handle_request(method, url, **kwargs):
    try:
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error during request to {url}: {e}")
        return None

# Initialize taxis with random locations
response = handle_request("POST", "http://localhost:8000/taxis/init/")
if response:
    print(response)

# Run the simulation
for t in range(0, SIMULATION_DURATION, INTERVAL):
    print(f"\n=== Time: {t} seconds ===")

    # Add a new ride request
    ride_request = {
        "start": {"x": random.randint(0, CITY_SIZE), "y": random.randint(0, CITY_SIZE)},
        "end": {"x": random.randint(0, CITY_SIZE), "y": random.randint(0, CITY_SIZE)}
    }
    ride_response = handle_request("POST", "http://localhost:8000/ride-request/", json=ride_request)
    if ride_response:
        print(f"Added ride request: {ride_response}")

    # Update taxi locations
    response = handle_request("POST", "http://localhost:8000/taxis/update-locations/")
    if response:
        print(response)

    # Get the state of all taxis
    taxi_response = handle_request("GET", "http://localhost:8000/taxis/")
    if taxi_response:
        print("Taxis:")
        for taxi in taxi_response:
            availability = 'standing' if taxi['available'] else 'driving'
            print(f"  Taxi-{taxi['id']}: Location: {taxi['location']} ({availability})")

    # Try to allocate a taxi for each ride request
    assign_response = handle_request("GET", "http://localhost:8000/dispatcher/assign/")
    if assign_response:
        print(assign_response)

    time.sleep(INTERVAL)

import requests
import random
import time

# Constants
CITY_SIZE = 20000 
TAXIS = 10
SIMULATION_DURATION = 300
INTERVAL = 20
BASE_URL = "http://nginx:8000"

def handle_request(method, url, **kwargs):
    try:
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error during request to {url}: {e}")
        return None

# Initialize taxis with random locations
response = handle_request("POST", f"{BASE_URL}/taxis/init/")
if response:
    print(response['message'])

# Run the simulation
for t in range(0, SIMULATION_DURATION, INTERVAL):
    if t == 0:
        print("Initial taxi locations:")
    else:
        print(f"After {t} seconds:")

    # Add a new ride request
    ride_request = {
        "start": {"x": random.randint(0, CITY_SIZE), "y": random.randint(0, CITY_SIZE)},
        "end": {"x": random.randint(0, CITY_SIZE), "y": random.randint(0, CITY_SIZE)}
    }
    ride_response = handle_request("POST", f"{BASE_URL}/ride-request/", json=ride_request)

    # Update taxi locations
    response = handle_request("POST", f"{BASE_URL}/taxis/update-locations/")

    # Get the state of all taxis
    taxi_response = handle_request("GET", f"{BASE_URL}/taxis/")
    if taxi_response:
        print("Taxi locations:")
        for taxi in taxi_response:
            availability = 'standing' if taxi['available'] else 'driving'
            print(f"  Taxi-{taxi['id']}: {taxi['location_x']}Km, {taxi['location_y']}Km ({availability})")

    # Try to allocate a taxi for each ride request
    assign_response = handle_request("GET", f"{BASE_URL}/dispatcher/assign/")
    if assign_response:
        print(assign_response['message'])

    time.sleep(INTERVAL)

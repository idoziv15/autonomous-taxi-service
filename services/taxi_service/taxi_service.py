import random
import redis
from fastapi import FastAPI
from shared.database import redis_client
from utils import update_taxi_state

app = FastAPI()

SPEED = 20
INTERVALS_TIME = 20

@app.post("/init-taxis/")
def initialize_taxis():
    """
    Initializes 10 taxis with random (X, Y) locations and available states.
    Clears any existing taxis in Redis before initialization.
    """
    try:
        # Clear existing taxis
        for key in redis_client.keys("taxi:*"):
            redis_client.delete(key)
        
        # Initialize 10 taxis
        for taxi_id in range(1, 11):
            redis_client.hset(f"taxi:{taxi_id}", mapping={
                "id": taxi_id,
                "location_x": random.randint(0, 20000),
                "location_y": random.randint(0, 20000),
                "available": "True"
            })
        return {"message": "Taxis initialized with random locations"}
    except redis.RedisError as e:
        print(f"Error initializing taxis: {e}")
        return {"error": "Failed to initialize taxis"}

@app.get("/taxis/")
def get_all_taxis():
    """
    Retrieves all taxis stored in Redis.
    """
    try:
        taxis = []
        for key in redis_client.keys("taxi:*"):
            taxi_data = redis_client.hgetall(key)
            taxis.append({
                "id": int(taxi_data[b'id']),
                "location": {
                    "x": float(taxi_data[b'location_x']),
                    "y": float(taxi_data[b'location_y'])
                },
                "available": taxi_data[b'available'].decode('utf-8') == "True"
            })
        return taxis
    except redis.RedisError as e:
        print(f"Error retrieving taxis from Redis: {e}")
        return {"error": "Failed to retrieve taxis"}

@app.get("/taxis/{taxi_id}")
def get_taxi(taxi_id: int):
    """
    Retrieves a single taxi by its ID.
    """
    try:
        taxi = redis_client.hgetall(f"taxi:{taxi_id}")
        if taxi:
            return {
                "id": int(taxi[b'id']),
                "location": {
                    "x": float(taxi[b'location_x']),
                    "y": float(taxi[b'location_y'])
                },
                "available": taxi[b'available'].decode('utf-8') == "True"
            }
        return {"error": "Taxi not found"}
    except redis.RedisError as e:
        print(f"Error retrieving taxi {taxi_id} from Redis: {e}")
        return {"error": f"Failed to retrieve taxi with ID {taxi_id}"}

@app.post("/taxis/update/")
def update_taxi(taxi_id: int, location_x: float, location_y: float, available: bool):
    """
    Updates a taxi's location and availability status.
    """
    key = f"taxi:{taxi_id}"
    try:
        if redis_client.exists(key):
            redis_client.hset(key, mapping={
                "location_x": location_x,
                "location_y": location_y,
                "available": "True" if available else "False"
            })
            return {"message": "Taxi updated"}
        return {"error": "Taxi not found"}
    except redis.RedisError as e:
        print(f"Error updating taxi {taxi_id}: {e}")
        return {"error": f"Failed to update taxi with ID {taxi_id}"}



@app.post("/taxis/update-locations/")
def update_taxi_locations():
    """
    Updates the locations of all taxis based on their destinations, speed, and 90-degree turn logic.
    """
    try:
        taxis = redis_client.keys("taxi:*")
        for taxi_key in taxis:
            taxi = redis_client.hgetall(taxi_key)
            if taxi[b'available'].decode('utf-8') == "False":
                updated_state = update_taxi_state(taxi, SPEED, INTERVALS_TIME)
                redis_client.hset(taxi_key, mapping=updated_state)
    except redis.RedisError as e:
        print(f"Error updating taxi locations: {e}")
        return {"error": "Failed to update taxi locations"}
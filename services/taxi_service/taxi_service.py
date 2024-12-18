import random
from fastapi import FastAPI
from shared.database import redis_client

app = FastAPI()

@app.post("/init-taxis/")
def initialize_taxis():
    """
    Initializes 10 taxis with random (X, Y) locations and available states.
    Clears any existing taxis in Redis before initialization.
    """
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

@app.get("/taxis/")
def get_all_taxis():
    """
    Retrieves all taxis stored in Redis.
    """
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

@app.get("/taxis/{taxi_id}")
def get_taxi(taxi_id: int):
    """
    Retrieves a single taxi by its ID.
    """
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

@app.post("/taxis/update/")
def update_taxi(taxi_id: int, location_x: float, location_y: float, available: bool):
    """
    Updates a taxi's location and availability status.
    """
    key = f"taxi:{taxi_id}"
    if redis_client.exists(key):
        redis_client.hset(key, mapping={
            "location_x": location_x,
            "location_y": location_y,
            "available": "True" if available else "False"
        })
        return {"message": "Taxi updated"}
    return {"error": "Taxi not found"}

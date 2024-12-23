import random
import redis
from fastapi import FastAPI
from shared.database import redis_client
from utils import update_taxi_state
from shared.models import TaxiModel

app = FastAPI()

SPEED = 20
INTERVALS_TIME = 20
CITY_SIZE = 20000
MAX_TAXIS = 10

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
        for taxi_id in range(1, MAX_TAXIS + 1):
            redis_client.hset(f"taxi:{taxi_id}", mapping={
                "id": taxi_id,
                "location_x": random.randint(0, CITY_SIZE),
                "location_y": random.randint(0, CITY_SIZE),
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
            if not taxi_data:
                continue

            taxi = TaxiModel(
                id=int(taxi_data[b'id']),
                location_x=float(taxi_data[b'location_x']),
                location_y=float(taxi_data[b'location_y']),
                available=taxi_data[b'available'].decode('utf-8') == "True"
            )
            taxis.append(taxi.dict())
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
        if not taxi:
            return {"error": f"Taxi with ID {taxi_id} not found"}
        
        taxi = TaxiModel(
            id=int(taxi[b'id']),
            location_x=float(taxi[b'location_x']),
            location_y=float(taxi[b'location_y']),
            available=taxi[b'available'].decode('utf-8') == "True"
        )
        return taxi.dict()
    except redis.RedisError as e:
        print(f"Error retrieving taxi {taxi_id} from Redis: {e}")
        return {"error": f"Failed to retrieve taxi with ID {taxi_id}"}
    
@app.post("/taxis/update/")
def update_taxi(taxi: TaxiModel):
    """
    Safely reserves or updates a taxi's status using Redis transactions.
    """
    key = f"taxi:{taxi.id}"
    try:
        with redis_client.pipeline() as pipe:
            while True:
                try:
                    pipe.watch(key)
                    
                    if not redis_client.exists(key):
                        return {"error": "Taxi not found"}

                    current_taxi = redis_client.hgetall(key)
                    if current_taxi[b'available'].decode('utf-8') == "False":
                        return {"error": "Taxi is already reserved"}

                    mapping = {
                        "location_x": taxi.location_x,
                        "location_y": taxi.location_y,
                        "available": "True" if taxi.available else "False"
                    }

                    if taxi.destination_x is not None and taxi.destination_y is not None:
                        mapping["destination_x"] = taxi.destination_x
                        mapping["destination_y"] = taxi.destination_y

                    # Start the transaction
                    pipe.multi()
                    pipe.hset(key, mapping=mapping)
                    pipe.execute()
                    break

                except redis.WatchError:
                    # Retry if the key was modified during transaction
                    print("🚦 Retry due to concurrent modification on taxi key.")
                    continue

        return {"message": "Taxi updated successfully"}
    except redis.RedisError as e:
        print(f"❌ Error updating taxi {taxi.id}: {e}")
        return {"error": f"Failed to update taxi with ID {taxi.id}"}


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
        return {"message": "Taxis locations updated successfully"}
    except redis.RedisError as e:
        print(f"❌ Error updating taxi locations: {e}")
        return {"error": "Failed to update taxi locations"}
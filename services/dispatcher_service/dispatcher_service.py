from fastapi import FastAPI
from shared.database import SessionLocal, RideRequest, Taxi, init_db

app = FastAPI()
init_db()

@app.get("/assign")
def assign_taxi():
    db = SessionLocal()
    ride_request = db.query(RideRequest).filter(RideRequest.assigned_taxi == None).first()
    if not ride_request:
        return {"message": "No unassigned rides"}

    available_taxis = db.query(Taxi).filter(Taxi.available == True).all()
    # Find nearest taxi
    nearest_taxi = min(available_taxis, key=lambda taxi: abs(taxi.location_x - ride_request.start_x) + abs(taxi.location_y - ride_request.start_y), default=None)

    if nearest_taxi:
        nearest_taxi.available = False
        ride_request.assigned_taxi = nearest_taxi.id
        db.commit()
        response = {"ride_request_id": ride_request.id, "taxi_id": nearest_taxi.id}
    else:
        response = {"message": "No available taxis"}
    
    db.close()
    return response

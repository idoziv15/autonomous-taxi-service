from fastapi import FastAPI
from shared.database import SessionLocal, RideRequest, init_db
from shared.models import RideRequestModel

app = FastAPI()
init_db()

@app.post("/ride-request/")
def add_ride_request(request: RideRequestModel):
    db = SessionLocal()
    ride = RideRequest(
        start_x=request.start['x'],
        start_y=request.start['y'],
        end_x=request.end['x'],
        end_y=request.end['y']
    )
    db.add(ride)
    db.commit()
    db.close()
    return {"message": "Ride request added"}

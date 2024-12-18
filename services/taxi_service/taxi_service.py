import random
from fastapi import FastAPI
from shared.database import SessionLocal, Taxi, init_db

app = FastAPI()
init_db()

@app.post("/init-taxis/")
def initialize_taxis():
    db = SessionLocal()
    db.query(Taxi).delete()  # Clear existing taxis
    for taxi_id in range(1, 11):  # 10 taxis
        taxi = Taxi(
            id=taxi_id,
            location_x=random.randint(0, 20000),
            location_y=random.randint(0, 20000),
            available=True
        )
        db.add(taxi)
    db.commit()
    db.close()
    return {"message": "Taxis initialized with random locations"}

@app.get("/taxis/") 
def get_taxis():
    db = SessionLocal()
    taxis = db.query(Taxi).all()
    db.close()
    return [{"id": taxi.id, "location": {"x": taxi.location_x, "y": taxi.location_y}, "available": taxi.available} for taxi in taxis]

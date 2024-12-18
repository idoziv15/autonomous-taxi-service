from fastapi import FastAPI
from shared.database import SessionLocal, Taxi, init_db

app = FastAPI()
init_db()

@app.get("/taxis/")
def get_taxis():
    db = SessionLocal()
    taxis = db.query(Taxi).all()
    db.close()
    return [{"id": taxi.id, "location": {"x": taxi.location_x, "y": taxi.location_y}, "available": taxi.available} for taxi in taxis]

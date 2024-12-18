from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
import redis

# Redis Connection
redis_client = redis.Redis(host="redis", port=6379, db=0)

DATABASE_URL = "postgresql://user:password@shared_database:5432/taxi_service"
Base = declarative_base()

# Initialize Database Engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Ride Request Model
class RideRequest(Base):
    __tablename__ = "ride_requests"
    id = Column(Integer, primary_key=True, index=True)
    start_x = Column(Float)
    start_y = Column(Float)
    end_x = Column(Float)
    end_y = Column(Float)
    assigned_taxi = Column(String, nullable=True)

# Taxi Model
class Taxi(Base):
    __tablename__ = "taxis"
    id = Column(Integer, primary_key=True, index=True)
    location_x = Column(Float)
    location_y = Column(Float)
    available = Column(Boolean, default=True)

# Create Tables
def init_db():
    Base.metadata.create_all(bind=engine)

from pydantic import BaseModel

class RideRequestModel(BaseModel):
    start: dict
    end: dict

class TaxiModel(BaseModel):
    id: int
    location: dict
    available: bool

from pydantic import BaseModel

class RideRequestModel(BaseModel):
    start: dict
    end: dict

    def to_json(self):
        return self.dict()

class TaxiModel(BaseModel):
    id: int
    location: dict
    available: bool

    def to_json(self):
        return self.dict()
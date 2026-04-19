from pydantic import BaseModel, field_validator
from typing import Literal

class RouteRequest(BaseModel):
    start_lat: float
    start_lng: float
    end_lat: float
    end_lng: float
    time_of_day: Literal["day", "evening", "night"] = "day"

    @field_validator("start_lat", "end_lat")
    @classmethod
    def validate_lat(cls, v):
        if not (12.80 <= v <= 13.15):
            raise ValueError("Latitude must be within Bangalore (12.80 – 13.15)")
        return v

    @field_validator("start_lng", "end_lng")
    @classmethod
    def validate_lng(cls, v):
        if not (77.45 <= v <= 77.78):
            raise ValueError("Longitude must be within Bangalore (77.45 – 77.78)")
        return v
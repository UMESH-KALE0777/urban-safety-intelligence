from pydantic import BaseModel
from typing import List, Literal

class Waypoint(BaseModel):
    lat: float
    lng: float

class RouteResult(BaseModel):
    name: str
    label: Literal["safest", "fastest", "alternate"]
    waypoints: List[Waypoint]
    distance_km: float
    duration_min: int
    risk_score: float
    safety_pct: int

class Hotspot(BaseModel):
    id: int
    lat: float
    lng: float
    radius: int
    risk: Literal["low", "medium", "high"]
    count: int

class RouteResponse(BaseModel):
    routes: List[RouteResult]

class HotspotResponse(BaseModel):
    hotspots: List[Hotspot]
    total: int
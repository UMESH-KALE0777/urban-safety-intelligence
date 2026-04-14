from app.utils.geo import haversine
from app.utils.logger import get_logger

logger = get_logger(__name__)

TIME_WEIGHTS = {"day": 1.0, "evening": 1.4, "night": 1.9}

def calculate_risk(waypoints: list, hotspots: list, time_of_day: str = "day") -> float:
    tw = TIME_WEIGHTS.get(time_of_day, 1.0)
    score = 0.0
    for wp in waypoints:
        for h in hotspots:
            dist = haversine(wp, (h["lat"], h["lng"]))
            radius_km = h["radius"] / 1000
            if dist < radius_km * 1.5:
                weight = {"high": 4.0, "medium": 2.0, "low": 0.8}.get(h["risk"], 1.0)
                proximity = max(0, 1 - dist / (radius_km * 1.5))
                score += weight * proximity
    return round(score * tw, 2)

def to_safety_pct(score: float) -> int:
    return max(5, min(100, round(100 - score * 10)))
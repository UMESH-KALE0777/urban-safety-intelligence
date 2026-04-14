from app.utils.geo import haversine, midpoint
from app.ml.scorer import calculate_risk, to_safety_pct
from app.ml.clustering import get_hotspots
from app.utils.logger import get_logger

logger = get_logger(__name__)

def generate_routes(start: tuple, end: tuple, time_of_day: str = "day") -> list:
    hotspots = get_hotspots()
    dist = haversine(start, end)

    candidates = [
        {
            "name": "Route A",
            "waypoints": [start, midpoint(start, end,  0.012, -0.010), end],
            "distance_km": round(dist * 1.15, 1),
            "duration_min": round(dist * 5.0),
        },
        {
            "name": "Route B",
            "waypoints": [start, midpoint(start, end, -0.010,  0.012), end],
            "distance_km": round(dist * 1.05, 1),
            "duration_min": round(dist * 3.8),
        },
        {
            "name": "Route C",
            "waypoints": [start, midpoint(start, end,  0.018,  0.015), end],
            "distance_km": round(dist * 1.25, 1),
            "duration_min": round(dist * 5.8),
        },
    ]

    for r in candidates:
        r["risk_score"] = calculate_risk(r["waypoints"], hotspots, time_of_day)
        r["safety_pct"] = to_safety_pct(r["risk_score"])

    candidates.sort(key=lambda r: r["risk_score"])

    labels = ["safest", "fastest", "alternate"]
    for i, r in enumerate(candidates):
        r["label"] = labels[i]
        r["waypoints"] = [{"lat": wp[0], "lng": wp[1]} for wp in r["waypoints"]]

    logger.info(f"Generated {len(candidates)} routes | time={time_of_day}")
    return candidates
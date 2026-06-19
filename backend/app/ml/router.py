from app.ml.ors_client import get_alternative_routes
from app.ml.scorer import calculate_risk, to_safety_pct
from app.ml.clustering import get_hotspots
from app.utils.logger import get_logger

logger = get_logger(__name__)

def generate_routes(start: tuple, end: tuple, time_of_day: str = "day") -> list:
    hotspots = get_hotspots()

    raw_routes = get_alternative_routes(start, end, count=3)

    if not raw_routes:
        logger.error("No routes returned from ORS — check API key or coordinates")
        return []

    candidates = []
    for i, r in enumerate(raw_routes):
        candidates.append({
            "name": f"Route {chr(65+i)}",  # Route A, B, C
            "waypoints": r["waypoints"],
            "distance_km": r["distance_km"],
            "duration_min": r["duration_min"],
        })

    for r in candidates:
        r["risk_score"] = calculate_risk(r["waypoints"], hotspots, time_of_day)
        r["safety_pct"] = to_safety_pct(r["risk_score"])

    candidates.sort(key=lambda r: r["risk_score"])

    labels = ["safest", "fastest", "alternate"]
    for i, r in enumerate(candidates):
        r["label"] = labels[i] if i < len(labels) else "alternate"
        r["waypoints"] = [{"lat": wp[0], "lng": wp[1]} for wp in r["waypoints"]]

    logger.info(f"Generated {len(candidates)} real routes | time={time_of_day}")
    return candidates
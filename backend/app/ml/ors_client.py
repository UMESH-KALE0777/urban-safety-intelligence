import requests
from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

ORS_BASE_URL = "https://api.heigit.org/openrouteservice/v2/directions/driving-car/geojson"
def get_real_route(start: tuple, end: tuple) -> dict:
    headers = {
        "Authorization": settings.openrouteservice_api_key,
        "Content-Type": "application/json",
    }

    body = {
        "coordinates": [
            [start[1], start[0]],
            [end[1], end[0]],
        ]
    }

    try:
        res = requests.post(ORS_BASE_URL, json=body, headers=headers, timeout=10)
        res.raise_for_status()
        data = res.json()

        coords = data["features"][0]["geometry"]["coordinates"]
        waypoints = [(c[1], c[0]) for c in coords]

        summary = data["features"][0]["properties"]["summary"]
        distance_km = round(summary["distance"] / 1000, 2)
        duration_min = round(summary["duration"] / 60)

        return {
            "waypoints": waypoints,
            "distance_km": distance_km,
            "duration_min": duration_min,
        }
    except Exception as e:
        logger.error(f"ORS routing failed: {e}")
        return None


def get_alternative_routes(start: tuple, end: tuple, count: int = 3) -> list:
    headers = {
        "Authorization": settings.openrouteservice_api_key,
        "Content-Type": "application/json",
    }

    body = {
        "coordinates": [
            [start[1], start[0]],
            [end[1], end[0]],
        ],
        "alternative_routes": {
            "target_count": count,
            "weight_factor": 1.6,
            "share_factor": 0.6,
        },
    }

    try:
        res = requests.post(ORS_BASE_URL, json=body, headers=headers, timeout=10)
        res.raise_for_status()
        data = res.json()

        routes = []
        for feature in data["features"]:
            coords = feature["geometry"]["coordinates"]
            waypoints = [(c[1], c[0]) for c in coords]
            summary = feature["properties"]["summary"]
            routes.append({
                "waypoints": waypoints,
                "distance_km": round(summary["distance"] / 1000, 2),
                "duration_min": round(summary["duration"] / 60),
            })
        return routes
    except Exception as e:
        logger.error(f"ORS alternative routing failed: {e}")
        single = get_real_route(start, end)
        return [single] if single else []
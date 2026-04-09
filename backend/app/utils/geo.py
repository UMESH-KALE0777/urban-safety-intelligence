import math

def haversine(p1: tuple, p2: tuple) -> float:
    """Return distance in km between two (lat, lng) points."""
    R = 6371
    lat1, lng1 = math.radians(p1[0]), math.radians(p1[1])
    lat2, lng2 = math.radians(p2[0]), math.radians(p2[1])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def midpoint(p1: tuple, p2: tuple, offset_lat=0.0, offset_lng=0.0) -> tuple:
    """Return midpoint between two coords with optional offset."""
    return (
        (p1[0] + p2[0]) / 2 + offset_lat,
        (p1[1] + p2[1]) / 2 + offset_lng,
    )

def is_within_bangalore(lat: float, lng: float) -> bool:
    """Validate coordinates are within Bangalore bounding box."""
    return 12.80 <= lat <= 13.15 and 77.45 <= lng <= 77.78
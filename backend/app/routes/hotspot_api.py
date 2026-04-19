from fastapi import APIRouter
from app.ml.clustering import get_hotspots, run_clustering
from app.models.response import HotspotResponse

router = APIRouter()

@router.get("/", response_model=HotspotResponse)
def fetch_hotspots():
    hotspots = get_hotspots()
    return HotspotResponse(hotspots=hotspots, total=len(hotspots))

@router.post("/refresh")
def refresh_hotspots():
    """Re-run clustering — call this after adding new data."""
    hotspots = run_clustering()
    return {"message": "Hotspots refreshed", "total": len(hotspots)}
from fastapi import APIRouter
from app.models.request import RouteRequest
from app.models.response import RouteResponse
from app.ml.router import generate_routes

router = APIRouter()

@router.post("/safe", response_model=RouteResponse)
def get_safe_route(req: RouteRequest):
    routes = generate_routes(
        start=(req.start_lat, req.start_lng),
        end=(req.end_lat, req.end_lng),
        time_of_day=req.time_of_day,
    )
    return RouteResponse(routes=routes)
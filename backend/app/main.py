from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routes.route_api import router as route_router
from app.routes.hotspot_api import router as hotspot_router
from app.routes.health_api import router as health_router
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

app = FastAPI(
    title="Urban Safety Intelligence API",
    description="Safety-aware route recommender for Bangalore",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router,   prefix="/health",        tags=["Health"])
app.include_router(hotspot_router,  prefix="/api/hotspots",  tags=["Hotspots"])
app.include_router(route_router,    prefix="/api/routes",    tags=["Routes"])

@app.on_event("startup")
async def startup():
    logger.info("Urban Safety Intelligence API starting...")
    logger.info(f"Environment: {settings.app_env}")
from fastapi import APIRouter
from backend.app.api.v1.endpoints import health, panchayats, forecast

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="", tags=["Health"])
api_router.include_router(panchayats.router, prefix="", tags=["Panchayats"])
api_router.include_router(forecast.router, prefix="", tags=["Forecasts"])

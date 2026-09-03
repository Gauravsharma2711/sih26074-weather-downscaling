from typing import Dict, Any
from fastapi import APIRouter, status, Response
from backend.app.core.database import check_db_connection
from backend.app.core.config import settings

router = APIRouter()


@router.get("/health", response_model=Dict[str, str], tags=["Health"])
def health_check() -> Dict[str, str]:
    """
    Standard application health check endpoint.
    Returns {"status": "ok"} when the service is running.
    """
    return {"status": "ok"}


@router.get("/health/db", response_model=Dict[str, Any], tags=["Health"])
def database_health_check(response: Response) -> Dict[str, Any]:
    """
    Database health check endpoint.
    Verifies connection to the Supabase PostgreSQL database and inspects panchayat_weather_data.
    """
    db_info = check_db_connection()
    if not db_info.get("connected"):
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        
    return {
        "status": "ok" if db_info.get("connected") else "error",
        "service": settings.PROJECT_NAME,
        "database": db_info,
    }


@router.get("/health/details", response_model=Dict[str, Any], tags=["Health"])
def detailed_health_check(response: Response) -> Dict[str, Any]:
    """
    Detailed system health check including service environment and database diagnostic status.
    """
    db_info = check_db_connection()
    is_healthy = db_info.get("connected", False)
    if not is_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "ok" if is_healthy else "degraded",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "database": db_info,
    }

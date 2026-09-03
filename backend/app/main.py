from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.database import check_db_connection
from backend.app.api.v1.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="SIH26074: Downscaling of Weather Forecasts from Block Level to Panchayat Level for Agro-Meteorological Advisory Services",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# Configure CORS Middleware
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Root health endpoint directly at /health
@app.get("/health", tags=["Health"])
def root_health():
    """
    Direct root health check endpoint.
    Returns {"status": "ok"}
    """
    return {"status": "ok"}


# Direct database health check endpoint at /health/db
@app.get("/health/db", tags=["Health"])
def root_db_health(response: Response):
    """
    Direct root database health check endpoint.
    """
    db_info = check_db_connection()
    if not db_info.get("connected"):
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {
        "status": "ok" if db_info.get("connected") else "error",
        "service": settings.PROJECT_NAME,
        "database": db_info,
    }


# Include API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG,
    )

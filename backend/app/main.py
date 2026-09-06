from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.logging import setup_logging
from backend.app.core.database import check_db_connection
from backend.app.api.v1.router import api_router

# Initialize structured application logging
setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="SIH26074: Downscaling of Weather Forecasts from Block Level to Panchayat Level for Agro-Meteorological Advisory Services",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Also expose OpenAPI schema at /api/v1/openapi.json and documentation at /api/v1/docs
@app.get("/api/v1/openapi.json", include_in_schema=False)
def get_v1_openapi():
    return app.openapi()


@app.get("/api/v1/docs", include_in_schema=False)
def get_v1_docs():
    from fastapi.openapi.docs import get_swagger_ui_html
    return get_swagger_ui_html(openapi_url="/api/v1/openapi.json", title=f"{settings.PROJECT_NAME} - Swagger UI")


@app.get("/api/v1/redoc", include_in_schema=False)
def get_v1_redoc():
    from fastapi.openapi.docs import get_redoc_html
    return get_redoc_html(openapi_url="/api/v1/openapi.json", title=f"{settings.PROJECT_NAME} - ReDoc")

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

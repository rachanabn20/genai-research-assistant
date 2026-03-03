"""
FastAPI Application Entry Point
--------------------------------
Minimal configuration to ensure stable CI behavior.
"""

from fastapi import FastAPI
from app.routes import router
from core.config import get_settings


# Load settings once
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="GenAI Research Assistant API",
)


# Root endpoint (must return JSON for CI tests)
@app.get("/", tags=["Root"])
def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "status": "running",
    }


# Include API routes
app.include_router(router)

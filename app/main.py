"""
FastAPI Application Entry Point
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.routes import router
from core.config import get_settings
from core.logging_config import setup_logging, get_logger
from core.security import limiter


# Load settings ONCE
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    log = get_logger("app.main")

    log.info(
        "application_starting",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
    )

    yield

    log.info("application_shutting_down")


# Create app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)


# ✅ DEFINE ROOT FIRST (IMPORTANT)
@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "status": "running",
    }


# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log = get_logger("app.main")
    log.error("unhandled_exception", error=str(exc))

    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error"},
    )


# Include API routes AFTER root
app.include_router(router)


# Optional frontend
static_dir = Path(__file__).parent.parent / "static"

if static_dir.exists():

    @app.get("/app")
    async def serve_frontend():
        return FileResponse(static_dir / "index.html")

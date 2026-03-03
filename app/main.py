"""
FastAPI Application Entry Point
----------------------------------
Creates the app, configures middleware, registers routes,
and serves the frontend interface.
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


# ==========================================
# Load settings ONCE (important for CI)
# ==========================================

settings = get_settings()


# ==========================================
# Lifespan Events
# ==========================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs on application startup and shutdown."""
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


# ==========================================
# App Initialization
# ==========================================

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "AI-powered research paper analysis using RAG. "
        "Upload PDFs, ask questions, get summaries and analysis. "
        "Include X-API-Key header in all requests."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ==========================================
# Middleware
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ==========================================
# Global Exception Handler
# ==========================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch unhandled exceptions and return clean error responses."""
    log = get_logger("app.main")

    log.error(
        "unhandled_exception",
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred. Please try again later.",
        },
    )


# ==========================================
# Root Endpoint (CI Critical)
# ==========================================

@app.get("/", tags=["Root"])
async def root():
    """Return application information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "status": "running",
    }


# ==========================================
# Include API Routes
# ==========================================

app.include_router(router)


# ==========================================
# Serve Frontend (Optional)
# ==========================================

static_dir = Path(__file__).parent.parent / "static"

if static_dir.exists():

    @app.get("/app", tags=["Frontend"])
    async def serve_frontend():
        """Serve the frontend interface."""
        return FileResponse(static_dir / "index.html")

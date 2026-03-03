from fastapi import FastAPI
from app.routes import router
from core.config import get_settings
from core.security import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

# Attach rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/", tags=["Root"])
async def root():
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "docs": "/docs",
    }


app.include_router(router)

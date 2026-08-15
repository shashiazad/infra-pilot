from fastapi import FastAPI

from app.api.v1.health import router as health_router
from app.api.v1.incidents import router as incidents_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Agentic AI platform for "
        "infrastructure incident response."
    ),
)


app.include_router(
    health_router,
    prefix="/api/v1",
)

app.include_router(
    incidents_router,
    prefix="/api/v1",
)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "service": settings.app_name,
        "version": settings.app_version,
    }
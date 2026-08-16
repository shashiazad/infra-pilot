from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.health import router as health_router
from app.api.v1.incidents import router as incidents_router
from app.api.v1.investigations import (
    router as investigations_router,
)
from app.api.v1.runbooks import router as runbooks_router
from app.api.v1.services import router as services_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=("Agentic AI platform for infrastructure incident response."),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    health_router,
    prefix="/api/v1",
)

app.include_router(
    incidents_router,
    prefix="/api/v1",
)

app.include_router(
    investigations_router,
    prefix="/api/v1",
)

app.include_router(runbooks_router, prefix="/api/v1")
app.include_router(services_router, prefix="/api/v1")


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "service": settings.app_name,
        "version": settings.app_version,
    }

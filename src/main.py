"""
DERMS FastAPI application entrypoint.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router
from src.utils.config import get_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler — startup and shutdown logic."""
    logger.info("DERMS starting up", extra={"version": "0.1.0"})
    # TODO: initialise database connection pool, Redis client, MQTT subscriber
    yield
    logger.info("DERMS shutting down")
    # TODO: gracefully close connections


app = FastAPI(
    title="DERMS — Virtual Power Plant API",
    description=(
        "REST API for managing, monitoring, and optimising Distributed Energy "
        "Resources (DERs) including batteries, solar arrays, EV chargers, and "
        "demand-response loads."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/health", tags=["health"], summary="Health check")
async def health_check() -> dict:
    """Return the health status of DERMS and its dependencies."""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "simulation_mode": settings.simulation_mode,
    }

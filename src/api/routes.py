"""
DERMS REST API routes.

Registers all resource, optimization, and forecasting endpoints.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from src.core.derms_engine import DERMSEngine
from src.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()
engine = DERMSEngine()


# ---------------------------------------------------------------------------
# Request / Response schemas (inline for brevity — move to schemas.py later)
# ---------------------------------------------------------------------------


class RegisterResourceRequest(BaseModel):
    name: str
    type: str  # battery | solar | ev | load
    site_id: str
    capacity_kw: float
    metadata: dict = {}


class OptimizeRequest(BaseModel):
    horizon_hours: int = 24
    objective: str = "maximize_revenue"
    min_soc: float = 0.10
    max_soc: float = 0.95
    grid_export_limit_kw: float = 1000.0


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------


@router.get("/resources", tags=["resources"], summary="List all DERs")
async def list_resources(
    type: str | None = None,
    site_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    """Return a paginated list of registered Distributed Energy Resources."""
    resources = await engine.list_resources(
        type_filter=type, site_id=site_id, limit=limit, offset=offset
    )
    return {"total": len(resources), "resources": resources}


@router.post(
    "/resources",
    tags=["resources"],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new DER",
)
async def register_resource(payload: RegisterResourceRequest) -> dict:
    """Register a new Distributed Energy Resource with DERMS."""
    resource = await engine.register_resource(payload.model_dump())
    logger.info("Resource registered", extra={"resource_id": resource["id"]})
    return resource


@router.get(
    "/resources/{resource_id}/status",
    tags=["resources"],
    summary="Get real-time DER status",
)
async def get_resource_status(resource_id: str) -> dict:
    """Return the latest telemetry snapshot for a given DER."""
    status_data = await engine.get_resource_status(resource_id)
    if status_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource '{resource_id}' not found.",
        )
    return status_data


# ---------------------------------------------------------------------------
# Optimization
# ---------------------------------------------------------------------------


@router.post(
    "/optimize",
    tags=["optimization"],
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger an optimization run",
)
async def trigger_optimization(payload: OptimizeRequest) -> dict:
    """Queue an optimization job for all registered DERs."""
    job_id = await engine.run_optimization(payload.model_dump())
    return {"job_id": job_id, "status": "queued"}


# ---------------------------------------------------------------------------
# Forecasting
# ---------------------------------------------------------------------------


@router.get("/forecast", tags=["forecasting"], summary="Get load forecast")
async def get_forecast(
    site_id: str | None = None,
    horizon_h: int = 24,
    interval: str = "15min",
) -> dict:
    """Return the latest probabilistic load forecast."""
    forecast = await engine.get_forecast(
        site_id=site_id, horizon_hours=horizon_h, interval=interval
    )
    return forecast

"""
DERMS Engine — central orchestration service.

Manages DER registration, state tracking, optimization dispatch,
and forecast retrieval. In production this class wraps database and
Redis calls; in simulation mode it operates with in-memory state.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from src.utils.logger import get_logger

logger = get_logger(__name__)


class DERMSEngine:
    """Central orchestration engine for the DERMS platform.

    Responsibilities:
    - Maintain a registry of all Distributed Energy Resources (DERs).
    - Provide real-time status snapshots (from Redis cache in production).
    - Trigger and track optimization jobs.
    - Surface load forecasts from the ML forecasting module.
    """

    def __init__(self) -> None:
        # In-memory store for simulation / testing.
        # Replace with async DB + Redis clients in production.
        self._resources: dict[str, dict[str, Any]] = {}
        self._jobs: dict[str, dict[str, Any]] = {}
        logger.info("DERMSEngine initialised")

    # ------------------------------------------------------------------
    # Resource management
    # ------------------------------------------------------------------

    async def register_resource(self, data: dict[str, Any]) -> dict[str, Any]:
        """Register a new DER and return the created record.

        Args:
            data: Validated resource payload from the API layer.

        Returns:
            The persisted resource record including the generated ``id``.
        """
        resource_id = f"res-{uuid.uuid4().hex[:8]}"
        record = {
            "id": resource_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "online",
            **data,
        }
        self._resources[resource_id] = record
        logger.info(
            "Resource registered",
            extra={"id": resource_id, "type": data.get("type")},
        )
        return record

    async def list_resources(
        self,
        type_filter: str | None = None,
        site_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Return a filtered, paginated list of registered DERs.

        Args:
            type_filter: Optional DER type filter (``battery``, ``solar``, etc.).
            site_id: Optional site identifier filter.
            limit: Maximum number of records to return.
            offset: Pagination offset.

        Returns:
            List of resource records matching the filter criteria.
        """
        resources = list(self._resources.values())
        if type_filter:
            resources = [r for r in resources if r.get("type") == type_filter]
        if site_id:
            resources = [r for r in resources if r.get("site_id") == site_id]
        return resources[offset : offset + limit]

    async def get_resource_status(
        self, resource_id: str
    ) -> dict[str, Any] | None:
        """Return the latest telemetry snapshot for a DER.

        In production this reads from the Redis cache populated by the
        telemetry service. Here it returns a synthetic snapshot.

        Args:
            resource_id: The unique DER identifier.

        Returns:
            Status dict or ``None`` if the resource is not found.
        """
        resource = self._resources.get(resource_id)
        if resource is None:
            return None
        return {
            "id": resource_id,
            "type": resource.get("type"),
            "status": resource.get("status", "unknown"),
            "power_kw": 0.0,
            "state_of_charge": 0.5 if resource.get("type") == "battery" else None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Optimization
    # ------------------------------------------------------------------

    async def run_optimization(self, params: dict[str, Any]) -> str:
        """Queue an optimization job and return the job ID.

        Args:
            params: Optimization parameters (horizon, objective, constraints).

        Returns:
            Unique job identifier string.
        """
        from src.core.optimizer import BatteryOptimizer

        job_id = f"opt-{uuid.uuid4().hex[:8]}"
        self._jobs[job_id] = {"status": "queued", "params": params}

        # In production: push to task queue (Celery / ARQ).
        # For now, run synchronously in background.
        optimizer = BatteryOptimizer()
        resources = list(self._resources.values())
        result = optimizer.optimize(resources=resources, params=params)
        self._jobs[job_id] = {"status": "completed", "result": result}

        logger.info("Optimization job completed", extra={"job_id": job_id})
        return job_id

    # ------------------------------------------------------------------
    # Forecasting
    # ------------------------------------------------------------------

    async def get_forecast(
        self,
        site_id: str | None,
        horizon_hours: int,
        interval: str,
    ) -> dict[str, Any]:
        """Return the current load forecast from the ML module.

        Args:
            site_id: Optional site to scope the forecast.
            horizon_hours: Number of hours to forecast ahead.
            interval: Temporal resolution (``15min`` or ``1h``).

        Returns:
            Forecast payload with probabilistic load estimates.
        """
        from src.models.load_forecaster import LoadForecast, generate_dummy_forecast

        forecast_points = generate_dummy_forecast(
            horizon_hours=horizon_hours, interval=interval
        )
        return {
            "site_id": site_id or "all",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "horizon_hours": horizon_hours,
            "interval": interval,
            "forecast": [p.model_dump() for p in forecast_points],
        }

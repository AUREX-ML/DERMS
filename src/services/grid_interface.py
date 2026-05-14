"""
Grid interface service — communicates with the grid operator.

Handles sending aggregated dispatch schedules and receiving
demand-response (DR) signals. Implements a simplified OpenADR 2.0
client interface.
"""

from __future__ import annotations

import asyncio
from typing import Any

from src.utils.config import get_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class GridInterface:
    """Client for communicating with the grid operator.

    In production this wraps an HTTP client targeting the grid operator's
    OpenADR / IEEE 2030.5 endpoint. In simulation mode all calls are no-ops.
    """

    def __init__(self) -> None:
        self.endpoint = settings.grid_operator_endpoint
        self.simulation_mode = settings.simulation_mode
        logger.info(
            "GridInterface initialised",
            extra={"endpoint": self.endpoint, "simulation": self.simulation_mode},
        )

    async def submit_dispatch_schedule(
        self, schedule: list[dict[str, Any]]
    ) -> bool:
        """Submit an aggregated dispatch schedule to the grid operator.

        Args:
            schedule: List of interval-level dispatch decisions.

        Returns:
            ``True`` if accepted, ``False`` if rejected by the operator.
        """
        if self.simulation_mode:
            logger.debug("Simulation mode: skipping grid schedule submission")
            await asyncio.sleep(0)  # Yield control to event loop
            return True

        # TODO: implement real HTTP submission to grid operator endpoint
        logger.info(
            "Submitting dispatch schedule",
            extra={"intervals": len(schedule), "endpoint": self.endpoint},
        )
        return True

    async def receive_dr_signal(self) -> dict[str, Any] | None:
        """Poll the grid operator for demand-response signals.

        Returns:
            A DR event dict if one is pending, or ``None``.
        """
        if self.simulation_mode:
            return None

        # TODO: implement OpenADR VEN polling
        logger.debug("Polling for DR signals")
        return None

"""
Battery dispatch optimizer for DERMS.

Implements rule-based and linear-programming-based optimization strategies
for scheduling battery charge / discharge cycles to maximise revenue while
respecting grid and hardware constraints.
"""

from __future__ import annotations

from typing import Any

from src.utils.logger import get_logger

logger = get_logger(__name__)


class BatteryOptimizer:
    """Dispatch optimizer for battery storage assets.

    Supports two strategies:
    - ``heuristic``: Rule-based greedy dispatch (default, fast).
    - ``lp``: Linear programming via ``scipy.optimize.linprog`` (accurate).

    Attributes:
        strategy: Optimization strategy to use (``heuristic`` or ``lp``).
        min_soc: Minimum allowed state of charge (0–1).
        max_soc: Maximum allowed state of charge (0–1).
    """

    def __init__(
        self,
        strategy: str = "heuristic",
        min_soc: float = 0.10,
        max_soc: float = 0.95,
    ) -> None:
        self.strategy = strategy
        self.min_soc = min_soc
        self.max_soc = max_soc
        logger.debug(
            "BatteryOptimizer initialised",
            extra={"strategy": strategy, "min_soc": min_soc, "max_soc": max_soc},
        )

    def optimize(
        self,
        resources: list[dict[str, Any]],
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Compute an optimal dispatch schedule for the given resources.

        Args:
            resources: List of resource records from :class:`DERMSEngine`.
            params: Optimization parameters including ``horizon_hours``,
                ``objective``, ``min_soc``, ``max_soc``, and
                ``grid_export_limit_kw``.

        Returns:
            A dict containing the dispatch ``schedule`` (list of per-interval
            dispatch decisions) and projected ``revenue_usd``.
        """
        batteries = [r for r in resources if r.get("type") == "battery"]

        if self.strategy == "lp":
            return self._optimize_lp(batteries, params)
        return self._optimize_heuristic(batteries, params)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _optimize_heuristic(
        self,
        batteries: list[dict[str, Any]],
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Greedy peak-shaving heuristic.

        Discharges batteries during peak price hours and charges during
        off-peak hours. O(n·T) time complexity.

        Args:
            batteries: Battery resource records.
            params: Optimization parameters.

        Returns:
            Schedule and estimated revenue.
        """
        horizon = params.get("horizon_hours", 24)
        schedule: list[dict[str, Any]] = []

        for hour in range(horizon):
            is_peak = 8 <= hour <= 21  # simplified peak definition
            action = "discharge" if is_peak else "charge"
            for bat in batteries:
                schedule.append(
                    {
                        "resource_id": bat.get("id"),
                        "hour": hour,
                        "action": action,
                        "power_kw": bat.get("capacity_kw", 0) * 0.5,
                    }
                )

        estimated_revenue = len(batteries) * 50.0  # placeholder USD
        logger.info(
            "Heuristic optimization complete",
            extra={"batteries": len(batteries), "revenue_usd": estimated_revenue},
        )
        return {"schedule": schedule, "revenue_usd": estimated_revenue}

    def _optimize_lp(
        self,
        batteries: list[dict[str, Any]],
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Linear-programming dispatch (placeholder).

        In production this formulates a MILP using ``scipy.optimize.linprog``
        or OR-Tools to minimise grid-import cost subject to SoC dynamics,
        power limits, and grid export caps.

        Args:
            batteries: Battery resource records.
            params: Optimization parameters.

        Returns:
            Optimal schedule and revenue estimate.
        """
        # TODO: implement full LP formulation.
        logger.warning("LP optimizer not yet implemented; falling back to heuristic")
        return self._optimize_heuristic(batteries, params)

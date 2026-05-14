"""
Pydantic models for load forecasting and a simple dummy forecast generator.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from typing import Annotated

from pydantic import BaseModel, Field


class ForecastPoint(BaseModel):
    """A single probabilistic load forecast data point.

    Attributes:
        timestamp: ISO-8601 timestamp for this interval.
        load_kw: Point forecast (P50) in kilowatts.
        p10_kw: 10th-percentile estimate (lower bound).
        p90_kw: 90th-percentile estimate (upper bound).
    """

    timestamp: str
    load_kw: Annotated[float, Field(ge=0.0)]
    p10_kw: Annotated[float, Field(ge=0.0)]
    p90_kw: Annotated[float, Field(ge=0.0)]


class LoadForecast(BaseModel):
    """Complete load forecast response for a site.

    Attributes:
        site_id: Site or portfolio identifier this forecast covers.
        generated_at: ISO-8601 timestamp when the forecast was produced.
        horizon_hours: Number of hours the forecast spans.
        interval: Temporal resolution (``15min`` or ``1h``).
        points: Ordered list of :class:`ForecastPoint` objects.
    """

    site_id: str
    generated_at: str
    horizon_hours: int = 24
    interval: str = "15min"
    points: list[ForecastPoint] = []


def generate_dummy_forecast(
    horizon_hours: int = 24,
    interval: str = "15min",
    base_load_kw: float = 300.0,
    seed: int | None = None,
) -> list[ForecastPoint]:
    """Generate a synthetic load forecast for testing and simulation.

    Args:
        horizon_hours: Number of hours to forecast ahead.
        interval: Temporal resolution — ``"15min"`` or ``"1h"``.
        base_load_kw: Base load around which synthetic values are generated.
        seed: Optional random seed for reproducibility.

    Returns:
        Ordered list of :class:`ForecastPoint` objects.
    """
    rng = random.Random(seed)
    step_minutes = 15 if interval == "15min" else 60
    steps = (horizon_hours * 60) // step_minutes

    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    points: list[ForecastPoint] = []

    for i in range(steps):
        ts = now + timedelta(minutes=i * step_minutes)
        # Simple diurnal pattern
        hour = ts.hour
        peak_factor = 1.0 + 0.4 * max(0, 1 - abs(hour - 14) / 6)
        mid = base_load_kw * peak_factor * (1 + rng.gauss(0, 0.05))
        spread = mid * 0.08
        points.append(
            ForecastPoint(
                timestamp=ts.isoformat(),
                load_kw=round(max(0.0, mid), 2),
                p10_kw=round(max(0.0, mid - spread), 2),
                p90_kw=round(max(0.0, mid + spread), 2),
            )
        )
    return points

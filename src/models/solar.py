"""
Pydantic model for a solar photovoltaic (PV) array.
"""

from __future__ import annotations

from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, field_validator


class SolarStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    CURTAILED = "curtailed"
    FAULT = "fault"
    MAINTENANCE = "maintenance"


class SolarPanel(BaseModel):
    """Represents a solar photovoltaic (PV) installation.

    Attributes:
        id: Unique resource identifier.
        name: Human-readable asset name.
        site_id: Site or location identifier.
        capacity_kw: DC nameplate capacity in kilowatts.
        panel_count: Number of individual PV panels.
        inverter_efficiency: DC-to-AC inverter efficiency (0.0 – 1.0).
        tilt_angle: Panel tilt angle in degrees from horizontal (0 – 90).
        azimuth: Panel azimuth in degrees (0 = North, 180 = South).
        degradation_rate: Annual capacity degradation rate (0.0 – 1.0).
        current_output_kw: Current active power output.
        status: Current operational status.
    """

    id: str
    name: str
    site_id: str
    capacity_kw: Annotated[float, Field(gt=0, description="DC nameplate kW")]
    panel_count: Annotated[int, Field(gt=0)]
    inverter_efficiency: Annotated[float, Field(gt=0.0, le=1.0)] = 0.97
    tilt_angle: Annotated[float, Field(ge=0.0, le=90.0)] = 30.0
    azimuth: Annotated[float, Field(ge=0.0, lt=360.0)] = 180.0
    degradation_rate: Annotated[float, Field(ge=0.0, le=0.05)] = 0.005
    current_output_kw: Annotated[float, Field(ge=0.0)] = 0.0
    status: SolarStatus = SolarStatus.ONLINE

    @field_validator("current_output_kw")
    @classmethod
    def output_cannot_exceed_capacity(cls, v: float, info) -> float:
        capacity = info.data.get("capacity_kw")
        if capacity is not None and v > capacity:
            raise ValueError(
                f"current_output_kw ({v}) cannot exceed capacity_kw ({capacity})"
            )
        return v

    @property
    def ac_capacity_kw(self) -> float:
        """AC capacity after inverter losses."""
        return self.capacity_kw * self.inverter_efficiency

    @property
    def capacity_factor(self) -> float:
        """Instantaneous capacity factor (0.0 – 1.0)."""
        if self.capacity_kw == 0:
            return 0.0
        return self.current_output_kw / self.capacity_kw

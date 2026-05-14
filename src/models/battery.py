"""
Pydantic model for a battery storage asset.
"""

from __future__ import annotations

from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, field_validator


class BatteryStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    CHARGING = "charging"
    DISCHARGING = "discharging"
    FAULT = "fault"
    STANDBY = "standby"


class BatteryStorage(BaseModel):
    """Represents a battery energy storage system (BESS).

    Attributes:
        id: Unique resource identifier.
        name: Human-readable asset name.
        site_id: Site or location identifier.
        capacity_kwh: Usable energy capacity in kilowatt-hours.
        max_charge_rate_kw: Maximum charge power in kilowatts.
        max_discharge_rate_kw: Maximum discharge power in kilowatts.
        state_of_charge: Current SoC as a fraction (0.0 – 1.0).
        min_soc: Minimum permitted SoC to preserve battery health.
        max_soc: Maximum permitted SoC to preserve battery health.
        round_trip_efficiency: AC-AC round-trip efficiency (0.0 – 1.0).
        cycle_count: Number of full charge/discharge cycles completed.
        status: Current operational status.
    """

    id: str
    name: str
    site_id: str
    capacity_kwh: Annotated[float, Field(gt=0, description="kWh, must be positive")]
    max_charge_rate_kw: Annotated[float, Field(gt=0)]
    max_discharge_rate_kw: Annotated[float, Field(gt=0)]
    state_of_charge: Annotated[float, Field(ge=0.0, le=1.0)] = 0.5
    min_soc: Annotated[float, Field(ge=0.0, le=1.0)] = 0.10
    max_soc: Annotated[float, Field(ge=0.0, le=1.0)] = 0.95
    round_trip_efficiency: Annotated[float, Field(gt=0.0, le=1.0)] = 0.92
    cycle_count: Annotated[int, Field(ge=0)] = 0
    status: BatteryStatus = BatteryStatus.STANDBY

    @field_validator("max_soc")
    @classmethod
    def max_soc_must_exceed_min(cls, v: float, info) -> float:
        min_soc = info.data.get("min_soc", 0.0)
        if v <= min_soc:
            raise ValueError(f"max_soc ({v}) must be greater than min_soc ({min_soc})")
        return v

    @field_validator("state_of_charge")
    @classmethod
    def soc_within_limits(cls, v: float, info) -> float:
        min_soc = info.data.get("min_soc", 0.0)
        max_soc = info.data.get("max_soc", 1.0)
        if not (min_soc <= v <= max_soc):
            raise ValueError(
                f"state_of_charge ({v}) must be between min_soc ({min_soc}) "
                f"and max_soc ({max_soc})"
            )
        return v

    @property
    def available_energy_kwh(self) -> float:
        """Energy available to discharge above min_soc."""
        return (self.state_of_charge - self.min_soc) * self.capacity_kwh

    @property
    def headroom_kwh(self) -> float:
        """Capacity available to absorb charge below max_soc."""
        return (self.max_soc - self.state_of_charge) * self.capacity_kwh

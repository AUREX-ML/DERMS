"""
Unit tests for the BatteryStorage Pydantic model.
"""

import pytest

from src.models.battery import BatteryStorage, BatteryStatus


def _make_battery(**overrides) -> BatteryStorage:
    """Helper: create a valid BatteryStorage with sensible defaults."""
    defaults = {
        "id": "bat-test-001",
        "name": "Test Battery",
        "site_id": "site-test",
        "capacity_kwh": 500.0,
        "max_charge_rate_kw": 100.0,
        "max_discharge_rate_kw": 100.0,
        "state_of_charge": 0.5,
        "min_soc": 0.10,
        "max_soc": 0.95,
    }
    defaults.update(overrides)
    return BatteryStorage(**defaults)


class TestBatteryStorageValidation:
    def test_valid_battery_created_successfully(self):
        bat = _make_battery()
        assert bat.id == "bat-test-001"
        assert bat.capacity_kwh == 500.0
        assert bat.status == BatteryStatus.STANDBY

    def test_negative_capacity_raises(self):
        with pytest.raises(ValueError, match="greater than 0"):
            _make_battery(capacity_kwh=-10.0)

    def test_max_soc_must_exceed_min_soc(self):
        with pytest.raises(ValueError, match="max_soc"):
            _make_battery(min_soc=0.5, max_soc=0.4, state_of_charge=0.5)

    def test_state_of_charge_outside_limits_raises(self):
        with pytest.raises(ValueError):
            _make_battery(min_soc=0.20, max_soc=0.95, state_of_charge=0.10)

    def test_round_trip_efficiency_cannot_exceed_one(self):
        with pytest.raises(ValueError):
            _make_battery(round_trip_efficiency=1.1)


class TestBatteryStorageProperties:
    def test_available_energy_kwh(self):
        bat = _make_battery(capacity_kwh=500.0, state_of_charge=0.6, min_soc=0.10)
        # (0.6 - 0.1) * 500 = 250
        assert pytest.approx(bat.available_energy_kwh, rel=1e-3) == 250.0

    def test_headroom_kwh(self):
        bat = _make_battery(capacity_kwh=500.0, state_of_charge=0.6, max_soc=0.95)
        # (0.95 - 0.6) * 500 = 175
        assert pytest.approx(bat.headroom_kwh, rel=1e-3) == 175.0

    def test_fully_discharged_available_energy_is_zero(self):
        bat = _make_battery(min_soc=0.10, state_of_charge=0.10, max_soc=0.95)
        assert bat.available_energy_kwh == pytest.approx(0.0, abs=1e-6)

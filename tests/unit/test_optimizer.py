"""
Unit tests for the BatteryOptimizer.
"""

from src.core.optimizer import BatteryOptimizer


def _make_battery_resource(
    resource_id: str = "bat-001", capacity_kw: float = 100.0
) -> dict:
    return {
        "id": resource_id,
        "type": "battery",
        "site_id": "site-a",
        "capacity_kw": capacity_kw,
        "state_of_charge": 0.5,
    }


class TestBatteryOptimizerHeuristic:
    def test_returns_schedule_and_revenue(self):
        optimizer = BatteryOptimizer(strategy="heuristic")
        resources = [_make_battery_resource()]
        result = optimizer.optimize(resources, {"horizon_hours": 24})
        assert "schedule" in result
        assert "revenue_usd" in result
        assert result["revenue_usd"] > 0

    def test_schedule_has_correct_number_of_intervals(self):
        optimizer = BatteryOptimizer(strategy="heuristic")
        resources = [
            _make_battery_resource("bat-001"),
            _make_battery_resource("bat-002"),
        ]
        result = optimizer.optimize(resources, {"horizon_hours": 12})
        # 12 hours × 2 batteries = 24 schedule entries
        assert len(result["schedule"]) == 24

    def test_discharge_during_peak_hours(self):
        optimizer = BatteryOptimizer(strategy="heuristic")
        resources = [_make_battery_resource()]
        result = optimizer.optimize(resources, {"horizon_hours": 24})
        peak_entries = [e for e in result["schedule"] if 8 <= e["hour"] <= 21]
        assert all(e["action"] == "discharge" for e in peak_entries)

    def test_charge_during_off_peak_hours(self):
        optimizer = BatteryOptimizer(strategy="heuristic")
        resources = [_make_battery_resource()]
        result = optimizer.optimize(resources, {"horizon_hours": 24})
        off_peak = [e for e in result["schedule"] if e["hour"] < 8 or e["hour"] > 21]
        assert all(e["action"] == "charge" for e in off_peak)


class TestBatteryOptimizerLP:
    def test_lp_falls_back_to_heuristic(self):
        """LP optimizer currently falls back to heuristic — result is non-empty."""
        optimizer = BatteryOptimizer(strategy="lp")
        resources = [_make_battery_resource()]
        result = optimizer.optimize(resources, {"horizon_hours": 24})
        assert "schedule" in result
        assert len(result["schedule"]) > 0


class TestBatteryOptimizerEdgeCases:
    def test_no_batteries_returns_empty_schedule(self):
        optimizer = BatteryOptimizer()
        result = optimizer.optimize(resources=[], params={"horizon_hours": 24})
        assert result["schedule"] == []

    def test_solar_resources_are_ignored(self):
        optimizer = BatteryOptimizer()
        solar = {"id": "sol-001", "type": "solar", "capacity_kw": 200.0}
        result = optimizer.optimize(resources=[solar], params={"horizon_hours": 24})
        assert result["schedule"] == []

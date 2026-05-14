"""
Unit tests for the load forecaster.
"""

import pytest

from src.models.load_forecaster import (
    ForecastPoint,
    LoadForecast,
    generate_dummy_forecast,
)


class TestForecastPoint:
    def test_valid_forecast_point(self):
        point = ForecastPoint(
            timestamp="2026-05-14T09:00:00+00:00",
            load_kw=300.0,
            p10_kw=270.0,
            p90_kw=330.0,
        )
        assert point.load_kw == 300.0
        assert point.p10_kw <= point.load_kw <= point.p90_kw

    def test_negative_load_raises(self):
        with pytest.raises(ValueError):
            ForecastPoint(
                timestamp="2026-05-14T09:00:00+00:00",
                load_kw=-10.0,
                p10_kw=-15.0,
                p90_kw=-5.0,
            )


class TestGenerateDummyForecast:
    def test_correct_number_of_points_15min(self):
        points = generate_dummy_forecast(horizon_hours=24, interval="15min")
        # 24 h × 4 intervals/h = 96
        assert len(points) == 96

    def test_correct_number_of_points_1h(self):
        points = generate_dummy_forecast(horizon_hours=24, interval="1h")
        assert len(points) == 24

    def test_all_values_non_negative(self):
        points = generate_dummy_forecast(horizon_hours=48, interval="15min", seed=0)
        for p in points:
            assert p.load_kw >= 0.0
            assert p.p10_kw >= 0.0
            assert p.p90_kw >= 0.0

    def test_reproducible_with_seed(self):
        points_a = generate_dummy_forecast(horizon_hours=24, interval="1h", seed=42)
        points_b = generate_dummy_forecast(horizon_hours=24, interval="1h", seed=42)
        assert [p.load_kw for p in points_a] == [p.load_kw for p in points_b]

    def test_different_seeds_produce_different_results(self):
        points_a = generate_dummy_forecast(horizon_hours=24, interval="1h", seed=1)
        points_b = generate_dummy_forecast(horizon_hours=24, interval="1h", seed=2)
        assert [p.load_kw for p in points_a] != [p.load_kw for p in points_b]

    def test_timestamps_are_sequential(self):
        from datetime import datetime, timezone

        points = generate_dummy_forecast(horizon_hours=2, interval="1h", seed=0)
        timestamps = [datetime.fromisoformat(p.timestamp) for p in points]
        deltas = [
            (timestamps[i + 1] - timestamps[i]).seconds
            for i in range(len(timestamps) - 1)
        ]
        assert all(d == 3600 for d in deltas)

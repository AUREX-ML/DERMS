#!/usr/bin/env python3
"""
DERMS Simulation Runner.

Runs a standalone DERMS simulation without requiring live hardware or
network connections. Generates synthetic DER data, runs the optimization
engine, and prints a summary report.

Usage:
    python scripts/run_simulation.py --duration 3600 --resources 20 --seed 42
"""

import argparse
import asyncio
import os
import random
import sys
import time

# Ensure the project root is on the path so ``src`` imports work.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.derms_engine import DERMSEngine  # noqa: E402
from src.core.optimizer import BatteryOptimizer  # noqa: E402
from src.models.load_forecaster import generate_dummy_forecast  # noqa: E402
from src.utils.logger import get_logger  # noqa: E402

logger = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="DERMS Simulation Runner",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=3600,
        help="Simulation duration in seconds",
    )
    parser.add_argument(
        "--resources",
        type=int,
        default=10,
        help="Number of synthetic DER assets to create",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=0,
        help="Random seed for reproducibility",
    )
    parser.add_argument(
        "--horizon",
        type=int,
        default=24,
        help="Optimization horizon in hours",
    )
    return parser.parse_args()


def generate_synthetic_resources(n: int, rng: random.Random) -> list[dict]:
    """Create a list of synthetic DER resource definitions."""
    resources = []
    types = ["battery", "battery", "solar", "ev", "load"]  # weighted towards battery
    for i in range(n):
        res_type = rng.choice(types)
        resources.append(
            {
                "id": f"sim-res-{i:03d}",
                "name": f"Synthetic {res_type.capitalize()} {i}",
                "type": res_type,
                "site_id": f"site-{i % 3}",
                "capacity_kw": round(rng.uniform(50.0, 500.0), 1),
                "state_of_charge": round(rng.uniform(0.2, 0.8), 2)
                if res_type == "battery"
                else None,
            }
        )
    return resources


async def run_simulation(
    duration: int,
    num_resources: int,
    seed: int,
    horizon: int,
) -> None:
    """Main simulation coroutine.

    Args:
        duration: Simulation wall-clock duration in seconds.
        num_resources: Number of synthetic DER assets.
        seed: Random seed.
        horizon: Optimization horizon in hours.
    """
    rng = random.Random(seed)
    engine = DERMSEngine()
    optimizer = BatteryOptimizer(strategy="heuristic")

    print(f"\n{'=' * 60}")
    print(f"  DERMS Simulation")
    print(f"  Duration   : {duration}s")
    print(f"  Resources  : {num_resources}")
    print(f"  Seed       : {seed}")
    print(f"  Horizon    : {horizon}h")
    print(f"{'=' * 60}\n")

    # 1. Register synthetic resources
    synthetic = generate_synthetic_resources(num_resources, rng)
    for res in synthetic:
        await engine.register_resource(res)
    print(f"[✓] Registered {num_resources} synthetic DER assets")

    # 2. Generate a load forecast
    forecast_points = generate_dummy_forecast(
        horizon_hours=horizon, interval="1h", seed=seed
    )
    print(f"[✓] Generated {len(forecast_points)}-point load forecast")

    # 3. Run optimization
    start = time.monotonic()
    job_id = await engine.run_optimization(
        {
            "horizon_hours": horizon,
            "objective": "maximize_revenue",
            "min_soc": 0.10,
            "max_soc": 0.95,
            "grid_export_limit_kw": 2000.0,
        }
    )
    elapsed = time.monotonic() - start
    job = engine._jobs.get(job_id, {})
    revenue = job.get("result", {}).get("revenue_usd", 0.0)
    schedule_len = len(job.get("result", {}).get("schedule", []))

    print(f"[✓] Optimization complete (job_id={job_id}, elapsed={elapsed:.3f}s)")
    print(f"    Schedule intervals : {schedule_len}")
    print(f"    Projected revenue  : ${revenue:,.2f}")

    # 4. Simulate telemetry ticks (simplified)
    tick_interval = max(1, duration // 10)
    print(f"\n[→] Simulating {duration}s of operation ({tick_interval}s ticks)...")
    for tick in range(0, min(duration, 10 * tick_interval), tick_interval):
        print(f"    tick={tick:5d}s | active_resources={num_resources}")

    print(f"\n{'=' * 60}")
    print("  Simulation complete.")
    print(f"{'=' * 60}\n")


def main() -> None:
    args = parse_args()
    os.environ.setdefault("SIMULATION_MODE", "true")
    asyncio.run(
        run_simulation(
            duration=args.duration,
            num_resources=args.resources,
            seed=args.seed,
            horizon=args.horizon,
        )
    )


if __name__ == "__main__":
    main()

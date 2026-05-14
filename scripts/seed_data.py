#!/usr/bin/env python3
"""
DERMS Seed Data Script.

Loads sample DER data into the database and optionally imports the
bundled load profile CSV for local development and testing.

Usage:
    python scripts/seed_data.py
    python scripts/seed_data.py --csv data/sample_load_profile.csv
"""

import argparse
import asyncio
import csv
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.derms_engine import DERMSEngine  # noqa: E402
from src.utils.logger import get_logger  # noqa: E402

logger = get_logger(__name__)

SEED_RESOURCES = [
    {
        "name": "Site Alpha — Battery Bank 1",
        "type": "battery",
        "site_id": "site-alpha",
        "capacity_kw": 500.0,
        "metadata": {"vendor": "CATL", "model": "EnerC-500"},
    },
    {
        "name": "Site Alpha — Battery Bank 2",
        "type": "battery",
        "site_id": "site-alpha",
        "capacity_kw": 500.0,
        "metadata": {"vendor": "CATL", "model": "EnerC-500"},
    },
    {
        "name": "Site Beta — Solar Array",
        "type": "solar",
        "site_id": "site-beta",
        "capacity_kw": 250.0,
        "metadata": {"panel_count": 500, "inverter": "SMA Sunny Tripower"},
    },
    {
        "name": "Site Beta — Battery Bank",
        "type": "battery",
        "site_id": "site-beta",
        "capacity_kw": 200.0,
        "metadata": {"vendor": "BYD", "model": "Battery-Box-HV"},
    },
    {
        "name": "Site Gamma — EV Charging Hub",
        "type": "ev",
        "site_id": "site-gamma",
        "capacity_kw": 120.0,
        "metadata": {"charger_count": 20, "charger_type": "DC-fast"},
    },
    {
        "name": "Site Gamma — Demand Response Load",
        "type": "load",
        "site_id": "site-gamma",
        "capacity_kw": 80.0,
        "metadata": {"dr_program": "OpenADR-2.0b"},
    },
]


async def seed_resources(engine: DERMSEngine) -> None:
    """Register all seed resources with the DERMS engine."""
    print(f"\nSeeding {len(SEED_RESOURCES)} DER assets...")
    for resource_data in SEED_RESOURCES:
        record = await engine.register_resource(resource_data)
        print(f"  [+] {record['name']} (id={record['id']})")
    print(f"Done. {len(SEED_RESOURCES)} resources registered.\n")


def load_csv(csv_path: str) -> list[dict]:
    """Read the sample load profile CSV.

    Args:
        csv_path: Path to the CSV file.

    Returns:
        List of row dicts.
    """
    if not os.path.isfile(csv_path):
        print(f"[!] CSV not found: {csv_path}")
        return []
    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    print(f"[✓] Loaded {len(rows)} rows from {csv_path}")
    return rows


async def main(csv_path: str | None) -> None:
    os.environ.setdefault("SIMULATION_MODE", "true")
    engine = DERMSEngine()
    await seed_resources(engine)
    if csv_path:
        rows = load_csv(csv_path)
        print(f"    CSV preview (first 3 rows): {rows[:3]}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="DERMS seed data loader")
    parser.add_argument(
        "--csv",
        default=None,
        help="Path to load profile CSV (default: skip CSV import)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(csv_path=args.csv))

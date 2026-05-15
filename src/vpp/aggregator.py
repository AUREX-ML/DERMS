"""VPP-level DER aggregation and portfolio-wide dispatch.

Pulls live telemetry from all ThingsBoard-registered sites, computes
portfolio-level KPIs, and distributes dispatch commands proportionally
across available site capacity.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from src.utils.logger import get_logger
from src.vpp.cloud.thingsboard_client import ThingsBoardClient

logger = get_logger(__name__)

# Telemetry keys fetched from ThingsBoard for aggregation
_TELEMETRY_KEYS = [
    "active_power_kw",
    "energy_kwh",
    "carbon_offset_kg",
    "battery_capacity_kwh",
    "state_of_charge",
]
# Minimum SoC (%) for a battery to be considered dispatchable
_MIN_SOC_PCT = 20.0
# Look-back window for latest telemetry: 15 minutes in milliseconds
_TELEMETRY_LOOKBACK_MS = 15 * 60 * 1000


class SiteSnapshot(BaseModel):
    """Aggregated telemetry snapshot for a single VPP site."""

    site_id: str
    asset_id: str
    active_power_kw: float = Field(default=0.0)
    energy_kwh: float = Field(default=0.0)
    carbon_offset_kg: float = Field(default=0.0)
    battery_capacity_kwh: float = Field(default=0.0)
    average_soc_pct: float = Field(default=0.0)
    available_dispatch_kw: float = Field(default=0.0)


class VPPPortfolioSnapshot(BaseModel):
    """Aggregated VPP portfolio snapshot across all sites."""

    timestamp: str
    total_active_power_kw: float = Field(default=0.0)
    total_energy_kwh: float = Field(default=0.0)
    total_carbon_offset_kg: float = Field(default=0.0)
    total_battery_capacity_kwh: float = Field(default=0.0)
    average_soc_pct: float = Field(default=0.0)
    available_dispatch_kw: float = Field(default=0.0)
    sites: list[SiteSnapshot] = Field(default_factory=list)


def _latest_value(telemetry_series: list[dict[str, Any]]) -> float:
    """Extract the latest numeric value from a ThingsBoard telemetry series.

    Args:
        telemetry_series: List of ``{ts, value}`` dicts ordered ascending.

    Returns:
        Float value, or ``0.0`` if the series is empty.
    """
    if not telemetry_series:
        return 0.0
    try:
        return float(telemetry_series[-1]["value"])
    except (KeyError, ValueError, TypeError):
        return 0.0


class VPPAggregator:
    """Aggregates VPP portfolio data and dispatches across sites.

    Fetches live telemetry from ThingsBoard for each site asset and
    computes portfolio-level KPIs.  Dispatch commands are distributed
    proportionally to available battery capacity.

    Args:
        client: Optional :class:`ThingsBoardClient`. Created automatically.
    """

    def __init__(self, client: ThingsBoardClient | None = None) -> None:
        self._client = client or ThingsBoardClient()
        logger.info("VPPAggregator initialised")

    async def _fetch_site_snapshot(
        self,
        asset: dict[str, Any],
        now_ms: int,
    ) -> SiteSnapshot:
        """Fetch telemetry for a single site asset and build a snapshot.

        Args:
            asset: ThingsBoard asset dict (must contain ``id.id`` and ``name``).
            now_ms: Current time in epoch milliseconds.

        Returns:
            :class:`SiteSnapshot` for the site.
        """
        asset_id: str = asset["id"]["id"]
        site_id: str = asset.get("name", asset_id)
        start_ms = now_ms - _TELEMETRY_LOOKBACK_MS

        try:
            telemetry = await self._client.get_site_telemetry(
                device_id=asset_id,
                keys=_TELEMETRY_KEYS,
                start_ts=start_ms,
                end_ts=now_ms,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Failed to fetch telemetry for site",
                extra={"site_id": site_id, "error": str(exc)},
            )
            return SiteSnapshot(site_id=site_id, asset_id=asset_id)

        active_power = _latest_value(telemetry.get("active_power_kw", []))
        energy = _latest_value(telemetry.get("energy_kwh", []))
        carbon = _latest_value(telemetry.get("carbon_offset_kg", []))
        batt_cap = _latest_value(telemetry.get("battery_capacity_kwh", []))
        soc = _latest_value(telemetry.get("state_of_charge", []))
        soc_pct = soc * 100.0 if soc <= 1.0 else soc

        # Available dispatch: battery power available if SoC above minimum
        available = active_power if soc_pct > _MIN_SOC_PCT else 0.0

        return SiteSnapshot(
            site_id=site_id,
            asset_id=asset_id,
            active_power_kw=active_power,
            energy_kwh=energy,
            carbon_offset_kg=carbon,
            battery_capacity_kwh=batt_cap,
            average_soc_pct=soc_pct,
            available_dispatch_kw=available,
        )

    async def get_portfolio_snapshot(self) -> VPPPortfolioSnapshot:
        """Build an aggregated portfolio snapshot from all sites.

        Returns:
            :class:`VPPPortfolioSnapshot` with KPIs summed across all sites.
        """
        assets = await self._client.get_portfolio_summary()
        now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)

        site_snapshots: list[SiteSnapshot] = []
        for asset in assets:
            snapshot = await self._fetch_site_snapshot(asset, now_ms)
            site_snapshots.append(snapshot)

        total_power = sum(s.active_power_kw for s in site_snapshots)
        total_energy = sum(s.energy_kwh for s in site_snapshots)
        total_carbon = sum(s.carbon_offset_kg for s in site_snapshots)
        total_batt = sum(s.battery_capacity_kwh for s in site_snapshots)
        total_dispatch = sum(s.available_dispatch_kw for s in site_snapshots)

        weighted_soc = (
            sum(s.average_soc_pct * s.battery_capacity_kwh for s in site_snapshots)
            / total_batt
            if total_batt > 0
            else 0.0
        )

        portfolio = VPPPortfolioSnapshot(
            timestamp=datetime.now(timezone.utc).isoformat(),
            total_active_power_kw=total_power,
            total_energy_kwh=total_energy,
            total_carbon_offset_kg=total_carbon,
            total_battery_capacity_kwh=total_batt,
            average_soc_pct=round(weighted_soc, 2),
            available_dispatch_kw=total_dispatch,
            sites=site_snapshots,
        )
        logger.info(
            "Portfolio snapshot computed",
            extra={
                "sites": len(site_snapshots),
                "total_power_kw": total_power,
                "available_dispatch_kw": total_dispatch,
            },
        )
        return portfolio

    async def get_available_dispatch_capacity(self) -> float:
        """Return the total dispatchable capacity across the portfolio.

        Only counts battery resources with SoC above :data:`_MIN_SOC_PCT`.

        Returns:
            Total available dispatch power in kW.
        """
        snapshot = await self.get_portfolio_snapshot()
        return snapshot.available_dispatch_kw

    async def dispatch_portfolio(
        self,
        power_kw: float,
        duration_s: int,
    ) -> list[dict[str, Any]]:
        """Distribute a dispatch command proportionally across all sites.

        Each site receives a fraction of the requested ``power_kw``
        proportional to its ``available_dispatch_kw``.  Sites with no
        available capacity are skipped.

        Args:
            power_kw: Total power to dispatch in kW.
            duration_s: Duration of the dispatch in seconds.

        Returns:
            List of per-site RPC response dicts.
        """
        snapshot = await self.get_portfolio_snapshot()
        total_available = snapshot.available_dispatch_kw

        if total_available <= 0:
            logger.warning("No dispatch capacity available across portfolio")
            return []

        results: list[dict[str, Any]] = []
        for site in snapshot.sites:
            if site.available_dispatch_kw <= 0:
                continue
            fraction = site.available_dispatch_kw / total_available
            site_power_kw = round(power_kw * fraction, 2)
            try:
                resp = await self._client.send_dispatch_rpc(
                    device_id=site.asset_id,
                    method="set_power",
                    params={"power_kw": site_power_kw, "duration_s": duration_s},
                )
                results.append(
                    {
                        "site_id": site.site_id,
                        "power_kw": site_power_kw,
                        "response": resp,
                    }
                )
                logger.info(
                    "Dispatch RPC sent",
                    extra={"site_id": site.site_id, "power_kw": site_power_kw},
                )
            except Exception as exc:  # noqa: BLE001
                logger.error(
                    "Dispatch RPC failed",
                    extra={"site_id": site.site_id, "error": str(exc)},
                )
                results.append(
                    {
                        "site_id": site.site_id,
                        "power_kw": site_power_kw,
                        "error": str(exc),
                    }
                )

        return results

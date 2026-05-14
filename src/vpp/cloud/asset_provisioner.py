"""ThingsBoard asset hierarchy provisioner.

Reads ``config/thingsboard/asset_hierarchy.json`` and provisions the full
VPP asset/device tree in a ThingsBoard CE instance via the REST API.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.utils.logger import get_logger
from src.vpp.cloud.thingsboard_client import ThingsBoardClient

logger = get_logger(__name__)

_DEFAULT_HIERARCHY_PATH = (
    Path(__file__).resolve().parents[4] / "config" / "thingsboard" / "asset_hierarchy.json"
)


class AssetProvisioner:
    """Provisions the VPP asset and device hierarchy in ThingsBoard CE.

    Reads a JSON template and idempotently creates or retrieves:

    - A top-level **VPP Portfolio** asset
    - One **Site** asset per entry in the config
    - Individual DER **Device** objects linked to each site

    Args:
        client: :class:`ThingsBoardClient` instance. Created automatically if
            not provided.
        hierarchy_path: Path to the ``asset_hierarchy.json`` template.
    """

    def __init__(
        self,
        client: ThingsBoardClient | None = None,
        hierarchy_path: str | Path | None = None,
    ) -> None:
        self._client = client or ThingsBoardClient()
        self._hierarchy_path = Path(hierarchy_path or _DEFAULT_HIERARCHY_PATH)

    def _load_hierarchy(self) -> dict[str, Any]:
        """Load the hierarchy template from disk.

        Returns:
            Parsed hierarchy dict.

        Raises:
            FileNotFoundError: If the JSON template does not exist.
        """
        if not self._hierarchy_path.exists():
            raise FileNotFoundError(
                f"asset_hierarchy.json not found at {self._hierarchy_path}"
            )
        with self._hierarchy_path.open() as fh:
            return json.load(fh)

    # ------------------------------------------------------------------
    # Idempotent helpers
    # ------------------------------------------------------------------

    async def get_or_create_asset(self, name: str, asset_type: str) -> str:
        """Return the ThingsBoard asset ID, creating the asset if absent.

        Args:
            name: Asset display name.
            asset_type: ThingsBoard asset type string.

        Returns:
            Asset UUID string.
        """
        assets = await self._client.get_portfolio_summary()
        for asset in assets:
            if asset.get("name") == name and asset.get("type") == asset_type:
                logger.info("Asset already exists", extra={"name": name, "id": asset["id"]["id"]})
                return asset["id"]["id"]

        # Create the asset
        created = await self._client._request(
            "POST",
            "/api/asset",
            json={"name": name, "type": asset_type},
        )
        asset_id = created["id"]["id"]
        logger.info("Asset created", extra={"name": name, "type": asset_type, "id": asset_id})
        return asset_id

    async def _get_or_create_device(self, name: str, device_type: str) -> str:
        """Return the ThingsBoard device ID, creating it if absent.

        Args:
            name: Device display name.
            device_type: ThingsBoard device type string.

        Returns:
            Device UUID string.
        """
        # Query existing devices
        data = await self._client._request(
            "GET",
            "/api/tenant/devices",
            params={"pageSize": 1000, "page": 0},
        )
        for device in data.get("data", []):
            if device.get("name") == name and device.get("type") == device_type:
                logger.info("Device already exists", extra={"name": name, "id": device["id"]["id"]})
                return device["id"]["id"]

        created = await self._client._request(
            "POST",
            "/api/device",
            json={"name": name, "type": device_type},
        )
        device_id = created["id"]["id"]
        logger.info("Device created", extra={"name": name, "type": device_type, "id": device_id})
        return device_id

    async def link_device_to_asset(self, device_id: str, asset_id: str) -> None:
        """Create a ThingsBoard relation linking a device to an asset.

        Args:
            device_id: ThingsBoard device UUID.
            asset_id: ThingsBoard asset UUID.
        """
        await self._client._request(
            "POST",
            "/api/relation",
            json={
                "from": {"id": asset_id, "entityType": "ASSET"},
                "to": {"id": device_id, "entityType": "DEVICE"},
                "type": "Contains",
                "typeGroup": "COMMON",
            },
        )
        logger.debug(
            "Device linked to asset",
            extra={"device_id": device_id, "asset_id": asset_id},
        )

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    async def provision_site(self, site_config: dict[str, Any]) -> dict[str, Any]:
        """Provision a site asset and all its DER devices.

        Args:
            site_config: Site dict from the hierarchy JSON template.

        Returns:
            Report dict with ``site_id``, ``asset_id``, and ``devices`` list.
        """
        site_id = site_config["site_id"]
        site_asset_id = await self.get_or_create_asset(
            name=site_config["name"], asset_type=site_config["type"]
        )

        devices_report: list[dict[str, Any]] = []
        for device_cfg in site_config.get("devices", []):
            device_id = await self._get_or_create_device(
                name=device_cfg["name"],
                device_type=device_cfg["der_type"],
            )
            await self.link_device_to_asset(device_id, site_asset_id)
            devices_report.append(
                {"der_id": device_cfg["der_id"], "device_id": device_id, "name": device_cfg["name"]}
            )

        report = {
            "site_id": site_id,
            "asset_id": site_asset_id,
            "devices": devices_report,
        }
        logger.info(
            "Site provisioned",
            extra={"site_id": site_id, "device_count": len(devices_report)},
        )
        return report

    async def provision_all(self) -> dict[str, Any]:
        """Provision the complete VPP hierarchy from the JSON template.

        Returns:
            Provisioning report with counts of created and pre-existing resources.
        """
        hierarchy = self._load_hierarchy()

        # Provision the top-level portfolio asset
        portfolio_cfg = hierarchy.get("vpp_portfolio", {})
        portfolio_id = await self.get_or_create_asset(
            name=portfolio_cfg.get("name", "VPP Portfolio"),
            asset_type=portfolio_cfg.get("type", "VPP"),
        )

        site_reports: list[dict[str, Any]] = []
        for site_cfg in hierarchy.get("sites", []):
            report = await self.provision_site(site_cfg)
            # Link site asset to portfolio
            await self.link_device_to_asset(report["asset_id"], portfolio_id)
            site_reports.append(report)

        total_devices = sum(len(r["devices"]) for r in site_reports)
        logger.info(
            "VPP hierarchy provisioning complete",
            extra={"sites": len(site_reports), "devices": total_devices},
        )
        return {
            "portfolio_id": portfolio_id,
            "sites": site_reports,
            "total_devices": total_devices,
        }

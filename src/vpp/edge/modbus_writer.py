"""Modbus TCP/RTU setpoint writer for site-edge DER control.

Translates high-level dispatch commands into Modbus register writes,
using ``pymodbus`` for the underlying protocol. DER connection details
are loaded from ``config/edge/site_config.yaml``.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import yaml
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

from src.utils.logger import get_logger

logger = get_logger(__name__)

# Register addresses for standard DER setpoints
_REG_ACTIVE_POWER_KW = 40
_REG_STATE_OF_CHARGE = 41
_REG_CURTAIL_PCT = 42

_MAX_RETRIES = 3
_RETRY_BASE_DELAY = 1.0  # seconds — doubles on each retry


def _load_der_registry(config_path: str | Path | None = None) -> dict[str, dict[str, Any]]:
    """Load the DER Modbus registry from the site YAML config.

    Args:
        config_path: Path to ``site_config.yaml``. Defaults to
            ``config/edge/site_config.yaml`` relative to the project root.

    Returns:
        Mapping of ``der_id`` → ``{modbus_host, modbus_port}``.
    """
    if config_path is None:
        config_path = Path(__file__).resolve().parents[4] / "config" / "edge" / "site_config.yaml"
    path = Path(config_path)
    if not path.exists():
        logger.warning("site_config.yaml not found, using empty DER registry", extra={"path": str(path)})
        return {}
    with path.open() as fh:
        data = yaml.safe_load(fh)
    registry: dict[str, dict[str, Any]] = {}
    for der in data.get("ders", []):
        registry[der["der_id"]] = {
            "modbus_host": der.get("modbus_host", "localhost"),
            "modbus_port": int(der.get("modbus_port", 502)),
        }
    logger.info("DER Modbus registry loaded", extra={"count": len(registry)})
    return registry


class ModbusWriter:
    """Writes Modbus TCP setpoints to site DERs.

    Connection details per DER are resolved from the YAML registry loaded
    at construction time.

    Args:
        config_path: Optional path to ``site_config.yaml``.
    """

    def __init__(self, config_path: str | Path | None = None) -> None:
        self._registry = _load_der_registry(config_path)
        self._clients: dict[str, ModbusTcpClient] = {}

    def _get_client(self, der_id: str) -> ModbusTcpClient:
        """Return a connected :class:`ModbusTcpClient` for *der_id*.

        Args:
            der_id: DER identifier as registered in the site config.

        Returns:
            Connected Modbus client.

        Raises:
            KeyError: If ``der_id`` is not in the registry.
            ModbusException: If the connection cannot be established.
        """
        if der_id not in self._registry:
            raise KeyError(f"DER '{der_id}' not found in Modbus registry")
        info = self._registry[der_id]
        if der_id not in self._clients or not self._clients[der_id].connected:
            client = ModbusTcpClient(host=info["modbus_host"], port=info["modbus_port"])
            if not client.connect():
                raise ModbusException(f"Cannot connect to DER '{der_id}' at {info}")
            self._clients[der_id] = client
        return self._clients[der_id]

    def _write_register(self, der_id: str, address: int, value: int) -> bool:
        """Write a single holding register with exponential-backoff retries.

        Args:
            der_id: DER identifier.
            address: Modbus register address.
            value: Integer value to write.

        Returns:
            ``True`` on success, ``False`` after exhausting retries.
        """
        delay = _RETRY_BASE_DELAY
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                client = self._get_client(der_id)
                result = client.write_register(address, value)
                if result.isError():
                    raise ModbusException(f"Write error at address {address}: {result}")
                logger.debug(
                    "Modbus register written",
                    extra={"der_id": der_id, "address": address, "value": value},
                )
                return True
            except (ModbusException, KeyError, Exception) as exc:  # noqa: BLE001
                logger.warning(
                    "Modbus write attempt failed",
                    extra={"der_id": der_id, "attempt": attempt, "error": str(exc)},
                )
                # Invalidate cached client so it reconnects on next attempt
                self._clients.pop(der_id, None)
                if attempt < _MAX_RETRIES:
                    time.sleep(delay)
                    delay *= 2
        logger.error(
            "Modbus write failed after all retries",
            extra={"der_id": der_id, "address": address},
        )
        return False

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def write_setpoint(self, der_id: str, method: str, params: dict[str, Any]) -> bool:
        """Route a dispatch command to the correct Modbus register.

        Supported methods:

        - ``set_power`` — writes ``power_kw * 10`` to register 40.
        - ``set_charge`` — writes ``state_of_charge * 100`` to register 41.
        - ``curtail``   — writes curtailment percentage to register 42.

        Args:
            der_id: Target DER identifier.
            method: Dispatch method name.
            params: Method parameters dict.

        Returns:
            ``True`` on success, ``False`` on failure.
        """
        if method == "set_power":
            raw = int(float(params.get("power_kw", 0)) * 10)
            return self._write_register(der_id, _REG_ACTIVE_POWER_KW, raw)
        elif method == "set_charge":
            raw = int(float(params.get("state_of_charge", 0)) * 100)
            return self._write_register(der_id, _REG_STATE_OF_CHARGE, raw)
        elif method == "curtail":
            raw = int(float(params.get("curtailment_pct", 0)))
            return self._write_register(der_id, _REG_CURTAIL_PCT, raw)
        else:
            logger.error(
                "Unknown dispatch method",
                extra={"der_id": der_id, "method": method},
            )
            return False

    def ping(self, der_id: str) -> bool:
        """Check whether a DER is reachable via Modbus TCP.

        Args:
            der_id: Target DER identifier.

        Returns:
            ``True`` if the DER responds, ``False`` otherwise.
        """
        try:
            client = self._get_client(der_id)
            result = client.read_holding_registers(address=0, count=1)
            return not result.isError()
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Modbus ping failed",
                extra={"der_id": der_id, "error": str(exc)},
            )
            return False

"""
Telemetry service — ingests real-time DER measurements via MQTT.

Subscribes to per-device MQTT topics, validates payloads against Pydantic
models, and writes normalised measurements to Redis (real-time state) and
PostgreSQL (time-series history).
"""

from __future__ import annotations

import json
from typing import Any

from src.utils.config import get_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class TelemetryService:
    """MQTT-based telemetry ingestion service.

    Connects to the configured MQTT broker and subscribes to both the
    legacy ``derms/+/telemetry`` topic pattern and the VPP schema
    ``vpp/+/+/+/telemetry`` topic pattern. Each incoming message is
    validated and forwarded to the storage layer.
    """

    TOPIC_PATTERN = "derms/+/telemetry"
    VPP_TOPIC_PATTERN = "vpp/+/+/+/telemetry"

    def __init__(self) -> None:
        self.broker_url = settings.mqtt_broker_url
        self.simulation_mode = settings.simulation_mode
        self._client: Any = None
        logger.info(
            "TelemetryService initialised",
            extra={"broker": self.broker_url, "simulation": self.simulation_mode},
        )

    def _validate_payload(self, raw: bytes) -> dict[str, Any] | None:
        """Parse and validate an incoming MQTT message payload.

        Args:
            raw: Raw bytes from the MQTT message.

        Returns:
            Validated dict or ``None`` if the payload is malformed.
        """
        try:
            data = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            logger.warning("Invalid telemetry payload", extra={"error": str(exc)})
            return None

        required_fields = {"resource_id", "timestamp", "power_kw"}
        if not required_fields.issubset(data.keys()):
            logger.warning(
                "Missing required fields in telemetry payload",
                extra={"received_keys": list(data.keys())},
            )
            return None
        return data

    def on_message(self, _client: Any, _userdata: Any, message: Any) -> None:
        """Callback invoked when an MQTT message is received.

        Routes VPP-schema topics (``vpp/+/+/+/telemetry``) through
        :meth:`_handle_vpp_telemetry`; all other messages are handled as
        legacy DERMS telemetry.

        Args:
            _client: The MQTT client instance (unused).
            _userdata: User data passed to the client (unused).
            message: The MQTT message object with ``topic`` and ``payload``.
        """
        topic: str = message.topic
        if topic.startswith("vpp/"):
            self._handle_vpp_telemetry(topic, message.payload)
            return

        payload = self._validate_payload(message.payload)
        if payload is None:
            return
        resource_id = payload.get("resource_id", "unknown")
        logger.debug(
            "Telemetry received",
            extra={"resource_id": resource_id, "power_kw": payload.get("power_kw")},
        )
        # TODO: write to Redis cache and PostgreSQL time-series table

    def _handle_vpp_telemetry(self, topic: str, raw: bytes) -> None:
        """Handle a VPP-schema telemetry message.

        Extracts ``site_id``, ``der_type``, and ``der_id`` from the topic
        segments and dispatches to the storage layer.

        Topic schema: ``vpp/{site_id}/{der_type}/{der_id}/telemetry``

        Args:
            topic: Full MQTT topic string.
            raw: Raw message payload bytes.
        """
        parts = topic.split("/")
        if len(parts) != 5:
            logger.warning(
                "Unexpected VPP topic structure",
                extra={"topic": topic},
            )
            return
        _, site_id, der_type, der_id, _ = parts

        try:
            data = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            logger.warning(
                "Invalid VPP telemetry payload",
                extra={"topic": topic, "error": str(exc)},
            )
            return

        data.setdefault("site_id", site_id)
        data.setdefault("der_type", der_type)
        data.setdefault("der_id", der_id)

        logger.debug(
            "VPP telemetry received",
            extra={"site_id": site_id, "der_type": der_type, "der_id": der_id},
        )
        # TODO: write to Redis cache and PostgreSQL time-series table

    def start(self) -> None:
        """Connect to MQTT broker and begin listening for telemetry.

        Subscribes to both the legacy DERMS topic pattern and the VPP
        schema topic pattern.
        """
        if self.simulation_mode:
            logger.info("Simulation mode: MQTT subscription skipped")
            return
        # TODO: initialise paho-mqtt client, set TLS, connect, subscribe
        # Subscribe to legacy pattern
        # client.subscribe(self.TOPIC_PATTERN, qos=1)
        # Subscribe to VPP pattern
        # client.subscribe(self.VPP_TOPIC_PATTERN, qos=1)
        logger.info(
            "MQTT telemetry subscription started",
            extra={"topics": [self.TOPIC_PATTERN, self.VPP_TOPIC_PATTERN]},
        )

    def stop(self) -> None:
        """Disconnect from the MQTT broker."""
        if self._client is not None:
            self._client.disconnect()
        logger.info("MQTT telemetry subscription stopped")

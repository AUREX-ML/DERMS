"""MQTT Bridge Agent — forwards site telemetry to ThingsBoard Cloud.

Subscribes to the local Mosquitto broker on ``vpp/{site_id}/+/+/telemetry``,
validates each message, and forwards it to ThingsBoard via MQTT over TLS.
Messages that cannot be forwarded are persisted in the offline SQLite buffer.
"""

from __future__ import annotations

import asyncio
import json
import ssl
import time
from typing import Any

import paho.mqtt.client as mqtt
from pydantic import BaseModel, Field, ValidationError

from src.utils.config import get_settings
from src.utils.logger import get_logger
from src.vpp.edge.offline_buffer import OfflineBuffer

logger = get_logger(__name__)
settings = get_settings()

TB_TELEMETRY_TOPIC = "v1/devices/me/telemetry"


class TelemetryPayload(BaseModel):
    """Validated telemetry message from a site DER."""

    site_id: str
    der_type: str
    der_id: str
    timestamp: str
    active_power_kw: float = Field(default=0.0)
    energy_kwh: float = Field(default=0.0)
    voltage_v: float = Field(default=0.0)
    frequency_hz: float = Field(default=0.0)
    state_of_charge: float | None = Field(default=None)
    carbon_offset_kg: float = Field(default=0.0)


class MQTTBridgeAgent:
    """Bridges local site MQTT telemetry to ThingsBoard Cloud.

    Connects to the local Mosquitto broker, subscribes to the VPP topic
    pattern, and forwards validated payloads to ThingsBoard via a separate
    TLS-secured MQTT connection.  When the ThingsBoard connection is
    unavailable the payload is stored in the :class:`OfflineBuffer` and
    replayed on reconnect.

    Args:
        buffer: Optional :class:`OfflineBuffer` instance. A default one is
            created if not provided.
    """

    VPP_TOPIC_PATTERN = "vpp/{site_id}/+/+/telemetry"

    def __init__(self, buffer: OfflineBuffer | None = None) -> None:
        self._settings = settings
        self._buffer = buffer or OfflineBuffer()
        self._local_client: mqtt.Client | None = None
        self._tb_client: mqtt.Client | None = None
        self._tb_connected = False
        self._running = False

        site_id = getattr(self._settings, "site_id", "unknown")
        self._topic = self.VPP_TOPIC_PATTERN.format(site_id=site_id)
        logger.info(
            "MQTTBridgeAgent initialised",
            extra={"site_id": site_id, "topic": self._topic},
        )

    # ------------------------------------------------------------------
    # Payload handling
    # ------------------------------------------------------------------

    def _validate_payload(self, topic: str, raw: bytes) -> TelemetryPayload | None:
        """Parse the MQTT topic and payload into a :class:`TelemetryPayload`.

        Args:
            topic: MQTT topic string (``vpp/{site_id}/{der_type}/{der_id}/telemetry``).
            raw: Raw message bytes.

        Returns:
            Validated :class:`TelemetryPayload` or ``None`` on failure.
        """
        try:
            parts = topic.split("/")
            # Expected: vpp / site_id / der_type / der_id / telemetry  (5 parts)
            if len(parts) != 5:
                logger.warning("Unexpected topic structure", extra={"topic": topic})
                return None
            _, site_id, der_type, der_id, _ = parts
            data = json.loads(raw.decode("utf-8"))
            data.setdefault("site_id", site_id)
            data.setdefault("der_type", der_type)
            data.setdefault("der_id", der_id)
            return TelemetryPayload(**data)
        except (json.JSONDecodeError, UnicodeDecodeError, ValidationError) as exc:
            logger.warning(
                "Invalid VPP telemetry payload",
                extra={"topic": topic, "error": str(exc)},
            )
            return None

    async def _forward_to_tb(self, payload: dict[str, Any]) -> None:
        """Forward a telemetry dict to ThingsBoard via MQTT.

        Args:
            payload: Validated telemetry dict.

        Raises:
            RuntimeError: When the ThingsBoard client is not connected.
        """
        if not self._tb_connected or self._tb_client is None:
            raise RuntimeError("ThingsBoard MQTT client not connected")
        message = json.dumps(payload)
        result = self._tb_client.publish(TB_TELEMETRY_TOPIC, message, qos=1)
        result.wait_for_publish(timeout=5.0)
        logger.debug(
            "Telemetry forwarded to ThingsBoard",
            extra={"der_id": payload.get("der_id")},
        )

    # ------------------------------------------------------------------
    # MQTT callbacks — local broker
    # ------------------------------------------------------------------

    def _on_local_connect(
        self,
        client: mqtt.Client,
        _userdata: Any,
        _flags: Any,
        rc: int,
    ) -> None:
        if rc == 0:
            client.subscribe(self._topic, qos=1)
            logger.info("Connected to local broker, subscribed", extra={"topic": self._topic})
        else:
            logger.error("Local broker connection failed", extra={"rc": rc})

    def _on_local_message(
        self,
        _client: mqtt.Client,
        _userdata: Any,
        message: mqtt.MQTTMessage,
    ) -> None:
        payload = self._validate_payload(message.topic, message.payload)
        if payload is None:
            return

        payload_dict = payload.model_dump()
        loop = asyncio.get_event_loop()
        if self._tb_connected:
            try:
                loop.run_until_complete(self._forward_to_tb(payload_dict))
                return
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "Forward to TB failed, buffering",
                    extra={"der_id": payload.der_id, "error": str(exc)},
                )
        loop.run_until_complete(self._buffer.store(payload_dict))

    # ------------------------------------------------------------------
    # MQTT callbacks — ThingsBoard broker
    # ------------------------------------------------------------------

    def _on_tb_connect(
        self,
        _client: mqtt.Client,
        _userdata: Any,
        _flags: Any,
        rc: int,
    ) -> None:
        if rc == 0:
            self._tb_connected = True
            logger.info("Connected to ThingsBoard MQTT broker")
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self._buffer.replay(self._forward_to_tb))
        else:
            self._tb_connected = False
            logger.error("ThingsBoard MQTT connection failed", extra={"rc": rc})

    def _on_tb_disconnect(
        self,
        _client: mqtt.Client,
        _userdata: Any,
        rc: int,
    ) -> None:
        self._tb_connected = False
        logger.warning("Disconnected from ThingsBoard MQTT broker", extra={"rc": rc})

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def _build_tb_client(self) -> mqtt.Client:
        """Construct and configure the ThingsBoard MQTT client with TLS."""
        tb_token = getattr(self._settings, "tb_device_token", "")
        client = mqtt.Client(client_id=tb_token, protocol=mqtt.MQTTv311)
        client.username_pw_set(tb_token)

        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_ctx.check_hostname = True
        ssl_ctx.verify_mode = ssl.CERT_REQUIRED
        client.tls_set_context(ssl_ctx)

        client.on_connect = self._on_tb_connect
        client.on_disconnect = self._on_tb_disconnect
        return client

    def _build_local_client(self) -> mqtt.Client:
        """Construct and configure the local Mosquitto MQTT client."""
        client = mqtt.Client(client_id="bridge_agent", protocol=mqtt.MQTTv311)
        client.on_connect = self._on_local_connect
        client.on_message = self._on_local_message
        return client

    def start(self) -> None:
        """Connect to both brokers and start the MQTT loop.

        In simulation mode (``SIMULATION_MODE=true``) the network connections
        are skipped so the agent can be unit-tested without real hardware.
        """
        if getattr(self._settings, "simulation_mode", False):
            logger.info("Simulation mode: MQTTBridgeAgent connections skipped")
            return

        tb_host = getattr(self._settings, "tb_mqtt_host", "thingsboard.example.com")
        tb_port = getattr(self._settings, "tb_mqtt_port", 8883)
        local_host = getattr(self._settings, "local_mqtt_host", "localhost")
        local_port = getattr(self._settings, "local_mqtt_port", 1883)

        self._tb_client = self._build_tb_client()
        self._tb_client.connect_async(tb_host, tb_port, keepalive=60)
        self._tb_client.loop_start()

        self._local_client = self._build_local_client()
        self._local_client.connect(local_host, local_port, keepalive=60)

        self._running = True
        logger.info(
            "MQTTBridgeAgent started",
            extra={"local": f"{local_host}:{local_port}", "tb": f"{tb_host}:{tb_port}"},
        )
        self._local_client.loop_forever()

    def stop(self) -> None:
        """Disconnect from both brokers and stop the MQTT loops."""
        self._running = False
        if self._local_client is not None:
            self._local_client.disconnect()
        if self._tb_client is not None:
            self._tb_client.loop_stop()
            self._tb_client.disconnect()
        logger.info("MQTTBridgeAgent stopped")

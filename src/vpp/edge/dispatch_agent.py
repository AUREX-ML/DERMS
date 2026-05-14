"""Dispatch Agent — receives RPC commands and writes Modbus setpoints.

Subscribes to ``vpp/{site_id}/dispatch/commands`` on the local Mosquitto
broker, validates incoming :class:`DispatchCommand` payloads, delegates to
:class:`ModbusWriter`, and publishes acknowledgements.

Also exposes ``handle_tb_rpc`` for direct ThingsBoard server-side RPC
integration where ThingsBoard sends commands via
``v1/devices/me/rpc/request/+``.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import paho.mqtt.client as mqtt
from pydantic import BaseModel, ValidationError

from src.utils.config import get_settings
from src.utils.logger import get_logger
from src.vpp.edge.modbus_writer import ModbusWriter

logger = get_logger(__name__)
settings = get_settings()


class DispatchCommand(BaseModel):
    """Validated dispatch command received from ThingsBoard RPC."""

    method: str
    der_id: str
    der_type: str
    params: dict[str, Any]
    request_id: str
    issued_at: str


class DispatchAgent:
    """Receives and executes DER dispatch commands via local MQTT + Modbus.

    Connects to the local Mosquitto broker, subscribes to the dispatch
    command topic, validates each command, and routes it through the
    :class:`ModbusWriter`.  Acknowledgements are published back on the
    response topic.

    Also exposes :meth:`handle_tb_rpc` for direct ThingsBoard RPC integration.

    Args:
        modbus_writer: Optional :class:`ModbusWriter` instance. A default
            one is created if not provided.
    """

    COMMAND_TOPIC_PATTERN = "vpp/{site_id}/dispatch/commands"
    RESPONSE_TOPIC_PATTERN = "vpp/{site_id}/dispatch/responses"

    def __init__(self, modbus_writer: ModbusWriter | None = None) -> None:
        self._settings = settings
        self._writer = modbus_writer or ModbusWriter()
        self._client: mqtt.Client | None = None

        site_id = getattr(self._settings, "site_id", "unknown")
        self._command_topic = self.COMMAND_TOPIC_PATTERN.format(site_id=site_id)
        self._response_topic = self.RESPONSE_TOPIC_PATTERN.format(site_id=site_id)
        self._site_id = site_id
        logger.info(
            "DispatchAgent initialised",
            extra={"site_id": site_id, "command_topic": self._command_topic},
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _publish_ack(
        self,
        request_id: str,
        der_id: str,
        success: bool,
        error: str | None = None,
    ) -> None:
        """Publish a dispatch acknowledgement to the response topic.

        Args:
            request_id: ThingsBoard RPC request identifier.
            der_id: Target DER identifier.
            success: Whether the dispatch succeeded.
            error: Optional error message on failure.
        """
        ack: dict[str, Any] = {
            "request_id": request_id,
            "der_id": der_id,
            "status": "success" if success else "failed",
            "executed_at": datetime.now(timezone.utc).isoformat(),
        }
        if error:
            ack["error"] = error
        if self._client is not None:
            self._client.publish(self._response_topic, json.dumps(ack), qos=1)
            logger.debug(
                "Dispatch acknowledgement published",
                extra={"request_id": request_id, "status": ack["status"]},
            )

    def _execute_command(self, cmd: DispatchCommand) -> None:
        """Execute a validated dispatch command via Modbus.

        Args:
            cmd: Validated :class:`DispatchCommand`.
        """
        logger.info(
            "Executing dispatch command",
            extra={
                "request_id": cmd.request_id,
                "method": cmd.method,
                "der_id": cmd.der_id,
                "params": cmd.params,
            },
        )
        try:
            success = self._writer.write_setpoint(cmd.der_id, cmd.method, cmd.params)
            self._publish_ack(cmd.request_id, cmd.der_id, success)
            if not success:
                logger.error(
                    "Modbus write_setpoint returned False",
                    extra={"request_id": cmd.request_id, "der_id": cmd.der_id},
                )
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "Dispatch command execution error",
                extra={"request_id": cmd.request_id, "error": str(exc)},
            )
            self._publish_ack(cmd.request_id, cmd.der_id, False, error=str(exc))

    # ------------------------------------------------------------------
    # MQTT callbacks
    # ------------------------------------------------------------------

    def _on_connect(
        self,
        client: mqtt.Client,
        _userdata: Any,
        _flags: Any,
        rc: int,
    ) -> None:
        if rc == 0:
            client.subscribe(self._command_topic, qos=1)
            logger.info(
                "DispatchAgent connected to local broker",
                extra={"topic": self._command_topic},
            )
        else:
            logger.error("DispatchAgent broker connection failed", extra={"rc": rc})

    def _on_message(
        self,
        _client: mqtt.Client,
        _userdata: Any,
        message: mqtt.MQTTMessage,
    ) -> None:
        try:
            data = json.loads(message.payload.decode("utf-8"))
            cmd = DispatchCommand(**data)
        except (json.JSONDecodeError, UnicodeDecodeError, ValidationError) as exc:
            logger.warning(
                "Invalid dispatch command payload",
                extra={"topic": message.topic, "error": str(exc)},
            )
            return
        self._execute_command(cmd)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    async def handle_tb_rpc(self, rpc_payload: dict[str, Any]) -> None:
        """Handle a ThingsBoard server-side RPC message directly.

        ThingsBoard delivers RPC commands via MQTT on the topic
        ``v1/devices/me/rpc/request/+``.  This method validates the payload
        and routes it through the same execution pipeline as MQTT commands.

        Args:
            rpc_payload: Raw RPC payload dict from ThingsBoard, expected to
                contain ``method``, ``params``, and ``id`` fields.
        """
        try:
            params = rpc_payload.get("params", {})
            method = rpc_payload.get("method", "")
            der_id = params.get("der_id", "")
            if not method or not der_id:
                logger.warning(
                    "ThingsBoard RPC payload missing method or der_id",
                    extra={"payload_keys": list(rpc_payload.keys())},
                )
                return
            cmd = DispatchCommand(
                method=method,
                der_id=der_id,
                der_type=params.get("der_type", ""),
                params=params,
                request_id=str(rpc_payload.get("id", "")),
                issued_at=datetime.now(timezone.utc).isoformat(),
            )
        except ValidationError as exc:
            logger.warning(
                "Invalid ThingsBoard RPC payload",
                extra={"error": str(exc)},
            )
            return
        self._execute_command(cmd)

    def start(self) -> None:
        """Connect to the local broker and begin listening for commands.

        In simulation mode the broker connection is skipped.
        """
        if getattr(self._settings, "simulation_mode", False):
            logger.info("Simulation mode: DispatchAgent connection skipped")
            return

        local_host = getattr(self._settings, "local_mqtt_host", "localhost")
        local_port = getattr(self._settings, "local_mqtt_port", 1883)

        self._client = mqtt.Client(client_id="dispatch_agent", protocol=mqtt.MQTTv311)
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.connect(local_host, local_port, keepalive=60)
        logger.info(
            "DispatchAgent started",
            extra={"broker": f"{local_host}:{local_port}"},
        )
        self._client.loop_forever()

    def stop(self) -> None:
        """Disconnect from the local broker."""
        if self._client is not None:
            self._client.disconnect()
        logger.info("DispatchAgent stopped")

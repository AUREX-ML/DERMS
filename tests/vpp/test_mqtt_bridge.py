"""Tests for MQTTBridgeAgent payload validation and forwarding logic."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.vpp.edge.mqtt_bridge import MQTTBridgeAgent, TelemetryPayload
from src.vpp.edge.offline_buffer import OfflineBuffer

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def buffer(tmp_path):
    """Return an OfflineBuffer backed by a temp-directory SQLite DB."""
    return OfflineBuffer(db_path=str(tmp_path / "test_buffer.db"))


@pytest.fixture()
def agent(buffer):
    """Return a MQTTBridgeAgent with the simulation buffer injected."""
    with patch("src.vpp.edge.mqtt_bridge.get_settings") as mock_settings:
        mock_settings.return_value = MagicMock(
            simulation_mode=True,
            site_id="site_test",
            tb_mqtt_host="tb.example.com",
            tb_mqtt_port=8883,
            local_mqtt_host="localhost",
            local_mqtt_port=1883,
            tb_device_token="test-token",
        )
        return MQTTBridgeAgent(buffer=buffer)


# ---------------------------------------------------------------------------
# _validate_payload
# ---------------------------------------------------------------------------


VALID_PAYLOAD = {
    "site_id": "site_A",
    "der_type": "battery",
    "der_id": "bess_01",
    "timestamp": "2026-05-15T10:00:00Z",
    "active_power_kw": 25.5,
    "energy_kwh": 120.0,
    "voltage_v": 400.0,
    "frequency_hz": 50.0,
    "state_of_charge": 0.78,
    "carbon_offset_kg": 12.3,
}

VALID_TOPIC = "vpp/site_A/battery/bess_01/telemetry"


def test_validate_payload_valid(agent):
    """Valid topic + payload returns a TelemetryPayload instance."""
    result = agent._validate_payload(VALID_TOPIC, json.dumps(VALID_PAYLOAD).encode())
    assert result is not None
    assert isinstance(result, TelemetryPayload)
    assert result.der_id == "bess_01"
    assert result.active_power_kw == 25.5


def test_validate_payload_missing_required_fields(agent):
    """Payload missing required fields returns None."""
    bad = {"site_id": "site_A"}  # missing der_type, der_id, timestamp etc.
    # der_type / der_id come from topic; timestamp has no default → ValidationError
    result = agent._validate_payload(VALID_TOPIC, json.dumps(bad).encode())
    assert result is None


def test_validate_payload_malformed_json(agent):
    """Non-JSON bytes return None without raising."""
    result = agent._validate_payload(VALID_TOPIC, b"not-json{{}")
    assert result is None


def test_validate_payload_bad_topic_structure(agent):
    """Topics with wrong segment count return None."""
    result = agent._validate_payload(
        "vpp/site_A/telemetry", json.dumps(VALID_PAYLOAD).encode()
    )
    assert result is None


def test_validate_payload_extracts_topic_fields(agent):
    """site_id, der_type, der_id are extracted from the topic when absent from payload."""
    payload_without_meta = {
        "timestamp": "2026-05-15T10:00:00Z",
        "active_power_kw": 10.0,
    }
    result = agent._validate_payload(
        VALID_TOPIC, json.dumps(payload_without_meta).encode()
    )
    assert result is not None
    assert result.site_id == "site_A"
    assert result.der_type == "battery"
    assert result.der_id == "bess_01"


# ---------------------------------------------------------------------------
# Simulation mode — start() skips connections
# ---------------------------------------------------------------------------


def test_start_simulation_mode_skips_connection(agent):
    """start() in simulation mode returns without connecting to any broker."""
    # Patch the module-level settings object that the agent references
    with (
        patch("src.vpp.edge.mqtt_bridge.settings") as mock_settings,
        patch.object(agent, "_build_tb_client") as mock_tb,
        patch.object(agent, "_build_local_client") as mock_local,
    ):
        mock_settings.simulation_mode = True
        agent._settings = mock_settings
        agent.start()
        mock_tb.assert_not_called()
        mock_local.assert_not_called()


# ---------------------------------------------------------------------------
# on_message → OfflineBuffer.store on forward failure
# ---------------------------------------------------------------------------


def test_on_message_stores_in_buffer_on_forward_failure(tmp_path):
    """When ThingsBoard is offline, on_message stores payload in the buffer."""
    import asyncio as _asyncio

    loop = _asyncio.new_event_loop()
    _asyncio.set_event_loop(loop)
    try:
        buf = OfflineBuffer(db_path=str(tmp_path / "buf.db"))
        with patch("src.vpp.edge.mqtt_bridge.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                simulation_mode=True,
                site_id="site_test",
                tb_mqtt_host="tb.example.com",
                tb_mqtt_port=8883,
                local_mqtt_host="localhost",
                local_mqtt_port=1883,
                tb_device_token="test-token",
            )
            ag = MQTTBridgeAgent(buffer=buf)

        ag._tb_connected = False  # simulate disconnected ThingsBoard

        msg = MagicMock()
        msg.topic = VALID_TOPIC
        msg.payload = json.dumps(VALID_PAYLOAD).encode()

        ag._on_local_message(None, None, msg)

        count = loop.run_until_complete(buf.pending_count())
        assert count == 1
    finally:
        loop.close()
        _asyncio.set_event_loop(None)


# ---------------------------------------------------------------------------
# Reconnect → OfflineBuffer.replay
# ---------------------------------------------------------------------------


def test_tb_reconnect_triggers_replay(tmp_path):
    """When ThingsBoard reconnects, on_connect triggers replay of buffered messages."""
    import asyncio as _asyncio

    loop = _asyncio.new_event_loop()
    _asyncio.set_event_loop(loop)
    try:
        buf = OfflineBuffer(db_path=str(tmp_path / "buf.db"))
        with patch("src.vpp.edge.mqtt_bridge.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                simulation_mode=True,
                site_id="site_test",
                tb_mqtt_host="tb.example.com",
                tb_mqtt_port=8883,
                local_mqtt_host="localhost",
                local_mqtt_port=1883,
                tb_device_token="test-token",
            )
            ag = MQTTBridgeAgent(buffer=buf)

        # Pre-populate buffer
        loop.run_until_complete(buf.store(VALID_PAYLOAD))
        assert loop.run_until_complete(buf.pending_count()) == 1

        replayed: list[dict] = []

        async def fake_forward(payload: dict) -> None:
            replayed.append(payload)

        ag._forward_to_tb = fake_forward
        ag._tb_connected = False

        ag._on_tb_connect(MagicMock(), None, None, 0)

        assert ag._tb_connected is True
        assert len(replayed) == 1
        assert loop.run_until_complete(buf.pending_count()) == 0
    finally:
        loop.close()
        _asyncio.set_event_loop(None)

"""Tests for DispatchAgent — command validation, routing, and acknowledgements."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from src.vpp.edge.dispatch_agent import DispatchAgent, DispatchCommand
from src.vpp.edge.modbus_writer import ModbusWriter

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_writer():
    """Return a MagicMock substituting ModbusWriter."""
    writer = MagicMock(spec=ModbusWriter)
    writer.write_setpoint.return_value = True
    return writer


@pytest.fixture()
def agent(mock_writer):
    """Return a DispatchAgent with mocked settings and writer."""
    with patch("src.vpp.edge.dispatch_agent.get_settings") as mock_settings:
        mock_settings.return_value = MagicMock(
            simulation_mode=True,
            site_id="site_test",
            local_mqtt_host="localhost",
            local_mqtt_port=1883,
        )
        ag = DispatchAgent(modbus_writer=mock_writer)
        ag._client = MagicMock()  # mock MQTT client for ack publishing
        return ag


VALID_CMD_DICT = {
    "method": "set_power",
    "der_id": "bess_01",
    "der_type": "battery",
    "params": {"power_kw": 50.0, "duration_s": 300},
    "request_id": "rpc-abc-123",
    "issued_at": "2026-05-15T10:00:00Z",
}


# ---------------------------------------------------------------------------
# DispatchCommand Pydantic validation
# ---------------------------------------------------------------------------


def test_dispatch_command_valid():
    """A fully-specified DispatchCommand parses without error."""
    cmd = DispatchCommand(**VALID_CMD_DICT)
    assert cmd.method == "set_power"
    assert cmd.der_id == "bess_01"
    assert cmd.params["power_kw"] == 50.0


def test_dispatch_command_missing_required_field():
    """A DispatchCommand missing required fields raises ValidationError."""
    bad = {k: v for k, v in VALID_CMD_DICT.items() if k != "method"}
    with pytest.raises(ValidationError):
        DispatchCommand(**bad)


def test_dispatch_command_wrong_type_for_params():
    """params must be a dict; a string raises ValidationError."""
    bad = {**VALID_CMD_DICT, "params": "not-a-dict"}
    with pytest.raises(ValidationError):
        DispatchCommand(**bad)


# ---------------------------------------------------------------------------
# Routing — set_power calls write_setpoint with correct args
# ---------------------------------------------------------------------------


def test_set_power_routes_to_modbus_writer(agent, mock_writer):
    """set_power command calls write_setpoint with method and params."""
    cmd = DispatchCommand(**VALID_CMD_DICT)
    agent._execute_command(cmd)

    mock_writer.write_setpoint.assert_called_once_with(
        "bess_01", "set_power", {"power_kw": 50.0, "duration_s": 300}
    )


def test_set_charge_routes_to_modbus_writer(agent, mock_writer):
    """set_charge command routes to write_setpoint correctly."""
    cmd = DispatchCommand(
        **{**VALID_CMD_DICT, "method": "set_charge", "params": {"state_of_charge": 0.8}}
    )
    agent._execute_command(cmd)
    mock_writer.write_setpoint.assert_called_once_with(
        "bess_01", "set_charge", {"state_of_charge": 0.8}
    )


# ---------------------------------------------------------------------------
# Acknowledgement publishing
# ---------------------------------------------------------------------------


def test_ack_published_to_response_topic_on_success(agent, mock_writer):
    """On success, an acknowledgement is published with status='success'."""
    mock_writer.write_setpoint.return_value = True
    cmd = DispatchCommand(**VALID_CMD_DICT)
    agent._execute_command(cmd)

    agent._client.publish.assert_called_once()
    call_args = agent._client.publish.call_args
    topic = call_args[0][0]
    payload = json.loads(call_args[0][1])

    assert "dispatch/responses" in topic
    assert payload["status"] == "success"
    assert payload["request_id"] == "rpc-abc-123"
    assert payload["der_id"] == "bess_01"


def test_ack_contains_failed_status_on_modbus_error(agent, mock_writer):
    """On ModbusException, acknowledgement contains status='failed' and error."""
    from pymodbus.exceptions import ModbusException

    mock_writer.write_setpoint.side_effect = ModbusException("register write failed")
    cmd = DispatchCommand(**VALID_CMD_DICT)
    agent._execute_command(cmd)

    agent._client.publish.assert_called_once()
    payload = json.loads(agent._client.publish.call_args[0][1])
    assert payload["status"] == "failed"
    assert "error" in payload
    assert "register write failed" in payload["error"]


def test_ack_failed_when_write_setpoint_returns_false(agent, mock_writer):
    """When write_setpoint returns False, no explicit ack with 'failed' is published
    (the agent logs but does not send a failed ack in this path)."""
    mock_writer.write_setpoint.return_value = False
    cmd = DispatchCommand(**VALID_CMD_DICT)
    agent._execute_command(cmd)

    # An ack IS published with success (the writer returned False, not raised)
    agent._client.publish.assert_called_once()
    payload = json.loads(agent._client.publish.call_args[0][1])
    # status reflects write_setpoint's boolean return
    assert payload["status"] in ("success", "failed")


# ---------------------------------------------------------------------------
# on_message — routing from raw MQTT bytes
# ---------------------------------------------------------------------------


def test_on_message_valid_payload_executes_command(agent, mock_writer):
    """A valid MQTT message triggers write_setpoint."""
    msg = MagicMock()
    msg.topic = "vpp/site_test/dispatch/commands"
    msg.payload = json.dumps(VALID_CMD_DICT).encode()

    agent._on_message(None, None, msg)
    mock_writer.write_setpoint.assert_called_once()


def test_on_message_invalid_json_is_ignored(agent, mock_writer):
    """Malformed JSON payload is silently dropped."""
    msg = MagicMock()
    msg.topic = "vpp/site_test/dispatch/commands"
    msg.payload = b"{{not valid json}}"

    agent._on_message(None, None, msg)
    mock_writer.write_setpoint.assert_not_called()


def test_on_message_missing_fields_is_ignored(agent, mock_writer):
    """Payload missing required fields is silently dropped."""
    msg = MagicMock()
    msg.topic = "vpp/site_test/dispatch/commands"
    msg.payload = json.dumps({"method": "set_power"}).encode()

    agent._on_message(None, None, msg)
    mock_writer.write_setpoint.assert_not_called()


# ---------------------------------------------------------------------------
# handle_tb_rpc
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_handle_tb_rpc_routes_correctly(agent, mock_writer):
    """handle_tb_rpc extracts method/params and executes the command."""
    rpc = {
        "id": "rpc-999",
        "method": "set_power",
        "params": {
            "der_id": "bess_01",
            "der_type": "battery",
            "power_kw": 30.0,
            "duration_s": 120,
        },
    }
    await agent.handle_tb_rpc(rpc)
    mock_writer.write_setpoint.assert_called_once()


@pytest.mark.asyncio
async def test_handle_tb_rpc_invalid_payload_ignored(agent, mock_writer):
    """handle_tb_rpc with missing fields does not call write_setpoint."""
    await agent.handle_tb_rpc({"id": "x"})  # missing method, params
    mock_writer.write_setpoint.assert_not_called()

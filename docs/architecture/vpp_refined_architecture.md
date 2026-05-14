# VPP Refined Architecture

## Overview

This document describes the three-layer Virtual Power Plant (VPP) architecture
implemented in the DERMS repository. The design separates concerns across the
physical site edge, a cloud aggregation platform (ThingsBoard CE), and the
central DERMS intelligence layer.

**Design philosophy:**

- **Edge-first resilience** — sites continue operating during cloud outages
  using the SQLite offline buffer and local Mosquitto broker.
- **Standard protocols** — MQTT for telemetry, Modbus TCP/RTU for DER control,
  REST for analytics integration.
- **Async-first Python** — all I/O operations are `async`, enabling high
  concurrency on both the Raspberry Pi edge nodes and the central server.
- **Zero-trust security** — TLS everywhere, ACL-enforced MQTT topics, JWT
  token authentication for ThingsBoard.

---

## Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Layer 3 — DERMS Intelligence (this repo)                               │
│  VPPAggregator · ThingsBoardClient · ML Forecasting · BatteryOptimizer │
└────────────────────────┬──────────────────────────────────────────────┘
                         │  REST API (HTTPS)
┌────────────────────────▼──────────────────────────────────────────────┐
│  Layer 2 — ThingsBoard CE Cloud                                        │
│  Asset Hierarchy · Rule Engine · MQTT Broker · REST API · Dashboards  │
└────────────┬──────────────────────────────┬───────────────────────────┘
             │  MQTT / TLS (port 8883)       │  REST RPC
  ┌──────────▼────────┐           ┌──────────▼────────┐
  │  Layer 1 — Site A │           │  Layer 1 — Site B │
  │  Raspberry Pi     │           │  Raspberry Pi     │
  │  ┌─────────────┐  │           │  ┌─────────────┐  │
  │  │ MyEMS CE    │  │           │  │ MyEMS CE    │  │
  │  │ Mosquitto   │  │           │  │ Mosquitto   │  │
  │  │ Bridge Agent│  │           │  │ Bridge Agent│  │
  │  │ Dispatch Agt│  │           │  │ Dispatch Agt│  │
  │  │ SQLite Buf  │  │           │  │ SQLite Buf  │  │
  │  └──────┬──────┘  │           │  └──────┬──────┘  │
  │         │ Modbus  │           │         │ Modbus  │
  │  [DERs: Solar, Battery, EV]   │  [DERs: ...]      │
  └───────────────────┘           └───────────────────┘
```

---

## Layer 1 — Site Edge (Raspberry Pi)

### Components

| Component | File | Purpose |
|---|---|---|
| MyEMS CE | External | Full EMS — data acquisition, validation, local control |
| Mosquitto MQTT Broker | `config/mosquitto/mosquitto.conf` | Local message bus (ports 1883 / 8883) |
| MQTT Bridge Agent | `src/vpp/edge/mqtt_bridge.py` | Subscribes locally, forwards to ThingsBoard |
| Dispatch Agent | `src/vpp/edge/dispatch_agent.py` | Receives RPC commands, writes Modbus setpoints |
| Offline Buffer | `src/vpp/edge/offline_buffer.py` | SQLite persistence + replay on reconnect |
| Modbus Writer | `src/vpp/edge/modbus_writer.py` | Modbus TCP/RTU register writes |

### MQTT Topic Namespace

All site telemetry follows the schema:

```
vpp/{site_id}/{der_type}/{der_id}/{metric}
```

| Segment | Example | Description |
|---|---|---|
| `site_id` | `site_A` | Unique site identifier |
| `der_type` | `solar`, `battery`, `meter`, `evcharger` | DER category |
| `der_id` | `inv_01`, `bess_01` | DER device identifier |
| `metric` | `telemetry` | Message type |

**Example topics:**

```
vpp/site_A/solar/inv_01/telemetry
vpp/site_A/battery/bess_01/telemetry
vpp/site_B/meter/m_01/telemetry
vpp/site_A/dispatch/commands
vpp/site_A/dispatch/responses
```

### Telemetry Payload Schema

```json
{
  "site_id": "site_A",
  "der_type": "battery",
  "der_id": "bess_01",
  "timestamp": "2026-05-15T10:00:00Z",
  "active_power_kw": 25.5,
  "energy_kwh": 120.0,
  "voltage_v": 400.0,
  "frequency_hz": 50.0,
  "state_of_charge": 0.78,
  "carbon_offset_kg": 12.3
}
```

### Offline Resilience

When the ThingsBoard connection is unavailable:

1. `MQTTBridgeAgent` catches the forward failure.
2. Calls `OfflineBuffer.store(payload)` — inserts into `buffer.db`.
3. On ThingsBoard reconnect (`on_connect` callback fires), calls
   `OfflineBuffer.replay(forward_fn)`.
4. Each pending message is forwarded; successful ones marked `forwarded=1`.
5. Failed messages increment `retry_count`; they are retried on next replay.
6. `OfflineBuffer.prune(max_age_hours=48)` runs periodically to clean up
   successfully forwarded records.

SQLite buffer schema:

```sql
CREATE TABLE telemetry_buffer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site_id TEXT NOT NULL,
    der_id TEXT NOT NULL,
    payload TEXT NOT NULL,        -- JSON string
    timestamp TEXT NOT NULL,
    forwarded INTEGER DEFAULT 0,  -- 0=pending, 1=forwarded
    retry_count INTEGER DEFAULT 0,
    created_at TEXT NOT NULL
);
```

---

## Layer 2 — ThingsBoard CE Cloud

ThingsBoard is an external managed service. This repository provisions its
configuration but does not run it.

### Asset Hierarchy

```
VPP Portfolio (Asset, type=VPP)
└── Site A - Residential (Asset, type=VPP_Site)
    ├── Solar Inverter 01 (Device, type=solar)
    ├── Battery BESS 01 (Device, type=battery)
    ├── Smart Meter 01 (Device, type=meter)
    └── EV Charger 01 (Device, type=evcharger)
```

The hierarchy is defined in `config/thingsboard/asset_hierarchy.json` and
provisioned via `AssetProvisioner.provision_all()`.

### ThingsBoard Capabilities Used

- **MQTT Telemetry Ingestion** — devices publish to `v1/devices/me/telemetry`
  authenticated with a per-device token over TLS (port 8883).
- **Rule Engine** — triggers dispatch RPCs on configurable grid events
  (e.g., frequency deviation, price signal).
- **One-way RPC** — `POST /api/rpc/oneway/{device_id}` dispatches commands
  to site Dispatch Agents.
- **Server-scope Attributes** — optimization results pushed by DERMS are
  stored as device attributes for dashboard display.

---

## Layer 3 — DERMS Intelligence

### Components

| Component | File | Purpose |
|---|---|---|
| ThingsBoard Client | `src/vpp/cloud/thingsboard_client.py` | Authenticated REST API access |
| Asset Provisioner | `src/vpp/cloud/asset_provisioner.py` | Idempotent hierarchy provisioning |
| VPP Aggregator | `src/vpp/aggregator.py` | Portfolio KPI aggregation + dispatch |
| DERMS Engine | `src/core/derms_engine.py` | Orchestration + `get_vpp_snapshot()` |

### Data Flow — Telemetry

```
DER
  │ Modbus TCP
  ▼
MyEMS CE (validates, stores locally)
  │ MQTT publish → vpp/site_A/solar/inv_01/telemetry
  ▼
Local Mosquitto Broker
  │ MQTT subscribe
  ▼
MQTTBridgeAgent._on_local_message()
  │ Pydantic validation
  ├─[online]──► ThingsBoard MQTT (v1/devices/me/telemetry)
  └─[offline]─► OfflineBuffer.store()  ──► replay on reconnect
```

### Data Flow — Dispatch

```
DERMSEngine.get_vpp_snapshot()
  │ calls VPPAggregator.get_portfolio_snapshot()
  │ calls VPPAggregator.dispatch_portfolio(power_kw, duration_s)
  │ calls ThingsBoardClient.send_dispatch_rpc(device_id, method, params)
  ▼
ThingsBoard Rule Engine
  │ RPC oneway → MQTT v1/devices/me/rpc/request/{id}
  ▼
DispatchAgent._on_message() or handle_tb_rpc()
  │ DispatchCommand Pydantic validation
  ▼
ModbusWriter.write_setpoint(der_id, method, params)
  │ Modbus TCP write_register()
  ▼
DER hardware register updated
  │ MQTT publish
  ▼
vpp/{site_id}/dispatch/responses
```

---

## Security Considerations

### MQTT Security

- **Authentication**: All clients authenticate with username/password
  (`password_file /etc/mosquitto/passwd`). No anonymous connections.
- **TLS**: External connections (port 8883) require TLS 1.3 and client
  certificates (`require_certificate true`).
- **ACL**: Topic-level access control enforced via `/etc/mosquitto/acl`.
  Each agent has the minimum required permissions.
- **Token management**: ThingsBoard device tokens are stored in environment
  variables, never hardcoded.

### REST API Security

- **JWT tokens** are obtained via `POST /api/auth/login` and refreshed
  automatically on 401 responses.
- **HTTPS only**: `TB_REST_URL` must use `https://` in production.
- **Credentials**: `TB_USERNAME` and `TB_PASSWORD` are loaded from environment
  variables / `.env` file. Never committed to version control.

### Modbus Security

- Modbus TCP has no built-in authentication; restrict access via firewall
  rules so only the Raspberry Pi can reach DER Modbus ports.
- The `ModbusWriter` DER registry is loaded from YAML — validate this file
  on deployment and restrict write access (`chmod 600`).

---

## Raspberry Pi Deployment Steps

1. **Install OS**: Raspberry Pi OS Lite (64-bit), enable SSH.
2. **Install dependencies**:
   ```bash
   sudo apt-get install -y mosquitto mosquitto-clients python3-pip
   pip install pymodbus paho-mqtt aiosqlite pydantic pydantic-settings pyyaml
   ```
3. **Copy configuration**:
   ```bash
   sudo cp config/mosquitto/mosquitto.conf /etc/mosquitto/mosquitto.conf
   sudo cp config/edge/site_config.yaml /etc/derms/site_config.yaml
   ```
4. **Configure TLS certificates** in `/etc/mosquitto/certs/`.
5. **Set environment variables** in `/etc/derms/.env`:
   ```
   SITE_ID=site_A
   TB_MQTT_HOST=thingsboard.example.com
   TB_DEVICE_TOKEN=<token>
   SIMULATION_MODE=false
   ```
6. **Run agents** (use `systemd` for production):
   ```bash
   python -m src.vpp.edge.mqtt_bridge
   python -m src.vpp.edge.dispatch_agent
   ```
7. **Provision ThingsBoard hierarchy** (run once from the central server):
   ```bash
   python -c "import asyncio; from src.vpp.cloud.asset_provisioner import AssetProvisioner; asyncio.run(AssetProvisioner().provision_all())"
   ```

---

## Environment Variable Reference

| Variable | Description | Default |
|---|---|---|
| `SITE_ID` | Unique site identifier | `site_A` |
| `TB_REST_URL` | ThingsBoard REST base URL | `https://thingsboard.example.com` |
| `TB_USERNAME` | ThingsBoard admin email | — |
| `TB_PASSWORD` | ThingsBoard admin password | — |
| `TB_MQTT_HOST` | ThingsBoard MQTT broker hostname | `thingsboard.example.com` |
| `TB_MQTT_PORT` | ThingsBoard MQTT port (TLS) | `8883` |
| `TB_DEVICE_TOKEN` | Per-site device token for TB MQTT | — |
| `LOCAL_MQTT_HOST` | Local Mosquitto broker hostname | `localhost` |
| `LOCAL_MQTT_PORT` | Local Mosquitto broker port | `1883` |
| `SIMULATION_MODE` | Skip hardware connections for testing | `false` |
| `DATABASE_URL` | SQLAlchemy async DB URL | `sqlite+aiosqlite:///./derms_dev.db` |
| `MQTT_BROKER_URL` | Legacy DERMS MQTT broker URL | `mqtt://localhost:1883` |
| `LOG_LEVEL` | Python log level | `INFO` |

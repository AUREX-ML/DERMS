# DERMS Architecture

## Overview

DERMS (Distributed Energy Resource Management System) is structured as a
layered platform that ingests real-time telemetry from distributed energy
resources (DERs), forecasts load and generation, runs optimization algorithms,
and exposes control actions through a REST API and MQTT messaging.

---

## ASCII Block Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          External World                                  │
│  Solar Panels │ Battery Banks │ EV Chargers │ Smart Meters │ Grid SCADA │
└───────┬───────┴───────┬───────┴──────┬──────┴──────┬───────┴──────┬─────┘
        │               │              │              │              │
        └───────────────┴──────────────┴──────────────┴─────────────┘
                                       │
                               MQTT / REST / Modbus
                                       │
┌──────────────────────────────────────▼──────────────────────────────────┐
│                       Data Ingestion Layer                               │
│  src/services/telemetry.py — normalise & validate incoming measurements │
│  src/services/grid_interface.py — two-way grid operator comms           │
└──────────────────────────────────────┬──────────────────────────────────┘
                                       │
              ┌────────────────────────┼────────────────────────┐
              │                        │                        │
┌─────────────▼──────────┐ ┌──────────▼──────────┐ ┌──────────▼──────────┐
│   ML Forecasting       │ │  Optimization Engine │ │   Resource Registry  │
│  src/models/           │ │  src/core/optimizer  │ │  src/core/           │
│  load_forecaster.py    │ │  .py                 │ │  derms_engine.py     │
│  (scikit-learn, SB3)   │ │  (LP / RL dispatch)  │ │  (CRUD + state)      │
└─────────────┬──────────┘ └──────────┬──────────┘ └──────────┬──────────┘
              │                        │                        │
              └────────────────────────┴────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────┐
│                          Storage Layer                                   │
│  PostgreSQL (persistent state, audit log, history)                      │
│  Redis (real-time cache, pub/sub, rate limiting)                        │
└──────────────────────────────────────┬──────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────┐
│                            API Layer                                     │
│  src/api/routes.py — FastAPI REST endpoints                             │
│  src/main.py      — CORS, lifespan, OpenAPI docs at /docs               │
└──────────────────────────────────────┬──────────────────────────────────┘
                                       │
                              HTTP / WebSocket
                                       │
                        Operators │ SCADA │ Third-party Apps
```

---

## Component Descriptions

### Data Ingestion Layer
- **`src/services/telemetry.py`** — Subscribes to MQTT topics for each DER,
  validates incoming payloads against Pydantic models, and writes normalised
  measurements to PostgreSQL and Redis.
- **`src/services/grid_interface.py`** — Implements OpenADR 2.0 / IEEE 2030.5
  client to receive demand-response signals and submit dispatch schedules to
  the grid operator.

### Resource Registry (`src/core/derms_engine.py`)
Central service for CRUD operations on DER records. Maintains an in-memory
state cache backed by Redis for sub-millisecond status reads.

### ML Forecasting (`src/models/load_forecaster.py`)
- 24-hour ahead probabilistic load forecasting using gradient-boosted trees
  (scikit-learn).
- Features: historical load, weather data, calendar features, price signals.
- Retrained nightly via a scheduled GitHub Actions workflow.

### Optimization Engine (`src/core/optimizer.py`)
- **Short-term dispatch (< 15 min)**: Rule-based heuristics for frequency
  regulation.
- **Day-ahead scheduling**: Linear programming (scipy.optimize / OR-Tools) to
  maximise revenue subject to battery SoC, grid limits, and tariff schedules.
- **Reinforcement learning (experimental)**: Stable-Baselines3 agent for
  multi-asset joint dispatch.

### Storage Layer
| Store      | Technology          | Usage                               |
| ---------- | ------------------- | ----------------------------------- |
| Primary DB | PostgreSQL 15       | Asset registry, time-series, audit  |
| Cache      | Redis 7             | Real-time state, pub/sub, sessions  |
| Blob store | Local / S3-compat   | ML model artefacts, raw CSVs        |

### API Layer
FastAPI application exposing a versioned REST API. Swagger UI available at
`/docs`, ReDoc at `/redoc`. Supports OAuth 2.0 Bearer tokens for
authenticated endpoints.

---

## Deployment Topologies

### Local / Development
```
docker-compose up
```
All services (app, postgres, redis, mosquitto) run as containers on
`localhost`.

### Production (Kubernetes)
- DERMS app deployed as a `Deployment` with horizontal pod autoscaling.
- PostgreSQL via managed cloud service (e.g., Cloud SQL, RDS).
- Redis via managed service (e.g., Elasticache, Redis Cloud).
- MQTT broker (Eclipse Mosquitto or HiveMQ) as a `StatefulSet`.

---

## Data Flow: Optimization Cycle

1. Telemetry service receives DER measurements via MQTT.
2. Measurements written to Redis (real-time) and PostgreSQL (history).
3. Load forecaster runs every 15 minutes; forecast written to Redis.
4. Optimizer reads current SoC, forecast, grid signals.
5. Optimal dispatch schedule computed and published back via MQTT / REST.
6. Grid interface submits aggregated schedule to grid operator.

---

## Security Considerations

- All API endpoints (except `/health`) require Bearer token authentication.
- MQTT connections use TLS with client certificate authentication.
- Secrets managed via environment variables; never committed to VCS.
- CodeQL and `pip-audit` scans run on every push via GitHub Actions.
- See [SECURITY.md](../SECURITY.md) for vulnerability reporting.

# DERMS — Virtual Power Plant

[![CI](https://github.com/AUREX-ML/DERMS/actions/workflows/ci.yml/badge.svg)](https://github.com/AUREX-ML/DERMS/actions/workflows/ci.yml)
[![CodeQL](https://github.com/AUREX-ML/DERMS/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/AUREX-ML/DERMS/actions/workflows/codeql-analysis.yml)
[![codecov](https://codecov.io/gh/AUREX-ML/DERMS/branch/main/graph/badge.svg)](https://codecov.io/gh/AUREX-ML/DERMS)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

**DERMS** is an open-source software platform for managing, monitoring, and optimising
**Distributed Energy Resources (DERs)** — including battery storage systems, solar PV
arrays, EV charging hubs, and demand-response loads. Built on **FastAPI**, **PostgreSQL**,
**Redis**, and **MQTT**, DERMS enables Virtual Power Plant (VPP) operators to aggregate
and dispatch flexible capacity across multiple sites, maximise revenue from energy markets,
and maintain grid stability through intelligent scheduling.

---

## ✨ Features

| Feature | Description |
|---|---|
| **Real-time monitoring** | Sub-second telemetry ingestion via MQTT; Redis-backed state cache |
| **ML load forecasting** | 24-hour probabilistic forecasts with scikit-learn gradient-boosted models |
| **Battery optimisation** | Rule-based heuristics + LP dispatch; Reinforcement Learning (experimental) |
| **Grid integration** | OpenADR 2.0 / IEEE 2030.5 demand-response client |
| **REST API** | FastAPI with OpenAPI docs, Bearer auth, and rate limiting |
| **Simulation mode** | Full system simulation without real hardware |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose 2.20+

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/AUREX-ML/DERMS.git
cd DERMS

# 2. Create and activate a virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your database, Redis, and MQTT settings

# 5. Start all services
docker-compose up --build
```

The API is now available at **http://localhost:8000**  
Swagger UI: **http://localhost:8000/docs**

---

## 💻 Usage

### CLI — Simulation Mode

```bash
# Run a 1-hour simulation with 20 synthetic DER assets
python scripts/run_simulation.py --duration 3600 --resources 20 --seed 42
```

### API — Register a Battery Asset

```bash
curl -X POST http://localhost:8000/api/v1/resources \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "name": "Site Alpha — Battery Bank 1",
    "type": "battery",
    "site_id": "site-alpha",
    "capacity_kw": 500.0
  }'
```

### API — Trigger Optimization

```bash
curl -X POST http://localhost:8000/api/v1/optimize \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"horizon_hours": 24, "objective": "maximize_revenue"}'
```

---

## 🏗️ Architecture

DERMS follows a layered architecture:

```
DERs (batteries, solar, EVs)  →  MQTT Telemetry  →  Redis Cache
                                                         ↓
                                ML Forecasting  →  Optimizer
                                                         ↓
                                          FastAPI REST API
                                                         ↓
                                       Grid Operator (OpenADR)
```

See [docs/architecture.md](docs/architecture.md) for the full diagram and component descriptions.

---

## 📁 Project Structure

```
src/
├── api/           # FastAPI routes
├── core/          # DERMS engine + optimizer
├── models/        # Pydantic DER models + forecaster
├── services/      # Telemetry (MQTT) + grid interface
└── utils/         # Config (pydantic-settings) + logger
tests/
├── unit/          # Model and optimizer unit tests
└── integration/   # API end-to-end tests
docs/              # Architecture, API reference, getting started
scripts/           # Simulation runner + data seeder
notebooks/         # EDA notebook
```

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) before
opening a pull request. We follow [Conventional Commits](https://www.conventionalcommits.org/)
and require all CI checks to pass.

---

## 🔒 Security

Please **do not** open public issues for security vulnerabilities.
See [SECURITY.md](SECURITY.md) for our private disclosure process.

---

## 📄 License

DERMS is released under the [Apache 2.0 License](LICENSE).

---

## 👥 Maintainers

| Name | Role | Contact |
|---|---|---|
| AUREX-ML | Project Owner | [@AUREX-ML](https://github.com/AUREX-ML) |

For general questions, open a [Discussion](https://github.com/AUREX-ML/DERMS/discussions).

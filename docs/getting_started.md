# Getting Started with DERMS

## Prerequisites

| Requirement      | Minimum Version | Notes                         |
| ---------------- | --------------- | ----------------------------- |
| Python           | 3.11            | Use pyenv for version mgmt    |
| Docker           | 24.0            | For containerised services    |
| Docker Compose   | 2.20            | Bundled with Docker Desktop   |
| Git              | 2.40            |                               |
| PostgreSQL       | 15 (optional)   | If running without Docker     |
| Redis            | 7 (optional)    | If running without Docker     |

---

## 1. Clone the Repository

```bash
git clone https://github.com/AUREX-ML/DERMS.git
cd DERMS
```

---

## 2. Set Up a Virtual Environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate       # macOS / Linux
# .venv\Scripts\activate        # Windows PowerShell

pip install --upgrade pip
pip install -r requirements.txt
```

---

## 3. Configure Environment Variables

Copy the example environment file and fill in your values:

```bash
cp .env.example .env
```

Open `.env` in your editor and set at minimum:

```
DATABASE_URL=postgresql+asyncpg://derms:secret@localhost:5432/derms
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">
SIMULATION_MODE=false
LOG_LEVEL=INFO
```

> **Never commit `.env` to version control.**

---

## 4. Run with Docker Compose (Recommended)

This starts the DERMS API, PostgreSQL, Redis, and the Mosquitto MQTT broker:

```bash
docker-compose up --build
```

The API will be available at **http://localhost:8000**.
Interactive API documentation: **http://localhost:8000/docs**

To run in the background:

```bash
docker-compose up -d --build
```

To stop all services:

```bash
docker-compose down
```

---

## 5. Run Without Docker (Development)

Start PostgreSQL and Redis separately (e.g., via Homebrew on macOS):

```bash
brew services start postgresql@15
brew services start redis
```

Apply database migrations:

```bash
alembic upgrade head
```

Start the DERMS API server:

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 6. Run in Simulation Mode

Simulation mode bypasses real hardware connections and generates synthetic
DER data. Useful for local development and testing:

```bash
# Set in .env:
SIMULATION_MODE=true

# Or run the simulation script directly:
python scripts/run_simulation.py \
    --duration 3600 \
    --resources 20 \
    --seed 42
```

---

## 7. Access API Documentation

| URL                            | Description                       |
| ------------------------------ | --------------------------------- |
| http://localhost:8000/docs     | Swagger UI (interactive)          |
| http://localhost:8000/redoc    | ReDoc (read-only)                 |
| http://localhost:8000/health   | Health check endpoint             |

---

## 8. Run Tests

```bash
# All tests with coverage report
pytest --cov=src --cov-report=term-missing -v

# Unit tests only
pytest tests/unit/ -v

# Integration tests (requires running postgres + redis)
pytest tests/integration/ -v
```

---

## 9. Seed Sample Data

```bash
python scripts/seed_data.py
```

This loads `data/sample_load_profile.csv` into the database and registers
a set of synthetic DER assets (10 batteries, 5 solar arrays).

---

## Next Steps

- Read [docs/architecture.md](architecture.md) for a deep dive into the
  system design.
- Read [docs/api_reference.md](api_reference.md) for a complete API reference.
- Read [CONTRIBUTING.md](../CONTRIBUTING.md) before submitting a PR.

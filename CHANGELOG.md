# Changelog

All notable changes to DERMS are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- (Your next change goes here)

### Changed

### Deprecated

### Removed

### Fixed

### Security

---

## [0.1.0] — 2026-05-14

### Added
- Initial open-source scaffold for DERMS Virtual Power Plant system.
- FastAPI REST API with `/health`, `/resources`, `/optimize`, and `/forecast`
  endpoints (`src/api/routes.py`, `src/main.py`).
- `DERMSEngine` orchestration class with resource registration, status
  retrieval, optimization dispatch, and forecast aggregation
  (`src/core/derms_engine.py`).
- `BatteryOptimizer` with heuristic (peak-shaving) and LP placeholder
  strategies (`src/core/optimizer.py`).
- Pydantic models for `BatteryStorage`, `SolarPanel`, `LoadForecast`, and
  `ForecastPoint` (`src/models/`).
- `TelemetryService` MQTT ingestion skeleton (`src/services/telemetry.py`).
- `GridInterface` OpenADR 2.0 client skeleton (`src/services/grid_interface.py`).
- Structured JSON logger via `python-json-logger` (`src/utils/logger.py`).
- Pydantic-settings based configuration management (`src/utils/config.py`).
- Unit test suite covering battery model, optimizer, and forecaster
  (`tests/unit/`).
- Integration test suite for the REST API using `httpx.AsyncClient`
  (`tests/integration/`).
- CI/CD pipeline with lint, test, and security scan jobs
  (`.github/workflows/ci.yml`).
- CodeQL security analysis workflow
  (`.github/workflows/codeql-analysis.yml`).
- GitHub issue templates for bug reports and feature requests
  (`.github/ISSUE_TEMPLATE/`).
- Pull request template (`.github/pull_request_template.md`).
- Architecture documentation with ASCII block diagram (`docs/architecture.md`).
- Getting started guide (`docs/getting_started.md`).
- REST API reference (`docs/api_reference.md`).
- Docker Compose stack: DERMS app, PostgreSQL 15, Redis 7, Mosquitto 2
  (`docker-compose.yml`).
- Sample load profile CSV (`data/sample_load_profile.csv`).
- Seed data script (`scripts/seed_data.py`).
- Simulation runner CLI script (`scripts/run_simulation.py`).
- Exploratory data analysis notebook (`notebooks/eda_energy_resources.ipynb`).
- `pyproject.toml` with build config, black, isort, mypy, and pytest settings.
- `requirements.txt` with pinned dependencies.
- `.env.example` template.
- `.gitignore` covering Python, Jupyter, Docker, IDE, and OS artefacts.
- `CONTRIBUTING.md`, `BRANCHING_STRATEGY.md`, `CHANGELOG.md`.
- Updated `README.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`.

[Unreleased]: https://github.com/AUREX-ML/DERMS/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/AUREX-ML/DERMS/releases/tag/v0.1.0

# Contributing to DERMS

Thank you for your interest in contributing to the DERMS Virtual Power Plant
project! This document describes the contribution workflow, coding standards,
and expectations for contributors.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Fork & Clone](#fork--clone)
3. [Branch Naming Convention](#branch-naming-convention)
4. [Development Setup](#development-setup)
5. [Conventional Commits](#conventional-commits)
6. [Code Style](#code-style)
7. [Running Tests](#running-tests)
8. [Pull Request Checklist](#pull-request-checklist)
9. [Reporting Bugs](#reporting-bugs)
10. [Security Vulnerabilities](#security-vulnerabilities)

---

## Code of Conduct

All contributors are expected to uphold our [Code of Conduct](CODE_OF_CONDUCT.md).
Respectful, inclusive behaviour is required in all project spaces.

---

## Fork & Clone

1. **Fork** the repository on GitHub by clicking the "Fork" button.
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/<your-username>/DERMS.git
   cd DERMS
   ```
3. Add the upstream remote:
   ```bash
   git remote add upstream https://github.com/AUREX-ML/DERMS.git
   ```
4. Keep your fork up to date:
   ```bash
   git fetch upstream
   git merge upstream/develop
   ```

---

## Branch Naming Convention

| Branch type | Pattern                        | Example                          |
| ----------- | ------------------------------ | -------------------------------- |
| Feature     | `feature/<short-description>`  | `feature/battery-optimizer-lp`   |
| Bug fix     | `bugfix/<issue-id>-description`| `bugfix/42-fix-soc-validation`   |
| Hotfix      | `hotfix/<short-description>`   | `hotfix/null-pointer-telemetry`  |
| Release     | `release/<version>`            | `release/0.2.0`                  |
| Docs        | `docs/<short-description>`     | `docs/update-api-reference`      |

- **Never commit directly to `main` or `develop`.**
- All changes flow through pull requests.
- Branch from `develop`, not `main`.

---

## Development Setup

```bash
# Create and activate virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install all dependencies including dev extras
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your local settings

# Start backing services
docker-compose up -d postgres redis mosquitto
```

---

## Conventional Commits

All commit messages must follow the
[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) standard:

```
<type>(<scope>): <short summary>

[optional body]

[optional footer(s)]
```

**Types:**

| Type       | When to use                                    |
| ---------- | ---------------------------------------------- |
| `feat`     | New feature or capability                      |
| `fix`      | Bug fix                                        |
| `docs`     | Documentation only                             |
| `style`    | Formatting, whitespace (no logic change)       |
| `refactor` | Code restructuring (no feature/fix)            |
| `test`     | Adding or updating tests                       |
| `chore`    | Build process, dependency updates              |
| `ci`       | CI/CD pipeline changes                         |
| `perf`     | Performance improvements                       |
| `security` | Security-related changes                       |

**Examples:**
```
feat(optimizer): add linear programming dispatch strategy
fix(telemetry): handle malformed MQTT payloads gracefully
docs(api): update /forecast endpoint reference
test(battery): add SoC boundary condition tests
```

---

## Code Style

We use the following tools — all enforced by CI:

| Tool    | Purpose              | Config          |
| ------- | -------------------- | --------------- |
| `black` | Code formatting      | `pyproject.toml`|
| `flake8`| Style linting        | max-line=88     |
| `isort` | Import ordering      | `pyproject.toml`|
| `mypy`  | Static type checking | `pyproject.toml`|

Run all checks locally before pushing:

```bash
black src/ tests/ scripts/
isort src/ tests/ scripts/
flake8 src/ tests/ scripts/ --max-line-length=88
mypy src/ --ignore-missing-imports
```

---

## Running Tests

```bash
# Full test suite with coverage
pytest --cov=src --cov-report=term-missing -v

# Unit tests only
pytest tests/unit/ -v

# Integration tests (requires postgres + redis running)
pytest tests/integration/ -v
```

Aim to maintain or improve the coverage percentage with every PR.

---

## Pull Request Checklist

Before opening a PR, confirm:

- [ ] Code is formatted (`black`, `isort`)
- [ ] No linting errors (`flake8`, `mypy`)
- [ ] All existing tests pass (`pytest`)
- [ ] New functionality has accompanying tests
- [ ] Documentation updated if behaviour changed
- [ ] `CHANGELOG.md` updated under `[Unreleased]`
- [ ] PR description fills in all sections of the PR template
- [ ] PR is targeting the `develop` branch (not `main`)
- [ ] A reviewer has been assigned

---

## Reporting Bugs

Use the [Bug Report template](https://github.com/AUREX-ML/DERMS/issues/new?template=bug_report.md).
Include as much detail as possible: steps to reproduce, expected vs. actual
behaviour, environment details, and sanitised log output.

---

## Security Vulnerabilities

**Do NOT open a public GitHub issue for security vulnerabilities.**

Instead, follow the private disclosure process described in
[SECURITY.md](SECURITY.md). We will acknowledge within 72 hours and work
with you on a coordinated disclosure timeline.

# DERMS Branching Strategy

This document describes the Git branching model used by the DERMS project.
We follow a simplified **Git Flow** strategy suited for an open-source project
with rolling releases.

---

## Branch Overview

```
main
 └── develop
      ├── feature/battery-optimizer-lp
      ├── feature/openaddr-client
      ├── bugfix/42-telemetry-null-payload
      └── release/0.2.0
           └── hotfix/soc-validation-crash
```

| Branch            | Purpose                                           | Protected |
| ----------------- | ------------------------------------------------- | --------- |
| `main`            | Production-ready code; tagged releases only       | ✅ Yes    |
| `develop`         | Integration branch; next release staging          | ✅ Yes    |
| `feature/*`       | New features; branch from and merge back to `develop` | No    |
| `bugfix/*`        | Non-urgent bug fixes; branch from `develop`       | No        |
| `hotfix/*`        | Urgent production fixes; branch from `main`       | No        |
| `release/*`       | Release preparation; branch from `develop`        | No        |
| `docs/*`          | Documentation-only changes                        | No        |

---

## Rules

### `main`
- **No direct commits.** All changes arrive via a `release/*` or `hotfix/*` PR.
- Requires **at least 1 approving review** before merge.
- Every merge to `main` receives a **semantic version tag** (e.g. `v0.2.0`).
- CI must be green (lint + tests + security scan) before merge is permitted.

### `develop`
- **No direct commits** from contributors. All changes via PR.
- Requires **at least 1 approving review**.
- Feature and bugfix branches merge here via squash-and-merge or merge commit.

### `feature/*`
- Branch from `develop`:
  ```bash
  git checkout develop
  git pull upstream develop
  git checkout -b feature/my-feature-name
  ```
- Name format: `feature/<short-kebab-description>` (e.g. `feature/lp-optimizer`).
- Delete the branch after merge.

### `bugfix/*`
- Branch from `develop`.
- Name format: `bugfix/<issue-id>-short-description`
  (e.g. `bugfix/42-fix-soc-boundary`).
- Delete after merge.

### `hotfix/*`
- Branch from `main` for production-critical fixes:
  ```bash
  git checkout main
  git pull upstream main
  git checkout -b hotfix/critical-crash-fix
  ```
- After approval, merge into **both** `main` and `develop`.
- Tag the resulting `main` commit with a patch version (e.g. `v0.1.1`).

### `release/*`
- Branch from `develop` when preparing a release:
  ```bash
  git checkout develop
  git checkout -b release/0.2.0
  ```
- Only bug fixes, documentation, and version bumps are allowed here.
- Merge into `main` (tagged) and back into `develop` when release ships.

---

## Semantic Version Tags

Tags are applied to `main` only, following [SemVer](https://semver.org/):

| Increment | When                                              | Example           |
| --------- | ------------------------------------------------- | ----------------- |
| **MAJOR** | Breaking API or data model changes                | `v1.0.0 → v2.0.0`|
| **MINOR** | Backwards-compatible new features                 | `v0.1.0 → v0.2.0`|
| **PATCH** | Backwards-compatible bug fixes / hotfixes         | `v0.1.0 → v0.1.1`|

Tag a release:
```bash
git tag -a v0.2.0 -m "Release 0.2.0 — LP optimizer and OpenADR client"
git push upstream v0.2.0
```

---

## Branch Deletion Policy

- All merged `feature/*`, `bugfix/*`, `hotfix/*`, and `release/*` branches
  **must be deleted** after the PR is merged.
- Use the GitHub "Delete branch" button on the merged PR, or:
  ```bash
  git push origin --delete feature/my-feature-name
  ```

---

## PR Target Summary

| Branch type | PR target   |
| ----------- | ----------- |
| `feature/*` | `develop`   |
| `bugfix/*`  | `develop`   |
| `docs/*`    | `develop`   |
| `release/*` | `main`      |
| `hotfix/*`  | `main` + `develop` (two PRs) |

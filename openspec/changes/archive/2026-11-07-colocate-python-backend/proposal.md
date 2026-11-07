# Proposal

## Why

The repo is now a full-stack ledger app (Telegram + FastAPI + Vue) but Python still lives at the root (`src/`, `tests/`, `pyproject.toml`) while the SPA is already namespaced under `frontend/`. That mix makes the tree harder to scan and invites path mistakes (stdlib `http` collisions, `ruff`/`pytest` at the wrong level). The web change landed; this is the moment to give Python the same package home before more adapters pile onto the root.

## What Changes

- Treat the repository as a **two-package monolith**: `backend/` owns all Python (package, tests, uv project), `frontend/` stays the Vue app, root keeps Compose, env example, README, and OpenSpec.
- **BREAKING** for local commands: `uv sync`, `uv run pytest`, ruff, and mypy run from `backend/` (or `uv --directory backend`), not from the repo root. Import names (`income_expense_bot`) and HTTP/Telegram behavior stay the same.
- Move `src/income_expense_bot` to `backend/src/income_expense_bot` (keep src layout inside the Python project) and `tests/` to `backend/tests/`.
- Relocate `pyproject.toml` and `uv.lock` into `backend/`. Point Dockerfile and `.dockerignore` at the new tree. Update README setup/test/build commands.
- Do not rename the Python package, do not split a second uv workspace, do not rename `frontend/`, do not add nginx/Pi SPA hosting, do not change ledger behavior.

**Confirmed:** two-package tree; tests move with Python; package name unchanged.

**Assumed:** Dockerfile stays at the repo root (Compose/`docker buildx` from `.`) and copies `backend/` rather than moving the Dockerfile inside `backend/`. Root `.venv` is discarded in favor of `backend/.venv`.

**Out of scope:** new bots, shared libraries between bots, frontend folder rename, CI workflows (none exist).

## Capabilities

### New Capabilities

- `income-expense-workspace`: Operator-facing layout of this full-stack repo — where Python, tests, the SPA, and Compose live, and which directory is the Python project root.

### Modified Capabilities

- None. Ledger, HTTP, Telegram, logging, and hosting requirements stay as they are; only documented paths and the Docker build context change.

## Impact

- Files: `src/`, `tests/`, `pyproject.toml`, `uv.lock`, `Dockerfile`, `.dockerignore`, `README.md`, `.gitignore` (`backend/.venv`, `backend` test caches). Compose image name and Pi flow stay the same.
- APIs and domain: unchanged. Hexagonal layers stay inside `income_expense_bot`.
- Operator: clone/setup commands in README; GHCR rebuild after merge so the image contains `backend/src`.
- Pi: no compose change if the published image still runs `python -m income_expense_bot`.

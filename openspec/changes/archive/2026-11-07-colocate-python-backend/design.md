# Design

## Context

See `proposal.md` for motivation. Today: Hatch src layout at repo root (`src/income_expense_bot`, `tests/`, `pyproject.toml`, `uv.lock`, `.venv`), Vue already in `frontend/`, Compose/`Dockerfile`/`.env.example` at root. Image `COPY src ./src` then `CMD python -m income_expense_bot`. Hexagonal package internals stay put; this change only relocates the Python *project*.

## Goals / Non-Goals

**Goals:**

- One Python project directory that owns sources, tests, and uv metadata.
- Keep src layout *inside* that directory so hatch/pytest/mypy paths stay conventional.
- Keep Compose and secrets at the git root (Pi checkout).
- Leave `income_expense_bot` import path and CQRS/hexagonal layers unchanged.

**Non-Goals:**

- uv workspaces, npm workspaces, or a shared `packages/` library.
- Renaming `frontend/` to `web/` or `apps/web`.
- Moving Dockerfile into `backend/` (see decision 2).
- Changing domain, HTTP routes, or Telegram.

## Decisions

### 1. Two-package monolith (`backend/` + `frontend/`), not apps/* or a single src tree

Target tree:

```
personal-ops-bots/
  backend/
    src/income_expense_bot/
    tests/{unit,integration}
    pyproject.toml
    uv.lock
  frontend/                 # unchanged
  compose.yaml
  Dockerfile
  .env.example
  README.md
  openspec/
```

This is the usual layout for a small full-stack app with two runtimes (Python + Node): each package manager owns a folder; orchestration stays at the root.

**Alternative: keep `pyproject.toml` at root, only move code to `backend/`.** Rejected: uv/pytest/ruff would still treat the git root as the Python project, so `frontend/` keeps leaking into Python tooling.

**Alternative: `apps/backend` + `apps/frontend` (Nx-style).** Rejected: one app, `frontend/` already exists; extra rename with no tool that needs `apps/`.

**Alternative: `backend/income_expense_bot/` without inner `src/`.** Rejected: Hatch src layout is already in use; dropping it makes `cd backend` put the package on `sys.path` accidentally. Keep `[tool.hatch.build.targets.wheel] packages = ["src/income_expense_bot"]`, `pythonpath = ["src"]`, `mypy_path = "src"`, `ruff src = ["src", "tests"]`.

**Alternative: nest SPA under `backend/static` or `backend/frontend`.** Rejected: Vite/pnpm must stay independent of uv; spec requires sibling `frontend/`.

### 2. Dockerfile stays at repo root; copy `backend/`

Builder:

```
COPY backend/pyproject.toml backend/uv.lock ./
COPY backend/src ./src
```

Runtime still `COPY --from=builder /app/src /app/src` and `CMD ["python", "-m", "income_expense_bot"]`. Documented `docker buildx ... --push .` stays at the git root.

**Alternative: `backend/Dockerfile` + `docker build backend`.** Slightly cleaner isolation, but Compose and the Pi README currently build/push from `.`. Moving the Dockerfile would churn hosting docs for no runtime gain. Revisit if a second Python image appears.

`.dockerignore`: ignore `frontend/`, keep ignoring `openspec/`; stop ignoring a root `tests/` that no longer exists; do not send `backend/tests` into the image (optional explicit ignore).

### 3. Operator commands

README: `cd backend && uv sync` then `uv run python -m income_expense_bot`, `uv run uvicorn ...`, `uv run pytest`, `uv run ruff check src tests`, `uv run mypy src/income_expense_bot`. Frontend commands stay `cd frontend`. Root `.venv` is not used; gitignore `backend/.venv` (root `.venv/` pattern already matches nested venvs if named `.venv`).

No import rewrites inside `income_expense_bot` or tests except if any test hard-codes repo-root paths (none observed; pytest uses `pythonpath = ["src"]` relative to pyproject).

### 4. Git move

Use `git mv` for `src` → `backend/src`, `tests` → `backend/tests`, and the uv files so history follows.

## Risks / Trade-offs

- [Stale root `.venv`] → After move, `uv sync` in `backend/`; operator deletes root `.venv` locally. Do not commit it.
- [Image still has old `/app/src` layout] → Fine: container layout need not match the git tree. Rebuild/push GHCR after merge or the Pi keeps the old tree until refresh.
- [Someone runs `uv run pytest` at repo root] → Fails without pyproject. README is the mitigation; no root shim.
- [PR #4 still on `src/` at root] → Apply this change on a branch that includes or follows that layout; rebase if needed.

## Migration Plan

1. `git mv` sources, tests, uv files into `backend/`.
2. Fix Dockerfile, `.dockerignore`, README, gitignore if needed.
3. `cd backend && uv sync && uv run pytest && uv run ruff check src tests && uv run mypy src/income_expense_bot`.
4. Deploy: rebuild/push GHCR; Pi `compose pull` unchanged.

Rollback: reverse the `git mv` and restore root pyproject.

## Open Questions

None. Dockerfile-at-root is recorded as an assumption in the proposal.

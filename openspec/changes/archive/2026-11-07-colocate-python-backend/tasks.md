# Tasks

## 1. Relocate the Python project

- [x] 1.1 `git mv` `src` to `backend/src`, `tests` to `backend/tests`, and `pyproject.toml` plus `uv.lock` into `backend/`, then verify the repo root has no `src/`, `tests/`, or `pyproject.toml` (`income-expense-workspace`: Python project lives under backend)
- [x] 1.2 Run `uv sync` in `backend/` and verify `backend/.venv` exists and `uv run python -c "import income_expense_bot"` succeeds from `backend/` (`income-expense-workspace`: Python commands run from the backend project)

## 2. Image build context

- [x] 2.1 Update the root `Dockerfile` to copy `backend/pyproject.toml`, `backend/uv.lock`, and `backend/src`, and verify it still `CMD`s `python -m income_expense_bot` (`income-expense-workspace`: Compose and secrets stay at the repository root)
- [x] 2.2 Update `.dockerignore` so `frontend/` and `backend/tests` are not in the build context, and verify Compose remains `compose.yaml` at the repo root (`income-expense-workspace`: SPA stays a sibling of backend; Compose at root)

## 3. Operator docs and README tests

- [x] 3.1 Rewrite README setup, bot/API start, pytest, ruff, and mypy commands to run from `backend/` (`cd backend` or `uv --directory backend`) and verify they do not mention a root-level `tests/` directory (`income-expense-workspace`: Python commands run from the backend project)
- [x] 3.2 Extend `tests/unit/interfaces/test_readme.py` (now under `backend/tests`) so it asserts the README tells operators to work in `backend/` for Python and still documents no login, then verify that test passes (`income-expense-workspace`: documented pytest and bot start)

## 4. Integration checks

- [x] 4.1 From `backend/`, run `uv run pytest` and verify the full Python suite passes (`income-expense-workspace`: documented pytest)
- [x] 4.2 From `backend/`, run `uv run ruff check src tests` and `uv run mypy src/income_expense_bot` and verify no errors
- [x] 4.3 List the repo root and verify `frontend/` and `backend/` are siblings, `compose.yaml` is at the root, and `frontend/` was not moved (`income-expense-workspace`: SPA sibling; Compose at root)

## Workflow follow-up

- Archive the change after review.
- Rebuild and push the GHCR image so the Pi pull matches the new Docker context.

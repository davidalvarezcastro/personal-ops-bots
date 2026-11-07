# Tasks

## 1. Image

- [x] 1.1 Add `.dockerignore` excluding `.git`, `.env`, `data/`, tests, caches, and `openspec/`, and verify unit tests assert `.env` and `data/` are listed (`income-expense-hosting`: secrets not in image)
- [x] 1.2 Add a multi-stage `Dockerfile` (`python:3.12-slim`, `uv sync --frozen --no-dev`, `CMD python -m income_expense_bot`, `LEDGER_SQLITE_PATH=/data/ledger.sqlite`, `LOG_FORMAT=json`) that does not copy `.env`, and verify tests assert no `COPY .env` (`income-expense-hosting`: secrets; restartable process)

## 2. Compose and data dir

- [x] 2.1 Add `compose.yaml` with service `income-expense-bot`, `image: ghcr.io/davidalvarezcastro/income-expense-bot:latest`, no `build:`, no `ports:`, `restart: unless-stopped`, `mem_limit: 384m`, `env_file` `.env`, bind `./data:/data`, and verify a unit test asserts those properties (`income-expense-hosting`: Compose service; GHCR image; no ports; ledger survives)
- [x] 2.2 Gitignore `data/*` (keep `data/.gitkeep`) and verify `data/*.sqlite` is not tracked (`income-expense-hosting`: ledger on host)

## 3. Operator docs

- [x] 3.1 Document in README the Pi 3B 64-bit manual release: laptop `docker login` + `buildx --platform linux/arm64 --push` (`latest` and git SHA), Pi `chmod 600` `.env`, `LEDGER_SQLITE_PATH=/data/ledger.sqlite`, `docker login` + `docker compose pull` + `up -d`, on-Pi build as last resort, and verify tests require `ghcr.io`, `--push`, and `docker compose pull` (`income-expense-hosting`: off-host publish; pull then up)

## 4. Integration checks

- [x] 4.1 Run `uv run pytest` and verify tests pass
- [x] 4.2 Run `uv run ruff check src tests` and verify no errors
- [x] 4.3 If Docker is available, run `docker compose config` and verify the resolved image is the GHCR name; otherwise skip and note it

## Workflow follow-up

- Archive the change after implementation is verified.
- Merge delta specs into `openspec/specs/income-expense-hosting`.
- A later change can add GitHub Actions that push the same image name.

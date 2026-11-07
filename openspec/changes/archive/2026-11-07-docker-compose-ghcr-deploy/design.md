# Design

## Context

The bot is `python -m income_expense_bot` (Telegram polling, SQLite, env config). There is no Dockerfile or Compose yet. Hardware: Raspberry Pi 3B, 1 GB RAM — building Python images on the Pi is likely to OOM. See `proposal.md` for motivation; behavior is in `specs/income-expense-hosting/spec.md`.

## Goals / Non-Goals

**Goals:**

- Slim `linux/arm64` image from `uv.lock` without the `dev` group.
- Compose: one service, GHCR image, bind-mounted `./data`, host `.env`, `mem_limit: 384m`, `restart: unless-stopped`, no ports, no `build:`.
- Manual laptop `buildx --push`; Pi `login` + `pull` + `up`.
- Domain/application untouched.

**Non-Goals:**

- GitHub Actions workflows (same image name so they can be added later).
- Tarball/`docker load` as the documented path.
- Webhook, reverse proxy, extra Compose services.
- Building on the Pi as default.

## Decisions

### 1. Image name and registry

`ghcr.io/davidalvarezcastro/income-expense-bot:latest` plus git SHA tag on push. Package **private**.

**Alternative:** local tag + `docker save`/`scp`. Rejected: bulky on the Pi and a different name than future Actions.

**Alternative:** `compose build` on the Pi. Rejected (1 GB RAM). Mention in README as last resort only.

### 2. Multi-stage Dockerfile + uv

- `python:3.12-slim-bookworm`; copy official `uv`; `uv sync --frozen --no-dev --no-editable`.
- Runtime: venv + `src`, non-root user, `/data` writable.
- `CMD ["python", "-m", "income_expense_bot"]`.
- Image env: `LOG_FORMAT=json`, `LEDGER_SQLITE_PATH=/data/ledger.sqlite`, `TZ=Europe/Madrid`. Token still required at runtime.
- `.dockerignore`: `.git`, `.env`, `data/`, tests, caches, `openspec/`. No `COPY .env`.

### 3. Compose (run only)

```
services:
  income-expense-bot:
    image: ghcr.io/davidalvarezcastro/income-expense-bot:latest
    env_file:
      - path: .env
        required: false
    environment:
      LEDGER_SQLITE_PATH: /data/ledger.sqlite
      LOG_FORMAT: json
    volumes:
      - ./data:/data
    restart: unless-stopped
    mem_limit: 384m
    cpus: "1.0"
```

No `ports:`, no `build:`. `required: false` on `env_file` so `docker compose config` works without a local `.env`. Bind-mount the **directory** `./data`. Gitignore `data/*` with `data/.gitkeep`.

### 4. Manual release

Laptop:

```
docker login ghcr.io
docker buildx build --platform linux/arm64 \
  -t ghcr.io/davidalvarezcastro/income-expense-bot:latest \
  -t ghcr.io/davidalvarezcastro/income-expense-bot:$(git rev-parse --short HEAD) \
  --push .
```

Pi (`~/personal-ops-bots`): copy repo or at least `compose.yaml` + `.env.example`, `chmod 600 .env`, then `docker login` + `docker compose pull` + `up -d`.

### 5. Tests

File assertions: Compose image is GHCR, no `ports`/`build`, Dockerfile has no `COPY .env`, dockerignore lists `.env` and `data/`. README: `ghcr.io`, `--push`, `docker compose pull`. `docker compose config` when Docker exists. No Telegram live test.

## Risks / Trade-offs

- [GHCR 403 on pull] → Document `read:packages` and login on the Pi.
- [Cross-build needs qemu on the laptop] → First `buildx` is slow.
- [384 MB too low] → Bump `mem_limit` in Compose only.

## Migration Plan

- First deploy: push image, create `.env` and `data/` on the Pi, pull, `up -d`.
- Update: push new tags, `compose pull && up -d` (same volume).
- Rollback: push a previous SHA as `:latest` and pull again.

## Open Questions

- None that change specs. Host path is documented as `~/personal-ops-bots`.

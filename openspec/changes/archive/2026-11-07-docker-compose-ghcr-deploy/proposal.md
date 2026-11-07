# Proposal

## Why

The ledger bot only runs on a developer machine via `uv run`. It needs to stay up on a Raspberry Pi 3B (64-bit, 1 GB RAM) with Docker Compose. Building on that host is unsafe; the image should be built on a laptop and published to GitHub Container Registry so the Pi only pulls and runs.

## What Changes

- Add a production `linux/arm64` image (Python 3.12, `uv.lock`, no dev extras) whose default run command is the existing bot process.
- Add Compose with one service: image from GHCR, `restart: unless-stopped`, memory cap for 1 GB RAM, ledger on a host data directory, secrets from host `.env`, no published ports.
- Document a **manual** release: on the laptop, `buildx --platform linux/arm64 --push` to `ghcr.io/davidalvarezcastro/income-expense-bot`; on the Pi, `docker login`, `docker compose pull`, `docker compose up -d`.
- Do not add GitHub Actions in this change; the image name must stay usable for Actions later.
- Tarball/`docker load` is not the documented path.

### Confirmed decisions

- Target: Raspberry Pi 3B, 64-bit (`linux/arm64`), 1 GB RAM, 4 cores, ~150 GB disk, 1 GB swap.
- Runtime: Docker + Compose already on the Pi; outbound HTTPS only (Telegram polling).
- Image store: private GHCR. Build and push from a laptop, never as the default on the Pi.
- One Compose service for this bot; future bots get their own service and volume.

### Assumptions

- Operator can `docker login ghcr.io` with `write:packages` (laptop) and `read:packages` (Pi).
- Repo owner is `davidalvarezcastro`.
- Host `.env` lives on the Pi, not in git.

### Unresolved questions

- Host directory on the Pi (`~/personal-ops-bots` vs `/opt`) can stay a documented default.

### Acceptance criteria

- Compose `image:` is `ghcr.io/.../income-expense-bot` (not an un-namespaced local tag).
- `docker compose config` succeeds; no `ports:`; `restart: unless-stopped`.
- README describes laptop push and Pi pull/`up -d`; `.env` is chmod 600; token is not in the image.
- Recreating the container leaves the SQLite file on the host data directory.

## Capabilities

### New Capabilities

- `income-expense-hosting`: Run the income/expense bot as a long-lived Compose service whose image comes from GitHub Container Registry.

### Modified Capabilities

- None. Ledger commands, guidance, and log event shapes stay the same.

## Impact

- New `Dockerfile`, `.dockerignore`, `compose.yaml`, `data/` gitignore.
- README: Pi 3B + GHCR manual release.
- No domain/application Python changes.
- Operator maintains `.env` and a GHCR token on the Pi.

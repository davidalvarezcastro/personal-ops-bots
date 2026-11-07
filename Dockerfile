FROM python:3.12-slim-bookworm AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_NO_DEV=1

COPY pyproject.toml uv.lock ./
COPY src ./src
RUN uv sync --frozen --no-dev --no-editable

FROM python:3.12-slim-bookworm AS runtime

WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    LOG_FORMAT=json \
    LEDGER_SQLITE_PATH=/data/ledger.sqlite \
    TZ=Europe/Madrid

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

RUN groupadd --gid 1000 bot \
    && useradd --uid 1000 --gid bot --home-dir /app --no-create-home bot \
    && mkdir -p /data \
    && chown bot:bot /data

USER bot
VOLUME ["/data"]
CMD ["python", "-m", "income_expense_bot"]

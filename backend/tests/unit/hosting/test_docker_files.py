from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]


def test_dockerignore_excludes_secrets_and_data() -> None:
    text = (ROOT / ".dockerignore").read_text(encoding="utf-8")
    assert ".env" in text
    assert "data/" in text
    assert "backend/tests" in text
    assert "frontend/" in text
    assert "openspec/" in text


def test_dockerfile_does_not_copy_env() -> None:
    text = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "COPY .env" not in text
    assert "uv sync --frozen --no-dev" in text
    assert "python:3.12-slim" in text
    assert "income_expense_bot" in text
    assert "LEDGER_SQLITE_PATH=/data/ledger.sqlite" in text
    assert "LOG_FORMAT=json" in text
    assert "--uid 1000" in text
    assert "--gid 1000" in text


def test_data_sqlite_is_gitignored() -> None:
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "data/*" in gitignore
    assert "*.sqlite" in gitignore


def test_compose_uses_ghcr_and_is_unexposed() -> None:
    text = (ROOT / "compose.yaml").read_text(encoding="utf-8")
    assert "income-expense-bot:" in text
    assert "image: ghcr.io/davidalvarezcastro/income-expense-bot:latest" in text
    assert "build:" not in text
    assert "ports:" not in text
    assert "restart: unless-stopped" in text
    assert "mem_limit: 384m" in text
    assert "./data:/data" in text
    assert "user: \"1000:1000\"" in text
    assert ".env" in text
    assert "LEDGER_SQLITE_PATH: /data/ledger.sqlite" in text
    assert "LOG_FORMAT: json" in text

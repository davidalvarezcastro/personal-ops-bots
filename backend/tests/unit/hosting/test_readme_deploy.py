from pathlib import Path

README = Path(__file__).resolve().parents[4] / "README.md"
COMPOSE = Path(__file__).resolve().parents[4] / "compose.yaml"


def test_readme_documents_ghcr_manual_release() -> None:
    text = README.read_text(encoding="utf-8")
    compose = COMPOSE.read_text(encoding="utf-8")
    image = "ghcr.io/davidalvarezcastro/income-expense-bot"
    assert "linux/arm64" in text
    assert "buildx" in text
    assert "--push" in text
    assert "docker compose pull" in text
    assert "docker compose up -d" in text
    assert "chmod 600" in text
    assert "LEDGER_SQLITE_PATH=/data/ledger.sqlite" in text
    assert "LOG_FORMAT=json" in text
    pi_section = text.split("Raspberry Pi", 1)[1]
    assert "TELEGRAM_BOT_TOKEN=replace-me" in pi_section
    assert "TELEGRAM_ALLOWED_USER_IDS=123456789" in pi_section
    assert "LEDGER_SQLITE_PATH=ledger.sqlite" not in pi_section
    assert "last resort" in text.lower()
    assert image in text
    assert f"image: {image}:latest" in compose

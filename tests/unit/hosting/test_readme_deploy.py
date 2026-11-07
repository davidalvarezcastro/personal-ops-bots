from pathlib import Path

README = Path(__file__).resolve().parents[3] / "README.md"
COMPOSE = Path(__file__).resolve().parents[3] / "compose.yaml"


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
    assert "last resort" in text.lower()
    assert image in text
    assert f"image: {image}:latest" in compose

from pathlib import Path

README = Path(__file__).resolve().parents[3] / "README.md"


def test_readme_documents_commands_and_logging() -> None:
    text = README.read_text(encoding="utf-8")
    for command in ("/start", "/help", "/expense", "/income", "/balance"):
        assert command in text
    assert "LOG_LEVEL" in text
    assert "LOG_FORMAT" in text
    assert "stdout" in text.lower()
    assert "uvicorn income_expense_bot.interfaces.http.app:app" in text
    assert "pnpm dev" in text
    assert "There is no login." in text

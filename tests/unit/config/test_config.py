import pytest

from income_expense_bot.config import Config, ConfigError


def test_from_env_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token")
    monkeypatch.setenv("TELEGRAM_ALLOWED_USER_IDS", "1, 2")
    monkeypatch.setenv("LEDGER_SQLITE_PATH", "/tmp/ledger.sqlite")
    config = Config.from_env()
    assert config.telegram_bot_token == "token"
    assert config.telegram_allowed_user_ids == frozenset({1, 2})
    assert config.ledger_sqlite_path == "/tmp/ledger.sqlite"


def test_missing_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.setenv("TELEGRAM_ALLOWED_USER_IDS", "1")
    with pytest.raises(ConfigError):
        Config.from_env()


def test_empty_allowlist(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token")
    monkeypatch.setenv("TELEGRAM_ALLOWED_USER_IDS", "  ,  ")
    with pytest.raises(ConfigError):
        Config.from_env()

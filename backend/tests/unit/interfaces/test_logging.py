from __future__ import annotations

import json
from datetime import date
from io import StringIO
from unittest.mock import AsyncMock, MagicMock

from pytest import MonkeyPatch
from tests.unit.application.fakes import FakeUnitOfWork

from income_expense_bot.application.handler.record_expense import RecordExpenseHandler
from income_expense_bot.application.handler.record_income import RecordIncomeHandler
from income_expense_bot.application.query.balance import (
    AbstractBalanceReadModel,
    CategorySum,
    LedgerBalanceQueryService,
)
from income_expense_bot.application.query.period import DatePeriod
from income_expense_bot.interfaces.telegram.app import complete_startup
from income_expense_bot.interfaces.telegram.dispatch import TelegramDispatcher
from income_expense_bot.logging_config import configure_logging, get_logger


class FakeReadModel(AbstractBalanceReadModel):
    async def fetch_totals(self, period: DatePeriod) -> list[CategorySum]:
        return []


def _json_configure() -> StringIO:
    buf = StringIO()
    configure_logging(stream=buf, cache_logger_on_first_use=False)
    return buf


def _last_event(buf: StringIO) -> dict[str, object]:
    lines = [line for line in buf.getvalue().splitlines() if line.strip()]
    return json.loads(lines[-1])


def test_json_log_line_has_timestamp_level_event(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("LOG_FORMAT", "json")
    buf = _json_configure()
    get_logger("test").info("bot.running", component="telegram")
    payload = _last_event(buf)
    assert "timestamp" in payload
    assert payload["level"] == "info"
    assert payload["event"] == "bot.running"


async def test_expense_command_logs_fields(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("LOG_FORMAT", "json")
    buf = _json_configure()
    uow = FakeUnitOfWork()
    dispatcher = TelegramDispatcher(
        allowed_user_ids=frozenset({42}),
        expense_handler=RecordExpenseHandler(uow),
        income_handler=RecordIncomeHandler(uow),
        balance_query=LedgerBalanceQueryService(FakeReadModel(), today_provider=lambda: date(2026, 11, 6)),
    )

    async def reply(_text: str) -> None:
        return None

    await dispatcher.handle_expense(42, "/expense 12,50 Mercadona", reply)
    payload = _last_event(buf)
    assert payload["event"] == "command.received"
    assert payload["command"] == "expense"
    assert "12,50 Mercadona" in str(payload["parameters"])


async def test_help_command_logged(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("LOG_FORMAT", "json")
    buf = _json_configure()
    uow = FakeUnitOfWork()
    dispatcher = TelegramDispatcher(
        allowed_user_ids=frozenset({42}),
        expense_handler=RecordExpenseHandler(uow),
        income_handler=RecordIncomeHandler(uow),
        balance_query=LedgerBalanceQueryService(FakeReadModel(), today_provider=lambda: date(2026, 11, 6)),
    )

    async def reply(_text: str) -> None:
        return None

    await dispatcher.handle_help(42, "/help", reply)
    payload = _last_event(buf)
    assert payload["event"] == "command.received"
    assert payload["command"] == "help"


async def test_startup_running_event_omits_token(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("LOG_FORMAT", "json")
    token = "secret-bot-token-do-not-leak"
    buf = _json_configure()
    application = MagicMock()
    application.bot = AsyncMock()
    await complete_startup(application)
    raw = buf.getvalue()
    assert token not in raw
    payload = _last_event(buf)
    assert payload["event"] == "bot.running"
    assert "timestamp" in payload
    assert payload["level"] == "info"
    application.bot.set_my_commands.assert_awaited()

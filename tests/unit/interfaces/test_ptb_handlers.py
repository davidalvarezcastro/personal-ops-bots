from datetime import date
from unittest.mock import MagicMock

from telegram.ext import CommandHandler
from tests.unit.application.fakes import FakeUnitOfWork

from income_expense_bot.application.handler.record_expense import RecordExpenseHandler
from income_expense_bot.application.handler.record_income import RecordIncomeHandler
from income_expense_bot.application.query.balance import (
    AbstractBalanceReadModel,
    CategorySum,
    LedgerBalanceQueryService,
)
from income_expense_bot.application.query.period import DatePeriod
from income_expense_bot.config import Config
from income_expense_bot.interfaces.telegram.app import build_ptb_application
from income_expense_bot.interfaces.telegram.dispatch import TelegramDispatcher


class FakeReadModel(AbstractBalanceReadModel):
    async def fetch_totals(self, period: DatePeriod) -> list[CategorySum]:
        return []


def test_ptb_registers_command_handlers() -> None:
    uow = FakeUnitOfWork()
    dispatcher = TelegramDispatcher(
        allowed_user_ids=frozenset({1}),
        expense_handler=RecordExpenseHandler(uow),
        income_handler=RecordIncomeHandler(uow),
        balance_query=LedgerBalanceQueryService(FakeReadModel(), today_provider=lambda: date(2026, 11, 6)),
    )
    config = Config(telegram_bot_token="token", telegram_allowed_user_ids=frozenset({1}), ledger_sqlite_path="x.sqlite")
    application = build_ptb_application(config, dispatcher)
    names = {
        next(iter(handler.commands))
        for handler in application.handlers[0]
        if isinstance(handler, CommandHandler)
    }
    assert names == {"expense", "income", "balance"}
    assert application.post_init is None


def test_ptb_creates_schema_on_startup_when_engine_provided() -> None:
    uow = FakeUnitOfWork()
    dispatcher = TelegramDispatcher(
        allowed_user_ids=frozenset({1}),
        expense_handler=RecordExpenseHandler(uow),
        income_handler=RecordIncomeHandler(uow),
        balance_query=LedgerBalanceQueryService(FakeReadModel(), today_provider=lambda: date(2026, 11, 6)),
    )
    config = Config(telegram_bot_token="token", telegram_allowed_user_ids=frozenset({1}), ledger_sqlite_path="x.sqlite")
    engine = MagicMock()
    application = build_ptb_application(config, dispatcher, engine=engine)
    assert application.post_init is not None
    assert application.post_shutdown is not None

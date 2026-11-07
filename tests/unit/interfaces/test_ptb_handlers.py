from datetime import date
from unittest.mock import AsyncMock, MagicMock

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
from income_expense_bot.interfaces.telegram.app import MENU_COMMANDS, build_ptb_application, complete_startup
from income_expense_bot.interfaces.telegram.dispatch import TelegramDispatcher


class FakeReadModel(AbstractBalanceReadModel):
    async def fetch_totals(self, period: DatePeriod) -> list[CategorySum]:
        return []


def _dispatcher() -> TelegramDispatcher:
    uow = FakeUnitOfWork()
    return TelegramDispatcher(
        allowed_user_ids=frozenset({1}),
        expense_handler=RecordExpenseHandler(uow),
        income_handler=RecordIncomeHandler(uow),
        balance_query=LedgerBalanceQueryService(FakeReadModel(), today_provider=lambda: date(2026, 11, 6)),
    )


def test_ptb_registers_command_handlers() -> None:
    config = Config(telegram_bot_token="token", telegram_allowed_user_ids=frozenset({1}), ledger_sqlite_path="x.sqlite")
    application = build_ptb_application(config, _dispatcher())
    names = {
        next(iter(handler.commands))
        for handler in application.handlers[0]
        if isinstance(handler, CommandHandler)
    }
    assert names == {"start", "help", "expense", "income", "balance"}
    assert application.post_init is not None


def test_ptb_creates_schema_on_startup_when_engine_provided() -> None:
    config = Config(telegram_bot_token="token", telegram_allowed_user_ids=frozenset({1}), ledger_sqlite_path="x.sqlite")
    engine = MagicMock()
    application = build_ptb_application(config, _dispatcher(), engine=engine)
    assert application.post_init is not None
    assert application.post_shutdown is not None


async def test_startup_registers_menu_commands() -> None:
    application = MagicMock()
    application.bot = AsyncMock()
    await complete_startup(application)
    recorded = application.bot.set_my_commands.await_args.args[0]
    names = [command.command for command in recorded]
    assert names == ["start", "help", "expense", "income", "balance"]
    assert {command.command for command in MENU_COMMANDS} == set(names)

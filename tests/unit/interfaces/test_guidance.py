from datetime import date

from tests.unit.application.fakes import FakeUnitOfWork

from income_expense_bot.application.handler.record_expense import RecordExpenseHandler
from income_expense_bot.application.handler.record_income import RecordIncomeHandler
from income_expense_bot.application.query.balance import (
    AbstractBalanceReadModel,
    CategorySum,
    LedgerBalanceQueryService,
)
from income_expense_bot.application.query.period import DatePeriod
from income_expense_bot.interfaces.telegram.dispatch import TelegramDispatcher
from income_expense_bot.interfaces.telegram.guidance import HELP_REPLY, START_REPLY


class FakeReadModel(AbstractBalanceReadModel):
    async def fetch_totals(self, period: DatePeriod) -> list[CategorySum]:
        return []


def _dispatcher() -> TelegramDispatcher:
    uow = FakeUnitOfWork()
    return TelegramDispatcher(
        allowed_user_ids=frozenset({42}),
        expense_handler=RecordExpenseHandler(uow),
        income_handler=RecordIncomeHandler(uow),
        balance_query=LedgerBalanceQueryService(FakeReadModel(), today_provider=lambda: date(2026, 11, 6)),
    )


def test_start_and_help_copy_lists_commands() -> None:
    assert "ready" in START_REPLY.lower()
    assert "/help" in START_REPLY
    for name in ("/start", "/help", "/expense", "/income", "/balance"):
        assert name in HELP_REPLY
    assert "<amount>" in HELP_REPLY
    assert "<merchant" in HELP_REPLY or "<merchant...>" in HELP_REPLY


async def test_authorized_start_and_help() -> None:
    dispatcher = _dispatcher()
    replies: list[str] = []

    async def reply(text: str) -> None:
        replies.append(text)

    await dispatcher.handle_start(42, "/start", reply)
    assert replies == [START_REPLY]
    assert "ready" in replies[0].lower()
    assert "/help" in replies[0]

    replies.clear()
    await dispatcher.handle_help(42, "/help", reply)
    assert replies == [HELP_REPLY]
    for name in ("/start", "/help", "/expense", "/income", "/balance"):
        assert name in replies[0]


async def test_unauthorized_start_and_help_send_nothing() -> None:
    dispatcher = _dispatcher()
    replies: list[str] = []

    async def reply(text: str) -> None:
        replies.append(text)

    await dispatcher.handle_start(99, "/start", reply)
    await dispatcher.handle_help(99, "/help", reply)
    assert replies == []

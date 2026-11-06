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


class FakeReadModel(AbstractBalanceReadModel):
    async def fetch_totals(self, period: DatePeriod) -> list[CategorySum]:
        return [CategorySum("expense", "Uncategorized", 100)]


async def _dispatcher(uow: FakeUnitOfWork | None = None) -> tuple[TelegramDispatcher, FakeUnitOfWork]:
    uow = uow or FakeUnitOfWork()
    dispatcher = TelegramDispatcher(
        allowed_user_ids=frozenset({42}),
        expense_handler=RecordExpenseHandler(uow),
        income_handler=RecordIncomeHandler(uow),
        balance_query=LedgerBalanceQueryService(FakeReadModel(), today_provider=lambda: date(2026, 11, 6)),
    )
    return dispatcher, uow


async def test_unauthorized_expense_does_not_record() -> None:
    dispatcher, uow = await _dispatcher()
    replies: list[str] = []

    async def reply(text: str) -> None:
        replies.append(text)

    await dispatcher.handle_expense(99, "/expense 10 Shop", reply)
    assert uow.entries.items == []
    assert replies == []


async def test_unauthorized_balance_reveals_nothing() -> None:
    dispatcher, _uow = await _dispatcher()
    replies: list[str] = []

    async def reply(text: str) -> None:
        replies.append(text)

    await dispatcher.handle_balance(99, "/balance", reply)
    assert replies == []


async def test_authorized_expense_and_balance_reply() -> None:
    dispatcher, uow = await _dispatcher()
    replies: list[str] = []

    async def reply(text: str) -> None:
        replies.append(text)

    await dispatcher.handle_expense(42, "/expense 10 Shop", reply)
    assert len(uow.entries.items) == 1
    assert "10,00" in replies[0]
    replies.clear()
    await dispatcher.handle_balance(42, "/balance", reply)
    assert "Net:" in replies[0]
    assert "2026-11-01" in replies[0]


async def test_expense_missing_merchant_notifies_and_does_not_record() -> None:
    dispatcher, uow = await _dispatcher()
    replies: list[str] = []

    async def reply(text: str) -> None:
        replies.append(text)

    await dispatcher.handle_expense(42, "/expense 12,50", reply)
    assert uow.entries.items == []
    assert replies == ["merchant is required"]


async def test_balance_invalid_format_notifies_without_totals() -> None:
    dispatcher, _uow = await _dispatcher()
    replies: list[str] = []

    async def reply(text: str) -> None:
        replies.append(text)

    await dispatcher.handle_balance(42, "/balance 06/11/2026", reply)
    assert replies == ["date is invalid"]
    assert "Net:" not in replies[0]


async def test_balance_invalid_range_notifies_without_totals() -> None:
    dispatcher, _uow = await _dispatcher()
    replies: list[str] = []

    async def reply(text: str) -> None:
        replies.append(text)

    await dispatcher.handle_balance(42, "/balance 2026-11-15 2026-11-01", reply)
    assert replies == ["date range is invalid"]
    assert "Net:" not in replies[0]

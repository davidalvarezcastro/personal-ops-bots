from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio.session import AsyncSession

from income_expense_bot.application.commands import RecordExpenseCommand, RecordIncomeCommand
from income_expense_bot.application.handler.record_expense import RecordExpenseHandler
from income_expense_bot.application.handler.record_income import RecordIncomeHandler
from income_expense_bot.domain.model.entry_type import EntryType, PaymentMethod
from income_expense_bot.domain.model.ledger_entry import LedgerEntry
from income_expense_bot.infrastructure.unity_of_work import SqlAlchemyUnitOfWork


async def test_round_trip_expense_and_income(
    uow: SqlAlchemyUnitOfWork,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    before = datetime.now(UTC) - timedelta(seconds=2)
    await RecordExpenseHandler(uow).handle(
        RecordExpenseCommand(amount_cents=1250, payee="Mercadona", category="Uncategorized")
    )
    await RecordIncomeHandler(uow).handle(
        RecordIncomeCommand(amount_cents=180000, payee="Company", category="Salary")
    )
    after = datetime.now(UTC) + timedelta(seconds=2)

    async with session_factory() as session:
        rows = list((await session.execute(select(LedgerEntry))).scalars())
    by_type = {row.type: row for row in rows}
    assert by_type[EntryType.EXPENSE].amount_cents == 1250
    assert by_type[EntryType.EXPENSE].payee == "Mercadona"
    assert by_type[EntryType.EXPENSE].category == "Uncategorized"
    assert by_type[EntryType.EXPENSE].payment_method is PaymentMethod.CARD
    assert before <= by_type[EntryType.EXPENSE].occurred_at <= after
    assert by_type[EntryType.INCOME].amount_cents == 180000
    assert by_type[EntryType.INCOME].payee == "Company"
    assert by_type[EntryType.INCOME].category == "Salary"

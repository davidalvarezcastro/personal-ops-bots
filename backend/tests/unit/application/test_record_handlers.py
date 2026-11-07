from tests.unit.application.fakes import FakeUnitOfWork

from income_expense_bot.application.commands import RecordExpenseCommand, RecordIncomeCommand
from income_expense_bot.application.handler.record_expense import RecordExpenseHandler
from income_expense_bot.application.handler.record_income import RecordIncomeHandler
from income_expense_bot.domain.model.entry_type import EntryType


async def test_record_expense_persists_without_totals() -> None:
    uow = FakeUnitOfWork()
    handler = RecordExpenseHandler(uow)
    result = await handler.handle(
        RecordExpenseCommand(amount_cents=1250, payee="Mercadona", category="Uncategorized")
    )
    assert result is None
    assert uow.committed
    assert len(uow.entries.items) == 1
    entry = uow.entries.items[0]
    assert entry.type is EntryType.EXPENSE
    assert entry.amount_cents == 1250
    assert entry.payee == "Mercadona"


async def test_record_income_persists() -> None:
    uow = FakeUnitOfWork()
    handler = RecordIncomeHandler(uow)
    await handler.handle(RecordIncomeCommand(amount_cents=180000, payee="Company", category="Salary"))
    assert uow.entries.items[0].type is EntryType.INCOME
    assert uow.entries.items[0].amount_cents == 180000

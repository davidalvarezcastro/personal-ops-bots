import pytest
from tests.unit.application.fakes import FakeUnitOfWork

from income_expense_bot.application.commands import (
    ChangeEntryCategoryCommand,
    DeleteLedgerEntryCommand,
    RecordExpenseCommand,
)
from income_expense_bot.application.handler.change_entry_category import ChangeEntryCategoryHandler
from income_expense_bot.application.handler.delete_ledger_entry import DeleteLedgerEntryHandler
from income_expense_bot.application.handler.record_expense import RecordExpenseHandler
from income_expense_bot.domain.exception.ledger import EntryNotFoundError, InvalidCategoryError


async def test_change_category_on_expense() -> None:
    uow = FakeUnitOfWork()
    await RecordExpenseHandler(uow).handle(
        RecordExpenseCommand(amount_cents=1250, payee="Mercadona", category="Uncategorized")
    )
    entry_id = uow.entries.items[0].id
    await ChangeEntryCategoryHandler(uow).handle(
        ChangeEntryCategoryCommand(entry_id=entry_id, category="Groceries")
    )
    assert uow.entries.items[0].category == "Groceries"
    assert uow.entries.items[0].amount_cents == 1250


async def test_change_category_rejects_salary_on_expense() -> None:
    uow = FakeUnitOfWork()
    await RecordExpenseHandler(uow).handle(
        RecordExpenseCommand(amount_cents=1250, payee="Store", category="Uncategorized")
    )
    with pytest.raises(InvalidCategoryError):
        await ChangeEntryCategoryHandler(uow).handle(
            ChangeEntryCategoryCommand(entry_id=uow.entries.items[0].id, category="Salary")
        )


async def test_change_category_missing_id() -> None:
    uow = FakeUnitOfWork()
    with pytest.raises(EntryNotFoundError):
        await ChangeEntryCategoryHandler(uow).handle(
            ChangeEntryCategoryCommand(entry_id="missing", category="Groceries")
        )


async def test_delete_removes_entry() -> None:
    uow = FakeUnitOfWork()
    await RecordExpenseHandler(uow).handle(
        RecordExpenseCommand(amount_cents=2000, payee="Shop", category="Groceries")
    )
    entry_id = uow.entries.items[0].id
    await DeleteLedgerEntryHandler(uow).handle(DeleteLedgerEntryCommand(entry_id=entry_id))
    assert uow.entries.items == []


async def test_delete_missing_id() -> None:
    uow = FakeUnitOfWork()
    with pytest.raises(EntryNotFoundError):
        await DeleteLedgerEntryHandler(uow).handle(DeleteLedgerEntryCommand(entry_id="missing"))

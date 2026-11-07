from datetime import UTC, datetime

import pytest

from income_expense_bot.domain.exception.ledger import InvalidCategoryError
from income_expense_bot.domain.model.entry_type import EntryType, PaymentMethod
from income_expense_bot.domain.model.ledger_entry import LedgerEntry
from income_expense_bot.domain.model.money import Money


def test_record_expense_never_transfer() -> None:
    before = datetime.now(UTC)
    entry = LedgerEntry.record_expense(money=Money(cents=1000), payee="Shop", category="Uncategorized")
    after = datetime.now(UTC)
    assert entry.type is EntryType.EXPENSE
    assert entry.type is not EntryType.TRANSFER
    assert entry.payment_method is PaymentMethod.CARD
    assert before <= entry.occurred_at <= after


def test_record_income_never_transfer() -> None:
    entry = LedgerEntry.record_income(money=Money(cents=180000), payee="Company", category="Salary")
    assert entry.type is EntryType.INCOME
    assert entry.type is not EntryType.TRANSFER


def test_change_category_on_expense() -> None:
    entry = LedgerEntry.record_expense(money=Money(cents=1250), payee="Mercadona", category="Uncategorized")
    entry.change_category("Groceries")
    assert entry.category == "Groceries"
    assert entry.amount_cents == 1250
    assert entry.payee == "Mercadona"


def test_change_category_rejects_income_name_on_expense() -> None:
    entry = LedgerEntry.record_expense(money=Money(cents=1250), payee="Store", category="Uncategorized")
    with pytest.raises(InvalidCategoryError):
        entry.change_category("Salary")
    assert entry.category == "Uncategorized"
    assert entry.amount_cents == 1250

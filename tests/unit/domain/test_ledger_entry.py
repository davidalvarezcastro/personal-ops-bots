from datetime import UTC, datetime

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

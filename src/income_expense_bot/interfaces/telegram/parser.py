from __future__ import annotations

from datetime import date

from income_expense_bot.application.commands import RecordExpenseCommand, RecordIncomeCommand
from income_expense_bot.application.query.period import parse_iso_date
from income_expense_bot.domain.exception.ledger import InvalidAmountError, MissingPayeeError
from income_expense_bot.domain.model.category import split_category_and_payee
from income_expense_bot.domain.model.entry_type import EntryType
from income_expense_bot.domain.model.money import Money


def _body_tokens(text: str) -> list[str]:
    parts = text.strip().split()
    if parts and parts[0].startswith("/"):
        parts = parts[1:]
        if parts and parts[0].startswith("@"):
            parts = parts[1:]
    return parts


def parse_expense(text: str) -> RecordExpenseCommand:
    tokens = _body_tokens(text)
    if not tokens:
        raise InvalidAmountError("amount is required")
    money = Money.parse(tokens[0])
    category, payee = split_category_and_payee(EntryType.EXPENSE, " ".join(tokens[1:]))
    if not payee:
        raise MissingPayeeError("merchant is required")
    return RecordExpenseCommand(amount_cents=money.cents, payee=payee, category=category)


def parse_income(text: str) -> RecordIncomeCommand:
    tokens = _body_tokens(text)
    if not tokens:
        raise InvalidAmountError("amount is required")
    money = Money.parse(tokens[0])
    category, payee = split_category_and_payee(EntryType.INCOME, " ".join(tokens[1:]))
    if not payee:
        raise MissingPayeeError("source is required")
    return RecordIncomeCommand(amount_cents=money.cents, payee=payee, category=category)


def parse_balance_args(text: str) -> tuple[date | None, date | None]:
    tokens = _body_tokens(text)
    if not tokens:
        return None, None
    if len(tokens) == 1:
        return parse_iso_date(tokens[0]), None
    if len(tokens) == 2:
        return parse_iso_date(tokens[0]), parse_iso_date(tokens[1])
    raise InvalidAmountError("too many arguments")

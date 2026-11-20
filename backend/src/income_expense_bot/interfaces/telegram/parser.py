from __future__ import annotations

from datetime import date

from income_expense_bot.application.commands import RecordExpenseCommand, RecordIncomeCommand
from income_expense_bot.application.query.period import parse_iso_date
from income_expense_bot.domain.exception.ledger import InvalidAmountError, MissingPayeeError
from income_expense_bot.domain.model.category import split_category_and_payee
from income_expense_bot.domain.model.currency import DEFAULT_CURRENCY, resolve_currency_token, split_amount_token
from income_expense_bot.domain.model.entry_type import EntryType
from income_expense_bot.domain.model.money import Money


def _body_tokens(text: str) -> list[str]:
    parts = text.strip().split()
    if parts and parts[0].startswith("/"):
        parts = parts[1:]
        if parts and parts[0].startswith("@"):
            parts = parts[1:]
    return parts


def _parse_record(text: str, entry_type: EntryType) -> tuple[Money, str, str]:
    tokens = _body_tokens(text)
    if not tokens:
        raise InvalidAmountError("amount is required")
    amount_text, attached = split_amount_token(tokens[0])
    rest = tokens[1:]
    if attached:
        currency = attached
    elif rest:
        resolved = resolve_currency_token(rest[0])
        if resolved is not None:
            currency = resolved
            rest = rest[1:]
        else:
            currency = DEFAULT_CURRENCY
    else:
        currency = DEFAULT_CURRENCY
    money = Money.parse(amount_text, currency=currency)
    category, payee = split_category_and_payee(entry_type, " ".join(rest))
    return money, category, payee


def parse_expense(text: str) -> RecordExpenseCommand:
    money, category, payee = _parse_record(text, EntryType.EXPENSE)
    if not payee:
        raise MissingPayeeError("merchant is required")
    return RecordExpenseCommand(
        amount_cents=money.cents,
        payee=payee,
        category=category,
        currency=money.currency,
    )


def parse_income(text: str) -> RecordIncomeCommand:
    money, category, payee = _parse_record(text, EntryType.INCOME)
    if not payee:
        raise MissingPayeeError("source is required")
    return RecordIncomeCommand(
        amount_cents=money.cents,
        payee=payee,
        category=category,
        currency=money.currency,
    )


def parse_balance_args(text: str) -> tuple[date | None, date | None]:
    tokens = _body_tokens(text)
    if not tokens:
        return None, None
    if len(tokens) == 1:
        return parse_iso_date(tokens[0]), None
    if len(tokens) == 2:
        return parse_iso_date(tokens[0]), parse_iso_date(tokens[1])
    raise InvalidAmountError("too many arguments")

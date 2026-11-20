import pytest

from income_expense_bot.domain.exception.ledger import (
    InvalidAmountError,
    InvalidCurrencyError,
    InvalidDateFormatError,
    MissingPayeeError,
)
from income_expense_bot.interfaces.telegram.parser import parse_balance_args, parse_expense, parse_income


def test_expense_merchant_only() -> None:
    command = parse_expense("/expense 12,50 Mercadona")
    assert command.amount_cents == 1250
    assert command.currency == "EUR"
    assert command.payee == "Mercadona"
    assert command.category == "Uncategorized"


def test_expense_category_and_multi_word_merchant() -> None:
    command = parse_expense("/expense 89,90 Shopping El Corte Ingles")
    assert command.amount_cents == 8990
    assert command.category == "Shopping"
    assert command.payee == "El Corte Ingles"


def test_expense_food_and_drinks_category() -> None:
    command = parse_expense("/expense 15 Food & Drinks Cafe Central")
    assert command.amount_cents == 1500
    assert command.category == "Food & Drinks"
    assert command.payee == "Cafe Central"


def test_expense_missing_merchant() -> None:
    with pytest.raises(MissingPayeeError):
        parse_expense("/expense 12,50")


def test_income_examples() -> None:
    only_source = parse_income("/income 1800 Nomina")
    assert only_source.amount_cents == 180000
    assert only_source.payee == "Nomina"
    with_cat = parse_income("/income 1800 Salary Company")
    assert with_cat.category == "Salary"
    assert with_cat.payee == "Company"


def test_balance_none_one_two_dates() -> None:
    assert parse_balance_args("/balance") == (None, None)
    start, end = parse_balance_args("/balance 2026-11-06")
    assert start is not None and start.isoformat() == "2026-11-06"
    assert end is None
    start, end = parse_balance_args("/balance 2026-11-01 2026-11-15")
    assert start is not None and end is not None
    assert start.isoformat() == "2026-11-01"
    assert end.isoformat() == "2026-11-15"


def test_balance_invalid_format() -> None:
    with pytest.raises(InvalidDateFormatError):
        parse_balance_args("/balance 06/11/2026")


def test_invalid_amount_rejected() -> None:
    with pytest.raises(InvalidAmountError):
        parse_expense("/expense 12,345 Shop")


def test_expense_euro_symbol_spaced_and_attached() -> None:
    spaced = parse_expense("/expense 65 € Mercadona")
    assert spaced.amount_cents == 6500
    assert spaced.currency == "EUR"
    attached = parse_expense("/expense 65€ Mercadona")
    assert attached.amount_cents == 6500
    assert attached.currency == "EUR"


def test_expense_usd_iso() -> None:
    command = parse_expense("/expense 12,50 USD Starbucks")
    assert command.amount_cents == 1250
    assert command.currency == "USD"
    assert command.payee == "Starbucks"


def test_expense_yen_symbol() -> None:
    command = parse_expense("/expense 65 JP¥ Konbini")
    assert command.amount_cents == 65
    assert command.currency == "JPY"
    assert command.payee == "Konbini"


def test_expense_yuan_yen_sign_and_rmb() -> None:
    spaced = parse_expense("/expense 65 ¥ Shop")
    assert spaced.amount_cents == 6500
    assert spaced.currency == "CNY"
    attached = parse_expense("/expense 65¥ Shop")
    assert attached.amount_cents == 6500
    assert attached.currency == "CNY"
    rmb = parse_expense("/expense 12,50 RMB Shop")
    assert rmb.amount_cents == 1250
    assert rmb.currency == "CNY"
    assert rmb.payee == "Shop"


def test_unknown_iso_rejected() -> None:
    with pytest.raises(InvalidCurrencyError):
        parse_expense("/expense 10 INR Shop")

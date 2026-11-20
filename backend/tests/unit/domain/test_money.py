import pytest

from income_expense_bot.domain.exception.ledger import InvalidAmountError
from income_expense_bot.domain.model.money import Money


def test_one_fractional_digit_comma() -> None:
    money = Money.parse("25,2")
    assert money.cents == 2520
    assert money.currency == "EUR"


def test_two_fractional_digits_comma() -> None:
    assert Money.parse("0,99").cents == 99


def test_dot_separator() -> None:
    assert Money.parse("25.20").cents == 2520


def test_too_many_fractional_digits() -> None:
    with pytest.raises(InvalidAmountError):
        Money.parse("12,345")


def test_jpy_whole_yen() -> None:
    money = Money.parse("65", currency="JPY")
    assert money.cents == 65
    assert money.currency == "JPY"


def test_jpy_fraction_rejected() -> None:
    with pytest.raises(InvalidAmountError):
        Money.parse("65,50", currency="JPY")

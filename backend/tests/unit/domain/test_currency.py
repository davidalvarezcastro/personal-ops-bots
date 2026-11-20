import pytest

from income_expense_bot.domain.exception.ledger import InvalidCurrencyError
from income_expense_bot.domain.model.currency import currency_or_default, resolve_currency_token


def test_resolve_iso_and_symbols() -> None:
    assert resolve_currency_token("EUR") == "EUR"
    assert resolve_currency_token("eur") == "EUR"
    assert resolve_currency_token("€") == "EUR"
    assert resolve_currency_token("$") == "USD"
    assert resolve_currency_token("£") == "GBP"
    assert resolve_currency_token("JPY") == "JPY"
    assert resolve_currency_token("JP¥") == "JPY"
    assert resolve_currency_token("¥") == "CNY"
    assert resolve_currency_token("rmb") == "CNY"
    assert resolve_currency_token("RMB") == "CNY"
    assert resolve_currency_token("CNY") == "CNY"
    assert resolve_currency_token("CN¥") == "CNY"
    assert resolve_currency_token("USD") == "USD"


def test_reject_unknown_iso() -> None:
    with pytest.raises(InvalidCurrencyError):
        resolve_currency_token("INR")


def test_non_currency_token_is_none() -> None:
    assert resolve_currency_token("Mercadona") is None
    assert resolve_currency_token("Shop") is None


def test_blank_currency_defaults_to_eur() -> None:
    assert currency_or_default(None) == "EUR"
    assert currency_or_default("  ") == "EUR"

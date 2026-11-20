from __future__ import annotations

from dataclasses import dataclass

from income_expense_bot.domain.exception.ledger import InvalidCurrencyError


@dataclass(frozen=True)
class CurrencySpec:
    code: str
    exponent: int
    symbols: tuple[str, ...]


SPECS: tuple[CurrencySpec, ...] = (
    CurrencySpec("EUR", 2, ("€",)),
    CurrencySpec("USD", 2, ("$",)),
    CurrencySpec("GBP", 2, ("£",)),
    CurrencySpec("JPY", 0, ("¥",)),
    CurrencySpec("CNY", 2, ("CN¥",)),
)

BY_CODE: dict[str, CurrencySpec] = {spec.code: spec for spec in SPECS}
_SYMBOLS: tuple[tuple[str, CurrencySpec], ...] = tuple(
    sorted(
        ((symbol, spec) for spec in SPECS for symbol in spec.symbols),
        key=lambda item: len(item[0]),
        reverse=True,
    )
)

DEFAULT_CURRENCY = "EUR"


def spec_for(code: str) -> CurrencySpec:
    try:
        return BY_CODE[code]
    except KeyError as exc:
        raise InvalidCurrencyError(f"currency is not supported: {code}") from exc


def resolve_currency_token(token: str) -> str | None:
    stripped = token.strip()
    if not stripped:
        return None
    for symbol, spec in _SYMBOLS:
        if stripped == symbol:
            return spec.code
    upper = stripped.upper()
    if upper in BY_CODE:
        return upper
    if len(stripped) == 3 and stripped.isalpha():
        raise InvalidCurrencyError(f"currency is not supported: {token}")
    return None


def currency_or_default(token: str | None) -> str:
    if token is None or not token.strip():
        return DEFAULT_CURRENCY
    resolved = resolve_currency_token(token.strip())
    if resolved is None:
        raise InvalidCurrencyError(f"currency is not supported: {token}")
    return resolved


def split_amount_token(token: str) -> tuple[str, str | None]:
    for symbol, spec in _SYMBOLS:
        if token.endswith(symbol) and token != symbol:
            return token[: -len(symbol)], spec.code
    if len(token) > 3 and token[-3:].isalpha() and token[:-3] and token[0].isdigit():
        currency = resolve_currency_token(token[-3:])
        return token[:-3], currency
    return token, None

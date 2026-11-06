from datetime import date

import pytest

from income_expense_bot.application.query.period import parse_iso_date, resolve_period
from income_expense_bot.domain.exception.ledger import InvalidDateFormatError, InvalidDateRangeError


def test_current_month() -> None:
    period = resolve_period(None, None, today=date(2026, 11, 6))
    assert period.start == date(2026, 11, 1)
    assert period.end == date(2026, 11, 30)


def test_one_day() -> None:
    period = resolve_period(date(2026, 11, 6), None, today=date(2026, 11, 6))
    assert period.start == date(2026, 11, 6)
    assert period.end == date(2026, 11, 6)


def test_inclusive_range() -> None:
    period = resolve_period(date(2026, 11, 1), date(2026, 11, 15), today=date(2026, 11, 6))
    assert period.start == date(2026, 11, 1)
    assert period.end == date(2026, 11, 15)


def test_invalid_order() -> None:
    with pytest.raises(InvalidDateRangeError):
        resolve_period(date(2026, 11, 15), date(2026, 11, 1), today=date(2026, 11, 6))


def test_invalid_format() -> None:
    with pytest.raises(InvalidDateFormatError):
        parse_iso_date("06/11/2026")

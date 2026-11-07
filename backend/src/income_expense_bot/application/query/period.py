from __future__ import annotations

from calendar import monthrange
from dataclasses import dataclass
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from income_expense_bot.domain.exception.ledger import InvalidDateFormatError, InvalidDateRangeError

MADRID = ZoneInfo("Europe/Madrid")


@dataclass(frozen=True)
class DatePeriod:
    start: date
    end: date

    def start_utc(self) -> datetime:
        return datetime.combine(self.start, time.min, tzinfo=MADRID).astimezone(ZoneInfo("UTC"))

    def end_exclusive_utc(self) -> datetime:
        next_day = date.fromordinal(self.end.toordinal() + 1)
        return datetime.combine(next_day, time.min, tzinfo=MADRID).astimezone(ZoneInfo("UTC"))


def parse_iso_date(text: str) -> date:
    try:
        datetime.strptime(text, "%Y-%m-%d")
        year, month, day = (int(part) for part in text.split("-"))
        return date(year, month, day)
    except ValueError as exc:
        raise InvalidDateFormatError(text) from exc


def resolve_period(
    start: date | None,
    end: date | None,
    *,
    today: date,
) -> DatePeriod:
    if start is None and end is None:
        first = today.replace(day=1)
        last = date(today.year, today.month, monthrange(today.year, today.month)[1])
        return DatePeriod(start=first, end=last)
    if start is not None and end is None:
        return DatePeriod(start=start, end=start)
    if start is not None and end is not None:
        if end < start:
            raise InvalidDateRangeError("end date is before start date")
        return DatePeriod(start=start, end=end)
    raise InvalidDateFormatError("end date without start date")

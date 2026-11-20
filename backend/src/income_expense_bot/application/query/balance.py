from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date

from income_expense_bot.application.query.period import DatePeriod, resolve_period
from income_expense_bot.domain.model.currency import DEFAULT_CURRENCY
from income_expense_bot.domain.model.entry_type import EntryType


@dataclass(frozen=True)
class CategoryTotal:
    category: str
    amount_cents: int


@dataclass(frozen=True)
class CurrencyBalance:
    currency: str
    income_cents: int
    expense_cents: int
    net_cents: int
    expense_by_category: tuple[CategoryTotal, ...]
    income_by_category: tuple[CategoryTotal, ...]


@dataclass(frozen=True)
class BalanceResult:
    period: DatePeriod
    currencies: tuple[CurrencyBalance, ...]


@dataclass(frozen=True)
class CategorySum:
    entry_type: str
    category: str
    amount_cents: int
    currency: str = DEFAULT_CURRENCY


class AbstractBalanceReadModel(ABC):
    @abstractmethod
    async def fetch_totals(self, period: DatePeriod) -> list[CategorySum]: ...


def _empty_eur() -> CurrencyBalance:
    return CurrencyBalance(
        currency=DEFAULT_CURRENCY,
        income_cents=0,
        expense_cents=0,
        net_cents=0,
        expense_by_category=(),
        income_by_category=(),
    )


class LedgerBalanceQueryService:
    def __init__(
        self,
        read_model: AbstractBalanceReadModel,
        today_provider: Callable[[], date],
    ) -> None:
        self._read_model = read_model
        self._today_provider = today_provider

    async def get(self, start: date | None = None, end: date | None = None) -> BalanceResult:
        period = resolve_period(start, end, today=self._today_provider())
        rows = await self._read_model.fetch_totals(period)
        income: dict[str, int] = defaultdict(int)
        expense: dict[str, int] = defaultdict(int)
        income_cats: dict[str, list[CategoryTotal]] = defaultdict(list)
        expense_cats: dict[str, list[CategoryTotal]] = defaultdict(list)
        seen: set[str] = set()
        for row in rows:
            if row.entry_type == EntryType.TRANSFER:
                continue
            currency = row.currency
            seen.add(currency)
            if row.entry_type == EntryType.INCOME:
                income[currency] += row.amount_cents
                income_cats[currency].append(CategoryTotal(row.category, row.amount_cents))
            elif row.entry_type == EntryType.EXPENSE:
                expense[currency] += row.amount_cents
                expense_cats[currency].append(CategoryTotal(row.category, row.amount_cents))
        if not seen:
            return BalanceResult(period=period, currencies=(_empty_eur(),))
        groups = []
        for currency in sorted(seen):
            inc = income[currency]
            exp = expense[currency]
            groups.append(
                CurrencyBalance(
                    currency=currency,
                    income_cents=inc,
                    expense_cents=exp,
                    net_cents=inc - exp,
                    expense_by_category=tuple(expense_cats[currency]),
                    income_by_category=tuple(income_cats[currency]),
                )
            )
        return BalanceResult(period=period, currencies=tuple(groups))

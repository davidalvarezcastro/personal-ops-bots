from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date

from income_expense_bot.application.query.period import DatePeriod, resolve_period
from income_expense_bot.domain.model.entry_type import EntryType


@dataclass(frozen=True)
class CategoryTotal:
    category: str
    amount_cents: int


@dataclass(frozen=True)
class BalanceResult:
    period: DatePeriod
    income_cents: int
    expense_cents: int
    net_cents: int
    expense_by_category: tuple[CategoryTotal, ...]
    income_by_category: tuple[CategoryTotal, ...]


@dataclass(frozen=True)
class CategorySum:
    entry_type: str
    category: str
    amount_cents: int


class AbstractBalanceReadModel(ABC):
    @abstractmethod
    async def fetch_totals(self, period: DatePeriod) -> list[CategorySum]: ...


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
        income = 0
        expense = 0
        income_cats: list[CategoryTotal] = []
        expense_cats: list[CategoryTotal] = []
        for row in rows:
            if row.entry_type == EntryType.TRANSFER:
                continue
            if row.entry_type == EntryType.INCOME:
                income += row.amount_cents
                income_cats.append(CategoryTotal(row.category, row.amount_cents))
            elif row.entry_type == EntryType.EXPENSE:
                expense += row.amount_cents
                expense_cats.append(CategoryTotal(row.category, row.amount_cents))
        return BalanceResult(
            period=period,
            income_cents=income,
            expense_cents=expense,
            net_cents=income - expense,
            expense_by_category=tuple(expense_cats),
            income_by_category=tuple(income_cats),
        )

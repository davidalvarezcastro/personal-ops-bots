from datetime import date

from income_expense_bot.application.query.balance import (
    AbstractBalanceReadModel,
    CategorySum,
    LedgerBalanceQueryService,
)
from income_expense_bot.application.query.period import DatePeriod


class FakeReadModel(AbstractBalanceReadModel):
    def __init__(self, rows: list[CategorySum]) -> None:
        self.rows = rows

    async def fetch_totals(self, period: DatePeriod) -> list[CategorySum]:
        return list(self.rows)


async def test_mixed_month_totals() -> None:
    service = LedgerBalanceQueryService(
        FakeReadModel(
            [
                CategorySum("income", "Salary", 180000),
                CategorySum("expense", "Groceries", 2000),
                CategorySum("expense", "Uncategorized", 500),
                CategorySum("transfer", "Ignored", 999),
            ]
        ),
        today_provider=lambda: date(2026, 11, 6),
    )
    result = await service.get()
    assert result.income_cents == 180000
    assert result.expense_cents == 2500
    assert result.net_cents == 177500
    assert ("Groceries", 2000) in {(c.category, c.amount_cents) for c in result.expense_by_category}
    assert ("Uncategorized", 500) in {(c.category, c.amount_cents) for c in result.expense_by_category}
    assert ("Salary", 180000) in {(c.category, c.amount_cents) for c in result.income_by_category}


async def test_empty_period() -> None:
    service = LedgerBalanceQueryService(FakeReadModel([]), today_provider=lambda: date(2026, 11, 6))
    result = await service.get()
    assert result.income_cents == 0
    assert result.expense_cents == 0
    assert result.net_cents == 0
    assert result.expense_by_category == ()
    assert result.income_by_category == ()

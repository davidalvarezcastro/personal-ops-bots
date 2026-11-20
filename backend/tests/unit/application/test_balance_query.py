from datetime import date

from income_expense_bot.application.query.balance import (
    AbstractBalanceReadModel,
    BalanceResult,
    CategorySum,
    CurrencyBalance,
    LedgerBalanceQueryService,
)
from income_expense_bot.application.query.period import DatePeriod


class FakeReadModel(AbstractBalanceReadModel):
    def __init__(self, rows: list[CategorySum]) -> None:
        self.rows = rows

    async def fetch_totals(self, period: DatePeriod) -> list[CategorySum]:
        return list(self.rows)


def _eur(result: BalanceResult) -> CurrencyBalance:
    return next(group for group in result.currencies if group.currency == "EUR")


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
    eur = _eur(result)
    assert eur.income_cents == 180000
    assert eur.expense_cents == 2500
    assert eur.net_cents == 177500
    assert ("Groceries", 2000) in {(c.category, c.amount_cents) for c in eur.expense_by_category}
    assert ("Uncategorized", 500) in {(c.category, c.amount_cents) for c in eur.expense_by_category}
    assert ("Salary", 180000) in {(c.category, c.amount_cents) for c in eur.income_by_category}


async def test_empty_period() -> None:
    service = LedgerBalanceQueryService(FakeReadModel([]), today_provider=lambda: date(2026, 11, 6))
    result = await service.get()
    assert len(result.currencies) == 1
    eur = result.currencies[0]
    assert eur.currency == "EUR"
    assert eur.income_cents == 0
    assert eur.expense_cents == 0
    assert eur.net_cents == 0
    assert eur.expense_by_category == ()
    assert eur.income_by_category == ()


async def test_two_currencies_are_not_mixed() -> None:
    service = LedgerBalanceQueryService(
        FakeReadModel(
            [
                CategorySum("expense", "Groceries", 1000, currency="EUR"),
                CategorySum("expense", "Food & Drinks", 500, currency="USD"),
            ]
        ),
        today_provider=lambda: date(2026, 11, 6),
    )
    result = await service.get()
    by_code = {group.currency: group for group in result.currencies}
    assert by_code["EUR"].expense_cents == 1000
    assert by_code["USD"].expense_cents == 500
    assert by_code["EUR"].expense_cents != by_code["USD"].expense_cents

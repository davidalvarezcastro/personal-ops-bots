from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio.session import AsyncSession

from income_expense_bot.application.query.balance import LedgerBalanceQueryService
from income_expense_bot.domain.model.entry_type import EntryType, PaymentMethod
from income_expense_bot.domain.model.ledger_entry import LedgerEntry
from income_expense_bot.domain.model.money import Money
from income_expense_bot.infrastructure.read_model.balance_read_model import SqlBalanceReadModel
from income_expense_bot.infrastructure.unity_of_work import SqlAlchemyUnitOfWork


def _at(day: int) -> datetime:
    madrid = ZoneInfo("Europe/Madrid")
    return datetime(2026, 11, day, 12, 0, tzinfo=madrid).astimezone(UTC)


async def test_query_service_filters_by_range(
    uow: SqlAlchemyUnitOfWork,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with uow as unit:
        await unit.entries.add(
            LedgerEntry.record_expense(
                money=Money(cents=2000),
                payee="A",
                category="Groceries",
                occurred_at=_at(5),
            )
        )
        await unit.entries.add(
            LedgerEntry.record_expense(
                money=Money(cents=500),
                payee="B",
                category="Uncategorized",
                occurred_at=_at(20),
            )
        )
        await unit.entries.add(
            LedgerEntry.record_income(
                money=Money(cents=180000),
                payee="C",
                category="Salary",
                occurred_at=_at(3),
            )
        )
        await unit.entries.add(
            LedgerEntry.record_expense(
                money=Money(cents=500, currency="USD"),
                payee="D",
                category="Food & Drinks",
                occurred_at=_at(8),
            )
        )
        out_of_range = LedgerEntry(
            type=EntryType.EXPENSE,
            amount_cents=9999,
            payee="Old",
            category="Transport",
            payment_method=PaymentMethod.CARD,
            occurred_at=datetime(2026, 10, 1, 12, tzinfo=ZoneInfo("Europe/Madrid")).astimezone(UTC),
        )
        await unit.entries.add(out_of_range)
        await unit.commit()

    service = LedgerBalanceQueryService(
        SqlBalanceReadModel(session_factory),
        today_provider=lambda: datetime(2026, 11, 6, tzinfo=ZoneInfo("Europe/Madrid")).date(),
    )
    result = await service.get()
    by_code = {group.currency: group for group in result.currencies}
    assert by_code["EUR"].income_cents == 180000
    assert by_code["EUR"].expense_cents == 2500
    assert by_code["EUR"].net_cents == 177500
    assert by_code["USD"].expense_cents == 500
    assert by_code["USD"].income_cents == 0

    day = await service.get(
        datetime(2026, 11, 5, tzinfo=ZoneInfo("Europe/Madrid")).date(),
        datetime(2026, 11, 5, tzinfo=ZoneInfo("Europe/Madrid")).date(),
    )
    day_eur = next(group for group in day.currencies if group.currency == "EUR")
    assert day_eur.expense_cents == 2000
    assert day_eur.income_cents == 0

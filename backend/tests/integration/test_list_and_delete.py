from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio.session import AsyncSession

from income_expense_bot.application.commands import DeleteLedgerEntryCommand, RecordExpenseCommand
from income_expense_bot.application.handler.delete_ledger_entry import DeleteLedgerEntryHandler
from income_expense_bot.application.handler.record_expense import RecordExpenseHandler
from income_expense_bot.application.query.balance import LedgerBalanceQueryService
from income_expense_bot.application.query.entries import LedgerEntryListQueryService
from income_expense_bot.domain.model.ledger_entry import LedgerEntry
from income_expense_bot.domain.model.money import Money
from income_expense_bot.infrastructure.read_model.balance_read_model import SqlBalanceReadModel
from income_expense_bot.infrastructure.unity_of_work import SqlAlchemyUnitOfWork


async def test_list_recent_default_eight_and_cursor(
    uow: SqlAlchemyUnitOfWork,
) -> None:
    async with uow as unit:
        for index in range(12):
            await unit.entries.add(
                LedgerEntry.record_expense(
                    money=Money(cents=100 + index),
                    payee=f"Shop {index}",
                    category="Uncategorized",
                    occurred_at=datetime(2026, 11, 1, tzinfo=UTC) + timedelta(hours=index),
                )
            )
        await unit.commit()
        service = LedgerEntryListQueryService(unit.entries)
        first = await service.get()
        assert len(first.items) == 8
        assert first.next_cursor is not None
        second = await service.get(cursor=first.next_cursor)
        assert {item.id for item in first.items}.isdisjoint({item.id for item in second.items})
        assert len(second.items) == 4
        assert second.next_cursor is None
        await unit.entries.add(
            LedgerEntry.record_expense(
                money=Money(cents=1),
                payee="Newest",
                category="Uncategorized",
                occurred_at=datetime(2026, 12, 1, tzinfo=UTC),
            )
        )
        await unit.commit()
        continued = await service.get(cursor=first.next_cursor)
        assert "Newest" not in {item.payee for item in continued.items}
        assert {item.id for item in first.items}.isdisjoint({item.id for item in continued.items})


async def test_delete_omitted_from_balance(
    uow: SqlAlchemyUnitOfWork,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await RecordExpenseHandler(uow).handle(
        RecordExpenseCommand(amount_cents=2000, payee="Shop", category="Groceries")
    )
    async with uow as unit:
        page = await LedgerEntryListQueryService(unit.entries).get()
        entry_id = page.items[0].id
    await DeleteLedgerEntryHandler(uow).handle(DeleteLedgerEntryCommand(entry_id=entry_id))
    service = LedgerBalanceQueryService(
        SqlBalanceReadModel(session_factory),
        today_provider=lambda: datetime.now(UTC).date(),
    )
    result = await service.get()
    assert result.expense_cents == 0

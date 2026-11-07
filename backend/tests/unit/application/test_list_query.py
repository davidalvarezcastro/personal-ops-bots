from datetime import UTC, datetime, timedelta

from tests.unit.application.fakes import InMemoryLedgerEntryRepository

from income_expense_bot.application.query.entries import LedgerEntryListQueryService
from income_expense_bot.domain.model.entry_type import EntryType, PaymentMethod
from income_expense_bot.domain.model.ledger_entry import LedgerEntry
from income_expense_bot.domain.model.money import Money


def _expense(index: int, *, occurred_at: datetime | None = None) -> LedgerEntry:
    when = occurred_at or datetime(2026, 11, 1, tzinfo=UTC) + timedelta(hours=index)
    return LedgerEntry.record_expense(
        money=Money(cents=100 + index),
        payee=f"Shop {index}",
        category="Uncategorized",
        occurred_at=when,
    )


async def test_default_page_is_eight_newest() -> None:
    repo = InMemoryLedgerEntryRepository()
    for index in range(10):
        await repo.add(_expense(index))
    page = await LedgerEntryListQueryService(repo).get()
    assert [item.payee for item in page.items] == [f"Shop {i}" for i in range(9, 1, -1)]
    assert page.next_cursor is not None


async def test_second_page_via_cursor() -> None:
    repo = InMemoryLedgerEntryRepository()
    for index in range(12):
        await repo.add(_expense(index))
    service = LedgerEntryListQueryService(repo)
    first = await service.get()
    second = await service.get(cursor=first.next_cursor)
    first_ids = {item.id for item in first.items}
    second_ids = {item.id for item in second.items}
    assert first_ids.isdisjoint(second_ids)
    assert len(second.items) == 4
    assert second.next_cursor is None


async def test_newer_insert_does_not_duplicate_continued_page() -> None:
    repo = InMemoryLedgerEntryRepository()
    for index in range(10):
        await repo.add(_expense(index))
    service = LedgerEntryListQueryService(repo)
    first = await service.get()
    await repo.add(
        _expense(
            99,
            occurred_at=datetime(2026, 12, 1, tzinfo=UTC),
        )
    )
    second = await service.get(cursor=first.next_cursor)
    assert {item.id for item in first.items}.isdisjoint({item.id for item in second.items})
    assert "Shop 99" not in {item.payee for item in second.items}


async def test_transfers_omitted() -> None:
    repo = InMemoryLedgerEntryRepository()
    await repo.add(_expense(1))
    transfer = LedgerEntry(
        type=EntryType.TRANSFER,
        amount_cents=1,
        payee="X",
        category="Uncategorized",
        payment_method=PaymentMethod.CARD,
        occurred_at=datetime(2026, 11, 2, tzinfo=UTC),
    )
    await repo.add(transfer)
    page = await LedgerEntryListQueryService(repo).get()
    assert [item.payee for item in page.items] == ["Shop 1"]
    assert page.next_cursor is None

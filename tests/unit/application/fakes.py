from datetime import datetime

from income_expense_bot.application.unity_of_work import AbstractUnitOfWork
from income_expense_bot.domain.model.entry_type import EntryType
from income_expense_bot.domain.model.ledger_entry import LedgerEntry
from income_expense_bot.domain.repository.ledger_entry_repository import AbstractLedgerEntryRepository


class InMemoryLedgerEntryRepository(AbstractLedgerEntryRepository):
    def __init__(self) -> None:
        super().__init__()
        self.items: list[LedgerEntry] = []

    async def _add(self, entry: LedgerEntry) -> None:
        self.items.append(entry)

    async def get(self, entry_id: str) -> LedgerEntry | None:
        return next((item for item in self.items if item.id == entry_id), None)

    async def list_recent(
        self,
        *,
        limit: int,
        after: tuple[datetime, str] | None = None,
    ) -> list[LedgerEntry]:
        rows = [item for item in self.items if item.type is not EntryType.TRANSFER]
        rows.sort(key=lambda item: (item.occurred_at, item.id), reverse=True)
        if after is not None:
            occurred_at, entry_id = after
            rows = [
                item
                for item in rows
                if item.occurred_at < occurred_at or (item.occurred_at == occurred_at and item.id < entry_id)
            ]
        return rows[:limit]

    async def remove(self, entry: LedgerEntry) -> None:
        self.items = [item for item in self.items if item.id != entry.id]


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self) -> None:
        self.entries = InMemoryLedgerEntryRepository()
        self.committed = False
        self.rolled_back = False

    async def _commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from income_expense_bot.domain.model.ledger_entry import LedgerEntry


class AbstractLedgerEntryRepository(ABC):
    def __init__(self) -> None:
        self.seen: set[LedgerEntry] = set()

    async def add(self, entry: LedgerEntry) -> None:
        await self._add(entry)
        self.seen.add(entry)

    @abstractmethod
    async def _add(self, entry: LedgerEntry) -> None: ...

    @abstractmethod
    async def get(self, entry_id: str) -> LedgerEntry | None: ...

    @abstractmethod
    async def list_recent(
        self,
        *,
        limit: int,
        after: tuple[datetime, str] | None = None,
    ) -> list[LedgerEntry]: ...

    @abstractmethod
    async def remove(self, entry: LedgerEntry) -> None: ...

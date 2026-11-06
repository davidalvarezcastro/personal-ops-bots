from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from income_expense_bot.domain.model.ledger_entry import LedgerEntry
from income_expense_bot.domain.repository.ledger_entry_repository import AbstractLedgerEntryRepository


class SqlAlchemyLedgerEntryRepository(AbstractLedgerEntryRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self._session = session

    async def _add(self, entry: LedgerEntry) -> None:
        self._session.add(entry)

from __future__ import annotations

from datetime import datetime

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from income_expense_bot.domain.model.entry_type import EntryType
from income_expense_bot.domain.model.ledger_entry import LedgerEntry
from income_expense_bot.domain.repository.ledger_entry_repository import AbstractLedgerEntryRepository
from income_expense_bot.infrastructure.persistence.orm import ledger_entries_table


class SqlAlchemyLedgerEntryRepository(AbstractLedgerEntryRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self._session = session

    async def _add(self, entry: LedgerEntry) -> None:
        self._session.add(entry)

    async def get(self, entry_id: str) -> LedgerEntry | None:
        return await self._session.get(LedgerEntry, entry_id)

    async def list_recent(
        self,
        *,
        limit: int,
        after: tuple[datetime, str] | None = None,
    ) -> list[LedgerEntry]:
        stmt = (
            select(LedgerEntry)
            .where(ledger_entries_table.c.type != EntryType.TRANSFER)
            .order_by(ledger_entries_table.c.occurred_at.desc(), ledger_entries_table.c.id.desc())
            .limit(limit)
        )
        if after is not None:
            occurred_at, entry_id = after
            stmt = stmt.where(
                or_(
                    ledger_entries_table.c.occurred_at < occurred_at,
                    and_(
                        ledger_entries_table.c.occurred_at == occurred_at,
                        ledger_entries_table.c.id < entry_id,
                    ),
                )
            )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def remove(self, entry: LedgerEntry) -> None:
        await self._session.delete(entry)

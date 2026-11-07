from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from income_expense_bot.application.query.balance import AbstractBalanceReadModel, CategorySum
from income_expense_bot.application.query.period import DatePeriod
from income_expense_bot.domain.model.entry_type import EntryType
from income_expense_bot.infrastructure.persistence.orm import ledger_entries_table


class SqlBalanceReadModel(AbstractBalanceReadModel):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def fetch_totals(self, period: DatePeriod) -> list[CategorySum]:
        stmt = (
            select(
                ledger_entries_table.c.type,
                ledger_entries_table.c.category,
                func.sum(ledger_entries_table.c.amount_cents),
            )
            .where(
                ledger_entries_table.c.occurred_at >= period.start_utc(),
                ledger_entries_table.c.occurred_at < period.end_exclusive_utc(),
                ledger_entries_table.c.type != EntryType.TRANSFER,
            )
            .group_by(ledger_entries_table.c.type, ledger_entries_table.c.category)
        )
        async with self._session_factory() as session:
            result = await session.execute(stmt)
            rows: list[CategorySum] = []
            for entry_type, category, total in result.all():
                type_value = entry_type.value if isinstance(entry_type, EntryType) else str(entry_type)
                rows.append(
                    CategorySum(
                        entry_type=type_value,
                        category=str(category),
                        amount_cents=int(total or 0),
                    )
                )
            return rows

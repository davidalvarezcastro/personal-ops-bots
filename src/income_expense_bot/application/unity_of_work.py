from __future__ import annotations

from abc import ABC, abstractmethod
from types import TracebackType

from income_expense_bot.domain.repository.ledger_entry_repository import AbstractLedgerEntryRepository


class AbstractUnitOfWork(ABC):
    entries: AbstractLedgerEntryRepository

    async def __aenter__(self) -> AbstractUnitOfWork:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type:
            await self.rollback()
        else:
            await self._commit()

    async def commit(self) -> None:
        await self._commit()

    @abstractmethod
    async def _commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...

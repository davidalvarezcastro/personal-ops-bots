from income_expense_bot.application.unity_of_work import AbstractUnitOfWork
from income_expense_bot.domain.model.ledger_entry import LedgerEntry
from income_expense_bot.domain.repository.ledger_entry_repository import AbstractLedgerEntryRepository


class InMemoryLedgerEntryRepository(AbstractLedgerEntryRepository):
    def __init__(self) -> None:
        super().__init__()
        self.items: list[LedgerEntry] = []

    async def _add(self, entry: LedgerEntry) -> None:
        self.items.append(entry)


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self) -> None:
        self.entries = InMemoryLedgerEntryRepository()
        self.committed = False
        self.rolled_back = False

    async def _commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True

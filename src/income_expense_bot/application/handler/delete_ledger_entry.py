from income_expense_bot.application.commands import DeleteLedgerEntryCommand
from income_expense_bot.application.handler.base_handler import BaseHandler
from income_expense_bot.domain.exception.ledger import EntryNotFoundError


class DeleteLedgerEntryHandler(BaseHandler):
    async def handle(self, command: DeleteLedgerEntryCommand) -> None:
        async with self._uow as uow:
            entry = await uow.entries.get(command.entry_id)
            if entry is None:
                raise EntryNotFoundError(f"entry not found: {command.entry_id}")
            await uow.entries.remove(entry)
            await uow.commit()

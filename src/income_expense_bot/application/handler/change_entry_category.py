from income_expense_bot.application.commands import ChangeEntryCategoryCommand
from income_expense_bot.application.handler.base_handler import BaseHandler
from income_expense_bot.domain.exception.ledger import EntryNotFoundError


class ChangeEntryCategoryHandler(BaseHandler):
    async def handle(self, command: ChangeEntryCategoryCommand) -> None:
        async with self._uow as uow:
            entry = await uow.entries.get(command.entry_id)
            if entry is None:
                raise EntryNotFoundError(f"entry not found: {command.entry_id}")
            entry.change_category(command.category)
            await uow.commit()

from income_expense_bot.application.commands import RecordIncomeCommand
from income_expense_bot.application.handler.base_handler import BaseHandler
from income_expense_bot.domain.model.ledger_entry import LedgerEntry
from income_expense_bot.domain.model.money import Money


class RecordIncomeHandler(BaseHandler):
    async def handle(self, command: RecordIncomeCommand) -> None:
        async with self._uow as uow:
            entry = LedgerEntry.record_income(
                money=Money(cents=command.amount_cents),
                payee=command.payee,
                category=command.category,
            )
            await uow.entries.add(entry)
            await uow.commit()

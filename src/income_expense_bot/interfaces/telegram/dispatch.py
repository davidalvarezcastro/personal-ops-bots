from __future__ import annotations

from collections.abc import Awaitable, Callable

from income_expense_bot.application.handler.record_expense import RecordExpenseHandler
from income_expense_bot.application.handler.record_income import RecordIncomeHandler
from income_expense_bot.application.query.balance import LedgerBalanceQueryService
from income_expense_bot.domain.exception.ledger import (
    InvalidAmountError,
    InvalidDateFormatError,
    InvalidDateRangeError,
    LedgerError,
    MissingPayeeError,
    UnauthorizedError,
)
from income_expense_bot.interfaces.telegram.auth import require_authorized
from income_expense_bot.interfaces.telegram.formatting import format_balance, format_record_confirmation
from income_expense_bot.interfaces.telegram.parser import parse_balance_args, parse_expense, parse_income

Reply = Callable[[str], Awaitable[None]]


class TelegramDispatcher:
    def __init__(
        self,
        *,
        allowed_user_ids: frozenset[int],
        expense_handler: RecordExpenseHandler,
        income_handler: RecordIncomeHandler,
        balance_query: LedgerBalanceQueryService,
    ) -> None:
        self._allowed = allowed_user_ids
        self._expense_handler = expense_handler
        self._income_handler = income_handler
        self._balance_query = balance_query

    async def handle_expense(self, user_id: int | None, text: str, reply: Reply) -> None:
        try:
            require_authorized(user_id, self._allowed)
            command = parse_expense(text)
            await self._expense_handler.handle(command)
            await reply(
                format_record_confirmation(
                    kind="Expense",
                    amount_cents=command.amount_cents,
                    payee=command.payee,
                    category=command.category,
                )
            )
        except UnauthorizedError:
            return
        except MissingPayeeError:
            await reply("merchant is required")
        except InvalidAmountError:
            await reply("amount is invalid")
        except LedgerError as exc:
            await reply(str(exc))

    async def handle_income(self, user_id: int | None, text: str, reply: Reply) -> None:
        try:
            require_authorized(user_id, self._allowed)
            command = parse_income(text)
            await self._income_handler.handle(command)
            await reply(
                format_record_confirmation(
                    kind="Income",
                    amount_cents=command.amount_cents,
                    payee=command.payee,
                    category=command.category,
                )
            )
        except UnauthorizedError:
            return
        except MissingPayeeError:
            await reply("source is required")
        except InvalidAmountError:
            await reply("amount is invalid")
        except LedgerError as exc:
            await reply(str(exc))

    async def handle_balance(self, user_id: int | None, text: str, reply: Reply) -> None:
        try:
            require_authorized(user_id, self._allowed)
            start, end = parse_balance_args(text)
            result = await self._balance_query.get(start, end)
            await reply(format_balance(result))
        except UnauthorizedError:
            return
        except InvalidDateFormatError:
            await reply("date is invalid")
        except InvalidDateRangeError:
            await reply("date range is invalid")
        except LedgerError as exc:
            await reply(str(exc))

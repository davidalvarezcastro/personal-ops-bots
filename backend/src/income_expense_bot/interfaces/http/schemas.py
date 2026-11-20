from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from income_expense_bot.application.query.balance import BalanceResult
from income_expense_bot.domain.model.ledger_entry import LedgerEntry


class BalanceCategoryOut(BaseModel):
    category: str
    amount_cents: int


class CurrencyBalanceOut(BaseModel):
    currency: str
    income_cents: int
    expense_cents: int
    net_cents: int
    expense_by_category: list[BalanceCategoryOut]
    income_by_category: list[BalanceCategoryOut]


class BalanceOut(BaseModel):
    start: str
    end: str
    currencies: list[CurrencyBalanceOut]


class EntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    type: str
    amount_cents: int
    currency: str
    payee: str
    category: str
    payment_method: str
    occurred_at: datetime


class EntryPageOut(BaseModel):
    items: list[EntryOut]
    next_cursor: str | None = None


class EntryCreate(BaseModel):
    type: Literal["expense", "income"]
    amount: str
    payee: str
    category: str | None = None
    currency: str | None = None


class EntryPatch(BaseModel):
    category: str = Field(min_length=1)


def entry_to_out(entry: LedgerEntry) -> EntryOut:
    return EntryOut(
        id=entry.id,
        type=str(entry.type),
        amount_cents=entry.amount_cents,
        currency=entry.currency,
        payee=entry.payee,
        category=entry.category,
        payment_method=str(entry.payment_method),
        occurred_at=entry.occurred_at,
    )


def balance_to_out(result: BalanceResult) -> BalanceOut:
    return BalanceOut(
        start=result.period.start.isoformat(),
        end=result.period.end.isoformat(),
        currencies=[
            CurrencyBalanceOut(
                currency=group.currency,
                income_cents=group.income_cents,
                expense_cents=group.expense_cents,
                net_cents=group.net_cents,
                expense_by_category=[
                    BalanceCategoryOut(category=row.category, amount_cents=row.amount_cents)
                    for row in group.expense_by_category
                ],
                income_by_category=[
                    BalanceCategoryOut(category=row.category, amount_cents=row.amount_cents)
                    for row in group.income_by_category
                ],
            )
            for group in result.currencies
        ],
    )

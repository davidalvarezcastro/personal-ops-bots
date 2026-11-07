from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from income_expense_bot.domain.model.ledger_entry import LedgerEntry


class BalanceCategoryOut(BaseModel):
    category: str
    amount_cents: int


class BalanceOut(BaseModel):
    start: str
    end: str
    income_cents: int
    expense_cents: int
    net_cents: int
    expense_by_category: list[BalanceCategoryOut]
    income_by_category: list[BalanceCategoryOut]


class EntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    type: str
    amount_cents: int
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


class EntryPatch(BaseModel):
    category: str = Field(min_length=1)


def entry_to_out(entry: LedgerEntry) -> EntryOut:
    return EntryOut(
        id=entry.id,
        type=str(entry.type),
        amount_cents=entry.amount_cents,
        payee=entry.payee,
        category=entry.category,
        payment_method=str(entry.payment_method),
        occurred_at=entry.occurred_at,
    )

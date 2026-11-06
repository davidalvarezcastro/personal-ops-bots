from __future__ import annotations

from dataclasses import dataclass


class Command:
    """Marker for write-side messages."""


@dataclass(frozen=True)
class RecordExpenseCommand(Command):
    amount_cents: int
    payee: str
    category: str


@dataclass(frozen=True)
class RecordIncomeCommand(Command):
    amount_cents: int
    payee: str
    category: str

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from income_expense_bot.domain.exception.ledger import MissingPayeeError
from income_expense_bot.domain.model.entry_type import EntryType, PaymentMethod
from income_expense_bot.domain.model.money import Money


def _utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass(eq=False)
class LedgerEntry:
    amount_cents: int
    payee: str
    category: str
    type: EntryType
    id: str = field(default_factory=lambda: str(uuid4()))
    payment_method: PaymentMethod = PaymentMethod.CARD
    occurred_at: datetime = field(default_factory=_utc_now)

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LedgerEntry):
            return NotImplemented
        return self.id == other.id

    @classmethod
    def record_expense(
        cls,
        *,
        money: Money,
        payee: str,
        category: str,
        occurred_at: datetime | None = None,
    ) -> LedgerEntry:
        return cls._record(
            entry_type=EntryType.EXPENSE,
            money=money,
            payee=payee,
            category=category,
            occurred_at=occurred_at,
        )

    @classmethod
    def record_income(
        cls,
        *,
        money: Money,
        payee: str,
        category: str,
        occurred_at: datetime | None = None,
    ) -> LedgerEntry:
        return cls._record(
            entry_type=EntryType.INCOME,
            money=money,
            payee=payee,
            category=category,
            occurred_at=occurred_at,
        )

    @classmethod
    def _record(
        cls,
        *,
        entry_type: EntryType,
        money: Money,
        payee: str,
        category: str,
        occurred_at: datetime | None,
    ) -> LedgerEntry:
        if entry_type is EntryType.TRANSFER:
            raise ValueError("recording commands cannot create transfer entries")
        cleaned = payee.strip()
        if not cleaned:
            raise MissingPayeeError("merchant is required")
        kwargs: dict[str, object] = {
            "type": entry_type,
            "amount_cents": money.cents,
            "payee": cleaned,
            "category": category,
            "payment_method": PaymentMethod.CARD,
        }
        if occurred_at is not None:
            kwargs["occurred_at"] = occurred_at
        return cls(**kwargs)  # type: ignore[arg-type]

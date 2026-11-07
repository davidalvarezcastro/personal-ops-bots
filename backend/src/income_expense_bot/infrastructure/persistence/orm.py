from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from sqlalchemy import CheckConstraint, Column, DateTime, Index, Integer, MetaData, String, Table, TypeDecorator
from sqlalchemy.orm import registry

from income_expense_bot.domain.model.entry_type import EntryType, PaymentMethod
from income_expense_bot.domain.model.ledger_entry import LedgerEntry


class UtcDateTime(TypeDecorator[datetime]):
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect: object) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)

    def process_result_value(self, value: datetime | None, dialect: object) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)


class EnumValue(TypeDecorator[Any]):
    impl = String
    cache_ok = True

    def __init__(self, enum_cls: type[Enum], length: int = 32) -> None:
        super().__init__(length)
        self._enum_cls = enum_cls

    def process_bind_param(self, value: Enum | str | None, dialect: object) -> str | None:
        if value is None:
            return None
        if isinstance(value, Enum):
            return str(value.value)
        return str(value)

    def process_result_value(self, value: str | None, dialect: object) -> Enum | None:
        if value is None:
            return None
        return self._enum_cls(value)


metadata = MetaData()
mapper_registry = registry(metadata=metadata)

ledger_entries_table = Table(
    "ledger_entries",
    metadata,
    Column("id", String, primary_key=True),
    Column("type", EnumValue(EntryType), nullable=False),
    Column("amount_cents", Integer, nullable=False),
    Column("payee", String, nullable=False),
    Column("category", String, nullable=False),
    Column("payment_method", EnumValue(PaymentMethod), nullable=False),
    Column("occurred_at", UtcDateTime(), nullable=False),
    CheckConstraint(
        "type IN ('expense', 'income', 'transfer')",
        name="ck_ledger_entries_type",
    ),
    Index("ix_ledger_entries_occurred_at", "occurred_at"),
    Index("ix_ledger_entries_type_occurred_at", "type", "occurred_at"),
)

_MAPPED = False


def start_mappers() -> None:
    global _MAPPED
    if _MAPPED:
        return
    mapper_registry.map_imperatively(LedgerEntry, ledger_entries_table)
    _MAPPED = True

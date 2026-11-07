from __future__ import annotations

from base64 import urlsafe_b64decode, urlsafe_b64encode
from dataclasses import dataclass
from datetime import datetime

from income_expense_bot.domain.exception.ledger import InvalidCursorError
from income_expense_bot.domain.model.ledger_entry import LedgerEntry
from income_expense_bot.domain.repository.ledger_entry_repository import AbstractLedgerEntryRepository

DEFAULT_PAGE_SIZE = 8
MAX_PAGE_SIZE = 100


@dataclass(frozen=True)
class EntryPage:
    items: tuple[LedgerEntry, ...]
    next_cursor: str | None


def encode_cursor(occurred_at: datetime, entry_id: str) -> str:
    raw = f"{occurred_at.isoformat()}\n{entry_id}".encode()
    return urlsafe_b64encode(raw).decode("ascii")


def decode_cursor(cursor: str) -> tuple[datetime, str]:
    try:
        decoded = urlsafe_b64decode(cursor.encode("ascii")).decode()
        stamp, entry_id = decoded.split("\n", 1)
        occurred_at = datetime.fromisoformat(stamp)
    except (ValueError, UnicodeDecodeError) as exc:
        raise InvalidCursorError("invalid list cursor") from exc
    if not entry_id:
        raise InvalidCursorError("invalid list cursor")
    return occurred_at, entry_id


class LedgerEntryListQueryService:
    def __init__(self, repository: AbstractLedgerEntryRepository) -> None:
        self._repository = repository

    async def get(self, *, limit: int | None = None, cursor: str | None = None) -> EntryPage:
        page_size = DEFAULT_PAGE_SIZE if limit is None else limit
        if page_size < 1:
            page_size = DEFAULT_PAGE_SIZE
        page_size = min(page_size, MAX_PAGE_SIZE)
        after = decode_cursor(cursor) if cursor else None
        rows = await self._repository.list_recent(limit=page_size + 1, after=after)
        has_more = len(rows) > page_size
        items = tuple(rows[:page_size])
        next_cursor = None
        if has_more and items:
            last = items[-1]
            next_cursor = encode_cursor(last.occurred_at, last.id)
        return EntryPage(items=items, next_cursor=next_cursor)

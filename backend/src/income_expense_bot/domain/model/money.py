from __future__ import annotations

import re
from dataclasses import dataclass

from income_expense_bot.domain.exception.ledger import InvalidAmountError

_AMOUNT = re.compile(r"^(\d+)(?:([.,])(\d{1,2}))?$")


@dataclass(frozen=True)
class Money:
    cents: int

    def __post_init__(self) -> None:
        if self.cents < 0:
            raise InvalidAmountError("amount must be zero or positive")

    @classmethod
    def parse(cls, text: str) -> Money:
        raw = text.strip()
        if not raw or not _AMOUNT.fullmatch(raw):
            raise InvalidAmountError(f"invalid amount: {text}")
        match = _AMOUNT.fullmatch(raw)
        assert match is not None
        whole = int(match.group(1))
        fraction = match.group(3) or ""
        if len(fraction) == 1:
            fraction = f"{fraction}0"
        cents = whole * 100 + (int(fraction) if fraction else 0)
        return cls(cents=cents)

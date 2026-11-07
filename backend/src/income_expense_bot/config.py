from __future__ import annotations

import os
from dataclasses import dataclass


class ConfigError(ValueError):
    """Missing or invalid process configuration."""


def _require(key: str) -> str:
    value = os.getenv(key)
    if value is None or value.strip() == "":
        raise ConfigError(f"environment key {key} is not defined")
    return value.strip()


@dataclass(frozen=True)
class Config:
    telegram_bot_token: str
    telegram_allowed_user_ids: frozenset[int]
    ledger_sqlite_path: str

    @classmethod
    def from_env(cls) -> Config:
        token = _require("TELEGRAM_BOT_TOKEN")
        raw_ids = _require("TELEGRAM_ALLOWED_USER_IDS")
        ids: set[int] = set()
        for part in raw_ids.split(","):
            piece = part.strip()
            if not piece:
                continue
            ids.add(int(piece))
        if not ids:
            raise ConfigError("TELEGRAM_ALLOWED_USER_IDS must contain at least one user id")
        path = os.getenv("LEDGER_SQLITE_PATH", "ledger.sqlite").strip() or "ledger.sqlite"
        return cls(
            telegram_bot_token=token,
            telegram_allowed_user_ids=frozenset(ids),
            ledger_sqlite_path=path,
        )

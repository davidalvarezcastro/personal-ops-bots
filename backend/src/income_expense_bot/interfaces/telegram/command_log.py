from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from uuid import uuid4

import structlog

from income_expense_bot.logging_config import get_logger


def command_parameters(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return ""
    parts = stripped.split(maxsplit=1)
    return parts[1] if len(parts) > 1 else ""


@contextmanager
def command_context(*, command: str, user_id: int | None) -> Iterator[None]:
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        command=command,
        user_id=user_id,
        command_id=str(uuid4()),
    )
    try:
        yield
    finally:
        structlog.contextvars.clear_contextvars()


def log_command_received(text: str) -> None:
    get_logger(__name__).info("command.received", parameters=command_parameters(text))


def log_command_rejected() -> None:
    get_logger(__name__).warning("command.rejected")

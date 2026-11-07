from __future__ import annotations

import logging
import os
import sys
from typing import TextIO, cast

import structlog


def _log_level() -> int:
    raw = os.getenv("LOG_LEVEL", "INFO").strip().upper() or "INFO"
    level = logging.getLevelNamesMapping().get(raw)
    if level is None:
        return logging.INFO
    return level


def _use_console_renderer() -> bool:
    fmt = os.getenv("LOG_FORMAT")
    if fmt is None or fmt.strip() == "":
        return sys.stderr.isatty()
    return fmt.strip().lower() == "console"


def configure_logging(
    *,
    stream: TextIO | None = None,
    cache_logger_on_first_use: bool = True,
) -> None:
    level = _log_level()
    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)
    shared_processors: list[structlog.typing.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(level),
        cache_logger_on_first_use=cache_logger_on_first_use,
    )

    renderer: structlog.typing.Processor
    if _use_console_renderer():
        renderer = structlog.dev.ConsoleRenderer()
    else:
        renderer = structlog.processors.JSONRenderer()

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
        foreign_pre_chain=[
            *shared_processors,
            structlog.stdlib.ExtraAdder(),
        ],
    )

    handler = logging.StreamHandler(stream or sys.stdout)
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    return cast(structlog.stdlib.BoundLogger, structlog.get_logger(name))

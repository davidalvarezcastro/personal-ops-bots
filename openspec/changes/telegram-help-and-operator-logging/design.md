# Design

## Context

The ledger bot already dispatches `/expense`, `/income`, and `/balance` through `TelegramDispatcher` with allowlist auth. There is no logging, no `/start` or `/help`, and `run()` only calls `application.run_polling()`. See `proposal.md` for motivation; behavior is in `specs/telegram-guidance/spec.md` and `specs/operator-logging/spec.md`. Ledger domain and CQRS handlers stay unchanged.

## Goals / Non-Goals

**Goals:**

- Keep guidance in `interfaces/telegram`. Configure logging once in the composition root; emit events from the Telegram adapter (not from domain).
- Reuse existing allowlist (`require_authorized`) for `/start` and `/help`.
- Structured logs as of 2026 Python practice: **structlog** + stdlib `logging` so first-party and library logs share one pipeline.

**Non-Goals:**

- Pushing a Telegram message to allowlisted chats when the process boots.
- Rotating log files, syslog, or shipping to Loki/ELK from this process.
- OpenTelemetry traces/metrics in this change.
- Changing expense/income/balance parsing.

## Decisions

### 1. Guidance lives next to dispatch

Add `handle_start` / `handle_help` on `TelegramDispatcher` (or a small `guidance.py` used by the dispatcher) that reply with fixed copy. PTB `CommandHandler("start")` and `CommandHandler("help")` in `app.py`.

**Alternative:** a domain "Help" use case. Rejected: no ledger state; it is delivery UX.

### 2. Command menu via `set_my_commands` in `post_init`

After schema create, call `application.bot.set_my_commands([...])` for start, help, expense, income, balance.

### 3. structlog + stdlib ProcessorFormatter (not bare `basicConfig`)

This is the current recommended shape for application logs in Python:

- **structlog** event dicts (`event=` plus keyword fields), not `%s` interpolation.
- Shared processors: `merge_contextvars`, `add_log_level`, `TimeStamper(fmt="iso", utc=True)`, `format_exc_info`.
- Chain ends with `ProcessorFormatter.wrap_for_formatter`.
- A stdlib `StreamHandler(sys.stdout)` uses `ProcessorFormatter` so **python-telegram-bot** and **SQLAlchemy** loggers render the same way.
- Renderer: `ConsoleRenderer` when stderr is a TTY and `LOG_FORMAT` is unset; `JSONRenderer` otherwise or when `LOG_FORMAT=json`.
- `cache_logger_on_first_use=True`. Filter with `make_filtering_bound_logger` from `LOG_LEVEL` (default INFO).
- 12-factor: **stdout only**, no application log file.

Configure once in `run()` via a small `interfaces` or composition-root `configure_logging()` before building the Application.

**Alternative:** stdlib `basicConfig` only. Rejected: unstructured strings, no stable fields for later collectors.

**Alternative:** native structlog `WriteLogger` only, bypassing stdlib. Rejected: PTB/SQLAlchemy would still print a different format.

**Alternative:** OpenTelemetry Logging SDK. Rejected for this personal bot (no collector in v1); structlog JSON on stdout is the portable input those backends expect later.

### 4. Contextvars per command

At the start of each dispatcher handle: `clear_contextvars()`, then `bind_contextvars(command=..., user_id=..., command_id=<uuid4>)`. Log `command.received` (authorized) or `command.rejected` (unauthorized, WARNING, no parameters). Clear again in `finally`.

Startup: `logger.info("bot.running", component="telegram")` from `post_init` after schema + `set_my_commands`.

### 5. Never log the token

Do not pass `Config.telegram_bot_token` into log calls. No processor needs to redact if the token never enters the event dict; still avoid logging `repr(config)`.

## Risks / Trade-offs

- [Command args in logs] → Personal machine; token still never logged. Acceptable.
- [JSON vs pretty] → TTY auto-detect can surprise if someone pipes to `less`; `LOG_FORMAT` overrides.
- [structlog dependency] → One well-maintained library; uv.lock pins it.

## Migration Plan

- Add `structlog` with uv. No schema change. Restart the process. Existing SQLite files unchanged.

## Open Questions

- Exact welcome/help sentences (must include the required command names and syntax).

# Tasks

## 1. Guidance copy and dispatcher

- [x] 1.1 Add start/help reply text that states the bot is ready and lists `/start`, `/help`, `/expense`, `/income`, `/balance` with syntax, and verify unit tests assert those names appear (`telegram-guidance`: start welcome; help lists commands)
- [x] 1.2 Add dispatcher handlers for `/start` and `/help` using the existing allowlist, and verify authorized users get the text while unauthorized users get no reply (`telegram-guidance`: unauthorized operators)

## 2. Structured logging

- [x] 2.1 Add `structlog` with uv and implement `configure_logging()` (stdlib `ProcessorFormatter`, stdout, ISO UTC timestamp, `LOG_LEVEL`, `LOG_FORMAT` console|json / TTY default), and verify a unit test parses a JSON line with `timestamp`, `level`, and `event` when format is json (`operator-logging`: JSON; ready event)
- [x] 2.2 Bind contextvars per command and log structured `command.received` with `command` and `parameters` fields, and verify `/expense 12,50 Mercadona` yields those fields (`operator-logging`: authorized commands)
- [x] 2.3 Log `bot.running` from `post_init` after schema and command menu, and verify the event has no bot token (`operator-logging`: ready process; never include token)

## 3. Telegram wiring

- [x] 3.1 Register PTB `CommandHandler`s for `start` and `help` and verify the application handler set includes those commands (`telegram-guidance`)
- [x] 3.2 Call `set_my_commands` in `post_init` for start, help, expense, income, and balance, and verify a unit test with a stub bot records those five names (`telegram-guidance`: command menu)
- [x] 3.3 Update README with `/start`, `/help`, stdout structured logs, and `LOG_LEVEL` / `LOG_FORMAT`, and verify the documented commands match the specs

## 4. Cross-cutting

- [x] 4.1 Run `uv run pytest` and verify tests pass
- [x] 4.2 Run `uv run ruff check src tests` and `uv run mypy src/income_expense_bot` and verify no errors
- [x] 4.3 Grep `domain/` and `application/` and verify they import neither `telegram` nor `structlog`

## Workflow follow-up

- Archive the change after implementation is verified.
- Merge delta specs into `openspec/specs/telegram-guidance` and `openspec/specs/operator-logging`.

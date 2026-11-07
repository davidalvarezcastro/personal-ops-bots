# Proposal

## Why

The ledger bot only answers `/expense`, `/income`, and `/balance`. An operator cannot discover those commands in chat, `/start` is silent, and the process prints nothing when it boots or when a command arrives—so a successful launch and daily use are both opaque.

## What Changes

- Add `/start`: authorized operator receives a short welcome that the bot is ready and is pointed at `/help`.
- Add `/help`: authorized operator receives the list of available commands with syntax (and brief examples for ledger commands).
- Register the command list with Telegram so the client command menu matches `/help`.
- Emit **structured logs** to stdout (12-factor): ISO-8601 UTC timestamp, level, event name, and key/value fields. Pretty console when attached to a TTY; JSON when not (or when `LOG_FORMAT=json`).
- Log when the process is ready to poll and when a command is handled, with command name, parameters, and Telegram user id bound as context. Never log the bot token.
- Startup health for the person running the process is a structured `bot.running` event—not an unsolicited Telegram message to the allowlist.

Out of scope: changing ledger recording or balance rules; log files on disk; OpenTelemetry exporters; ELK/Loki as a required backend; BotFather web UI beyond `set_my_commands`; sending Telegram messages on process boot.

### Confirmed decisions

- `/start` is the in-chat welcome; process start is a structured log on stdout.
- `/help` documents `/start`, `/help`, `/expense`, `/income`, `/balance`.
- Allowlist still applies: unauthorized users get no help text and no ledger data.
- Logging follows current Python practice: **structlog** plus stdlib `logging` (`ProcessorFormatter`) so third-party loggers (PTB, SQLAlchemy) share the same JSON/console output.
- Default destination is **stdout**, not a file.

### Assumptions

- Welcome and help copy can be English, matching current bot replies.
- Command-menu descriptions are short English phrases.
- `LOG_LEVEL` default INFO; `LOG_FORMAT` is `console` | `json`, defaulting to console if stderr is a TTY else json.
- Unauthorized attempts are logged at WARNING with `user_id` and `command` only (no body, no ledger totals).

### Unresolved questions

- Exact wording of welcome and help (must list the commands and syntax).

### Acceptance criteria

- Authorized `/start` replies with a welcome and mentions `/help`.
- Authorized `/help` lists every supported command with its grammar.
- After `uv run python -m income_expense_bot` is up, stdout contains a structured event that the bot is running (timestamp + level + event name).
- Submitting `/expense 12,50 Mercadona` (authorized) produces a structured event with command `expense` and parameters containing `12,50 Mercadona`.
- Unauthorized `/help` or `/start` does not reveal the command list.
- Token is never written to logs.

## Capabilities

### New Capabilities

- `telegram-guidance`: In-chat orientation for the Telegram operator (`/start`, `/help`, command menu).
- `operator-logging`: Structured process and command visibility on stdout.

### Modified Capabilities

- None. Ledger record and balance behavior is unchanged.

## Impact

- `interfaces/telegram` (handlers, dispatch, PTB `post_init` for command menu and ready log).
- Logging configuration in the composition root: **structlog** + stdlib bridge; new runtime dependency `structlog` (via uv).
- Unit tests for `/start` and `/help` text and for captured structured events; no schema or domain model changes.
- README documents `/start`, `/help`, `LOG_LEVEL` / `LOG_FORMAT`, and stdout logging.

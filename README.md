# personal-ops-bots

Personal automation bots. The first bounded context is an income and expense ledger operated from Telegram.

## Income / expense bot

Record cashflow with text commands. Amounts are euros (cents internally). There is no web UI in this version.

### Setup

Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```sh
uv sync
cp .env.example .env
```

Fill `.env`:

| Variable | Meaning |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather |
| `TELEGRAM_ALLOWED_USER_IDS` | Comma-separated Telegram user ids |
| `LEDGER_SQLITE_PATH` | SQLite file path (default `ledger.sqlite`) |
| `LOG_LEVEL` | Log severity (default `INFO`) |
| `LOG_FORMAT` | `json` or `console`. Default: console if stderr is a TTY, otherwise JSON |

```sh
set -a && source .env && set +a
uv run python -m income_expense_bot
```

Logs go to **stdout** as structured events (ISO-8601 UTC timestamp, level, event name, fields). JSON is one object per line. The bot token is never logged. When the process is ready to poll you should see `bot.running`. Each command emits `command.received` (or `command.rejected` if the user is not allowlisted).

### Commands

```
/start
/help
/expense <amount> [<category>] <merchant...>
/income  <amount> [<category>] <source...>
/balance [<start_date>] [<end_date>]
```

`/start` confirms the bot is ready and points you at `/help`. `/help` lists the same commands with syntax. Telegram's command menu is registered on startup.

Amounts accept comma or dot decimals, including cents (`25,2` is 25.20 EUR). Dates are `YYYY-MM-DD`. `/balance` without dates is the current calendar month (`Europe/Madrid`) and shows net plus totals by category.

Examples:

```
/start
/help
/expense 12,50 Mercadona
/expense 89,90 Shopping El Corte Ingles
/expense 25,2 Groceries Mercadona
/income 1800 Salary Company
/balance
/balance 2026-11-06
/balance 2026-11-01 2026-11-30
```

Default category is `Uncategorized`. Default payment method is card (not part of the command).

### Tests and checks

```sh
uv run pytest
uv run ruff check src tests
uv run mypy src/income_expense_bot
```

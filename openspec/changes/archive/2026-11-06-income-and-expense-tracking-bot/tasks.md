# Tasks

## 1. Project skeleton

- [x] 1.1 Add `pyproject.toml` for package `income_expense_bot` under `src/` (Python 3.12+, pytest, pytest-asyncio, mypy, ruff, python-telegram-bot v21+, SQLAlchemy 2, aiosqlite) and verify `uv sync` succeeds
- [x] 1.2 Create packages `src/income_expense_bot/{domain/{model,repository,exception},application/{handler,query},infrastructure/{persistence,read_model},interfaces/telegram}` plus `tests/{unit,integration}` and verify the empty packages import
- [x] 1.3 Add frozen `Config` plus `.env.example` with `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_USER_IDS`, and `LEDGER_SQLITE_PATH`, and verify missing token or empty allowlist fail fast in unit tests

## 2. Domain: money and categories

- [x] 2.1 Implement value object `Money` (cents, comma/dot parse, 0–2 decimals) and verify unit tests cover `25,2`→2520, `0,99`→99, `25.20`→2520, and rejection of `12,345` (`ledger-entries`: Amounts are euro cents)
- [x] 2.2 Implement expense/income category catalogs with longest case-insensitive prefix match and `Uncategorized` fallback, and verify unit tests cover `Food & Drinks`, `Mercadona`→uncategorized, and `Salary` ignored on expense (`ledger-entries`: Category optional; Entry type owns catalog)

## 3. Domain entry, ports, and command handlers

- [x] 3.1 Add `LedgerEntry` (type expense/income, cents, payee, category, payment_method `card`, UTC `occurred_at`) and domain exceptions, and verify unit tests assert recording never produces `transfer` (`ledger-entries`: Single ledger; Default payment method)
- [x] 3.2 Add abstract `LedgerEntryRepository`, `AbstractUnitOfWork`, frozen `RecordExpenseCommand` / `RecordIncomeCommand`, and async handlers that persist inside `async with uow` without returning totals, and verify unit tests with a fake UoW (`ledger-entries`: record expense/income)

## 4. SQLite infrastructure (write)

- [x] 4.1 Implement async engine/session factory (`sqlite+aiosqlite`) and `ledger_entries` mapping (type check, indexes, persistence-free domain classes) and verify an integration test creates the file and table on startup
- [x] 4.2 Implement SQLAlchemy repository + `SqlAlchemyUnitOfWork` and verify an integration test round-trips expense and income with cents, payee, category, `card`, and occurrence time (`ledger-entries`: persist typed entries)

## 5. Balance query

- [x] 5.1 Implement period resolution in `Europe/Madrid`: no dates → current month, one `YYYY-MM-DD` → that day, two dates → inclusive range, invalid format/order → error, and verify unit tests for those cases (`ledger-balance`: Default month; One date; Two dates)
- [x] 5.2 Implement `LedgerBalanceQueryService` plus SQL read model (`SUM`/`GROUP BY`, exclude `transfer`) and verify unit tests for mixed-month and empty-period totals (`ledger-balance`: Balance reports net and category totals)
- [x] 5.3 Add an integration test that inserted entries in/out of range produce the expected cents totals via the query service

## 6. Telegram interface

- [x] 6.1 Parse `/expense` and `/income` text into commands (amount, optional category, greedy payee) and verify unit tests match the spec examples, including missing merchant (`ledger-entries`: record grammars)
- [x] 6.2 Parse `/balance` args (none / one date / two dates) and verify unit tests for valid ISO dates and invalid format `06/11/2026` (`ledger-balance`: date grammars)
- [x] 6.3 Implement allowlist auth on user id and verify unit tests that unauthorized updates do not call handlers or the query service (`ledger-entries` / `ledger-balance`: unauthorized operators)
- [x] 6.4 Wire PTB handlers to command handlers and `LedgerBalanceQueryService` so confirmations include amount and balance replies include period, net, and category totals, and verify tests with fake UoW / stub query (`interfaces` equivalent of API routers)

## 7. Composition root

- [x] 7.1 Wire config, engine, UoW factory, handlers, and query service (composition root analogous to `dependencies.py`) and verify `python -m income_expense_bot` is documented in README
- [x] 7.2 Add README with v1 commands, euro-cent examples, and env vars, and verify the documented commands match the specs

## 8. Cross-cutting checks

- [x] 8.1 Run unit and integration tests and verify they pass
- [x] 8.2 Run mypy and ruff on `src/income_expense_bot` and verify no errors
- [x] 8.3 Grep `domain/` and `application/` and verify they import neither `telegram` nor `sqlalchemy` nor `aiosqlite`

## Workflow follow-up

- Archive the change after implementation is verified.
- Merge delta specs into `openspec/specs/ledger-entries` and `openspec/specs/ledger-balance`.

# Design

## Context

Greenfield repo: no application packages yet. Constraints: Python, hexagonal architecture, CQRS, isolated bot runtime and data. See `proposal.md` for motivation and the ledger specs for behavior.

Layering, CQRS split, async I/O, and test shapes follow the same architectural style as `itx-fullstackengineer-davidalvarezcastro-20260504/backend` (Cosmic Python: domain / application / infrastructure / interfaces). That API is FastAPI + Postgres + a message bus; this bot is Telegram + SQLite and does **not** copy those delivery or scale choices.

## Goals / Non-Goals

**Goals:**

- Same dependency rule: `domain/` has zero framework imports; infrastructure and interfaces depend inward.
- Async from Telegram handlers through persistence (`await` all the way).
- CQRS: command handlers mutate via Unit of Work; query services read a projection and never write.
- SQLite file, integer cents, no currency column; a future web `interfaces/` adapter can reuse the same application/domain.

**Non-Goals:**

- In-process message bus and domain events in v1 (no second aggregate, no reactions).
- Postgres, Alembic, materialized views, FastAPI, httpx outbound clients.
- Shared kernel for future bots.
- Merchant classification engine.

## Decisions

### 1. Package layout (same hexagon as the reference backend)

```
src/income_expense_bot/
  domain/
    model/          # LedgerEntry, Money, Category, PaymentMethod
    repository/     # abstract write repository (port)
    exception/
  application/
    commands.py     # frozen dataclasses
    handler/        # RecordExpense, RecordIncome
    query/          # GetBalance / LedgerBalanceQueryService
    unity_of_work.py
  infrastructure/
    persistence/    # SQLAlchemy repo + table mapping
    database.py     # async engine / session factory
    unity_of_work.py
    read_model/     # SQL aggregation for balance (not the write aggregate)
  interfaces/
    telegram/       # parse, auth, PTB handlers — equivalent to FastAPI routers
  config.py
tests/
  unit/             # domain + fake UoW handlers
  integration/      # handlers/queries against SQLite
```

Driving adapter: `interfaces/telegram`. Driven adapters: `infrastructure/*`. Repository **ports** live in `domain/repository` as ABCs (not Protocols in `application`). Domain does not import SQLAlchemy, Telegram, or httpx.

**Taken from the reference:** `src/` layout, four layers, abstract repository with `seen` only if events appear later, fake UoW in unit tests, integration tests for handlers/queries.

**Not taken:** `MessageBus`, domain `events.py`, Alembic, classical mapping complexity beyond one table, Poetry (this repo can use uv/pip).

**Alternative:** `adapters/telegram` + `adapters/persistence`. Rejected so the bot matches the mental model already used in the supplier API.

### 2. CQRS: command handlers vs query services

Same split as the reference (`application/handler/*` vs `application/query/*`):

- Commands: frozen dataclasses `RecordExpenseCommand`, `RecordIncomeCommand`. Handlers `async def handle(...)` inside `async with uow`. They persist and return nothing (or an id/status). They MUST NOT return period totals.
- After a command, the Telegram interface may load a confirmation DTO; it MUST NOT ask the handler for a balance.
- Query: `LedgerBalanceQueryService` reads a **read model** (SQL `SUM`/`GROUP BY`), not by hydrating `LedgerEntry` aggregates. MUST NOT write. Exclude `type = transfer`.

Telegram controllers dispatch commands to handlers and `/balance` to the query service — the same role FastAPI routers play with `messagebus.handle` vs `CandidateQueryService`.

v1 calls handlers **directly**. A message bus would only pay off when an entry recorded should fan out (Obsidian, notifications). Adding `application/messagebus.py` later does not change specs.

**Alternative:** one `LedgerService`. Rejected: mixes write and read at the application boundary.

### 3. Async Unit of Work

`AbstractUnitOfWork` with `async with`, commit on success, rollback on error, exposing `entries` (write repository). Infrastructure: SQLAlchemy `AsyncSession` via `aiosqlite`.

Telegram is async; the reference stack is async (`AsyncSession`, `asyncpg`, `httpx.AsyncClient`). Sync `sqlite3` + executor would break that grain and complicate tests.

**Alternative:** stdlib `sqlite3` in a thread pool. Rejected: extra sync seam for no gain.

**Alternative:** Postgres + `asyncpg` now. Rejected: personal bot, no web yet. Engine URL is the swap point.

### 4. Persistence: SQLAlchemy 2 async + SQLite, one table

One `ledger_entries` table, mapped so domain dataclasses stay persistence-free (classical mapping or an infrastructure DTO — domain classes MUST NOT subclass `DeclarativeBase`):

- `id`, `type` (`expense` | `income`; check may allow unused `transfer`), `amount_cents`, `payee`, `category`, `payment_method`, `occurred_at` (UTC).

No `currency` column. Indexes on `occurred_at` and `(type, occurred_at)`. `CREATE TABLE IF NOT EXISTS` on startup. No Alembic in v1.

Balance read model: SQL aggregation in `infrastructure/read_model`, analogous to `PotentialSuppliersReadModel`, not `SELECT *` of aggregates.

### 5. Domain model

Frozen/immutable value objects (`Money`, category name, payment method) with invariants in `__post_init__`, plus `LedgerEntry` as the write model. Domain exceptions for invalid amount, missing payee, invalid period. No Telegram types in domain.

`Money` stores `cents: int`. Parse `25,2` / `25.20` in domain. Format `"25,20"` in `interfaces/telegram`.

### 6. Telegram interface: python-telegram-bot, long polling

PTB v21+ Application. Auth: `update.effective_user.id` in `TELEGRAM_ALLOWED_USER_IDS`. Parse text in the interface into commands; longest category match uses domain catalog.

Composition root (`interfaces/telegram` + `config.py`) wires engine, UoW factory, handlers, query service — the equivalent of FastAPI `dependencies.py`.

### 7. Timezone and config

Store `occurred_at` UTC; period boundaries in `Europe/Madrid`. Config: frozen dataclass from env, fail fast (same idea as the reference `Config`). `.env.example`: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_USER_IDS`, `LEDGER_SQLITE_PATH`.

### 8. Tooling

Python ≥ 3.12 managed with **uv** (`uv.lock`, `uv sync`, `uv run`). pytest + pytest-asyncio (`asyncio_mode = auto`), ruff, mypy. Tests: `tests/unit` (domain, fake UoW), `tests/integration` (SQLite handlers/queries). No HTTP e2e suite in v1.

## Risks / Trade-offs

- [SQLAlchemy for one table] → Slightly heavier than raw SQL; keeps the same persistence style as the reference and a clean Postgres swap. Accepted.
- [No message bus] → New reactions later need a bus or extra calls in the interface. Accepted until there is a second listener.
- [Allowlist only] → No per-user ledger isolation.
- [No Alembic] → First real schema change needs a migration tool. Accepted for greenfield SQLite.

## Migration Plan

- Greenfield: `src/income_expense_bot`, `pyproject.toml`, SQLite file created on boot.
- Deploy: bot process + env vars.
- Rollback: stop process; SQLite file remains.

## Open Questions

- Exact wording of Telegram confirmation and error messages (must still include amount, period, net, and category totals where specified).

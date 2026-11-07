# Proposal

## Why

The ledger is only reachable from Telegram text commands. Recategorizing bot entries (often `Uncategorized`) and reviewing the month at a glance is awkward in chat. A small unauthenticated web app plus HTTP API lets the operator see the current month, recent movements, and add/edit/delete entries with a form, while Telegram keeps working on the same SQLite ledger.

## What Changes

- Expose the existing ledger (record expense/income, period balance) over an unauthenticated FastAPI HTTP API.
- Add ledger behaviors that Telegram does not have yet: list recent entries, change an entry (mainly category), and delete an entry.
- Add a Vue 3 SPA: home shows the current calendar month (`Europe/Madrid`) plus the last 8 movements with a way to see more; `+`/`-` open a simple amount-and-category form; entries can be edited and deleted.
- This version has **no authentication**: anyone who can reach the API or SPA may read and mutate the ledger.
- Telegram command syntax, allowlist, and log event shapes stay the same.
- Raspberry Pi Compose/nginx packaging of the SPA is out of scope (local `uvicorn` + Vite is enough). GitHub Actions stay out of scope.

### Confirmed decisions

- Access: no login, token, or allowlist on the web/API in this version.
- UI: SPA (not MPA/SSR). Home is month balance + recent list (Monefy-like capture, not a copy of the donut-only home).
- Stack intent: Vue 3 + Vite SPA (ITX frontend as reference); FastAPI HTTP adapter (ITX backend as reference); same Python hexagonal/CQRS core and SQLite file as the bot.
- Amounts remain euro cents; categories remain the existing expense/income catalogs.
- Entry lists use cursor (keyset) pagination, not limit/offset.

### Assumptions

- `occurred_at` on web creates is “now” (UTC), same as Telegram; no backdating in this version.
- Payment method stays `card`.
- API and bot may run at the same time against one SQLite file (WAL).
- SPA talks to the API over HTTP; CORS allows the Vite origin in development.

### Unresolved questions

- None that change this version’s behavior. Auth and Pi static hosting can be later changes.

### Acceptance criteria

- Unauthenticated `GET` balance for the current month matches `/balance` semantics (period, net, category totals in cents).
- Unauthenticated clients can create expense/income, list recent entries, change category, and delete.
- SPA home shows current-month summary and 8 recent entries, with capture forms and edit/delete.
- Telegram `/expense`, `/income`, and `/balance` still work on the same database.

## Capabilities

### New Capabilities

- `ledger-http-api`: Unauthenticated HTTP API for ledger balance, entry list, create, update, and delete on the income/expense ledger.
- `ledger-web`: Vue SPA for month overview, recent movements, and simple expense/income forms including edit and delete.

### Modified Capabilities

- `ledger-entries`: Operators can list stored entries, change an existing entry (especially category), and delete an entry. Create rules for amount, payee, catalogs, and types stay.

## Impact

- New FastAPI adapter, Vue app (separate frontend tree), application commands/queries for list/update/delete, repository `get`/`remove`.
- Shared SQLite (`LEDGER_SQLITE_PATH`); domain stays framework-free.
- New runtime deps: FastAPI/Uvicorn on Python; Vue toolchain in the frontend package. README for local run.
- No change to Telegram handlers unless they reuse new application services internally.

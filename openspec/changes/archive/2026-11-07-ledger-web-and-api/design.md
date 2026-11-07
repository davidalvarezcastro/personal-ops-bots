# Design

## Context

Telegram is the only adapter. Application layer has record-expense/income commands and a balance query; the repository can only `add`. SQLite lives at `LEDGER_SQLITE_PATH`. See `proposal.md` for motivation; behavior is in the delta specs.

## Goals / Non-Goals

**Goals:**

- FastAPI as a hexagonal HTTP adapter: Pydantic v2 schemas, lifespan-owned async engine, no auth.
- Vue 3 SPA (Vite, Composition API, Vue Router) as a second adapter talking only to that API.
- New application commands/queries for list, recategorize, delete; domain stays free of FastAPI/Vue.
- Same SQLite file as the bot; WAL so both processes can write.

**Non-Goals:**

- Authentication, Telegram Login, or copying the bot allowlist onto HTTP.
- Pi Compose/nginx image for the SPA.
- Backdating `occurred_at`, payment-method UI, charts beyond the month summary, or user accounts.
- Replacing Telegram.

## Decisions

### 1. HTTP adapter inside the existing package

`src/income_expense_bot/interfaces/http/` (app, routers, schemas). Run with `uvicorn income_expense_bot.interfaces.http.app:app`. Telegram module unchanged.

**Alternative:** a second Python package. Rejected: one bounded context, one SQLite, one uv project.

### 2. Resource shape (observable, not UI)

| Method | Path | Notes |
|---|---|---|
| GET | `/api/v1/balance` | `start`, `end` optional `YYYY-MM-DD`; omit both = current Madrid month |
| GET | `/api/v1/entries` | `limit` default 8, max 100; opaque `cursor` for the next older page (omit on first page) |

**Pagination:** keyset cursor, not `offset`. Newest-first plus live Telegram inserts would make offset skip or duplicate rows on “see more”. Dataset is small; stability matters more than index theory. **Alternative:** `limit`/`offset`. Rejected for that reason.
| POST | `/api/v1/entries` | `{type, amount, payee, category?}` amount as decimal string |
| PATCH | `/api/v1/entries/{id}` | at least `{category}`; other fields optional |
| DELETE | `/api/v1/entries/{id}` | 204 or 404 |
| GET | `/api/v1/categories` | `type=expense\|income` |

Money in JSON responses: integer `amount_cents` plus a display string is optional in the SPA only. Create body accepts the same decimal text as Telegram (`12,50`). Errors: 422 validation, 404 missing id, 400 invalid period or illegal category. OpenAPI from FastAPI. CORS: Vite origin in dev (`CORS_ORIGINS` env, default `http://localhost:5173`).

**Alternative:** JSON:API or RPC. Rejected: YAGNI.

### 3. CQRS additions

- Query: list entries (read model / repository read), reuse `LedgerBalanceQueryService`.
- Commands: `ChangeEntryCategoryCommand`, `DeleteLedgerEntryCommand`; reuse record handlers for POST.
- `AbstractLedgerEntryRepository`: `get(id)`, `list_recent(limit, cursor)`, `remove(id)` besides `add`. Keyset: `ORDER BY occurred_at DESC, id DESC` and `WHERE (occurred_at, id) < (cursor_time, cursor_id)`. Cursor is opaque (e.g. base64 of those two fields). Response includes `next_cursor` only when another page exists.
- Domain: `LedgerEntry.change_category(name)` validates `catalog_for(type)`; no FastAPI types.

Handlers return void; HTTP maps not-found/invalid-category exceptions to status codes.

### 4. SQLite

Enable WAL (`PRAGMA journal_mode=WAL`) on the shared engine. One `async_sessionmaker` in FastAPI lifespan (`expire_on_commit=False`); bot process keeps its own engine. Same `LEDGER_SQLITE_PATH`. Keep existing `create_all` on API startup (no Alembic in this change).

### 5. Vue app at `frontend/`

Reference: ITX frontend (Vue 3.5, Vite, Vue Router, Tailwind 4, Vitest, `src/features`). This app is smaller:

- `src/features/ledger/` pages: home, entries list; components: month summary, entry row, capture sheet.
- TanStack Vue Query for server state; no Pinia unless a sheet needs it.
- `fetch` + typed DTOs aligned with OpenAPI; Zod only if it stays thin.
- Routes: `/` home, `/entries` full list. Capture as overlay, not a separate marketing site.
- `VITE_API_BASE_URL` (public, not a secret).

**Alternative:** Nuxt. Rejected: user asked for SPA; ITX is Vite SPA.

**Alternative:** copy Monefy donut-only home. Rejected: recategorize needs a visible list (see `ledger-web` spec).

### 6. No authentication

No middleware, no API keys. Document that the process MUST NOT be published on the public internet in this version.

## Risks / Trade-offs

- [Open HTTP on a reachable network] → README warning; later change can add a token.
- [SQLite writer lock with bot + API] → WAL; keep transactions short.
- [Pi 1 GB if someone builds Vue on-device] → document laptop `pnpm build`; packaging later.
- [Two `create_all` processes] → idempotent; Alembic later if schema actually migrates.

## Migration Plan

- Dev: `uv sync` (FastAPI/uvicorn), `pnpm` in `frontend/`, run API + Vite, optional bot against the same SQLite.
- Rollback: stop API and SPA; bot and existing tables unchanged. Delete is destructive for rows; no extra backup in this change.

## Open Questions

- None that change specs or this task breakdown.

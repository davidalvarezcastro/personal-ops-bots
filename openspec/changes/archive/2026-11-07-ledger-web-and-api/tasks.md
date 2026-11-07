# Tasks

## 1. Domain and application (list, recategorize, delete)

- [x] 1.1 Add `LedgerEntry.change_category` that accepts only the catalog for that entry type, and verify unit tests cover a valid recategorize, rejected `Salary` on an expense, and unchanged amount (`ledger-entries`: change category)
- [x] 1.2 Extend the ledger repository port and SQLAlchemy adapter with `get`, `list_recent` (newest first, skip `transfer`, default limit 8, keyset cursor), and `remove`, and verify persistence tests for default eight, second page via cursor, no duplicates after a newer insert, missing id, and delete (`ledger-entries`: list; cursor)
- [x] 1.3 Add `ChangeEntryCategory` and `DeleteLedgerEntry` command handlers plus a list query service, and verify application tests for recategorize, not-found, illegal category, and delete omitted from a following balance (`ledger-entries`: change category; delete; list)
- [x] 1.4 Enable SQLite WAL on the shared engine helper and verify a unit or smoke test that the connection uses WAL (`ledger-http-api`: concurrent bot+API assumption)

## 2. FastAPI HTTP adapter

- [x] 2.1 Add FastAPI, uvicorn, and httpx (dev) with uv, create `interfaces/http` with lifespan engine, CORS from `CORS_ORIGINS`, no auth middleware, and verify `GET /api/v1/balance` with no dates and no credentials returns the current Madrid month (`ledger-http-api`: no credentials; balance period)
- [x] 2.2 Implement `GET /api/v1/entries` (`limit` default 8, opaque `cursor`, `next_cursor`) and `GET /api/v1/categories`, and verify HTTP tests for default page, second page via cursor, omitted cursor on the last page, transfers omitted, and category catalogs by type (`ledger-http-api`: list; cursor)
- [x] 2.3 Implement `POST /api/v1/entries` using existing record handlers and Telegram amount parsing, and verify 201 for `12,50` Groceries/Mercadona, 400/422 for empty payee, and no auth header required (`ledger-http-api`: record; no credentials)
- [x] 2.4 Implement `PATCH` and `DELETE /api/v1/entries/{id}`, and verify recategorize keeps amount, 404 for unknown id, and deleted cents disappear from current-month balance (`ledger-http-api`: change category; delete)
- [x] 2.5 Document local `uvicorn` in README (no login, do not expose publicly) and verify the documented module path matches the app object (`ledger-http-api`: no credentials)

## 3. Vue SPA

- [x] 3.1 Scaffold `frontend/` (Vue 3, Vite, Vue Router, Tailwind, Vitest, TanStack Query) with `VITE_API_BASE_URL`, and verify `pnpm test` and `pnpm build` succeed on the empty shell
- [x] 3.2 Build home: current-month summary (income, expense, net, by category) and eight recent rows, and verify a component/page test for November empty zeros and for eight-row list (`ledger-web`: home)
- [x] 3.3 Add “see more” / entries route that loads further pages via `next_cursor`, and verify a test that older rows appear without duplicating the first eight (`ledger-web`: longer list)
- [x] 3.4 Add expense and income capture sheets (amount, payee, type catalog) that POST then refresh home, and verify tests for grocery save and income catalog excluding `Groceries` (`ledger-web`: forms)
- [x] 3.5 Add edit (category) and confirm-delete from a row, and verify tests for Uncategorized → Transport and row gone after confirm (`ledger-web`: edit and delete)
- [x] 3.6 Document `pnpm dev` + API base URL in README and verify the SPA has no login route (`ledger-web`: no login)

## 4. Integration checks

- [x] 4.1 Run `uv run pytest` and verify all tests pass, including existing Telegram tests
- [x] 4.2 Run `uv run ruff check src tests` and verify no errors
- [x] 4.3 Run `pnpm test` (and type-check if configured) in `frontend/` and verify success

## Workflow follow-up

- Archive the change after implementation is verified.
- Merge delta specs into `openspec/specs/ledger-entries`, `ledger-http-api`, and `ledger-web`.
- A later change can add authentication and Pi static hosting.

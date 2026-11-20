# Proposal

## Why

Wallet and travel spend is not always EUR, but `/expense` and `/income` treat every amount as euro cents. The operator needs to tag a currency immediately after the amount (`/expense 65 €`) so the ledger, HTTP API, and web summary keep currencies separate instead of mixing them.

## What Changes

- Parse an optional currency **immediately after the amount** on expense and income (Telegram, HTTP, web). Omitted currency is **EUR**.
- Accept a closed table of **ISO 4217 codes** (case-insensitive) and their **symbols** (`€`, `$`, `£`, `¥`, `CN¥`). Words such as EURO, DOLLAR, RMB are out of scope. Unknown tokens are not currency (they stay category/payee) unless they look like a currency and fail the table — then reject.
- Persist ISO code on each entry with the amount in that currency's **minor units** (EUR/USD/GBP/CNY: 2 fraction digits; JPY: 0). No FX conversion.
- **BREAKING** (HTTP + Telegram `/balance` + web home): totals are **per currency**. Never add EUR minor units to USD/JPY.
- Existing SQLite rows without a currency become EUR.
- `/help` grammar includes the optional currency.

**Confirmed:** default EUR; store ISO + native amount; split balance by currency; all three surfaces.

**Assumed:** catalog is EUR, USD, GBP, JPY, CNY; `¥` → JPY, `CN¥` → CNY, `$` → USD, `£` → GBP; optional space (`65 €` and `65€`).

**Out of scope:** FX rates, changing currency on an existing entry, extra ISO codes, descriptive names (EURO, DOLLAR).

## Capabilities

### New Capabilities

- None. Currency is part of recording and summarizing ledger amounts.

### Modified Capabilities

- `ledger-entries`: amount grammar, stored currency, minor-unit rules
- `ledger-balance`: period totals split by currency
- `ledger-http-api`: create/list/balance expose currency; create accepts optional currency
- `ledger-web`: capture, list, and month summary show and send currency
- `telegram-guidance`: `/help` syntax includes optional currency after amount

## Impact

- Domain: `Money` carries currency; `LedgerEntry` persists ISO; commands/queries include currency.
- SQLite: new `currency` column; existing files need a compatible schema bump (no Alembic yet).
- Telegram parser, confirmations, `/balance` text, `/help`.
- HTTP JSON shape for balance and entry resources.
- Vue types, formatters, capture form, month summary.
- Tests: parser, money exponents, balance grouping, HTTP, Vue.

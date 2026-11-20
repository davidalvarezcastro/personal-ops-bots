# Proposal

## Why

Bare `¥` currently stores Japanese yen, which collides with everyday Chinese yuan spend. The operator wants yen only when they write `JPY` or `JP¥`, and yuan when they write `¥`, `RMB`, `CNY`, or `CN¥`.

## What Changes

- **BREAKING:** Token `¥` (including attached `65¥`) MUST resolve to `CNY`, not `JPY`.
- Japanese yen tokens: `JPY` and `JP¥` only. Stored ISO remains `JPY` (exponent 0).
- Chinese yuan tokens: `¥`, `RMB` (case-insensitive), `CNY`, `CN¥`. Stored ISO remains `CNY` (exponent 2).
- Telegram, HTTP optional `currency` field, and README/help examples MUST use this mapping. Vue capture still offers ISO codes; typing `RMB` or `JP¥` in HTTP/Telegram is enough.
- Existing SQLite rows keep their stored ISO; this change does not rewrite `JPY` rows that were recorded from `¥`.

**Confirmed:** closed catalog stays EUR, USD, GBP, JPY, CNY. No FX. No extra ISO codes.

**Assumed:** `RMB` is an input alias only (never stored); `JP¥` is a symbol, not a stored code.

## Capabilities

### New Capabilities

- None

### Modified Capabilities

- `ledger-entries`: yen/yuan token mapping on optional currency after amount
- `ledger-http-api`: HTTP `currency` accepts the same aliases (`RMB`, `JP¥`, `¥`)

## Impact

- Domain catalog in `backend/src/income_expense_bot/domain/model/currency.py` and unit/parser tests that treat `¥` as JPY
- HTTP `currency_or_default` via the same resolver
- README / `/help` examples that list `¥` as yen
- No schema or balance-query change

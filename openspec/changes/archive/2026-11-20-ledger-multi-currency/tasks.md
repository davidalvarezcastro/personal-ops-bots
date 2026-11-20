# Tasks

## 1. Domain money and catalog

- [x] 1.1 Add a closed currency catalog (EUR, USD, GBP, JPY, CNY with symbols `€` `$` `£` `¥` `CN¥`) and verify unit tests resolve ISO and symbols, reject `INR`, and treat `¥` as JPY (`ledger-entries`: optional currency)
- [x] 1.2 Extend `Money.parse` with currency exponent (2 vs 0) and verify `25,2` → 2520 EUR, `65` JPY → 65, and `65,50 JPY` is invalid (`ledger-entries`: fraction digits)
- [x] 1.3 Store ISO on `LedgerEntry` / record commands (default EUR) and verify record-expense unit tests keep EUR when currency is omitted

## 2. Telegram parse, help, and confirmations

- [x] 2.1 Parse `/expense` and `/income` with optional currency after amount (`65 €`, `65€`, `12,50 USD`) and verify parser tests plus INR rejection (`ledger-entries`: optional currency; category after currency)
- [x] 2.2 Update confirmations and `/help` grammar to show optional currency after amount and verify guidance/readme tests (`telegram-guidance`: help lists currency)

## 3. SQLite column

- [x] 3.1 Add `currency` VARCHAR(3) NOT NULL DEFAULT `EUR` and an ALTER path when the column is missing, then verify integration against a ledger table created without `currency` still reads old rows as EUR

## 4. Balance, HTTP, and read models

- [x] 4.1 Group balance totals by currency (never mix) and verify unit/integration: EUR-only month, empty period as EUR zeros, EUR+USD split (`ledger-balance`: net and category totals)
- [x] 4.2 Expose `currency` on HTTP entry list/create (optional body field, default EUR) and a `currencies` array on balance, then verify HTTP tests for default EUR create, USD create, and split balance (`ledger-http-api`)

## 5. Web

- [x] 5.1 Add currency to entry types, default EUR on capture, format amounts per ISO, and show month totals per currency; verify Vue tests for grocery save in EUR and a mixed-currency summary (`ledger-web`)

## 6. Integration checks

- [x] 6.1 From `backend/`, run `uv run pytest` and verify the suite passes
- [x] 6.2 From `backend/`, run `uv run ruff check src tests` and `uv run mypy src/income_expense_bot` and verify no errors
- [x] 6.3 From `frontend/`, run `pnpm test` and verify the suite passes

## Workflow follow-up

- Archive the change after review.
- Rebuild and push GHCR so the Pi ALTER runs on bot start.

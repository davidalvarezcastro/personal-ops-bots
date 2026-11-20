# Tasks

## 1. Domain catalog

- [x] 1.1 Map JPY symbols to `JP¥` only, CNY symbols to `¥` and `CN¥`, and alias `RMB` → `CNY`; verify unit tests (`test_currency.py`) for `JPY`/`JP¥` → JPY, `¥`/`rmb`/`CNY`/`CN¥` → CNY, and `INR` still rejected (`ledger-entries`)

## 2. Telegram and HTTP

- [x] 2.1 Parse `/expense 65 JP¥ Konbini` as JPY, `/expense 65 ¥ Shop` and `/expense 12,50 RMB Shop` as CNY (including attached `65¥`); verify parser tests (`ledger-entries`)
- [x] 2.2 Accept HTTP `currency` `RMB` storing `CNY`; verify HTTP test (`ledger-http-api`)
- [x] 2.3 Update README and `/help` examples so `¥` is yuan and yen is `JPY`/`JP¥`; verify guidance/readme tests

## 3. Integration checks

- [x] 3.1 From `backend/`, run `uv run pytest` and verify the suite passes
- [x] 3.2 From `backend/`, run `uv run ruff check src tests` and `uv run mypy src/income_expense_bot` and verify no errors

## Workflow follow-up

- Archive the change after review.

# Proposal

## Why

There is no lightweight way to record personal income and expenses as fast text from Telegram, in the style of Monefy but without a mobile UI. This change introduces a standalone personal ledger bot so daily cashflow can be captured now, with a data model that can later feed a web view without rewriting the domain.

## What Changes

- Add an independently deployable Telegram bot that records **expenses** and **income** and shows a **period balance**.
- Persist every movement in a **single ledger** of entries (not separate income/expense stores).
- Commands:
  - `/expense <amount> [<category>] <merchant...>`
  - `/income <amount> [<category>] <source...>`
  - `/balance [<start_date>] [<end_date>]`
- Amounts are euros in v1, parsed with cents (`25,2` → 25.20 EUR), stored as integer cents.
- Optional category; omitted category is `Uncategorized`. No merchant-to-category rules in this change.
- Merchant/source is the remainder of the message (spaces allowed).
- `/balance` with no dates covers the **current month**, and returns **net total plus totals by category**.
- Payment method is stored as `card` by default and is **not** part of the command grammar.
- Entry `type` includes `expense` and `income`. `transfer` is reserved in the model and has **no** Telegram command in this change.

Out of scope: web UI, FX/multi-currency, merchant classification rules, `/transfer`, `/list` of movements, accounts/wallets.

### Confirmed decisions

- One bounded context / one bot / one ledger table with a `type` column.
- Default category `Uncategorized`; merchant rules deferred.
- Default `/balance` period is the current calendar month.
- `/balance` shows net (income − expense) and a category breakdown.
- Commerce/source is the last (greedy) parameter.
- v1 amounts are always euros; no currency token and no currency column.
- Internal amount is integer cents.
- Default payment method `card`, not in the command.

### Assumptions

- `/balance` with one date means that calendar day; with two dates means an inclusive range.
- Period boundaries use timezone `Europe/Madrid`.
- Balance dates in the command use `YYYY-MM-DD`.
- Only allowlisted Telegram user IDs may mutate or read the ledger.
- Category names are matched case-insensitively; expense and income catalogs are distinct except for shared `Uncategorized`.
- Transfers, when added later, must not affect net income − expense.

### Unresolved questions

- Exact Telegram library (delivery adapter only; does not change observable ledger behavior).
- Copy/formatting of bot replies (as long as amount, period, net, and per-category totals are present).

### Acceptance criteria

- An authorized user can record an expense and an income from Telegram with the grammars above.
- `25,2` is stored as 2520 cents and shown as euros with cents.
- Omitting category stores `Uncategorized`.
- `/balance` without dates summarizes the current month with net and per-category totals.
- Unauthorized users cannot record or read entries.
- Domain logic has no dependency on Telegram, HTTP, or a specific database driver.

## Capabilities

### New Capabilities

- `ledger-entries`: Recording personal ledger entries (expense and income) with amount in euro cents, payee/source, category, payment method, and occurrence time.
- `ledger-balance`: Querying net cashflow and category totals for a date period.

### Modified Capabilities

- None. The project has no existing specs.

## Impact

- Greenfield Python service under this repo: new bot package, tests, and local persistence. No existing application code to modify.
- New runtime dependencies for Telegram delivery and SQL persistence (chosen in design). Isolated credentials, database, and process; no shared models with future bots.
- Future web UI is expected to read the same ledger port; this change does not add HTTP APIs.

# Design

## Context

See `proposal.md` for motivation. Today `Money` is only `cents`, the parser takes `tokens[0]` as a euro amount, SQLite has `amount_cents` with no currency, and `/balance` plus HTTP/web sum a single net. Hexagonal CQRS stays; this change extends the money value object and read models.

## Goals / Non-Goals

**Goals:**

- Domain `Money` is `(minor_units, currency)` with a closed catalog and exponent per ISO.
- Telegram, HTTP, and Vue share the same catalog and parse rules.
- SQLite on the Pi gains a `currency` column without wiping `data/ledger.sqlite`.
- Keep the `amount_cents` column name as integer minor units (JPY yen, EUR cents) to avoid a table rewrite.

**Non-Goals:**

- Alembic, FX, extra ISO codes, renaming JSON `amount_cents` to `amount_minor`.

## Decisions

### 1. Closed catalog in domain

`domain/model/currency.py`: ISO → exponent (0 or 2) and symbols. Resolve token case-insensitively. `$`/`£`/`€`/`¥`/`CN¥` map as in the proposal. A 3-letter alphabetic token after the amount is always a currency attempt: in catalog → use it; otherwise `InvalidCurrencyError`. Other tokens go to category/payee.

**Alternative:** accept any ISO 4217 via a library. Rejected: unknown exponents and `$` ambiguity; YAGNI.

### 2. Parse amount then currency

`Money.parse(amount_text, currency="EUR")` applies exponent. Telegram: split first token so `65€` works; else consume second token if it is a currency attempt. Then `split_category_and_payee` on the rest.

HTTP/web: `amount` stays decimal text; optional `currency` field (ISO or symbol), default EUR. Do not require the suffix inside `amount` on HTTP.

### 3. Persistence

Column `currency` `String(3) NOT NULL DEFAULT 'EUR'`. After `create_all`, if the live table lacks `currency`, `ALTER TABLE ledger_entries ADD COLUMN currency VARCHAR(3) NOT NULL DEFAULT 'EUR'`. Existing rows read as EUR.

Commands grow `currency: str`. `LedgerEntry` stores it. Queries group by `currency`.

### 4. Balance JSON (breaking)

Replace the single `income_cents`/`expense_cents`/`net_cents` object with:

```json
{
  "start": "...",
  "end": "...",
  "currencies": [
    {
      "currency": "EUR",
      "income_cents": 0,
      "expense_cents": 0,
      "net_cents": 0,
      "expense_by_category": [],
      "income_by_category": []
    }
  ]
}
```

Empty period: one EUR zero group. Telegram `/balance` prints one block per currency. Vue `MonthSummary` iterates `currencies`. Entry resources add `"currency": "EUR"`.

**Alternative:** keep top-level EUR totals plus extras. Rejected: silent wrong nets.

### 5. Display

Confirmations and lists use ISO (and symbol optional). JPY: no `,00`. EUR: keep `12,50 EUR`.

## Risks / Trade-offs

- [Pi SQLite without ALTER] → Startup `ensure_currency_column`; test against a table created without the column.
- [INR-like 3-letter payee] → `/expense 10 Bob Shop` is fine (`Bob` is not 3 letters); `/expense 10 INR Shop` is rejected by spec. Accept that cost.
- [Clients of GET /api/v1/balance] → Only the Vue app; update it in the same change.
- [`$` is USD only] → CAD/AUD must use ISO.

## Migration Plan

1. Domain catalog + Money + entry field; unit tests.
2. Parser, commands, ORM column + ALTER; integration on a pre-column DB file.
3. Balance query + Telegram format + HTTP schemas; Vue form and summary.
4. Deploy: rebuild GHCR; Pi pull. `create_schema` + ALTER on bot start.

Rollback: revert image; column can remain unused.

## Open Questions

None.

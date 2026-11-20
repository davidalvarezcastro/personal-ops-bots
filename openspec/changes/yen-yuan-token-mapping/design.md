# Design

## Context

See `proposal.md`. Resolver lives in `domain/model/currency.py`: `CurrencySpec.symbols` plus `BY_CODE`. Today JPY owns `¥` and CNY owns `CN¥`. `resolve_currency_token` treats any other 3-letter alphabetic token as a failed currency attempt (`INR`). HTTP uses the same helper via `currency_or_default`. `split_amount_token` matches suffixes longest-first.

## Goals / Non-Goals

**Goals:**

- One domain mapping shared by Telegram parse and HTTP `currency`.
- Store ISO only (`JPY`, `CNY`); never persist `RMB` or `JP¥`.

**Non-Goals:**

- Rewriting existing `JPY` rows, Vue ISO dropdown labels, FX, extra ISO codes.

## Decisions

### 1. Aliases in the domain catalog

Keep `SPECS` as stored ISO + exponent. Put `JP¥` on JPY symbols; put `¥` and `CN¥` on CNY symbols. Add a small case-insensitive alias map `RMB` → `CNY` consulted after symbols and before `BY_CODE` / the 3-letter reject path.

**Alternative:** treat `RMB` as a sixth stored code. Rejected: balances would split CNY vs RMB.

### 2. Longest suffix still wins

`JP¥` and `CN¥` are longer than `¥`, so `65JP¥` is JPY and `65¥` / `65CN¥` are CNY. No parser grammar change.

### 3. Vue stays ISO-only

Capture sheet keeps EUR/USD/GBP/JPY/CNY. Telegram and HTTP accept the extra tokens.

## Risks / Trade-offs

- [`/expense 65 ¥ Konbini` becomes CNY] → Breaking; tests and README must switch yen examples to `JPY`/`JP¥`.
- [`RMB` occupies the 3-letter currency slot] → Intentional; `INR` still rejected.

## Migration Plan

1. Update catalog, unit tests, parser tests, HTTP RMB create test, README/help examples.
2. Deploy with the rest of the multi-currency image; no SQLite ALTER.

Rollback: revert image. Stored ISO values stay valid.

## Open Questions

None.

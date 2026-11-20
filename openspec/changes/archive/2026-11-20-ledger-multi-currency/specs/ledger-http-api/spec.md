# Spec Delta

## MODIFIED Requirements

### Requirement: HTTP balance matches Telegram period rules
When a client requests a balance over HTTP with no dates, one `YYYY-MM-DD` date, or two dates, the system SHALL return the same period bounds and the same per-currency income, expense, net, and category totals as `/balance` would for those arguments (`Europe/Madrid`, integer minor units, no mixing currencies, no `transfer` rows).

#### Scenario: Default month
- **WHEN** a client requests HTTP balance with no dates during November 2026
- **THEN** the payload period is 2026-11-01 through 2026-11-30 inclusive and totals include only entries in that period, grouped by currency

#### Scenario: Invalid range
- **WHEN** a client requests HTTP balance with start after end
- **THEN** the system MUST NOT return totals and MUST respond that the date range is invalid

### Requirement: HTTP can list ledger entries newest first
The system SHALL list stored expense and income entries over HTTP, newest occurrence first, excluding `transfer` rows. The client MAY pass a positive page size; when omitted the page size MUST be 8. Each item MUST include id, type, amount in minor units, currency ISO code, payee, category, payment method, and occurrence time.

#### Scenario: Default page
- **GIVEN** twelve persisted expenses with distinct occurrence times
- **WHEN** a client lists entries over HTTP with no page size and no cursor
- **THEN** the response contains the eight newest expenses in descending occurrence order

#### Scenario: Transfers omitted
- **GIVEN** a stored `transfer` row and an expense
- **WHEN** a client lists entries over HTTP
- **THEN** the transfer is absent and the expense is present

### Requirement: HTTP can record expense and income
The system SHALL persist an expense or income over HTTP when the body includes type, a valid amount, a non-empty payee or source, and a category allowed for that type (or omit category to store `Uncategorized`). Amount parsing MUST match Telegram (comma or dot, fraction digits allowed for that currency). Currency MAY be an ISO code or catalog symbol; when omitted it MUST be `EUR`.

#### Scenario: Expense created
- **WHEN** a client posts type `expense`, amount `12,50`, payee `Mercadona`, and category `Groceries`
- **THEN** the system stores 1250 EUR minor units, currency `EUR`, payee `Mercadona`, category `Groceries`, type `expense`, payment method `card`

#### Scenario: Expense created in USD
- **WHEN** a client posts type `expense`, amount `12,50`, currency `USD`, payee `Starbucks`, and category `Food & Drinks`
- **THEN** the system stores 1250 USD minor units and currency `USD`

#### Scenario: Missing payee rejected
- **WHEN** a client posts type `expense` and amount `10` with an empty payee
- **THEN** the system MUST NOT persist an entry and MUST notify that merchant is required

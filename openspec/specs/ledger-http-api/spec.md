# ledger-http-api Specification

## Purpose

Lets any caller read and change the income/expense ledger over HTTP without presenting credentials, using the same period and money rules as the Telegram bot.

## Requirements

### Requirement: HTTP callers need no credentials
The HTTP ledger API MUST accept read and write requests without authentication or an operator allowlist.

#### Scenario: Balance without credentials
- **WHEN** a client requests the current-month balance over HTTP with no auth header or cookie
- **THEN** the system returns the balance payload and MUST NOT require a login

#### Scenario: Create without credentials
- **WHEN** a client submits a valid new expense over HTTP with no auth header or cookie
- **THEN** the system persists the expense

### Requirement: HTTP balance matches Telegram period rules
When a client requests a balance over HTTP with no dates, one `YYYY-MM-DD` date, or two dates, the system SHALL return the same period bounds, income, expense, net, and category totals as `/balance` would for those arguments (`Europe/Madrid`, integer cents, no `transfer` rows).

#### Scenario: Default month
- **WHEN** a client requests HTTP balance with no dates during November 2026
- **THEN** the payload period is 2026-11-01 through 2026-11-30 inclusive and totals include only entries in that period

#### Scenario: Invalid range
- **WHEN** a client requests HTTP balance with start after end
- **THEN** the system MUST NOT return totals and MUST respond that the date range is invalid

### Requirement: HTTP can list ledger entries newest first
The system SHALL list stored expense and income entries over HTTP, newest occurrence first, excluding `transfer` rows. The client MAY pass a positive page size; when omitted the page size MUST be 8. Each item MUST include id, type, amount in cents, payee, category, payment method, and occurrence time.

#### Scenario: Default page
- **GIVEN** twelve persisted expenses with distinct occurrence times
- **WHEN** a client lists entries over HTTP with no page size and no cursor
- **THEN** the response contains the eight newest expenses in descending occurrence order

#### Scenario: Transfers omitted
- **GIVEN** a stored `transfer` row and an expense
- **WHEN** a client lists entries over HTTP
- **THEN** the transfer is absent and the expense is present

### Requirement: HTTP continues an entry list with a cursor
The system SHALL continue a list using an opaque cursor from the previous page, not a numeric offset. A request that sends that cursor MUST return older entries and MUST NOT repeat the previous page. When no older entries remain, the response MUST omit a next cursor.

#### Scenario: Second page via cursor
- **GIVEN** twelve persisted expenses with distinct occurrence times
- **WHEN** a client lists entries with no cursor, then lists again with the returned cursor
- **THEN** the second page contains older expenses that were not on the first page

#### Scenario: Last page has no cursor
- **GIVEN** three persisted expenses
- **WHEN** a client lists entries over HTTP with no cursor
- **THEN** the response omits a next-page cursor

### Requirement: HTTP can record expense and income
The system SHALL persist an expense or income over HTTP when the body includes type, a valid euro amount, a non-empty payee or source, and a category allowed for that type (or omit category to store `Uncategorized`). Amount parsing MUST match Telegram (comma or dot, at most two fractional digits, stored as cents).

#### Scenario: Expense created
- **WHEN** a client posts type `expense`, amount `12,50`, payee `Mercadona`, and category `Groceries`
- **THEN** the system stores 1250 cents, payee `Mercadona`, category `Groceries`, type `expense`, payment method `card`

#### Scenario: Missing payee rejected
- **WHEN** a client posts type `expense` and amount `10` with an empty payee
- **THEN** the system MUST NOT persist an entry and MUST notify that merchant is required

### Requirement: HTTP can change an entry category
The system SHALL update a persisted entry's category over HTTP when the id exists and the new category is allowed for that entry's type. Other fields MAY be updated in the same request only when supplied; omitted fields MUST stay unchanged.

#### Scenario: Recategorize uncategorized expense
- **GIVEN** an expense id whose category is `Uncategorized`
- **WHEN** a client sets that entry's category to `Groceries` over HTTP
- **THEN** the stored category is `Groceries` and amount and payee are unchanged

#### Scenario: Unknown id
- **WHEN** a client updates a ledger id that does not exist
- **THEN** the system MUST NOT create an entry and MUST notify that the entry was not found

### Requirement: HTTP can delete an entry
The system SHALL remove a persisted expense or income over HTTP when the id exists. After deletion the entry MUST NOT appear in lists or balance totals.

#### Scenario: Delete then balance
- **GIVEN** an expense of 500 cents in the current month
- **WHEN** a client deletes that entry over HTTP
- **THEN** a current-month balance no longer includes those 500 cents

#### Scenario: Delete unknown id
- **WHEN** a client deletes a ledger id that does not exist
- **THEN** the system MUST notify that the entry was not found

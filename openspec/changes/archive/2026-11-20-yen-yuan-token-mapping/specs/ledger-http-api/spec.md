# Spec Delta

## MODIFIED Requirements

### Requirement: HTTP can record expense and income
The system SHALL persist an expense or income over HTTP when the body includes type, a valid amount, a non-empty payee or source, and a category allowed for that type (or omit category to store `Uncategorized`). Amount parsing MUST match Telegram (comma or dot, fraction digits allowed for that currency). Currency MAY be an ISO code, catalog symbol, or listed alias (`RMB`, `JP¥`, `¥`); when omitted it MUST be `EUR`. Aliases MUST store the matching ISO code.

#### Scenario: Expense created
- **WHEN** a client posts type `expense`, amount `12,50`, payee `Mercadona`, and category `Groceries`
- **THEN** the system stores 1250 EUR minor units, currency `EUR`, payee `Mercadona`, category `Groceries`, type `expense`, payment method `card`

#### Scenario: Expense created in USD
- **WHEN** a client posts type `expense`, amount `12,50`, currency `USD`, payee `Starbucks`, and category `Food & Drinks`
- **THEN** the system stores 1250 USD minor units and currency `USD`

#### Scenario: Expense created with RMB
- **WHEN** a client posts type `expense`, amount `12,50`, currency `RMB`, payee `Shop`, and category `Shopping`
- **THEN** the system stores 1250 CNY minor units and currency `CNY`

#### Scenario: Missing payee rejected
- **WHEN** a client posts type `expense` and amount `10` with an empty payee
- **THEN** the system MUST NOT persist an entry and MUST notify that merchant is required

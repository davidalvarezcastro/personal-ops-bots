# ledger-balance Specification

## Purpose

Summarizes recorded income and expenses for a date period so the operator can see net cashflow and spend by category.

## Requirements

### Requirement: Default balance is the current calendar month
When an authorized operator requests a balance with no dates, the system SHALL summarize entries whose occurrence date falls in the current calendar month in timezone `Europe/Madrid`.

#### Scenario: Balance without dates
- **WHEN** an authorized operator submits `/balance` during November 2026
- **THEN** the summary period is 2026-11-01 through 2026-11-30 inclusive

### Requirement: One date selects a single day
When an authorized operator requests a balance with exactly one `YYYY-MM-DD` date, the system SHALL summarize entries whose occurrence date equals that day in timezone `Europe/Madrid`.

#### Scenario: Balance for one day
- **WHEN** an authorized operator submits `/balance 2026-11-06`
- **THEN** the summary period is 2026-11-06 through 2026-11-06 inclusive

### Requirement: Two dates select an inclusive range
When an authorized operator requests a balance with two `YYYY-MM-DD` dates, the system SHALL summarize entries whose occurrence date falls from the first date through the second date inclusive in timezone `Europe/Madrid`.

#### Scenario: Balance for a range
- **WHEN** an authorized operator submits `/balance 2026-11-01 2026-11-15`
- **THEN** the summary period is 2026-11-01 through 2026-11-15 inclusive

#### Scenario: Invalid date order
- **WHEN** an authorized operator submits `/balance 2026-11-15 2026-11-01`
- **THEN** the system MUST NOT return a summary and MUST notify that the date range is invalid

#### Scenario: Invalid date format
- **WHEN** an authorized operator submits `/balance 06/11/2026`
- **THEN** the system MUST NOT return a summary and MUST notify that the date is invalid

### Requirement: Balance reports net and category totals
The system SHALL return, for the selected period: total income in cents, total expense in cents, net (income minus expense), expense totals grouped by category, and income totals grouped by category. Amounts MUST be exact integer-cent sums. Entries of type `transfer` MUST NOT be included in these totals.

#### Scenario: Month with mixed entries
- **GIVEN** the current month contains income of 180000 cents in `Salary` and expenses of 2000 cents in `Groceries` and 500 cents in `Uncategorized`
- **WHEN** an authorized operator submits `/balance`
- **THEN** the system reports income 180000 cents, expense 2500 cents, net 177500 cents, expense `Groceries` 2000, expense `Uncategorized` 500, and income `Salary` 180000

#### Scenario: Empty period
- **WHEN** an authorized operator requests a balance for a period with no entries
- **THEN** the system reports income 0, expense 0, net 0, and empty category totals

### Requirement: Unauthorized operators cannot read balances
The system SHALL reject balance requests from operators who are not allowlisted and MUST NOT reveal ledger totals.

#### Scenario: Unknown operator balance
- **WHEN** an operator who is not allowlisted submits `/balance`
- **THEN** the system MUST NOT return income, expense, or net totals

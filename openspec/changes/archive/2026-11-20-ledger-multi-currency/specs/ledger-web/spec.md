# Spec Delta

## MODIFIED Requirements

### Requirement: Home shows current month and recent entries
When the operator opens the app's home view with no extra navigation, the system SHALL show the current calendar month summary (`Europe/Madrid`) including, per currency, income, expense, net, and totals by category, and SHALL show the eight most recent ledger entries with type, amount, currency, payee, and category.

#### Scenario: Open home in November
- **WHEN** the operator opens the home view during November 2026
- **THEN** the visible period is November 2026 and the list shows up to eight newest entries

#### Scenario: Empty ledger
- **WHEN** the operator opens home with no stored entries
- **THEN** the summary shows a EUR group with zero income, expense, and net, and the recent list is empty rather than an error

### Requirement: Operator can record expense and income from forms
The system SHALL provide distinct expense and income capture flows. Each MUST collect amount, optional currency (default EUR), payee or source, and an optional category from that type's catalog. On success the new entry MUST appear in the recent list and the month summary MUST include it in that currency's totals.

#### Scenario: Save grocery expense
- **WHEN** the operator opens expense capture, enters `12,50`, payee `Mercadona`, category `Groceries`, leaves currency as EUR, and saves
- **THEN** home lists a `Groceries` expense of 12,50 EUR for Mercadona and the EUR month expense total increases by 1250 minor units

#### Scenario: Income capture uses income categories
- **WHEN** the operator opens income capture
- **THEN** the category choices are the income catalog and MUST NOT list expense-only names such as `Groceries`

# Spec Delta

## Purpose

Gives the operator a single-page web app to see this month's cashflow and recent movements, and to add, recategorize, or delete ledger entries without signing in.

## ADDED Requirements

### Requirement: Home shows current month and recent entries
When the operator opens the app's home view with no extra navigation, the system SHALL show the current calendar month summary (`Europe/Madrid`) including income, expense, net, and totals by category, and SHALL show the eight most recent ledger entries with type, amount, payee, and category.

#### Scenario: Open home in November
- **WHEN** the operator opens the home view during November 2026
- **THEN** the visible period is November 2026 and the list shows up to eight newest entries

#### Scenario: Empty ledger
- **WHEN** the operator opens home with no stored entries
- **THEN** the summary shows zero income, expense, and net, and the recent list is empty rather than an error

### Requirement: Operator can open a longer entry list
The system SHALL provide a control on home that loads older movements using the list cursor from the first eight, not a numeric offset.

#### Scenario: See more
- **GIVEN** home is showing eight of twelve entries
- **WHEN** the operator chooses to see more entries
- **THEN** the remaining older entries become visible and the original eight are not duplicated

### Requirement: Operator can record expense and income from forms
The system SHALL provide distinct expense and income capture flows. Each MUST collect amount, payee or source, and an optional category from that type's catalog. On success the new entry MUST appear in the recent list and the month summary MUST include it.

#### Scenario: Save grocery expense
- **WHEN** the operator opens expense capture, enters `12,50`, payee `Mercadona`, category `Groceries`, and saves
- **THEN** home lists a `Groceries` expense of 12,50 EUR for Mercadona and the month expense total increases by 1250 cents

#### Scenario: Income capture uses income categories
- **WHEN** the operator opens income capture
- **THEN** the category choices are the income catalog and MUST NOT list expense-only names such as `Groceries`

### Requirement: Operator can edit and delete a listed entry
From a listed entry the operator SHALL be able to change its category (and other editable fields the form exposes) and SHALL be able to delete it after confirmation. After delete the entry MUST disappear from the list and from the month summary.

#### Scenario: Recategorize from the list
- **GIVEN** a listed expense with category `Uncategorized`
- **WHEN** the operator sets its category to `Transport` and saves
- **THEN** the list shows `Transport` for that row and category totals reflect the change

#### Scenario: Delete confirmed
- **GIVEN** a listed expense
- **WHEN** the operator confirms deletion
- **THEN** that row is gone from the list

### Requirement: Web app does not require a login
The SPA MUST load and perform balance, list, create, update, and delete actions without asking the operator for a username, password, or token.

#### Scenario: First visit
- **WHEN** the operator opens the app with an empty browser store
- **THEN** home loads ledger data without a login screen

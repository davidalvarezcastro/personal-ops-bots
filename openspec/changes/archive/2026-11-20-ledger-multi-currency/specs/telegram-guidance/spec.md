# Spec Delta

## MODIFIED Requirements

### Requirement: Authorized operator can list commands
When an authorized operator submits `/help`, the system SHALL reply with the supported commands and their parameter grammar, including `/start`, `/help`, `/expense`, `/income`, and `/balance`. Expense and income grammar MUST show optional currency immediately after amount.

#### Scenario: Help lists ledger and guidance commands
- **WHEN** an authorized operator submits `/help`
- **THEN** the reply includes `/start`, `/help`, `/expense`, `/income`, and `/balance` with their syntax, and expense/income syntax includes optional currency after the amount

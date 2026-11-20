# Spec Delta

## MODIFIED Requirements

### Requirement: Balance reports net and category totals
The system SHALL return, for the selected period, one group per currency that has activity (or a single EUR group of zeros when the period is empty): total income in that currency's minor units, total expense in that currency's minor units, net (income minus expense) in that currency, expense totals grouped by category, and income totals grouped by category. Amounts MUST be exact integer minor-unit sums within that currency. The system MUST NOT add amounts across currencies. Entries of type `transfer` MUST NOT be included.

#### Scenario: Month with mixed entries
- **GIVEN** the current month contains income of 180000 EUR minor units in `Salary` and expenses of 2000 EUR minor units in `Groceries` and 500 EUR minor units in `Uncategorized`
- **WHEN** an authorized operator submits `/balance`
- **THEN** the EUR group reports income 180000, expense 2500, net 177500, expense `Groceries` 2000, expense `Uncategorized` 500, and income `Salary` 180000

#### Scenario: Empty period
- **WHEN** an authorized operator requests a balance for a period with no entries
- **THEN** the system reports a EUR group with income 0, expense 0, net 0, and empty category totals

#### Scenario: Two currencies are not mixed
- **GIVEN** the current month contains an expense of 1000 EUR minor units and an expense of 500 USD minor units
- **WHEN** an authorized operator submits `/balance`
- **THEN** the EUR group expense is 1000 and the USD group expense is 500, and neither total includes the other currency

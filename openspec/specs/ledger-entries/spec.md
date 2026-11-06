# ledger-entries Specification

## Purpose

Records personal expense and income movements in a single ledger so daily cashflow can be captured quickly from text commands.

## Requirements

### Requirement: Authorized operator can record an expense
The system SHALL record an expense when an authorized operator submits `/expense <amount> [<category>] <merchant...>`. The merchant MUST be the remaining text after amount and optional category.

#### Scenario: Expense with merchant only
- **WHEN** an authorized operator submits `/expense 12,50 Mercadona`
- **THEN** the system records an expense of 1250 cents with merchant `Mercadona` and category `Uncategorized`

#### Scenario: Expense with category and multi-word merchant
- **WHEN** an authorized operator submits `/expense 89,90 Shopping El Corte Ingles`
- **THEN** the system records an expense of 8990 cents with category `Shopping` and merchant `El Corte Ingles`

#### Scenario: Expense rejected without merchant
- **WHEN** an authorized operator submits `/expense 12,50`
- **THEN** the system MUST NOT record an entry and MUST notify that merchant is required

### Requirement: Authorized operator can record income
The system SHALL record income when an authorized operator submits `/income <amount> [<category>] <source...>`. The source MUST be the remaining text after amount and optional category.

#### Scenario: Income with source only
- **WHEN** an authorized operator submits `/income 1800 Nomina`
- **THEN** the system records income of 180000 cents with source `Nomina` and category `Uncategorized`

#### Scenario: Income with category
- **WHEN** an authorized operator submits `/income 1800 Salary Company`
- **THEN** the system records income of 180000 cents with category `Salary` and source `Company`

### Requirement: Amounts are euro cents parsed from decimal text
The system SHALL treat amounts as euros, accept comma or dot as the decimal separator, allow 0 to 2 fractional digits, normalize one fractional digit to two (`25,2` is 25.20 EUR), and persist the value as an integer number of cents. Amounts with more than two fractional digits MUST be rejected.

#### Scenario: One fractional digit with comma
- **WHEN** an authorized operator records an expense amount `25,2`
- **THEN** the system stores 2520 cents

#### Scenario: Two fractional digits with comma
- **WHEN** an authorized operator records an expense amount `0,99`
- **THEN** the system stores 99 cents

#### Scenario: Dot decimal separator
- **WHEN** an authorized operator records an expense amount `25.20`
- **THEN** the system stores 2520 cents

#### Scenario: Too many fractional digits
- **WHEN** an authorized operator records an expense amount `12,345`
- **THEN** the system MUST NOT record an entry and MUST notify that the amount is invalid

### Requirement: Category is optional with longest catalog match
The system SHALL treat category as optional. After the amount, it MUST consume the longest case-insensitive prefix that matches a category allowed for that entry type. If none matches, category MUST be `Uncategorized` and the remaining text MUST be the merchant or source.

#### Scenario: Known multi-word expense category
- **WHEN** an authorized operator submits `/expense 15 Food & Drinks Cafe Central`
- **THEN** the system records category `Food & Drinks` and merchant `Cafe Central`

#### Scenario: Unknown token is merchant not category
- **WHEN** an authorized operator submits `/expense 15 Mercadona`
- **THEN** the system records category `Uncategorized` and merchant `Mercadona`

### Requirement: Entry type owns its category catalog
Expense categories MUST be Uncategorized, Food & Drinks, Groceries, Transport, Shopping, Entertainment, Health, Personal Care, Bills & Utilities, Subscriptions, Travel, and Education. Income categories MUST be Uncategorized, Salary, Bonus, Interest, Gifts, and Refunds. A name valid only on the other type MUST NOT be treated as a category.

#### Scenario: Income category is not valid on expense
- **WHEN** an authorized operator submits `/expense 15 Salary Store`
- **THEN** the system records category `Uncategorized` and merchant `Salary Store`

### Requirement: Default payment method and occurrence time
The system SHALL store payment method `card` on every recorded entry in this version and SHALL set occurrence time to the moment of recording. The operator MUST NOT be required to supply payment method or timestamp.

#### Scenario: Expense without payment method
- **WHEN** an authorized operator records `/expense 10 Shop`
- **THEN** the stored entry has payment method `card` and an occurrence time equal to the recording time

### Requirement: Single ledger of typed entries
The system SHALL persist expenses and income in one ledger of entries distinguished by type `expense` or `income`. Recording commands MUST NOT create `transfer` entries.

#### Scenario: Expense type stored
- **WHEN** an authorized operator records an expense
- **THEN** the stored entry type is `expense`

#### Scenario: Income type stored
- **WHEN** an authorized operator records income
- **THEN** the stored entry type is `income`

### Requirement: Unauthorized operators cannot record entries
The system SHALL reject recording attempts from operators who are not allowlisted and MUST NOT persist an entry.

#### Scenario: Unknown operator expense
- **WHEN** an operator who is not allowlisted submits `/expense 10 Shop`
- **THEN** the system MUST NOT persist an entry

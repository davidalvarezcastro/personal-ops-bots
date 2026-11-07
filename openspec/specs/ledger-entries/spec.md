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

### Requirement: Operator can list ledger entries newest first
The system SHALL return stored expense and income entries ordered by occurrence time descending, excluding `transfer` entries. A requested page size MUST be honored when it is a positive integer; otherwise the page size MUST be 8.

#### Scenario: Default eight
- **GIVEN** ten expenses with distinct occurrence times
- **WHEN** an operator lists entries without a page size and without a cursor
- **THEN** the result contains the eight newest expenses in descending occurrence order

### Requirement: Operator can continue an entry list with a cursor
The system SHALL continue a list from an opaque cursor for the last item of the previous page, not from a numeric offset. The next page MUST be older remaining entries and MUST NOT repeat the previous page. When no older entries remain, the result MUST omit a next cursor.

#### Scenario: Second page via cursor
- **GIVEN** twelve expenses with distinct occurrence times
- **WHEN** an operator lists the first page and then continues with the returned cursor
- **THEN** the second page contains older expenses that were not on the first page

#### Scenario: Inserts do not duplicate a continued page
- **GIVEN** an operator has a cursor after the eight newest entries
- **WHEN** a newer expense is recorded and the operator continues with that cursor
- **THEN** the next page still starts at the same older entries and MUST NOT repeat the original eight

### Requirement: Operator can change an entry category
The system SHALL persist a new category on an existing expense or income when the name is in that entry type's catalog. Amount, payee, type, and occurrence time MUST remain unchanged when only category is supplied.

#### Scenario: Expense recategorized
- **GIVEN** an expense stored as `Uncategorized`
- **WHEN** an operator changes its category to `Groceries`
- **THEN** the stored category is `Groceries` and the amount is unchanged

#### Scenario: Income category rejected on expense
- **GIVEN** an expense
- **WHEN** an operator tries to set its category to `Salary`
- **THEN** the system MUST NOT change the entry and MUST notify that the category is not allowed

#### Scenario: Missing entry
- **WHEN** an operator changes the category of an id that is not stored
- **THEN** the system MUST notify that the entry was not found

### Requirement: Operator can delete a ledger entry
The system SHALL remove an existing expense or income by id. After removal the entry MUST NOT appear in lists or in later balance totals.

#### Scenario: Deleted expense omitted from balance
- **GIVEN** a current-month expense of 2000 cents
- **WHEN** an operator deletes that entry
- **THEN** a current-month balance does not include those 2000 cents

#### Scenario: Missing entry on delete
- **WHEN** an operator deletes an id that is not stored
- **THEN** the system MUST notify that the entry was not found

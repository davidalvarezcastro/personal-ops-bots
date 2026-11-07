# Spec Delta

## ADDED Requirements

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

# Spec Delta

## ADDED Requirements

### Requirement: Optional currency follows the amount
Immediately after the amount, the operator MAY supply a currency as an ISO 4217 code or a catalog symbol, with or without a space (`65 €`, `65€`, `65 EUR`). When omitted, the stored currency MUST be `EUR`. Allowed codes are EUR, USD, GBP, JPY, and CNY. Symbols: `€` EUR, `$` USD, `£` GBP, `¥` JPY, `CN¥` CNY.

#### Scenario: Euro symbol
- **WHEN** an authorized operator submits `/expense 65 € Mercadona`
- **THEN** the system records 6500 EUR minor units and currency `EUR`

#### Scenario: ISO code
- **WHEN** an authorized operator submits `/expense 12,50 USD Starbucks`
- **THEN** the system records 1250 USD minor units and currency `USD`

#### Scenario: Omitted currency stays euro
- **WHEN** an authorized operator submits `/expense 12,50 Mercadona`
- **THEN** the stored currency is `EUR` and the amount is 1250 EUR minor units

#### Scenario: Yen has no fraction
- **WHEN** an authorized operator submits `/expense 65 ¥ Konbini`
- **THEN** the system records 65 JPY minor units and currency `JPY`

#### Scenario: Unknown ISO code rejected
- **WHEN** an authorized operator submits `/expense 10 INR Shop`
- **THEN** the system MUST NOT record an entry and MUST notify that the currency is not supported

### Requirement: Fraction digits follow the currency
EUR, USD, GBP, and CNY MUST use 0–2 fractional digits (one digit normalized to two). JPY MUST be a whole number with no fractional part. Too many fraction digits for that currency MUST be rejected.

#### Scenario: JPY with cents rejected
- **WHEN** an authorized operator submits `/expense 65,50 JPY Shop`
- **THEN** the system MUST NOT record an entry and MUST notify that the amount is invalid

## MODIFIED Requirements

### Requirement: Authorized operator can record an expense
The system SHALL record an expense when an authorized operator submits `/expense <amount> [<currency>] [<category>] <merchant...>`. Currency, when present, MUST sit immediately after the amount. The merchant MUST be the remaining text after amount, optional currency, and optional category.

#### Scenario: Expense with merchant only
- **WHEN** an authorized operator submits `/expense 12,50 Mercadona`
- **THEN** the system records an expense of 1250 EUR minor units with merchant `Mercadona`, category `Uncategorized`, and currency `EUR`

#### Scenario: Expense with category and multi-word merchant
- **WHEN** an authorized operator submits `/expense 89,90 Shopping El Corte Ingles`
- **THEN** the system records an expense of 8990 EUR minor units with category `Shopping` and merchant `El Corte Ingles`

#### Scenario: Expense rejected without merchant
- **WHEN** an authorized operator submits `/expense 12,50`
- **THEN** the system MUST NOT record an entry and MUST notify that merchant is required

### Requirement: Authorized operator can record income
The system SHALL record income when an authorized operator submits `/income <amount> [<currency>] [<category>] <source...>`. Currency, when present, MUST sit immediately after the amount. The source MUST be the remaining text after amount, optional currency, and optional category.

#### Scenario: Income with source only
- **WHEN** an authorized operator submits `/income 1800 Nomina`
- **THEN** the system records income of 180000 EUR minor units with source `Nomina`, category `Uncategorized`, and currency `EUR`

#### Scenario: Income with category
- **WHEN** an authorized operator submits `/income 1800 Salary Company`
- **THEN** the system records income of 180000 EUR minor units with category `Salary` and source `Company`

### Requirement: Amounts are euro cents parsed from decimal text
The system SHALL parse the amount as decimal text (comma or dot separator) and persist an integer number of minor units for the entry's currency. For EUR (the default), 0 to 2 fractional digits apply and one fractional digit is normalized to two (`25,2` is 25.20 EUR). Amounts with more fractional digits than the currency allows MUST be rejected.

#### Scenario: One fractional digit with comma
- **WHEN** an authorized operator records an expense amount `25,2`
- **THEN** the system stores 2520 EUR minor units

#### Scenario: Two fractional digits with comma
- **WHEN** an authorized operator records an expense amount `0,99`
- **THEN** the system stores 99 EUR minor units

#### Scenario: Dot decimal separator
- **WHEN** an authorized operator records an expense amount `25.20`
- **THEN** the system stores 2520 EUR minor units

#### Scenario: Too many fractional digits
- **WHEN** an authorized operator records an expense amount `12,345`
- **THEN** the system MUST NOT record an entry and MUST notify that the amount is invalid

### Requirement: Category is optional with longest catalog match
The system SHALL treat category as optional. After the amount and optional currency, it MUST consume the longest case-insensitive prefix that matches a category allowed for that entry type. If none matches, category MUST be `Uncategorized` and the remaining text MUST be the merchant or source.

#### Scenario: Known multi-word expense category
- **WHEN** an authorized operator submits `/expense 15 Food & Drinks Cafe Central`
- **THEN** the system records category `Food & Drinks` and merchant `Cafe Central`

#### Scenario: Unknown token is merchant not category
- **WHEN** an authorized operator submits `/expense 15 Mercadona`
- **THEN** the system records category `Uncategorized` and merchant `Mercadona`

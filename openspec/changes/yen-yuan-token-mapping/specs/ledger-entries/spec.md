# Spec Delta

## MODIFIED Requirements

### Requirement: Optional currency follows the amount
Immediately after the amount, the operator MAY supply a currency as an ISO 4217 code, catalog symbol, or listed alias, with or without a space (`65 €`, `65€`, `65 EUR`). When omitted, the stored currency MUST be `EUR`. Allowed stored codes are EUR, USD, GBP, JPY, and CNY. Tokens: `€` EUR, `$` USD, `£` GBP, `JPY`/`JP¥` JPY, `¥`/`RMB`/`CNY`/`CN¥` CNY. Aliases MUST store the ISO code, not the alias text.

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
- **WHEN** an authorized operator submits `/expense 65 JP¥ Konbini`
- **THEN** the system records 65 JPY minor units and currency `JPY`

#### Scenario: Unknown ISO code rejected
- **WHEN** an authorized operator submits `/expense 10 INR Shop`
- **THEN** the system MUST NOT record an entry and MUST notify that the currency is not supported

#### Scenario: Bare yen sign is yuan
- **WHEN** an authorized operator submits `/expense 65 ¥ Shop`
- **THEN** the system records 6500 CNY minor units and currency `CNY`

#### Scenario: RMB alias is yuan
- **WHEN** an authorized operator submits `/expense 12,50 RMB Shop`
- **THEN** the system records 1250 CNY minor units and currency `CNY`

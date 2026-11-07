# Spec Delta

## Purpose

Orients the Telegram operator so they can tell the bot is ready and discover the commands it accepts.

## ADDED Requirements

### Requirement: Authorized operator receives a start welcome
When an authorized operator submits `/start`, the system SHALL reply with a welcome that states the bot is ready and that `/help` lists commands.

#### Scenario: Authorized start
- **WHEN** an authorized operator submits `/start`
- **THEN** the reply states the bot is ready and mentions `/help`

### Requirement: Authorized operator can list commands
When an authorized operator submits `/help`, the system SHALL reply with the supported commands and their parameter grammar, including `/start`, `/help`, `/expense`, `/income`, and `/balance`.

#### Scenario: Help lists ledger and guidance commands
- **WHEN** an authorized operator submits `/help`
- **THEN** the reply includes `/start`, `/help`, `/expense`, `/income`, and `/balance` with their syntax

### Requirement: Telegram command menu matches help
The system SHALL publish the same command names to the Telegram command menu so the client can suggest them while typing.

#### Scenario: Menu includes help and ledger commands
- **WHEN** the bot process becomes ready to receive updates
- **THEN** the Telegram command menu includes at least `/start`, `/help`, `/expense`, `/income`, and `/balance`

### Requirement: Unauthorized operators do not receive guidance
The system SHALL NOT send welcome or help text to operators who are not allowlisted.

#### Scenario: Unknown operator start
- **WHEN** an operator who is not allowlisted submits `/start`
- **THEN** the system MUST NOT send a welcome or command list

#### Scenario: Unknown operator help
- **WHEN** an operator who is not allowlisted submits `/help`
- **THEN** the system MUST NOT send a command list

# operator-logging Specification

## Purpose

Makes bot startup and incoming commands visible as structured stdout events without leaking secrets, so an operator or log collector can follow what the process is doing.

## Requirements

### Requirement: Ready process emits a structured running event
When the bot is ready to receive Telegram updates, the system SHALL write a structured log event to stdout with a UTC timestamp, a severity level, and an event name that states the bot is running.

#### Scenario: Polling started
- **WHEN** the bot process finishes startup and begins receiving updates
- **THEN** stdout contains a structured event whose name indicates the bot is running and that includes a UTC timestamp and a log level

### Requirement: Authorized commands emit structured events with fields
When an authorized operator submits a command, the system SHALL write a structured log event that includes distinct fields for command name and submitted parameter text (not only a single interpolated sentence).

#### Scenario: Expense command logged
- **WHEN** an authorized operator submits `/expense 12,50 Mercadona`
- **THEN** a structured event includes a command field `expense` and a parameters field containing `12,50 Mercadona`

#### Scenario: Help command logged
- **WHEN** an authorized operator submits `/help`
- **THEN** a structured event includes a command field `help`

### Requirement: Non-TTY output is machine-readable JSON
When log output is not attached to an interactive terminal, or when JSON format is selected, each log event SHALL be a single JSON object on one line with keys for timestamp, level, and event name.

#### Scenario: JSON line when format is JSON
- **WHEN** the process emits a running or command event with JSON log format
- **THEN** the line is parseable as a JSON object that includes `timestamp`, `level`, and `event`

### Requirement: Logs never include the bot token
Log output MUST NOT contain the Telegram bot token.

#### Scenario: Startup logs omit token
- **WHEN** the bot process starts
- **THEN** no log event contains the configured bot token

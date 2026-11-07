# Spec Delta

## Purpose

Runs the income and expense Telegram bot as a long-lived Compose service on the operator's host, using an image published to GitHub Container Registry from a machine other than that host.

## ADDED Requirements

### Requirement: Operator can start the bot as a restartable Compose service
The system SHALL provide a committed Compose definition that starts the income/expense bot as a single service that restarts after a crash or host reboot until the operator stops it.

#### Scenario: Compose brings the bot up
- **WHEN** an operator runs Compose up with a valid host environment file and the registry image available
- **THEN** the bot process is running and ready to receive Telegram updates

#### Scenario: Process restarts after crash
- **WHEN** the bot process exits unexpectedly
- **THEN** the runtime starts it again without a new manual Compose up

### Requirement: Compose uses a GitHub Container Registry image
The committed Compose service SHALL reference the bot image by its GitHub Container Registry name (`ghcr.io`, repository owner, and `income-expense-bot`), not by an un-namespaced local tag only.

#### Scenario: Image field is on GHCR
- **WHEN** an operator inspects the Compose service image
- **THEN** the name starts with `ghcr.io/` and includes the owner and `income-expense-bot`

### Requirement: Image is built off the host and published to the registry
Operator documentation SHALL describe building the image on a laptop (or equivalent) for `linux/arm64` and pushing it to that registry name. Building on the Raspberry Pi MUST NOT be the documented default.

#### Scenario: Documented publish is push not load
- **WHEN** an operator follows the documented release
- **THEN** they push to GitHub Container Registry and do not copy an image tarball as the default path

### Requirement: Operator can refresh the bot from the registry
After a new image is published, the operator SHALL be able to pull it on the host and start Compose without copying a tarball.

#### Scenario: Pull then up
- **WHEN** the operator is logged in to the registry and runs pull then Compose up
- **THEN** the running service uses the registry image

### Requirement: Ledger data survives container replacement
The system SHALL keep ledger records on a host directory that remains after the container is removed and created again.

#### Scenario: Recreate keeps the sqlite file
- **WHEN** the operator recreates the bot container after recording at least one ledger entry
- **THEN** the same SQLite file is still present on the host data directory

### Requirement: Secrets are not shipped in the image
The container image MUST NOT contain the Telegram bot token or a production `.env` file. The operator SHALL supply token and allowlist through the host environment at run time.

#### Scenario: Image has no token file
- **WHEN** an operator inspects the image build context and Dockerfile
- **THEN** `.env` is not copied into the image

#### Scenario: Missing token fails fast
- **WHEN** Compose starts the service without `TELEGRAM_BOT_TOKEN`
- **THEN** the process MUST NOT stay up as a healthy polling bot

### Requirement: Host does not publish Telegram listener ports
The Compose service MUST NOT publish ports on the host. The bot reaches Telegram by outbound connections only.

#### Scenario: No published ports
- **WHEN** the operator inspects the Compose service
- **THEN** it has no host port mappings

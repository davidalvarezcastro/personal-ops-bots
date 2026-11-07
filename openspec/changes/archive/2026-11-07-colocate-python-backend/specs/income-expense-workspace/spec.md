# Spec Delta

## Purpose

Makes this full-stack ledger repo a two-package tree so operators know where Python, tests, the SPA, and Compose live.

## ADDED Requirements

### Requirement: Python project lives under backend
The committed tree MUST place the Python package, its tests, and the Python project metadata under a `backend/` directory. The repository root MUST NOT contain a top-level `src/` or `tests/` directory for this bot.

#### Scenario: Inspect the tree
- **WHEN** an operator lists the repository root and `backend/`
- **THEN** `backend/` contains the Python package sources and the Python tests, and the root has no `src/` or `tests/` directories

### Requirement: Python commands run from the backend project
Operator documentation SHALL instruct installing dependencies and running the bot, HTTP API, and Python tests from the `backend/` Python project (or an equivalent command that targets that directory). Those documented commands MUST succeed without a root-level Python project file.

#### Scenario: Documented pytest
- **WHEN** an operator follows the documented Python test command after a fresh clone and dependency install
- **THEN** the Python test suite runs from the backend project and the documentation does not tell them to run pytest against a root-level `tests/` directory

#### Scenario: Documented bot start
- **WHEN** an operator follows the documented local bot start
- **THEN** the process starts from the backend Python project and still runs as module `income_expense_bot`

### Requirement: SPA stays a sibling of backend
The Vue web app MUST remain in a `frontend/` directory at the repository root, sibling to `backend/`, not nested inside `backend/`.

#### Scenario: Frontend location
- **WHEN** an operator lists the repository root
- **THEN** `frontend/` and `backend/` are both present as sibling directories

### Requirement: Compose and secrets stay at the repository root
The committed Compose definition, host data directory convention, and documented `.env` location MUST remain at the repository root so a Pi checkout does not have to `cd` into `backend/` to start the container.

#### Scenario: Compose up from clone root
- **WHEN** an operator runs Compose up from the repository root with a valid host `.env`
- **THEN** the bot service starts without requiring Compose files inside `backend/`

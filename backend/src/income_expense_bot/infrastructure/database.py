from __future__ import annotations

from pathlib import Path

from sqlalchemy import Connection, event, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from income_expense_bot.config import Config
from income_expense_bot.infrastructure.persistence.orm import metadata, start_mappers


def sqlite_url(path: str) -> str:
    resolved = Path(path).expanduser().resolve()
    return f"sqlite+aiosqlite:///{resolved}"


def _enable_wal(dbapi_connection: object, _connection_record: object) -> None:
    cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()


def create_engine_from_config(config: Config) -> AsyncEngine:
    engine = create_async_engine(sqlite_url(config.ledger_sqlite_path), echo=False)
    event.listen(engine.sync_engine, "connect", _enable_wal)
    return engine


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )


def _ensure_currency_column(sync_connection: Connection) -> None:
    rows = sync_connection.execute(text("PRAGMA table_info(ledger_entries)")).fetchall()
    names = {row[1] for row in rows}
    if "currency" not in names:
        sync_connection.execute(
            text("ALTER TABLE ledger_entries ADD COLUMN currency VARCHAR(3) NOT NULL DEFAULT 'EUR'")
        )


async def create_schema(engine: AsyncEngine) -> None:
    start_mappers()
    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)
        await connection.run_sync(_ensure_currency_column)

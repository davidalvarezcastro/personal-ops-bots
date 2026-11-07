from __future__ import annotations

from pathlib import Path

from sqlalchemy import event
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


async def create_schema(engine: AsyncEngine) -> None:
    start_mappers()
    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)

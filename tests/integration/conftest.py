from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from income_expense_bot.config import Config
from income_expense_bot.infrastructure.database import (
    create_engine_from_config,
    create_schema,
    create_session_factory,
)
from income_expense_bot.infrastructure.unity_of_work import SqlAlchemyUnitOfWork


@pytest.fixture
async def engine(tmp_path: Path) -> AsyncIterator[AsyncEngine]:
    config = Config(
        telegram_bot_token="test-token",
        telegram_allowed_user_ids=frozenset({1}),
        ledger_sqlite_path=str(tmp_path / "ledger.sqlite"),
    )
    engine = create_engine_from_config(config)
    await create_schema(engine)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture
def session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return create_session_factory(engine)


@pytest.fixture
def uow(session_factory: async_sessionmaker[AsyncSession]) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(session_factory)

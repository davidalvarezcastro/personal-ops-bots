from pathlib import Path

from sqlalchemy import text

from income_expense_bot.config import Config
from income_expense_bot.infrastructure.database import create_engine_from_config, create_schema


async def test_engine_enables_wal(tmp_path: Path) -> None:
    config = Config(
        telegram_bot_token="test-token",
        telegram_allowed_user_ids=frozenset({1}),
        ledger_sqlite_path=str(tmp_path / "ledger.sqlite"),
    )
    engine = create_engine_from_config(config)
    await create_schema(engine)
    try:
        async with engine.connect() as connection:
            mode = (await connection.execute(text("PRAGMA journal_mode"))).scalar_one()
        assert str(mode).lower() == "wal"
    finally:
        await engine.dispose()

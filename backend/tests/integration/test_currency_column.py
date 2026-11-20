from pathlib import Path

from sqlalchemy import text

from income_expense_bot.config import Config
from income_expense_bot.infrastructure.database import (
    create_engine_from_config,
    create_schema,
    create_session_factory,
)
from income_expense_bot.infrastructure.unity_of_work import SqlAlchemyUnitOfWork


async def test_legacy_rows_read_as_eur(tmp_path: Path) -> None:
    config = Config(
        telegram_bot_token="test-token",
        telegram_allowed_user_ids=frozenset({1}),
        ledger_sqlite_path=str(tmp_path / "legacy.sqlite"),
    )
    engine = create_engine_from_config(config)
    try:
        async with engine.begin() as connection:
            await connection.execute(
                text(
                    """
                    CREATE TABLE ledger_entries (
                        id VARCHAR PRIMARY KEY,
                        type VARCHAR NOT NULL,
                        amount_cents INTEGER NOT NULL,
                        payee VARCHAR NOT NULL,
                        category VARCHAR NOT NULL,
                        payment_method VARCHAR NOT NULL,
                        occurred_at DATETIME NOT NULL
                    )
                    """
                )
            )
            await connection.execute(
                text(
                    """
                    INSERT INTO ledger_entries
                    (id, type, amount_cents, payee, category, payment_method, occurred_at)
                    VALUES
                    ('legacy-1', 'expense', 1000, 'Shop', 'Uncategorized', 'card', '2026-11-01 12:00:00')
                    """
                )
            )
        await create_schema(engine)
        uow = SqlAlchemyUnitOfWork(create_session_factory(engine))
        async with uow as unit:
            entry = await unit.entries.get("legacy-1")
        assert entry is not None
        assert entry.currency == "EUR"
        assert entry.amount_cents == 1000
    finally:
        await engine.dispose()

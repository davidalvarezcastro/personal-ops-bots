from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncEngine


async def test_schema_creates_ledger_entries(engine: AsyncEngine) -> None:
    async with engine.connect() as connection:
        tables = await connection.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())
        assert "ledger_entries" in tables
        result = await connection.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        assert "ledger_entries" in [row[0] for row in result]

from calendar import monthrange
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient

from income_expense_bot.config import Config
from income_expense_bot.interfaces.http.app import create_app


def _client(tmp_path: Path) -> TestClient:
    config = Config(
        telegram_bot_token="test-token",
        telegram_allowed_user_ids=frozenset({1}),
        ledger_sqlite_path=str(tmp_path / "ledger.sqlite"),
    )
    return TestClient(create_app(config))


def test_balance_current_month_without_credentials(tmp_path: Path) -> None:
    with _client(tmp_path) as client:
        response = client.get("/api/v1/balance")
    assert response.status_code == 200
    payload = response.json()
    today = datetime.now(ZoneInfo("Europe/Madrid")).date()
    last = monthrange(today.year, today.month)[1]
    assert payload["start"] == today.replace(day=1).isoformat()
    assert payload["end"] == today.replace(day=last).isoformat()
    assert payload["income_cents"] == 0
    assert payload["expense_cents"] == 0
    assert payload["net_cents"] == 0


def test_balance_invalid_range(tmp_path: Path) -> None:
    with _client(tmp_path) as client:
        response = client.get("/api/v1/balance", params={"start": "2026-11-15", "end": "2026-11-01"})
    assert response.status_code == 400


def test_list_entries_default_page_and_cursor(tmp_path: Path) -> None:
    with _client(tmp_path) as client:
        for index in range(12):
            created = client.post(
                "/api/v1/entries",
                json={
                    "type": "expense",
                    "amount": f"{index + 1}",
                    "payee": f"Shop {index}",
                    "category": "Groceries",
                },
            )
            assert created.status_code == 201
        first = client.get("/api/v1/entries")
        assert first.status_code == 200
        body = first.json()
        assert len(body["items"]) == 8
        assert body["next_cursor"]
        second = client.get("/api/v1/entries", params={"cursor": body["next_cursor"]})
        second_body = second.json()
        first_ids = {item["id"] for item in body["items"]}
        second_ids = {item["id"] for item in second_body["items"]}
        assert first_ids.isdisjoint(second_ids)
        assert len(second_body["items"]) == 4
        assert second_body["next_cursor"] is None


def test_list_last_page_omits_cursor(tmp_path: Path) -> None:
    with _client(tmp_path) as client:
        for index in range(3):
            client.post(
                "/api/v1/entries",
                json={"type": "expense", "amount": "1", "payee": f"Shop {index}", "category": "Groceries"},
            )
        payload = client.get("/api/v1/entries").json()
        assert len(payload["items"]) == 3
        assert payload["next_cursor"] is None


def test_categories_by_type(tmp_path: Path) -> None:
    with _client(tmp_path) as client:
        expense = client.get("/api/v1/categories", params={"type": "expense"})
        income = client.get("/api/v1/categories", params={"type": "income"})
    assert "Groceries" in expense.json()["categories"]
    assert "Salary" in income.json()["categories"]
    assert "Groceries" not in income.json()["categories"]


def test_post_expense_and_reject_empty_payee(tmp_path: Path) -> None:
    with _client(tmp_path) as client:
        ok = client.post(
            "/api/v1/entries",
            json={"type": "expense", "amount": "12,50", "payee": "Mercadona", "category": "Groceries"},
        )
        assert ok.status_code == 201
        assert ok.json()["amount_cents"] == 1250
        assert ok.json()["payee"] == "Mercadona"
        assert ok.json()["category"] == "Groceries"
        bad = client.post(
            "/api/v1/entries",
            json={"type": "expense", "amount": "10", "payee": "  ", "category": "Groceries"},
        )
        assert bad.status_code == 400


def test_patch_and_delete_entry(tmp_path: Path) -> None:
    with _client(tmp_path) as client:
        created = client.post(
            "/api/v1/entries",
            json={"type": "expense", "amount": "5,00", "payee": "Shop", "category": "Uncategorized"},
        )
        entry_id = created.json()["id"]
        amount = created.json()["amount_cents"]
        patched = client.patch(f"/api/v1/entries/{entry_id}", json={"category": "Transport"})
        assert patched.status_code == 200
        assert patched.json()["category"] == "Transport"
        assert patched.json()["amount_cents"] == amount
        missing = client.patch("/api/v1/entries/not-there", json={"category": "Transport"})
        assert missing.status_code == 404
        deleted = client.delete(f"/api/v1/entries/{entry_id}")
        assert deleted.status_code == 204
        balance = client.get("/api/v1/balance").json()
        assert balance["expense_cents"] == 0
        gone = client.delete(f"/api/v1/entries/{entry_id}")
        assert gone.status_code == 404

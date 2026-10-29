from __future__ import annotations

import hashlib
import hmac
import json
import time

import pytest
from fastapi.testclient import TestClient

from backend import main
from backend.database import database
from backend.services import auth


@pytest.fixture
def client(monkeypatch, tmp_path):
    """Run the API lifespan against a fresh per-test SQLite database."""
    db_path = tmp_path / "cafe-test.sqlite3"
    monkeypatch.setenv("CAFE_DB_PATH", str(db_path))
    # DB_PATH is read at module import, so update it after setting the env var.
    monkeypatch.setattr(database, "DB_PATH", db_path)
    with TestClient(main.app) as test_client:
        yield test_client


@pytest.fixture
def customer_headers(client):
    """Log in a test customer and return their bearer-token headers."""
    response = client.post(
        "/api/login",
        json={"name": "Test Customer", "phone": "9876543210"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_order_uses_database_price(client, customer_headers):
    connection = database.get_connection()
    try:
        item = connection.execute("SELECT id FROM menu_items LIMIT 1").fetchone()
        menu_item_id = item["id"]
        connection.execute("UPDATE menu_items SET price = 731 WHERE id = ?", (menu_item_id,))
        connection.commit()
    finally:
        connection.close()

    response = client.post(
        "/api/orders",
        headers=customer_headers,
        json={"items": [{"menu_item_id": menu_item_id, "quantity": 2}]},
    )

    assert response.status_code == 200
    order = response.json()
    assert order["items"][0]["unit_price"] == 731
    assert order["items"][0]["line_total"] == 1462
    assert order["total"] == 1462


def test_order_rejects_duplicate_items(client, customer_headers):
    item_id = client.get("/api/menu").json()["Hot Beverages"][0]["id"]
    response = client.post(
        "/api/orders",
        headers=customer_headers,
        json={"items": [
            {"menu_item_id": item_id, "quantity": 1},
            {"menu_item_id": item_id, "quantity": 2},
        ]},
    )
    assert response.status_code == 422


def test_order_rejects_quantity_above_twenty(client, customer_headers):
    item_id = client.get("/api/menu").json()["Hot Beverages"][0]["id"]
    response = client.post(
        "/api/orders",
        headers=customer_headers,
        json={"items": [{"menu_item_id": item_id, "quantity": 21}]},
    )
    assert response.status_code == 422


def test_order_returns_400_for_unknown_item(client, customer_headers):
    response = client.post(
        "/api/orders",
        headers=customer_headers,
        json={"items": [{"menu_item_id": 999999, "quantity": 1}]},
    )
    assert response.status_code == 400


def test_second_rating_same_utc_day_is_rejected(client, customer_headers):
    first = client.post("/api/ratings", headers=customer_headers, json={"stars": 5})
    second = client.post("/api/ratings", headers=customer_headers, json={"stars": 4})

    assert first.status_code == 200
    assert second.status_code == 422
    assert "one rating per UTC day" in second.json()["detail"]


@pytest.mark.parametrize("stars", [0, 6])
def test_rating_rejects_stars_outside_one_to_five(client, customer_headers, stars):
    response = client.post(
        "/api/ratings",
        headers=customer_headers,
        json={"stars": stars},
    )
    assert response.status_code == 422


def test_rating_rejects_comment_longer_than_500_characters(client, customer_headers):
    response = client.post(
        "/api/ratings",
        headers=customer_headers,
        json={"stars": 5, "comment": "x" * 501},
    )
    assert response.status_code == 422


def test_forged_session_token_returns_401(client):
    response = client.post(
        "/api/orders",
        headers={"Authorization": "Bearer forged.payload"},
        json={"items": [{"menu_item_id": 1, "quantity": 1}]},
    )
    assert response.status_code == 401


def _expired_token(customer_id: int = 1) -> str:
    payload = json.dumps(
        {"sub": customer_id, "exp": int(time.time()) - 1},
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    encoded_payload = auth._encode(payload)
    signature = hmac.new(
        auth._SESSION_SECRET,
        encoded_payload.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{encoded_payload}.{auth._encode(signature)}"


def test_expired_session_token_returns_401(client):
    response = client.post(
        "/api/orders",
        headers={"Authorization": f"Bearer {_expired_token()}"},
        json={"items": [{"menu_item_id": 1, "quantity": 1}]},
    )
    assert response.status_code == 401
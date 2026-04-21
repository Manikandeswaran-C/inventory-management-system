"""
Unit tests for the Inventory Management API.
Uses TestClient with an in-memory SQLite database so tests are isolated.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import create_app
from app.database import Base, get_db
from app.models import Item

# ── In-memory test database setup ─────────────────────────────────────────────
# StaticPool ensures ALL connections reuse the SAME in-memory SQLite instance.
# Without it, each new connection gets a blank DB and "no such table" errors occur.
TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # ← critical for in-memory SQLite tests
)
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Replace the production DB dependency with the test DB."""
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client():
    """
    Provide a fresh TestClient per test function.
    Tables are created before the test and dropped afterwards.
    """
    Base.metadata.create_all(bind=test_engine)
    app = create_app()
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    Base.metadata.drop_all(bind=test_engine)


# ── Helper ─────────────────────────────────────────────────────────────────────
def _create_item(client: TestClient, name: str = "Widget A", quantity: int = 50):
    """Convenience helper to create an item and return the response."""
    return client.post("/items/", json={"name": name, "quantity": quantity})


# ══════════════════════════════════════════════════════════════════════════════
# Health Endpoints
# ══════════════════════════════════════════════════════════════════════════════
class TestHealth:
    def test_root_returns_online(self, client):
        r = client.get("/")
        assert r.status_code == 200
        assert r.json()["status"] == "online"

    def test_health_endpoint(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "healthy"


# ══════════════════════════════════════════════════════════════════════════════
# POST /items/ — Create Item
# ══════════════════════════════════════════════════════════════════════════════
class TestCreateItem:
    def test_create_item_success(self, client):
        r = _create_item(client, name="Widget A", quantity=50)
        assert r.status_code == 201
        data = r.json()
        assert data["name"] == "Widget A"
        assert data["quantity"] == 50
        assert data["low_stock"] is False
        assert "id" in data

    def test_create_item_zero_quantity(self, client):
        """Zero quantity is valid but triggers low_stock immediately."""
        r = _create_item(client, name="Empty Box", quantity=0)
        assert r.status_code == 201
        assert r.json()["low_stock"] is True

    def test_create_item_sets_low_stock_flag(self, client):
        """Items with quantity <= 10 must have low_stock=True on creation."""
        r = _create_item(client, name="Critical Item", quantity=5)
        assert r.status_code == 201
        assert r.json()["low_stock"] is True

    def test_create_item_exactly_threshold(self, client):
        """Exactly 10 units is still low stock (≤ 10)."""
        r = _create_item(client, name="Threshold Item", quantity=10)
        assert r.status_code == 201
        assert r.json()["low_stock"] is True

    def test_create_item_above_threshold(self, client):
        """11 units is not low stock."""
        r = _create_item(client, name="Safe Item", quantity=11)
        assert r.status_code == 201
        assert r.json()["low_stock"] is False

    def test_create_item_negative_quantity_rejected(self, client):
        """⚠️ Trick Logic: Negative stock must be rejected with 422."""
        r = client.post("/items/", json={"name": "Bad Item", "quantity": -1})
        assert r.status_code == 422

    def test_create_item_blank_name_rejected(self, client):
        """Blank name after stripping must be rejected."""
        r = client.post("/items/", json={"name": "   ", "quantity": 10})
        assert r.status_code == 422

    def test_create_item_missing_name_rejected(self, client):
        r = client.post("/items/", json={"quantity": 10})
        assert r.status_code == 422

    def test_create_item_missing_quantity_rejected(self, client):
        r = client.post("/items/", json={"name": "Widget"})
        assert r.status_code == 422


# ══════════════════════════════════════════════════════════════════════════════
# GET /items/ — List Items
# ══════════════════════════════════════════════════════════════════════════════
class TestListItems:
    def test_list_empty_inventory(self, client):
        r = client.get("/items/")
        assert r.status_code == 200
        data = r.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["low_stock_count"] == 0

    def test_list_returns_created_items(self, client):
        _create_item(client, "Widget A", 50)
        _create_item(client, "Widget B", 5)
        r = client.get("/items/")
        assert r.status_code == 200
        data = r.json()
        assert data["total"] == 2
        assert data["low_stock_count"] == 1

    def test_list_pagination_skip(self, client):
        for i in range(5):
            _create_item(client, f"Item {i}", 100)
        r = client.get("/items/?skip=3&limit=10")
        assert r.status_code == 200
        assert len(r.json()["items"]) == 2


# ══════════════════════════════════════════════════════════════════════════════
# GET /items/{id} — Get Single Item
# ══════════════════════════════════════════════════════════════════════════════
class TestGetItem:
    def test_get_existing_item(self, client):
        created = _create_item(client).json()
        r = client.get(f"/items/{created['id']}")
        assert r.status_code == 200
        assert r.json()["id"] == created["id"]

    def test_get_nonexistent_item_returns_404(self, client):
        r = client.get("/items/9999")
        assert r.status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
# PATCH /items/{id}/stock — Update Stock
# ══════════════════════════════════════════════════════════════════════════════
class TestUpdateStock:
    def test_update_stock_success(self, client):
        created = _create_item(client, quantity=50).json()
        r = client.patch(f"/items/{created['id']}/stock", json={"quantity": 30})
        assert r.status_code == 200
        assert r.json()["quantity"] == 30
        assert r.json()["low_stock"] is False

    def test_update_stock_triggers_low_stock_flag(self, client):
        """⚠️ Trick Logic: Dropping below threshold must flip low_stock=True."""
        created = _create_item(client, quantity=50).json()
        r = client.patch(f"/items/{created['id']}/stock", json={"quantity": 8})
        assert r.status_code == 200
        assert r.json()["low_stock"] is True

    def test_update_stock_clears_low_stock_flag(self, client):
        """Bringing stock back above 10 must clear the low_stock flag."""
        created = _create_item(client, quantity=3).json()
        assert created["low_stock"] is True
        r = client.patch(f"/items/{created['id']}/stock", json={"quantity": 100})
        assert r.status_code == 200
        assert r.json()["low_stock"] is False

    def test_update_stock_negative_rejected(self, client):
        """⚠️ Trick Logic: Negative stock value must be rejected (422)."""
        created = _create_item(client, quantity=50).json()
        r = client.patch(f"/items/{created['id']}/stock", json={"quantity": -5})
        assert r.status_code == 422

    def test_update_stock_to_zero(self, client):
        """Setting stock to 0 is valid; low_stock must be True."""
        created = _create_item(client, quantity=50).json()
        r = client.patch(f"/items/{created['id']}/stock", json={"quantity": 0})
        assert r.status_code == 200
        assert r.json()["quantity"] == 0
        assert r.json()["low_stock"] is True

    def test_update_stock_nonexistent_item(self, client):
        r = client.patch("/items/9999/stock", json={"quantity": 10})
        assert r.status_code == 404

    def test_update_stock_exactly_threshold(self, client):
        """Quantity == 10 is still low stock."""
        created = _create_item(client, quantity=50).json()
        r = client.patch(f"/items/{created['id']}/stock", json={"quantity": 10})
        assert r.status_code == 200
        assert r.json()["low_stock"] is True


# ══════════════════════════════════════════════════════════════════════════════
# DELETE /items/{id}
# ══════════════════════════════════════════════════════════════════════════════
class TestDeleteItem:
    def test_delete_existing_item(self, client):
        created = _create_item(client).json()
        r = client.delete(f"/items/{created['id']}")
        assert r.status_code == 200
        # Confirm it's gone
        assert client.get(f"/items/{created['id']}").status_code == 404

    def test_delete_nonexistent_item(self, client):
        r = client.delete("/items/9999")
        assert r.status_code == 404

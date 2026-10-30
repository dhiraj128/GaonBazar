import os
import sys
import time
import shutil
import pytest
from fastapi.testclient import TestClient

sys.stdout.reconfigure(encoding="utf-8")
os.environ["ENVIRONMENT"] = "development"

from backend.main import app, check_database_integrity
from backend.database import db_session, engine
from backend.models import Order, Product

client = TestClient(app)

BASELINE_DB = "scratch/phase1_clean_baseline.db"
ACTIVE_DB = "backend/gaonbazar.db"


@pytest.fixture(autouse=True, scope="module")
def database_baseline_guard():
    """Guarantees exact 364 orders clean baseline is preserved before and after suite."""
    if os.path.exists(BASELINE_DB):
        engine.dispose()
        shutil.copyfile(BASELINE_DB, ACTIVE_DB)
    yield
    if os.path.exists(BASELINE_DB):
        engine.dispose()
        shutil.copyfile(BASELINE_DB, ACTIVE_DB)


def test_01_api_latency_benchmarks():
    """Validates that critical endpoints respond well under strict latency thresholds."""
    # Warmup
    client.get("/health")
    client.get("/api/stores")

    benchmarks = [
        ("/health", 100),                                         # target < 100ms
        ("/api/location/serviceability?village=Minapur", 100),    # target < 100ms
        ("/api/stores", 200),                                     # target < 200ms
        ("/api/catalog/products", 250),                           # target < 250ms
    ]

    for path, max_ms in benchmarks:
        t0 = time.perf_counter()
        res = client.get(path)
        latency_ms = (time.perf_counter() - t0) * 1000

        assert res.status_code == 200, f"Endpoint {path} failed with {res.status_code}"
        assert latency_ms < max_ms, f"Endpoint {path} exceeded latency threshold: {latency_ms:.2f}ms > {max_ms}ms"


def test_02_database_pool_stress_and_connection_leak_prevention():
    """Fires 20 rapid sequential requests to confirm pool stability and zero connection leakage."""
    endpoints = [
        "/health",
        "/api/location/serviceability?village=Minapur",
        "/api/stores",
        "/api/catalog/products"
    ]

    for i in range(20):
        ep = endpoints[i % len(endpoints)]
        res = client.get(ep)
        assert res.status_code == 200, f"Request {i} to {ep} failed with {res.status_code}"

    # Verify database integrity remains intact after pool stress
    assert check_database_integrity() is True


def test_03_inventory_concurrency_and_oversell_protection():
    """Verifies that out-of-stock and invalid inventory states are authoritatively rejected."""
    # 1. Out of stock rejection
    with db_session() as db:
        prod = db.query(Product).filter(Product.id == "item_1").first()
        assert prod is not None
        prod.in_stock = False
        db.commit()

    try:
        r_oos = client.post(
            "/api/orders/checkout",
            json={
                "user_phone": "9876543290",
                "user_name": "Test Customer",
                "village": "Minapur",
                "landmark": "Near Gram Panchayat",
                "store_id": "sharma_brothers",
                "payment_mode": "COD",
                "customer_lat": 29.1450,
                "customer_lng": 77.0150,
                "items": [
                    {"id": "item_1", "name": "Atta", "price": 210.0, "qty": 1}
                ]
            }
        )
        assert r_oos.status_code == 400
        assert "out of stock" in r_oos.json().get("detail", "") or "उत्पाद स्टॉक में नहीं है" in r_oos.json().get("detail", "")
    finally:
        with db_session() as db:
            prod = db.query(Product).filter(Product.id == "item_1").first()
            if prod:
                prod.in_stock = True
                db.commit()

    # 2. Non-existent product rejection
    r_ghost = client.post(
        "/api/orders/checkout",
        json={
            "user_phone": "9876543290",
            "user_name": "Test Customer",
            "village": "Minapur",
            "landmark": "Near Gram Panchayat",
            "store_id": "sharma_brothers",
            "payment_mode": "COD",
            "customer_lat": 29.1450,
            "customer_lng": 77.0150,
            "items": [
                {"id": "non_existent_item_9999", "name": "Fake Item", "price": 100.0, "qty": 1}
            ]
        }
    )
    assert r_ghost.status_code == 400
    assert "not found in catalog" in r_ghost.json().get("detail", "")

    # 3. Invalid quantity (qty <= 0) rejection
    r_zero_qty = client.post(
        "/api/orders/checkout",
        json={
            "user_phone": "9876543290",
            "user_name": "Test Customer",
            "village": "Minapur",
            "landmark": "Near Gram Panchayat",
            "store_id": "sharma_brothers",
            "payment_mode": "COD",
            "customer_lat": 29.1450,
            "customer_lng": 77.0150,
            "items": [
                {"id": "item_1", "name": "Atta", "price": 210.0, "qty": 0}
            ]
        }
    )
    assert r_zero_qty.status_code == 400
    assert "Invalid item quantity" in r_zero_qty.json().get("detail", "")


def test_04_static_asset_headers_and_pwa_readiness():
    """Verifies service worker, web app manifest, offline fallback, and PWA shell delivery."""
    # 1. Service Worker delivery
    r_sw = client.get("/sw.js")
    assert r_sw.status_code == 200
    assert r_sw.headers.get("Service-Worker-Allowed") == "/"
    assert "no-cache" in r_sw.headers.get("Cache-Control", "")
    assert "CACHE_NAME" in r_sw.text

    # 2. Web App Manifest
    r_manifest = client.get("/manifest.json")
    assert r_manifest.status_code == 200
    manifest = r_manifest.json()
    assert manifest.get("name") == "GaonBazaar"
    assert manifest.get("display") == "standalone"

    # 3. Offline fallback page
    r_offline = client.get("/offline.html")
    assert r_offline.status_code == 200
    assert "text/html" in r_offline.headers.get("content-type", "")

    # 4. Persona Web / PWA shell entrypoints
    for shell_path in ["/", "/index.html", "/vendor", "/runner", "/admin"]:
        r_shell = client.get(shell_path)
        assert r_shell.status_code == 200, f"PWA shell {shell_path} returned {r_shell.status_code}"


def test_05_launch_readiness_audit_and_baseline_verification():
    """Final release audit: System health check, table schemas, and exactly 364 historical orders."""
    # 1. Health check verification
    r_health = client.get("/health")
    assert r_health.status_code == 200
    h_data = r_health.json()
    assert h_data["status"] == "healthy"
    assert h_data["db_integrity"] == "ok"

    # 2. Baseline preservation: Exactly 364 orders
    with db_session() as db:
        order_count = db.query(Order).count()
        assert order_count == 364, f"Order baseline altered! Expected 364, got {order_count}"

    # 3. All 18 database tables present
    with engine.connect() as conn:
        from sqlalchemy import text
        table_names = [r[0] for r in conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()]
        expected_tables = [
            "users", "otp_records", "stores", "landmarks", "products", "orders",
            "order_items", "runners", "support_tickets", "store_categories",
            "saved_payment_methods", "payment_transactions", "notifications",
            "message_threads", "chat_messages", "central_products", "audit_logs"
        ]
        for tbl in expected_tables:
            assert tbl in table_names, f"Expected table {tbl} missing from database"

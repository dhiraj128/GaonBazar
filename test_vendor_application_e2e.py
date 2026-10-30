import os
import sys
from urllib.parse import quote
import pytest
from fastapi.testclient import TestClient

sys.stdout.reconfigure(encoding="utf-8")
os.environ["ENVIRONMENT"] = "development"

from backend.main import app
from backend.database import get_db
from backend.models import Order, Store, Product, AuditLog
from backend.security import issue_vendor_token, issue_user_token, issue_admin_token

client = TestClient(app)


def test_01_vendor_auth_and_isolation():
    """Vendor can access their own store profile and orders; cross-store access is blocked."""
    sharma_token = issue_vendor_token("sharma_brothers", "9876543210")
    headers_sharma = {"Authorization": f"Bearer {sharma_token}"}

    # 1. Access own store profile -> 200
    r_self = client.get("/api/vendor/profile?store_id=sharma_brothers", headers=headers_sharma)
    assert r_self.status_code == 200
    profile = r_self.json()
    assert profile["store_id"] == "sharma_brothers"
    assert "name" in profile
    assert "village" in profile

    # 2. Access another vendor's store -> 403
    r_cross = client.get("/api/vendor/profile?store_id=kisan_seva", headers=headers_sharma)
    assert r_cross.status_code == 403, f"Expected 403 for cross-store profile access, got {r_cross.status_code}"

    # 3. Customer token trying to access vendor profile -> 403
    cust_token = issue_user_token(999, "9876543219")
    r_cust = client.get("/api/vendor/profile?store_id=sharma_brothers", headers={"Authorization": f"Bearer {cust_token}"})
    assert r_cust.status_code == 403


def test_02_vendor_order_lifecycle():
    """Vendor advances order through Stage 2 (Accepted) and Stage 3 (Packed). Cannot mark Delivered."""
    sharma_token = issue_vendor_token("sharma_brothers", "9876543210")
    headers = {"Authorization": f"Bearer {sharma_token}"}

    # Find an existing order for sharma_brothers
    orders_res = client.get("/api/vendor/stores/sharma_brothers/orders", headers=headers)
    assert orders_res.status_code == 200
    orders = orders_res.json()
    assert len(orders) > 0, "Expected at least one historical order for sharma_brothers"
    test_order = orders[0]
    encoded_order_id = quote(test_order["id"])

    # 1. Vendor Accept -> Stage 2
    r_accept = client.post(f"/api/vendor/orders/{encoded_order_id}/quick-action?action=accept", headers=headers)
    assert r_accept.status_code == 200
    assert r_accept.json()["timeline_stage"] == 2
    assert "Accepted" in r_accept.json()["status"]

    # 2. Vendor Pack -> Stage 3
    r_pack = client.post(f"/api/vendor/orders/{encoded_order_id}/quick-action?action=pack", headers=headers)
    assert r_pack.status_code == 200
    assert r_pack.json()["timeline_stage"] == 3
    assert "Ready" in r_pack.json()["status"]

    # 3. Vendor cannot mark Delivered -> 403 (enforced doorstep OTP runner requirement)
    r_deliv = client.post(f"/api/vendor/orders/{encoded_order_id}/quick-action?action=deliver", headers=headers)
    assert r_deliv.status_code == 403

    # Reset order back to original stage to preserve demo state
    client.post(
        f"/api/vendor/orders/{encoded_order_id}/status",
        headers=headers,
        json={"stage": test_order.get("timeline_stage", 1), "note": "Reverting test state"}
    )


def test_03_vendor_inventory_management():
    """Vendor can view inventory, toggle stock, update selling price, and sync with catalog."""
    sharma_token = issue_vendor_token("sharma_brothers", "9876543210")
    headers = {"Authorization": f"Bearer {sharma_token}"}

    # 1. View inventory
    inv_res = client.get("/api/vendor/inventory?store_id=sharma_brothers", headers=headers)
    assert inv_res.status_code == 200
    items = inv_res.json()
    assert len(items) > 0, "Expected inventory items for sharma_brothers"
    target_item = items[0]
    prod_id = target_item["id"]
    original_price = target_item["price"]

    # 2. Update stock & price
    new_price = round(original_price + 5.0, 2)
    update_res = client.put(
        f"/api/vendor/inventory/{prod_id}",
        headers=headers,
        json={"price": new_price, "in_stock": True, "stock_qty": 75}
    )
    assert update_res.status_code == 200
    updated_data = update_res.json()
    assert updated_data["price"] == new_price
    assert updated_data["stock_qty"] == 75

    # 3. Check customer catalog reflection
    cat_res = client.get(f"/api/catalog/products/{prod_id}")
    if cat_res.status_code == 200:
        cat_data = cat_res.json()
        assert cat_data["price"] == new_price

    # Revert price back to original
    client.put(
        f"/api/vendor/inventory/{prod_id}",
        headers=headers,
        json={"price": original_price, "in_stock": True, "stock_qty": 50}
    )


def test_04_vendor_ledger_and_payout_settings():
    """Vendor can access earnings ledger and safely update payout bank details."""
    sharma_token = issue_vendor_token("sharma_brothers", "9876543210")
    headers = {"Authorization": f"Bearer {sharma_token}"}

    # 1. Fetch vendor ledger
    r_ledger = client.get("/api/vendor/stores/sharma_brothers/ledger", headers=headers)
    assert r_ledger.status_code == 200
    ledger = r_ledger.json()
    assert "total_orders" in ledger
    assert "gross_sales" in ledger
    assert "net_dukandaar_payout" in ledger
    assert "completed_orders_count" in ledger

    # 2. Update bank payout details
    r_bank = client.put(
        "/api/vendor/bank?store_id=sharma_brothers",
        headers=headers,
        json={
            "payout_mode": "bank",
            "account_holder": "Sharma Brothers Kirana",
            "account_number": "918273645012",
            "ifsc": "SBIN0001234"
        }
    )
    assert r_bank.status_code == 200
    assert r_bank.json()["success"] is True

    # 3. Fetch payout settings and verify account masking
    r_settings = client.get("/api/vendor/stores/sharma_brothers/payout-settings", headers=headers)
    assert r_settings.status_code == 200
    settings_data = r_settings.json()
    acc_masked = settings_data.get("account_number_masked", "")
    assert "••••" in acc_masked or "XXXX" in acc_masked or "..." in acc_masked, f"Account number should be masked: {acc_masked}"


import os
import sys
import shutil
from urllib.parse import quote
import pytest
from fastapi.testclient import TestClient

sys.stdout.reconfigure(encoding="utf-8")
os.environ["ENVIRONMENT"] = "development"

from backend.main import app
from backend.database import db_session, engine
from backend.models import Order, Store, User, Product, AuditLog
from backend.security import (
    issue_user_token,
    issue_vendor_token,
    issue_runner_token,
    issue_admin_token
)

client = TestClient(app)

BASELINE_DB = "scratch/phase1_clean_baseline.db"
ACTIVE_DB = "backend/gaonbazar.db"


@pytest.fixture(autouse=True, scope="module")
def database_baseline_guard():
    """Ensures exact 364 orders clean baseline is restored before and after integration suite."""
    if os.path.exists(BASELINE_DB):
        engine.dispose()
        shutil.copyfile(BASELINE_DB, ACTIVE_DB)
    yield
    if os.path.exists(BASELINE_DB):
        engine.dispose()
        shutil.copyfile(BASELINE_DB, ACTIVE_DB)


def test_01_complete_four_app_order_lifecycle():
    """
    Full end-to-end multi-role lifecycle:
    1. Customer places order (Stage 1: Order Placed).
    2. Vendor views order, accepts (Stage 2), and marks packed (Stage 3).
    3. Customer updates precise doorstep delivery GPS coordinates.
    4. Runner views mission queue and confirms store pickup (Stage 4).
    5. Runner verifies customer 4-digit OTP at doorstep (Stage 5: Delivered).
    6. Vendor ledger, Runner ledger, Admin reports, and Audit trail are reconciled.
    """
    cust_phone = "9876543210"
    cust_token = issue_user_token(1, cust_phone, "Ramesh Kumar")
    headers_cust = {"Authorization": f"Bearer {cust_token}"}

    vendor_store_id = "sharma_brothers"
    vendor_token = issue_vendor_token(vendor_store_id, "9876543211", "Sharma Brothers Kirana")
    headers_vendor = {"Authorization": f"Bearer {vendor_token}"}

    runner_id = "gm_1"
    runner_token = issue_runner_token(runner_id, "9876543212", "Kamal Singh")
    headers_runner = {"Authorization": f"Bearer {runner_token}"}

    admin_token = issue_admin_token("super_admin")
    headers_admin = {"Authorization": f"Bearer {admin_token}"}

    # -------------------------------------------------------------
    # STEP 1: Customer Places Order
    # -------------------------------------------------------------
    r_checkout = client.post(
        "/api/orders/checkout",
        json={
            "user_phone": cust_phone,
            "user_name": "Ramesh Kumar",
            "village": "Minapur",
            "landmark": "Near Gram Panchayat Bhawan",
            "store_id": vendor_store_id,
            "payment_mode": "COD",
            "customer_lat": 29.1450,
            "customer_lng": 77.0150,
            "items": [
                {"id": "item_1", "name": "Aashirvaad Chakki Atta", "price": 210.0, "qty": 1}
            ]
        }
    )
    assert r_checkout.status_code == 200, f"Checkout failed: {r_checkout.text}"
    checkout_data = r_checkout.json()
    order_id = checkout_data["order_id"]
    delivery_otp = checkout_data["delivery_otp"]

    assert order_id.startswith("#RUR-")
    assert checkout_data["status"] == "Order Placed"
    assert checkout_data["timeline_stage"] == 1
    assert checkout_data["subtotal"] == 210.0
    assert checkout_data["platform_fee"] == 3.0
    assert checkout_data["delivery_fee"] == 15.0
    assert checkout_data["total_amount"] == 228.0
    assert len(delivery_otp) == 4

    encoded_order_id = quote(order_id)

    # -------------------------------------------------------------
    # STEP 2: Vendor Receives Order, Accepts (Stage 2), and Packs (Stage 3)
    # -------------------------------------------------------------
    r_v_orders = client.get(f"/api/vendor/stores/{vendor_store_id}/orders", headers=headers_vendor)
    assert r_v_orders.status_code == 200
    vendor_orders = r_v_orders.json()
    found_order = next((o for o in vendor_orders if o["id"] == order_id), None)
    assert found_order is not None, "Vendor order queue must contain newly placed order"

    # Vendor accepts order -> Stage 2
    r_accept = client.post(f"/api/vendor/orders/{encoded_order_id}/quick-action?action=accept", headers=headers_vendor)
    assert r_accept.status_code == 200
    assert r_accept.json()["timeline_stage"] == 2

    # Vendor packs order -> Stage 3
    r_pack = client.post(f"/api/vendor/orders/{encoded_order_id}/quick-action?action=pack", headers=headers_vendor)
    assert r_pack.status_code == 200
    assert r_pack.json()["timeline_stage"] == 3

    # -------------------------------------------------------------
    # STEP 3: Customer Shares Updated Doorstep GPS Coordinates
    # -------------------------------------------------------------
    r_loc = client.put(
        f"/api/orders/{encoded_order_id}/delivery-location",
        headers=headers_cust,
        json={
            "customer_lat": 29.1455,
            "customer_lng": 77.0155,
            "landmark": "Exact Doorstep: Blue Gate beside Minapur High School"
        }
    )
    assert r_loc.status_code == 200
    loc_data = r_loc.json()
    assert loc_data["customer_lat"] == 29.1455
    assert loc_data["customer_lng"] == 77.0155
    assert "Blue Gate" in loc_data["landmark"]

    # -------------------------------------------------------------
    # STEP 4: Runner Shift Online, Discover Mission, and Confirm Pickup (Stage 4)
    # -------------------------------------------------------------
    r_shift = client.post("/api/runner/shift", headers=headers_runner, json={"runner_id": "gm_1", "is_online": True})
    assert r_shift.status_code == 200

    r_missions = client.get("/api/runner/missions", headers=headers_runner)
    assert r_missions.status_code == 200
    missions = r_missions.json()
    mission = next((m for m in missions if m["id"] == order_id), None)
    assert mission is not None, "Runner missions queue must include packed order"
    # Verify delivery_otp is NOT exposed to runner in mission queue
    assert mission.get("delivery_otp") is None

    # Runner confirms store pickup -> Stage 4
    r_pickup = client.post(f"/api/runner/orders/{encoded_order_id}/pickup", headers=headers_runner)
    assert r_pickup.status_code == 200
    assert r_pickup.json()["timeline_stage"] == 4
    assert r_pickup.json()["status"] == "Out for Delivery"

    # -------------------------------------------------------------
    # STEP 5: Runner Handover with 4-Digit OTP (Stage 5: Delivered)
    # -------------------------------------------------------------
    # Rejection on bad OTP
    r_bad = client.post(
        f"/api/runner/orders/{encoded_order_id}/verify-otp",
        headers=headers_runner,
        json={"otp": "0000"}
    )
    assert r_bad.status_code == 400

    # Successful verification with valid OTP
    r_deliver = client.post(
        f"/api/runner/orders/{encoded_order_id}/verify-otp",
        headers=headers_runner,
        json={"otp": delivery_otp}
    )
    assert r_deliver.status_code == 200
    deliv_data = r_deliver.json()
    assert deliv_data["timeline_stage"] == 5
    assert deliv_data["status"] == "Delivered"

    # -------------------------------------------------------------
    # STEP 6: Multi-App Financial & Ledger Reconciliation
    # -------------------------------------------------------------
    # 1. Vendor ledger reflects order
    r_v_ledger = client.get(f"/api/vendor/stores/{vendor_store_id}/ledger", headers=headers_vendor)
    assert r_v_ledger.status_code == 200
    v_ledger = r_v_ledger.json()
    assert "gross_sales" in v_ledger
    assert "total_orders" in v_ledger
    assert "net_dukandaar_payout" in v_ledger

    # 2. Runner ledger reflects delivery
    r_r_ledger = client.get("/api/runner/ledger", headers=headers_runner)
    assert r_r_ledger.status_code == 200
    r_ledger = r_r_ledger.json()
    assert r_ledger["completed_today"] > 0
    assert r_ledger["total_earnings"] > 0.0

    # 3. Super Admin orders report includes completed order
    r_adm_rep = client.get("/api/admin/reports/orders?format=json", headers=headers_admin)
    assert r_adm_rep.status_code == 200
    admin_orders = r_adm_rep.json()["orders"]
    matching_adm = next((o for o in admin_orders if o["order_id"] == order_id), None)
    assert matching_adm is not None
    assert matching_adm["status"] == "Delivered"
    assert matching_adm["total_amount"] == 228.0

    # 4. Super Admin audit logs confirm full trace
    with db_session() as db:
        logs = db.query(AuditLog).filter(AuditLog.target_id == order_id).all()
        actions = [log.action for log in logs]
        assert "VENDOR_ORDER_ACCEPT" in actions
        assert "VENDOR_ORDER_PACK" in actions
        assert "RUNNER_ORDER_PICKUP" in actions
        assert "RUNNER_DELIVERY_HANDOVER" in actions
        assert "CUSTOMER_LOCATION_UPDATE" in actions


def test_02_geofence_boundary_and_pilot_rejection():
    """Orders with delivery coordinates > 8.0 km from store are rejected with HTTP 400."""
    r = client.post(
        "/api/orders/checkout",
        json={
            "user_phone": "9876543299",
            "user_name": "Far Away User",
            "village": "Distant Outpost",
            "landmark": "Beyond Boundary",
            "store_id": "sharma_brothers",
            "payment_mode": "COD",
            # ~24 km away from store
            "customer_lat": 29.3500,
            "customer_lng": 77.0100,
            "items": [
                {"id": "item_1", "name": "Atta", "price": 210.0, "qty": 1}
            ]
        }
    )
    assert r.status_code == 400
    err_detail = r.json().get("detail", "")
    assert "Outside delivery zone" in err_detail or "exceeds 8.0 km" in err_detail


def test_03_price_tampering_and_mov_defense():
    """Client-side price alterations are ignored; minimum order value is strictly enforced."""
    # 1. Price tampering defense
    r_tamper = client.post(
        "/api/orders/checkout",
        json={
            "user_phone": "9876543298",
            "user_name": "Tamper Test",
            "village": "Minapur",
            "landmark": "Market Crossing",
            "store_id": "sharma_brothers",
            "payment_mode": "COD",
            "customer_lat": 29.1450,
            "customer_lng": 77.0150,
            "items": [
                # Client attempts to pay ₹5.00 for ₹210.00 item
                {"id": "item_1", "name": "Aashirvaad Atta", "price": 5.0, "qty": 1}
            ]
        }
    )
    assert r_tamper.status_code == 200
    # Server calculated subtotal strictly from DB product catalog (₹210.00)
    assert r_tamper.json()["subtotal"] == 210.0
    assert r_tamper.json()["total_amount"] == 228.0

    # 2. Minimum Order Value (MOV < ₹99) defense
    r_mov = client.post(
        "/api/orders/checkout",
        json={
            "user_phone": "9876543298",
            "user_name": "Low Value Test",
            "village": "Minapur",
            "landmark": "Market Crossing",
            "store_id": "sharma_brothers",
            "payment_mode": "COD",
            "customer_lat": 29.1450,
            "customer_lng": 77.0150,
            "items": [
                # Tata Salt Iodized is ₹24.00, below MOV ₹99
                {"id": "item_3", "name": "Tata Salt", "price": 24.0, "qty": 1}
            ]
        }
    )
    assert r_mov.status_code == 400
    assert "Minimum order is ₹99" in r_mov.json().get("detail", "") or "कम से कम ₹99" in r_mov.json().get("detail", "")


def test_04_cross_role_security_and_privilege_isolation():
    """Strict privilege boundaries between Customer, Vendor, Runner, and Super Admin personas."""
    cust_token = issue_user_token(10, "9876543250", "Regular Customer")
    headers_cust = {"Authorization": f"Bearer {cust_token}"}

    vendor_token = issue_vendor_token("sharma_brothers", "9876543211", "Sharma Brothers")
    headers_vendor = {"Authorization": f"Bearer {vendor_token}"}

    runner_token = issue_runner_token("gm_1", "9876543212", "Kamal Singh")
    headers_runner = {"Authorization": f"Bearer {runner_token}"}

    # 1. Vendor cannot bypass Runner doorstep OTP delivery
    r_bypass = client.post(
        "/api/vendor/orders/%23RUR-1001/quick-action?action=deliver",
        headers=headers_vendor
    )
    assert r_bypass.status_code == 403

    # 2. Ordinary customer cannot access Super Admin reports
    r_adm_rep = client.get("/api/admin/reports/orders", headers=headers_cust)
    assert r_adm_rep.status_code == 403

    # 3. Ordinary customer cannot access Super Admin audit logs
    r_adm_audit = client.get("/api/admin/audit-logs", headers=headers_cust)
    assert r_adm_audit.status_code == 403

    # 4. Runner cannot modify vendor inventory
    r_inv = client.put(
        "/api/vendor/inventory/item_1",
        headers=headers_runner,
        json={"price": 190.0}
    )
    assert r_inv.status_code == 403


def test_05_pre_pickup_order_cancellation_flow():
    """Customer can cancel order before pickup; cancelled orders are excluded from Runner mission queue."""
    cust_phone = "9876543277"
    cust_token = issue_user_token(77, cust_phone, "Cancel Test User")
    headers_cust = {"Authorization": f"Bearer {cust_token}"}

    runner_token = issue_runner_token("gm_1", "9876543212", "Kamal Singh")
    headers_runner = {"Authorization": f"Bearer {runner_token}"}

    # 1. Place order
    r_order = client.post(
        "/api/orders/checkout",
        json={
            "user_phone": cust_phone,
            "user_name": "Cancel Test User",
            "village": "Minapur",
            "landmark": "Near Old Banyan Tree",
            "store_id": "sharma_brothers",
            "payment_mode": "COD",
            "customer_lat": 29.1450,
            "customer_lng": 77.0150,
            "items": [
                {"id": "item_1", "name": "Atta", "price": 210.0, "qty": 1}
            ]
        }
    )
    assert r_order.status_code == 200
    cancel_order_id = r_order.json()["order_id"]
    encoded_id = quote(cancel_order_id)

    # 2. Customer cancels order
    r_cancel = client.post(
        f"/api/orders/{encoded_id}/cancel",
        headers=headers_cust,
        json={"reason": "Ordered by mistake / गलती से ऑर्डर हो गया"}
    )
    assert r_cancel.status_code == 200
    c_data = r_cancel.json()
    assert c_data["status"] == "Cancelled"
    assert c_data["timeline_stage"] in [0, -1]

    # 3. Runner missions queue excludes cancelled order
    r_missions = client.get("/api/runner/missions", headers=headers_runner)
    assert r_missions.status_code == 200
    missions = r_missions.json()
    assert not any(m["id"] == cancel_order_id for m in missions)

    # 4. Runner cannot confirm pickup on cancelled order -> 400
    r_bad_pickup = client.post(f"/api/runner/orders/{encoded_id}/pickup", headers=headers_runner)
    assert r_bad_pickup.status_code == 400
    assert "not yet packed and ready" in r_bad_pickup.json().get("detail", "")

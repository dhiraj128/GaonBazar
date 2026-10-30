"""
test_phase3a_security_data_integrity.py
Comprehensive Phase 3A Security, IDOR Hardening & Data Integrity Verification Suite for GaonBazaar.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Ensure isolated test database
os.environ["ENVIRONMENT"] = "development"
os.environ["TEST_MODE"] = "1"
os.environ["GAONBAZAR_REQUIRE_POSTGRES"] = "0"
os.environ["ADMIN_SECRET_KEY"] = "gaonbazar_super_admin_secret_2026"
os.environ["JWT_SECRET"] = "gb-bankgrade-production-secret-9a8b7c6d5e4f3a2b1c-2026"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from backend.main import app
from backend.database import get_db, Base
from backend.models import (
    User, Store, Product, Order, OrderItem, ArchivedOrderItem,
    PaymentTransaction, ArchivedPaymentTransaction, Runner, SupportTicket
)
from backend.security import (
    issue_user_token, issue_vendor_token, issue_runner_token, issue_admin_token
)
from backend.schema_migrator import repair_database_schema

client = TestClient(app)

def run_phase3a_audit():
    print("=" * 80)
    print("GAONBAZAR PHASE 3A: SECURITY & DATA INTEGRITY VERIFICATION SUITE")
    print("=" * 80)

    checks_passed = 0
    checks_total = 0

    def assert_check(title: str, condition: bool, detail: str = ""):
        nonlocal checks_passed, checks_total
        checks_total += 1
        if condition:
            checks_passed += 1
            print(f"  [PASS] {title}")
        else:
            print(f"  [FAIL] {title} - {detail}")
            raise AssertionError(f"Check failed: {title} ({detail})")

    # -------------------------------------------------------------------------
    # PART 1: DATA INTEGRITY & RECONCILIATION AUDIT
    # -------------------------------------------------------------------------
    print("\n--- 1. Relational Integrity & Historical Data Ledger ---")
    
    # Run repair_database_schema to align schema and repair historical records
    from backend.database import engine
    repair_summary = repair_database_schema(engine)
    assert_check("Database schema & integrity repair executed cleanly", repair_summary.get("status") == "success")

    # Check inspection endpoint via admin
    admin_token = issue_admin_token("super_admin")
    insp_resp = client.get("/api/admin/database-inspection", headers={"Authorization": f"Bearer {admin_token}"})
    assert_check("Admin database inspection responds 200", insp_resp.status_code == 200)
    insp_data = insp_resp.json()

    integrity = insp_data.get("integrity_checks", {})
    assert_check("Zero orphaned orders (missing user_id)", integrity.get("orphan_orders") == 0, f"got {integrity.get('orphan_orders')}")
    assert_check("Zero orphaned order_items", integrity.get("orphan_order_items") == 0, f"got {integrity.get('orphan_order_items')}")
    assert_check("Zero orphaned payment_transactions", integrity.get("orphan_payment_transactions") == 0, f"got {integrity.get('orphan_payment_transactions')}")

    finances = insp_data.get("financial_volumes", {})
    t_counts = insp_data.get("table_counts", {})
    
    total_items = t_counts.get("order_items", 0) + t_counts.get("archived_order_items", 0)
    assert_check("100% Order Items Retained (active + archived = 2,085)", total_items >= 2085, f"got {total_items}")

    total_pmts = t_counts.get("payment_transactions", 0) + t_counts.get("archived_payment_transactions", 0)
    assert_check("100% Payment Transactions Retained (active + archived = 64)", total_pmts >= 64, f"got {total_pmts}")

    total_pmt_val = finances.get("total_reconciled_payments_sum_inr", 0.0)
    assert_check("100% Financial Ledger Volume Preserved (>= Rs. 18,112.00 baseline)", total_pmt_val >= 18112.0, f"got {total_pmt_val}")

    # -------------------------------------------------------------------------
    # PART 2: ADMIN METRICS SEGREGATION (LIVE VS DEMO)
    # -------------------------------------------------------------------------
    print("\n--- 2. Admin Analytics & Historical Demo Data Segregation ---")
    metrics_resp = client.get("/api/admin/metrics", headers={"Authorization": f"Bearer {admin_token}"})
    assert_check("Admin metrics responds 200", metrics_resp.status_code == 200)
    metrics = metrics_resp.json()
    assert_check("Admin metrics includes live_orders_count", "live_orders_count" in metrics)
    assert_check("Admin metrics includes demo_orders_count", "demo_orders_count" in metrics)
    assert_check("Admin metrics includes live_gmv", "live_gmv" in metrics)
    assert_check("Admin metrics includes demo_gmv", "demo_gmv" in metrics)
    assert_check("Total orders equals live + demo orders", metrics.get("total_orders") == (metrics.get("live_orders_count") + metrics.get("demo_orders_count")))
    print(f"      [Live: {metrics.get('live_orders_count')} orders (Rs.{metrics.get('live_gmv'):.2f}) | Historical Demo: {metrics.get('demo_orders_count')} orders (Rs.{metrics.get('demo_gmv'):.2f})]")

    # -------------------------------------------------------------------------
    # PART 3: IDOR & BOLA HARDENING ACROSS SENSITIVE ROUTES
    # -------------------------------------------------------------------------
    print("\n--- 3. IDOR / BOLA Route-Level Authorization Hardening ---")
    
    # Setup test users and orders
    cust_a_phone = "9876543210"
    cust_b_phone = "9876543299"
    tok_cust_a = issue_user_token(user_id=72, phone=cust_a_phone, name="Customer A")
    tok_cust_b = issue_user_token(user_id=99, phone=cust_b_phone, name="Customer B")
    tok_runner_1 = issue_runner_token(runner_id="gm_1", phone="9876543220")
    tok_runner_2 = issue_runner_token(runner_id="gm_2", phone="9876543221")

    from backend.database import db_session
    test_ord_id = "ORD-PH3A-TEST-01"
    with db_session() as db:
        db.query(Order).filter(Order.id == test_ord_id).delete()
        test_order = Order(
            id=test_ord_id,
            user_phone=cust_a_phone,
            user_name="Customer A",
            user_id=72,
            village="Rampur",
            landmark="Near Well",
            store_id="sharma_brothers",
            store_name="Sharma Brothers",
            subtotal=200.0,
            total_amount=215.0,
            payment_mode="COD",
            status="Packed",
            timeline_stage=3,
            delivery_otp="4821",
            runner_id="gm_1",
            data_origin="live"
        )
        db.add(test_order)
        db.commit()

    try:
        # 3.1 Order Cancellation IDOR
        # Attacker Customer B attempts to cancel Customer A's order
        res_cancel_b = client.post(
            f"/api/orders/{test_ord_id}/cancel",
            json={"reason": "Malicious cancellation attempt"},
            headers={"Authorization": f"Bearer {tok_cust_b}"}
        )
        assert_check("Customer B blocked from cancelling Customer A's order (HTTP 403)", res_cancel_b.status_code == 403)

        # Runner attempts to cancel customer order
        res_cancel_r = client.post(
            f"/api/orders/{test_ord_id}/cancel",
            json={"reason": "Runner cancelling order"},
            headers={"Authorization": f"Bearer {tok_runner_1}"}
        )
        assert_check("Runner blocked from cancelling Customer order (HTTP 403)", res_cancel_r.status_code == 403)

        # 3.2 Order Status IDOR
        # Customer B attempts to view Customer A's order status
        res_status_b = client.get(
            f"/api/orders/{test_ord_id}/status",
            headers={"Authorization": f"Bearer {tok_cust_b}"}
        )
        assert_check("Customer B blocked from viewing Customer A's order (HTTP 403)", res_status_b.status_code == 403)

        # Owner Customer A views own order status
        res_status_a = client.get(
            f"/api/orders/{test_ord_id}/status",
            headers={"Authorization": f"Bearer {tok_cust_a}"}
        )
        assert_check("Customer A allowed to view own order status (HTTP 200)", res_status_a.status_code == 200)

        # 3.3 Runner Shift Toggle IDOR
        # Runner 2 attempts to toggle shift of Runner 1
        res_shift_idor = client.post(
            "/api/runner/shift",
            json={"runner_id": "gm_1", "is_online": False},
            headers={"Authorization": f"Bearer {tok_runner_2}"}
        )
        assert_check("Runner 2 blocked from toggling shift of Runner 1 (HTTP 403)", res_shift_idor.status_code == 403)

        # Runner 1 toggles own shift
        res_shift_own = client.post(
            "/api/runner/shift",
            json={"runner_id": "gm_1", "is_online": True},
            headers={"Authorization": f"Bearer {tok_runner_1}"}
        )
        assert_check("Runner 1 allowed to toggle own shift (HTTP 200)", res_shift_own.status_code == 200)

        # 3.4 Runner Pickup IDOR
        # Runner 2 attempts to pick up order assigned to Runner 1
        res_pickup_idor = client.post(
            f"/api/runner/orders/{test_ord_id}/pickup",
            headers={"Authorization": f"Bearer {tok_runner_2}"}
        )
        assert_check("Runner 2 blocked from picking up order assigned to Runner 1 (HTTP 403)", res_pickup_idor.status_code == 403)

        # Runner 1 successfully picks up assigned order
        res_pickup_own = client.post(
            f"/api/runner/orders/{test_ord_id}/pickup",
            headers={"Authorization": f"Bearer {tok_runner_1}"}
        )
        assert_check("Runner 1 successfully picks up assigned order (HTTP 200)", res_pickup_own.status_code == 200)

        # 3.5 Delivery Completion IDOR
        # Customer B attempts to mark order delivered
        res_deliv_cust = client.post(
            f"/api/orders/{test_ord_id}/deliver",
            headers={"Authorization": f"Bearer {tok_cust_b}"}
        )
        assert_check("Customer blocked from calling /api/orders/{id}/deliver (HTTP 403)", res_deliv_cust.status_code == 403)

    finally:
        with db_session() as db:
            db.query(Order).filter(Order.id == test_ord_id).delete()
            db.commit()

    # -------------------------------------------------------------------------
    # PART 4: SUMMARY & VERDICT
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print(f"PHASE 3A SECURITY & DATA INTEGRITY SUMMARY: {checks_passed}/{checks_total} CHECKS PASSED (100.0%)")
    print("=" * 80)
    return checks_passed == checks_total

if __name__ == "__main__":
    success = run_phase3a_audit()
    if not success:
        sys.exit(1)

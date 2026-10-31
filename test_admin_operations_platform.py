import os
import sys
import csv
import io
import pytest
from fastapi.testclient import TestClient

sys.stdout.reconfigure(encoding="utf-8")
os.environ["ENVIRONMENT"] = "development"

from backend.main import app
from backend.database import get_db, record_audit_log
from backend.models import Order, Store, Runner, SupportTicket, AuditLog
from backend.security import issue_admin_token, issue_user_token, issue_vendor_token, issue_runner_token, get_admin_secret_key

client = TestClient(app)


def test_01_admin_rbac_protection():
    """Unauthenticated and unauthorized roles must be rejected from admin endpoints."""
    # 1. Unauthenticated -> 401
    r_unauth = client.get("/api/admin/metrics")
    assert r_unauth.status_code == 401, f"Expected 401, got {r_unauth.status_code}"

    # 2. Customer token -> 403
    cust_token = issue_user_token(999, "9876543210")
    r_cust = client.get("/api/admin/metrics", headers={"Authorization": f"Bearer {cust_token}"})
    assert r_cust.status_code == 403, f"Expected 403 for customer, got {r_cust.status_code}"

    # 3. Vendor token -> 403
    vendor_token = issue_vendor_token("store_test_01", "9876543211")
    r_vendor = client.get("/api/admin/metrics", headers={"Authorization": f"Bearer {vendor_token}"})
    assert r_vendor.status_code == 403, f"Expected 403 for vendor, got {r_vendor.status_code}"

    # 4. Runner token -> 403
    runner_token = issue_runner_token("runner_test_01", "9876543212")
    r_runner = client.get("/api/admin/metrics", headers={"Authorization": f"Bearer {runner_token}"})
    assert r_runner.status_code == 403, f"Expected 403 for runner, got {r_runner.status_code}"

    # 5. Valid Admin token -> 200
    admin_token = issue_admin_token("admin_test_platform")
    r_admin = client.get("/api/admin/metrics", headers={"Authorization": f"Bearer {admin_token}"})
    assert r_admin.status_code == 200
    data = r_admin.json()
    assert "total_gmv" in data
    assert "total_orders" in data
    assert "total_vendors" in data
    assert "total_runners" in data


def test_02_admin_login_and_audit_trail():
    """Admin login authenticates with credentials and writes immutable audit log."""
    secret = get_admin_secret_key()
    
    # Failed login -> 401
    r_fail = client.post("/api/admin/login", json={"admin_key": "wrong_key", "username": "admin"})
    assert r_fail.status_code == 401

    # Successful login -> 200 and audit log entry
    r_ok = client.post("/api/admin/login", json={"admin_key": secret, "username": "superadmin_tester"})
    assert r_ok.status_code == 200
    res_data = r_ok.json()
    assert res_data["success"] is True
    assert res_data["role"] == "admin"
    token = res_data["token"]
    assert token is not None

    # Verify audit log was created
    r_logs = client.get("/api/admin/audit-logs?action=ADMIN_LOGIN", headers={"Authorization": f"Bearer {token}"})
    assert r_logs.status_code == 200
    logs_data = r_logs.json()
    assert logs_data["total"] >= 1
    found_login = any(l["action"] == "ADMIN_LOGIN" for l in logs_data["logs"])
    assert found_login, "ADMIN_LOGIN audit log not found"


def test_03_admin_vendor_and_runner_lifecycle_audit():
    """Privileged actions (approve/reject/block) must update state and record audit log."""
    admin_token = issue_admin_token("audit_admin")
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Vendor approval
    r_approve_v = client.post("/api/admin/vendors/sharma_brothers/approve", headers=headers)
    assert r_approve_v.status_code == 200
    assert r_approve_v.json()["status"] == "approved"

    # 2. Runner approval
    r_approve_r = client.post("/api/admin/runners/gm_1/approve", headers=headers)
    assert r_approve_r.status_code == 200
    assert r_approve_r.json()["status"] == "approved"

    # 3. Payout verification status update
    r_payout = client.post(
        "/api/admin/payout-verifications/vendor/sharma_brothers/status",
        headers=headers,
        json={"status": "verified"}
    )
    assert r_payout.status_code == 200
    assert r_payout.json()["status"] == "verified"

    # Verify audit logs captured these actions
    r_logs = client.get("/api/admin/audit-logs?limit=20", headers=headers)
    assert r_logs.status_code == 200
    recent_actions = [l["action"] for l in r_logs.json()["logs"]]
    assert "APPROVE_VENDOR" in recent_actions
    assert "APPROVE_RUNNER" in recent_actions
    assert "UPDATE_PAYOUT_STATUS" in recent_actions


def test_04_admin_reports_orders_export():
    """Export orders report in both JSON and CSV formats."""
    admin_token = issue_admin_token("reports_admin")
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. JSON Export
    r_json = client.get("/api/admin/reports/orders?format=json&limit=50", headers=headers)
    assert r_json.status_code == 200
    data = r_json.json()
    assert "count" in data
    assert "total_gmv" in data
    assert "orders" in data
    assert isinstance(data["orders"], list)
    if data["orders"]:
        first_order = data["orders"][0]
        assert "order_id" in first_order
        assert "total_amount" in first_order
        assert "village" in first_order

    # 2. CSV Export
    r_csv = client.get("/api/admin/reports/orders?format=csv&limit=50", headers=headers)
    assert r_csv.status_code == 200
    assert "text/csv" in r_csv.headers.get("content-type", "")
    assert "filename=gaonbazar_orders_report.csv" in r_csv.headers.get("content-disposition", "")
    
    # Parse CSV content to verify columns
    csv_reader = csv.reader(io.StringIO(r_csv.text))
    header_row = next(csv_reader)
    expected_cols = ["order_id", "created_at", "user_phone", "store_id", "total_amount"]
    for col in expected_cols:
        assert col in header_row, f"Column {col} missing from orders CSV header"


def test_05_admin_reports_financials_export():
    """Export platform financials report in both JSON and CSV formats."""
    admin_token = issue_admin_token("financials_admin")
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. JSON Export
    r_json = client.get("/api/admin/reports/financials?format=json", headers=headers)
    assert r_json.status_code == 200
    fin_data = r_json.json()
    assert "total_gmv" in fin_data
    assert "vendor_payouts_total" in fin_data
    assert "runner_payouts_total" in fin_data
    assert "platform_profits_total" in fin_data
    assert "order_counts" in fin_data
    assert "gmv_distribution" in fin_data

    # 2. CSV Export
    r_csv = client.get("/api/admin/reports/financials?format=csv", headers=headers)
    assert r_csv.status_code == 200
    assert "text/csv" in r_csv.headers.get("content-type", "")
    csv_reader = csv.reader(io.StringIO(r_csv.text))
    header_row = next(csv_reader)
    assert header_row == ["metric", "value", "unit", "description"]
    rows = list(csv_reader)
    metrics = [r[0] for r in rows]
    assert "total_gmv" in metrics
    assert "vendor_payouts" in metrics
    assert "runner_payouts" in metrics
    assert "platform_profits" in metrics

"""
GaonBazaar Super Admin RBAC Security & Deny-by-Default Integration Tests
========================================================================
Verifies strict role-based access control (RBAC) across all /api/admin/* endpoints:
1. Deny-by-default (401 Unauthorized) when unauthenticated
2. Role segregation (403 Forbidden) when requested with Customer, Vendor, or Runner tokens
3. Authorized access (200 OK) with genuine Super Admin JWT token
4. Super Admin Login & JWT issuance via /api/admin/login
5. Cookie-based authentication support for admin web session
"""

import sys
import os
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.main import app
from backend.security import (
    issue_admin_token,
    issue_user_token,
    issue_vendor_token,
    issue_runner_token,
)

client = TestClient(app)

ADMIN_TOKEN = issue_admin_token("super_admin")
CUSTOMER_TOKEN = issue_user_token(1, "9876543210")
VENDOR_TOKEN = issue_vendor_token("sharma_brothers", "9876543211")
RUNNER_TOKEN = issue_runner_token("gm_1", "9876543220")

ADMIN_HEADERS = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
CUSTOMER_HEADERS = {"Authorization": f"Bearer {CUSTOMER_TOKEN}"}
VENDOR_HEADERS = {"Authorization": f"Bearer {VENDOR_TOKEN}"}
RUNNER_HEADERS = {"Authorization": f"Bearer {RUNNER_TOKEN}"}


def test_anonymous_requests_denied():
    """Unauthenticated requests must be denied with 401 Unauthorized across all admin routes."""
    admin_routes = [
        ("GET", "/api/admin/metrics"),
        ("GET", "/api/admin/support/tickets"),
        ("POST", "/api/admin/support/tickets/TCK-1/action"),
        ("GET", "/api/admin/pending-vendors"),
        ("GET", "/api/admin/vendors/store_1"),
        ("POST", "/api/admin/vendors/store_1/approve"),
        ("POST", "/api/admin/vendors/store_1/reject"),
        ("GET", "/api/admin/pending-runners"),
        ("GET", "/api/admin/runners/gm_1"),
        ("POST", "/api/admin/runners/gm_1/approve"),
        ("POST", "/api/admin/runners/gm_1/reject"),
        ("GET", "/api/admin/orders/god-view"),
        ("GET", "/api/admin/users/risk-profile"),
        ("GET", "/api/admin/commission-ledger"),
        ("GET", "/api/admin/payout-verifications"),
    ]

    for method, path in admin_routes:
        if method == "GET":
            resp = client.get(path)
        else:
            resp = client.post(path)
        assert resp.status_code == 401, f"Expected 401 for anonymous {method} {path}, got {resp.status_code}: {resp.text}"


def test_role_segregation_forbidden():
    """Customer, Vendor, and Runner tokens must receive 403 Forbidden on Super Admin routes."""
    test_endpoints = [
        "/api/admin/metrics",
        "/api/admin/orders/god-view",
        "/api/admin/commission-ledger",
        "/api/admin/payout-verifications",
    ]

    for ep in test_endpoints:
        # Customer
        c_resp = client.get(ep, headers=CUSTOMER_HEADERS)
        assert c_resp.status_code == 403, f"Expected 403 for Customer on {ep}, got {c_resp.status_code}"

        # Vendor
        v_resp = client.get(ep, headers=VENDOR_HEADERS)
        assert v_resp.status_code == 403, f"Expected 403 for Vendor on {ep}, got {v_resp.status_code}"

        # Runner
        r_resp = client.get(ep, headers=RUNNER_HEADERS)
        assert r_resp.status_code == 403, f"Expected 403 for Runner on {ep}, got {r_resp.status_code}"


def test_super_admin_authorized_access():
    """Super Admin Bearer token must receive 200 OK on admin endpoints."""
    resp = client.get("/api/admin/metrics", headers=ADMIN_HEADERS)
    assert resp.status_code == 200, f"Expected 200 for Super Admin, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "total_gmv" in data
    assert "total_orders" in data


def test_super_admin_login_endpoint():
    """Super Admin login endpoint must issue a valid JWT token with role 'admin'."""
    login_resp = client.post("/api/admin/login", json={"admin_key": "gaonbazar_super_admin_secret_2026"})
    assert login_resp.status_code == 200
    data = login_resp.json()
    assert data["success"] is True
    assert "token" in data
    assert data["role"] == "admin"

    # Use the issued token to access admin endpoint
    issued_token = data["token"]
    metrics_resp = client.get("/api/admin/metrics", headers={"Authorization": f"Bearer {issued_token}"})
    assert metrics_resp.status_code == 200


def test_super_admin_cookie_auth():
    """Super Admin cookie gaonbazar_admin_token must grant authenticated access."""
    cookie_client = TestClient(app)
    cookie_client.cookies.set("gaonbazar_admin_token", ADMIN_TOKEN)
    resp = cookie_client.get("/api/admin/metrics")
    assert resp.status_code == 200, f"Expected 200 via cookie auth, got {resp.status_code}"


if __name__ == "__main__":
    test_anonymous_requests_denied()
    print("✓ test_anonymous_requests_denied PASSED")
    test_role_segregation_forbidden()
    print("✓ test_role_segregation_forbidden PASSED")
    test_super_admin_authorized_access()
    print("✓ test_super_admin_authorized_access PASSED")
    test_super_admin_login_endpoint()
    print("✓ test_super_admin_login_endpoint PASSED")
    test_super_admin_cookie_auth()
    print("✓ test_super_admin_cookie_auth PASSED")
    print("\nALL 5 SUPER ADMIN RBAC SECURITY TESTS PASSED 100%!")

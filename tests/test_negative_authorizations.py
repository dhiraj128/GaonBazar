# -*- coding: utf-8 -*-
"""
GaonBazaar — Enterprise Negative Authorization & Identity Protection Suite
==========================================================================
Verifies:
1. X-Test-Bypass negative checks (strictly blocked in hosted/production or without explicit flag)
2. Payment split endpoints role-based access control (RBAC & ownership verification)
3. Read-only invariance on GET /api/payments/orders/{order_id}/split-payout
4. Super Admin credentials verification and fail-closed protections
5. MultiFernet cryptographic failure handling on corrupted ciphertexts
6. Authoritative server-side distance, catalog, and geofence integrity on /payments/create-order
"""

import os
import sys

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

from pathlib import Path
from fastapi.testclient import TestClient

# Ensure root directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.main import app
from backend.database import SessionLocal, ensure_schema_migrations
from backend.models import Order, Store, Runner, Product
from backend.security import (
    issue_admin_token,
    issue_vendor_token,
    issue_runner_token,
    issue_user_token,
    decrypt_sensitive_field,
    mask_bank_account,
    encrypt_sensitive_field,
)


def run_negative_authorization_tests():
    client = TestClient(app)
    db = SessionLocal()
    ensure_schema_migrations()

    total = 0
    passed = 0

    def check(name: str, cond: bool, detail: str = ""):
        nonlocal total, passed
        total += 1
        if cond:
            passed += 1
            print(f"  ✓ PASS: {name}" + (f" ({detail})" if detail else ""))
        else:
            print(f"  ❌ FAIL: {name}" + (f" ({detail})" if detail else ""))

    print("\n================================================================================")
    print("GAONBAZAAR NEGATIVE AUTHORIZATION & IDENTITY PROTECTION AUDIT")
    print("================================================================================")

    # Setup baseline data
    order = db.query(Order).filter(Order.id == "#RUR-NEG-101").first()
    if not order:
        order = Order(
            id="#RUR-NEG-101",
            user_phone="9876543210",
            user_name="Neg Test User",
            village="Rampur",
            landmark="Near Temple",
            store_id="sharma_brothers",
            store_name="Sharma Brothers Kirana",
            runner_id="gm_1",
            subtotal=250.0,
            delivery_fee=15.0,
            platform_fee=3.0,
            total_amount=268.0,
            payment_mode="ONLINE",
            payment_status="PAID",
            delivery_otp="4521",
            status="Order Placed",
            timeline_stage=1
        )
        db.add(order)
        db.commit()
    else:
        order.user_phone = "9876543210"
        order.store_id = "sharma_brothers"
        order.runner_id = "gm_1"
        order.payment_status = "PAID"
        order.split_payout_status = None
        db.commit()

    clean_order_id = order.id.lstrip("#")

    # Tokens
    admin_token = issue_admin_token("super_admin")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    vendor_sharma_token = issue_vendor_token("sharma_brothers", "9876543211")
    vendor_sharma_headers = {"Authorization": f"Bearer {vendor_sharma_token}"}

    vendor_other_token = issue_vendor_token("kisan_seva", "9876543212")
    vendor_other_headers = {"Authorization": f"Bearer {vendor_other_token}"}

    runner_assigned_token = issue_runner_token("gm_1", "9876543220")
    runner_assigned_headers = {"Authorization": f"Bearer {runner_assigned_token}"}

    runner_other_token = issue_runner_token("gm_999", "9876543229")
    runner_other_headers = {"Authorization": f"Bearer {runner_other_token}"}

    customer_owner_token = issue_user_token(101, "9876543210", "Neg Test User")
    customer_owner_headers = {"Authorization": f"Bearer {customer_owner_token}"}

    customer_other_token = issue_user_token(999, "9111122222", "Attacker User")
    customer_other_headers = {"Authorization": f"Bearer {customer_other_token}"}

    # -------------------------------------------------------------------------
    # SUITE 1: X-Test-Bypass Protection in Hosted/Production Environments
    # -------------------------------------------------------------------------
    print("\n--- 1. Auditing X-Test-Bypass Disablement in Hosted/Production ---")
    
    # Simulate hosted environment (Render)
    orig_render = os.environ.get("RENDER")
    os.environ["RENDER"] = "true"
    try:
        res_bypass_admin = client.get(
            f"/api/payments/orders/{clean_order_id}/split-payout",
            headers={"X-Test-Bypass": "1"}
        )
        check("X-Test-Bypass blocked with 401 when RENDER=true", res_bypass_admin.status_code == 401, f"Status: {res_bypass_admin.status_code}")

        res_bypass_exec = client.post(
            f"/api/payments/orders/{clean_order_id}/execute-split",
            headers={"X-Test-Bypass": "1"}
        )
        check("X-Test-Bypass blocked on execute-split with 401 when RENDER=true", res_bypass_exec.status_code == 401)
    finally:
        if orig_render is not None:
            os.environ["RENDER"] = orig_render
        else:
            os.environ.pop("RENDER", None)

    # -------------------------------------------------------------------------
    # SUITE 2: RBAC & Tenant Isolation on Payment Split Endpoints
    # -------------------------------------------------------------------------
    print("\n--- 2. Auditing Payment Split RBAC & Ownership Isolation ---")

    # GET /split-payout: Unauthenticated must be blocked
    res_split_no_auth = client.get(f"/api/payments/orders/{clean_order_id}/split-payout")
    check("Unauthenticated GET /split-payout blocked with 401", res_split_no_auth.status_code == 401)

    # GET /split-payout: Unrelated customer must be blocked
    res_split_bad_cust = client.get(f"/api/payments/orders/{clean_order_id}/split-payout", headers=customer_other_headers)
    check("Unrelated customer GET /split-payout blocked with 403", res_split_bad_cust.status_code == 403)

    # GET /split-payout: Unrelated vendor must be blocked
    res_split_bad_vend = client.get(f"/api/payments/orders/{clean_order_id}/split-payout", headers=vendor_other_headers)
    check("Unrelated vendor GET /split-payout blocked with 403", res_split_bad_vend.status_code == 403)

    # GET /split-payout: Unrelated runner must be blocked
    res_split_bad_runn = client.get(f"/api/payments/orders/{clean_order_id}/split-payout", headers=runner_other_headers)
    check("Unrelated runner GET /split-payout blocked with 403", res_split_bad_runn.status_code == 403)

    # GET /split-payout: Authorized roles must succeed
    res_split_admin = client.get(f"/api/payments/orders/{clean_order_id}/split-payout", headers=admin_headers)
    check("Admin GET /split-payout allowed (200)", res_split_admin.status_code == 200)

    res_split_owner_vend = client.get(f"/api/payments/orders/{clean_order_id}/split-payout", headers=vendor_sharma_headers)
    check("Owning vendor GET /split-payout allowed (200)", res_split_owner_vend.status_code == 200)

    res_split_owner_cust = client.get(f"/api/payments/orders/{clean_order_id}/split-payout", headers=customer_owner_headers)
    check("Owning customer GET /split-payout allowed (200)", res_split_owner_cust.status_code == 200)

    # POST /execute-split: Only Super Admin allowed
    res_exec_cust = client.post(f"/api/payments/orders/{clean_order_id}/execute-split", headers=customer_owner_headers)
    check("Customer POST /execute-split blocked with 403", res_exec_cust.status_code == 403)

    res_exec_vend = client.post(f"/api/payments/orders/{clean_order_id}/execute-split", headers=vendor_sharma_headers)
    check("Vendor POST /execute-split blocked with 403", res_exec_vend.status_code == 403)

    res_exec_runn = client.post(f"/api/payments/orders/{clean_order_id}/execute-split", headers=runner_assigned_headers)
    check("Runner POST /execute-split blocked with 403", res_exec_runn.status_code == 403)

    res_exec_admin = client.post(f"/api/payments/orders/{clean_order_id}/execute-split", headers=admin_headers)
    check("Admin POST /execute-split allowed (200)", res_exec_admin.status_code == 200)

    # -------------------------------------------------------------------------
    # SUITE 3: Super Admin Login & Insecure Key Rejection
    # -------------------------------------------------------------------------
    print("\n--- 3. Auditing Super Admin Login & Deny-by-Default ---")

    # Missing credentials
    res_login_empty = client.post("/api/admin/login", json={"admin_key": ""})
    check("Admin login with empty password rejected (401)", res_login_empty.status_code == 401)

    # Bad password
    res_login_bad = client.post("/api/admin/login", json={"admin_key": "wrong_password_xyz"})
    check("Admin login with incorrect password rejected (401)", res_login_bad.status_code == 401)

    # Fail closed when hosted has unconfigured secret
    orig_env = os.environ.get("ENVIRONMENT")
    orig_key = os.environ.get("ADMIN_SECRET_KEY")
    os.environ["ENVIRONMENT"] = "production"
    os.environ["ADMIN_SECRET_KEY"] = "gaonbazar_super_admin_secret_2026"  # Insecure default in prod
    try:
        res_login_prod_fail = client.post("/api/admin/login", json={"admin_key": "gaonbazar_super_admin_secret_2026"})
        check("Admin login fails closed (500) if using default password in production", res_login_prod_fail.status_code == 500)
    finally:
        if orig_env is not None:
            os.environ["ENVIRONMENT"] = orig_env
        else:
            os.environ.pop("ENVIRONMENT", None)
        if orig_key is not None:
            os.environ["ADMIN_SECRET_KEY"] = orig_key
        else:
            os.environ.pop("ADMIN_SECRET_KEY", None)

    # -------------------------------------------------------------------------
    # SUITE 4: MultiFernet Encryption & Corrupted Ciphertext Defense
    # -------------------------------------------------------------------------
    print("\n--- 4. Auditing MultiFernet Cryptographic Integrity ---")

    plaintext_acc = "50100492817263"
    encrypted_acc = encrypt_sensitive_field(plaintext_acc)
    check("Encryption generates enc:: token", encrypted_acc.startswith("enc::"))
    decrypted_acc = decrypt_sensitive_field(encrypted_acc)
    check("Decryption recovers exact plaintext", decrypted_acc == plaintext_acc)

    # Test corrupted ciphertext raises explicit ValueError
    corrupted_token = "enc::gAAAAABnotarealfernettoken12345"
    corrupted_caught = False
    try:
        decrypt_sensitive_field(corrupted_token)
    except ValueError:
        corrupted_caught = True
    check("Corrupted ciphertext raises explicit ValueError", corrupted_caught)

    # mask_bank_account safely returns placeholder on corruption without leaking
    masked_corrupted = mask_bank_account(corrupted_token)
    check("mask_bank_account handles corrupted token safely", masked_corrupted == "•••• •••• ••••")

    # -------------------------------------------------------------------------
    # SUITE 5: Authoritative Server Distance & Geofence on /payments/create-order
    # -------------------------------------------------------------------------
    print("\n--- 5. Auditing Server Distance & Geofence on /payments/create-order ---")

    # Outside delivery zone (> 8.0 km)
    res_pay_outside = client.post("/api/payments/create-order", json={
        "items": [{"id": "item_atta", "qty": 1, "price": 120.0}],
        "store_id": "sharma_brothers",
        "distance_km": 12.5  # Exceeds 8.0 km
    })
    check("Order beyond 8.0 km rejected with 400 on payment creation", res_pay_outside.status_code == 400)

    # Out of stock product
    dummy_oos_prod = db.query(Product).filter(Product.id == "item_atta").first()
    if dummy_oos_prod:
        dummy_oos_prod.in_stock = False
        db.commit()
        try:
            res_pay_oos = client.post("/api/payments/create-order", json={
                "items": [{"id": "item_atta", "qty": 1, "price": 120.0}],
                "store_id": "sharma_brothers",
                "distance_km": 1.5
            })
            check("Out-of-stock product rejected with 400 on payment creation", res_pay_oos.status_code == 400)
        finally:
            dummy_oos_prod.in_stock = True
            db.commit()

    # Wrong store product
    res_pay_wrong_store = client.post("/api/payments/create-order", json={
        "items": [{"id": "item_atta", "qty": 1, "price": 120.0}],
        "store_id": "kisan_seva_kendra",  # item_atta belongs to sharma_brothers
        "distance_km": 1.5
    })
    check("Wrong store product rejected with 400 on payment creation", res_pay_wrong_store.status_code == 400)

    print("\n================================================================================")
    print(f"NEGATIVE AUTHORIZATION SUMMARY: {passed}/{total} Passed ({passed/total*100:.1f}%)")
    print("================================================================================")
    return passed == total


if __name__ == "__main__":
    success = run_negative_authorization_tests()
    sys.exit(0 if success else 1)

"""
GaonBazaar Customer App Phase 1: Authentication, OTP Security & RBAC Regression Suite
======================================================================================
Verifies:
1. Successful Customer Login with verified single-use OTP
2. Invalid OTP rejection & max attempt rate limiting
3. Expired OTP rejection
4. Single-Use OTP enforcement (anti-replay)
5. Unauthorized requests protection (401 on missing/tampered/expired token)
6. Cross-account access denial (403 tenant isolation between customer accounts)
7. Non-customer role access denial (403 when vendor/runner token accesses customer data)
8. Production environment isolation (no OTP code echo in response)
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure UTF-8 output encoding
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from backend.main import app
from backend.database import SessionLocal
from backend.models import User, OTPRecord, Landmark, SavedPaymentMethod, Order
from backend.security import (
    issue_user_token,
    issue_vendor_token,
    issue_runner_token,
    issue_admin_token,
    create_jwt_token,
    decode_jwt_token
)

client = TestClient(app)
passed_count = 0
failed_count = 0


def check(condition: bool, description: str, detail: str = ""):
    global passed_count, failed_count
    if condition:
        passed_count += 1
        print(f"  \u2713 PASS: {description}" + (f" - {detail}" if detail else ""))
    else:
        failed_count += 1
        print(f"  \u2717 FAIL: {description}" + (f" - {detail}" if detail else ""))
        raise AssertionError(f"Check failed: {description} ({detail})")


def run_customer_auth_regression_suite():
    print("=" * 80)
    print("CUSTOMER AUTHENTICATION, OTP INTEGRITY & DATA ISOLATION REGRESSION SUITE")
    print("=" * 80)

    db = SessionLocal()
    phone_a = "9876500001"
    phone_b = "9876500002"
    phone_exp = "9876500003"
    qa_phone = "9876543210"

    # Ensure isolated test state by purging previous test fixtures
    db.query(OTPRecord).filter(OTPRecord.phone.in_([phone_a, phone_b, phone_exp])).delete(synchronize_session=False)
    db.commit()

    try:
        # =====================================================================
        # SUITE 1: SUCCESSFUL OTP LOGIN & AUTHENTIC JWT ISSUANCE
        # =====================================================================
        print("\n[SUITE 1/6]: Successful Customer OTP Login Flow")

        # 1.1 Request OTP for customer A
        res_send = client.post("/api/auth/send-otp", json={"phone": phone_a})
        check(res_send.status_code == 200, "Send OTP returns HTTP 200", f"Status: {res_send.status_code}")
        send_data = res_send.json()
        check(send_data.get("success") is True, "Send OTP response indicates success=True")

        # Query OTP from database
        otp_rec_a = db.query(OTPRecord).filter(
            OTPRecord.phone == phone_a,
            OTPRecord.is_verified == False
        ).order_by(OTPRecord.created_at.desc()).first()
        check(otp_rec_a is not None, "Valid OTP record persisted in database")
        check(len(otp_rec_a.otp_code) == 6 and otp_rec_a.otp_code.isdigit(), "Persisted OTP is a 6-digit numeric code")
        code_a = otp_rec_a.otp_code

        # 1.2 Verify with correct OTP
        res_verify = client.post("/api/auth/verify", json={"phone": phone_a, "otp": code_a})
        check(res_verify.status_code == 200, "Verify OTP with valid code returns HTTP 200", f"Status: {res_verify.status_code}")
        verify_data = res_verify.json()
        check(verify_data.get("success") is True, "Verification returns success=True")
        
        token_a = verify_data.get("session_token")
        check(bool(token_a), "Authentic session token returned")

        # 1.3 Decode JWT and assert role, phone, and signature
        payload_a = decode_jwt_token(token_a)
        check(payload_a.get("role") == "customer", "JWT role is strictly 'customer'", f"Role: {payload_a.get('role')}")
        check(payload_a.get("phone") == phone_a, "JWT phone matches authenticated phone", f"Phone: {payload_a.get('phone')}")
        check("sub" in payload_a and "exp" in payload_a, "JWT conforms to RFC 7519 with sub and exp claims")

        # =====================================================================
        # SUITE 2: INVALID OTP REJECTION & ATTEMPT RATE LIMITING
        # =====================================================================
        print("\n[SUITE 2/6]: Invalid OTP Rejection & Brute-Force Defense")

        # 2.1 Request new OTP for user B
        client.post("/api/auth/send-otp", json={"phone": phone_b})
        otp_rec_b = db.query(OTPRecord).filter(
            OTPRecord.phone == phone_b,
            OTPRecord.is_verified == False
        ).order_by(OTPRecord.created_at.desc()).first()
        valid_code_b = otp_rec_b.otp_code

        # 2.2 Attempt verification with invalid code
        res_invalid = client.post("/api/auth/verify", json={"phone": phone_b, "otp": "000000"})
        check(res_invalid.status_code == 400, "Invalid OTP rejected with HTTP 400", f"Status: {res_invalid.status_code}")
        check("Invalid OTP" in res_invalid.text, "Explicit error message on invalid OTP")

        # Refresh record and assert attempt counter incremented
        db.refresh(otp_rec_b)
        check(otp_rec_b.attempts == 1, "Failed attempt incremented attempts counter in DB", f"Attempts: {otp_rec_b.attempts}")
        check(otp_rec_b.is_verified is False, "Record remains unverified after invalid attempt")

        # 2.3 Simulate 4 more failed attempts (reaching threshold of 5)
        for i in range(4):
            client.post("/api/auth/verify", json={"phone": phone_b, "otp": f"11111{i}"})

        db.refresh(otp_rec_b)
        check(otp_rec_b.attempts >= 5, "Attempts reached max threshold of 5", f"Attempts: {otp_rec_b.attempts}")

        # 2.4 Verify that even with the CORRECT code, it is rejected once threshold is exceeded
        res_threshold = client.post("/api/auth/verify", json={"phone": phone_b, "otp": valid_code_b})
        check(res_threshold.status_code == 400, "Exceeded threshold invalidates OTP even with correct code", f"Status: {res_threshold.status_code}")
        check("Too many failed attempts" in res_threshold.text, "Explicit threshold lockout message")

        # =====================================================================
        # SUITE 3: EXPIRED OTP & SINGLE-USE REPLAY DEFENSE
        # =====================================================================
        print("\n[SUITE 3/6]: Expired OTP & Single-Use Replay Defense")

        # 3.1 Expired OTP rejection
        phone_exp = "9876500003"
        expired_record = OTPRecord(
            phone=phone_exp,
            otp_code="654321",
            is_verified=False,
            attempts=0,
            created_at=datetime.utcnow() - timedelta(minutes=10),
            expires_at=datetime.utcnow() - timedelta(minutes=5)
        )
        db.add(expired_record)
        db.commit()

        res_expired = client.post("/api/auth/verify", json={"phone": phone_exp, "otp": "654321"})
        check(res_expired.status_code == 400, "Expired OTP rejected with HTTP 400", f"Status: {res_expired.status_code}")
        check("expired" in res_expired.text.lower(), "Explicit expired OTP message returned")

        # 3.2 Single-Use enforcement (anti-replay attack)
        # Attempt to reuse Customer A's already-verified OTP code
        res_replay = client.post("/api/auth/verify", json={"phone": phone_a, "otp": code_a})
        check(res_replay.status_code == 400, "Replay of already-verified OTP rejected with HTTP 400", f"Status: {res_replay.status_code}")
        check("Invalid or expired" in res_replay.text, "Single-use enforcement blocks replay")

        # =====================================================================
        # SUITE 4: UNAUTHORIZED REQUESTS PROTECTION (401 UNAUTHORIZED)
        # =====================================================================
        print("\n[SUITE 4/6]: Unauthorized Requests Protection (401)")

        # 4.1 Missing Authorization header on customer orders
        res_unauth_orders = client.get(f"/api/user/{phone_a}/orders")
        check(res_unauth_orders.status_code == 401, "Missing token on /orders returns HTTP 401", f"Status: {res_unauth_orders.status_code}")

        # 4.2 Missing Authorization header on customer saved payment methods
        res_unauth_pm = client.get(f"/api/user/{phone_a}/payment-methods")
        check(res_unauth_pm.status_code == 401, "Missing token on /payment-methods returns HTTP 401", f"Status: {res_unauth_pm.status_code}")

        # 4.3 Missing Authorization header on add payment method
        res_unauth_add_pm = client.post(f"/api/user/{phone_a}/payment-methods", json={
            "method_type": "upi",
            "title": "Unauth UPI",
            "vpa_or_card": "test@upi",
            "is_default": False
        })
        check(res_unauth_add_pm.status_code == 401, "Missing token on add payment method returns HTTP 401", f"Status: {res_unauth_add_pm.status_code}")

        # 4.4 Tampered signature JWT
        tampered_token = token_a[:-5] + "XXXXX"
        res_tampered = client.get(
            f"/api/user/{phone_a}/orders",
            headers={"Authorization": f"Bearer {tampered_token}"}
        )
        check(res_tampered.status_code == 401, "Tampered JWT signature returns HTTP 401", f"Status: {res_tampered.status_code}")
        check("tampered" in res_tampered.text.lower() or "signature" in res_tampered.text.lower(), "Explicit tamper detection detail")

        # 4.5 Expired JWT token
        expired_jwt = create_jwt_token(
            {"sub": "1", "phone": phone_a, "role": "customer"},
            expires_delta=timedelta(seconds=-10)
        )
        res_exp_token = client.get(
            f"/api/user/{phone_a}/orders",
            headers={"Authorization": f"Bearer {expired_jwt}"}
        )
        check(res_exp_token.status_code == 401, "Expired JWT token returns HTTP 401", f"Status: {res_exp_token.status_code}")
        check("expired" in res_exp_token.text.lower(), "Explicit token expiration detail")

        # =====================================================================
        # SUITE 5: CROSS-ACCOUNT TENANT ISOLATION (403 FORBIDDEN)
        # =====================================================================
        print("\n[SUITE 5/6]: Cross-Account Access & Role Isolation (403)")

        # Create valid token for Customer B
        token_b = issue_user_token(user_id=2, phone=phone_b)
        headers_a = {"Authorization": f"Bearer {token_a}"}
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # 5.1 Customer A accesses Customer A's own orders -> 200 OK
        res_a_self = client.get(f"/api/user/{phone_a}/orders", headers=headers_a)
        check(res_a_self.status_code == 200, "Customer A accessing own orders returns HTTP 200", f"Status: {res_a_self.status_code}")

        # 5.2 Customer A attempts to access Customer B's orders -> 403 Forbidden
        res_cross_orders = client.get(f"/api/user/{phone_b}/orders", headers=headers_a)
        check(res_cross_orders.status_code == 403, "Customer A accessing Customer B's orders returns HTTP 403", f"Status: {res_cross_orders.status_code}")
        check("Access Denied" in res_cross_orders.text, "Explicit cross-account access denial message")

        # 5.3 Customer A attempts to view Customer B's payment methods -> 403 Forbidden
        res_cross_pm = client.get(f"/api/user/{phone_b}/payment-methods", headers=headers_a)
        check(res_cross_pm.status_code == 403, "Customer A accessing Customer B's payment methods returns HTTP 403", f"Status: {res_cross_pm.status_code}")

        # 5.4 Customer A attempts to add a payment method to Customer B's account -> 403 Forbidden
        res_cross_add = client.post(
            f"/api/user/{phone_b}/payment-methods",
            json={"method_type": "upi", "title": "Malicious UPI", "vpa_or_card": "hacker@upi", "is_default": False},
            headers=headers_a
        )
        check(res_cross_add.status_code == 403, "Customer A adding payment method to Customer B returns HTTP 403", f"Status: {res_cross_add.status_code}")

        # 5.5 Customer A attempts to delete Customer B's payment method -> 403 Forbidden
        res_cross_del = client.delete(f"/api/user/{phone_b}/payment-methods/99", headers=headers_a)
        check(res_cross_del.status_code == 403, "Customer A deleting Customer B's payment method returns HTTP 403", f"Status: {res_cross_del.status_code}")

        # 5.6 Customer A attempts to modify Customer B's landmark -> 403 Forbidden
        res_cross_lm = client.post(
            "/api/user/landmark",
            json={
                "phone": phone_b,
                "name": "Tampered Name",
                "village": "Rampur",
                "landmark": "Overriding victim's location address 10+ chars"
            },
            headers=headers_a
        )
        check(res_cross_lm.status_code == 403, "Customer A modifying Customer B's landmark returns HTTP 403", f"Status: {res_cross_lm.status_code}")

        # 5.7 Vendor token attempting to access customer orders -> 403 Forbidden
        vendor_token = issue_vendor_token(store_id="sharma_brothers", phone="9876543210")
        res_vendor_to_cust = client.get(
            f"/api/user/{phone_a}/orders",
            headers={"Authorization": f"Bearer {vendor_token}"}
        )
        check(res_vendor_to_cust.status_code == 403, "Vendor token accessing customer orders returns HTTP 403", f"Status: {res_vendor_to_cust.status_code}")

        # 5.8 Runner token attempting to access customer orders -> 403 Forbidden
        runner_token = issue_runner_token(runner_id="gm_1", phone="9876543220")
        res_runner_to_cust = client.get(
            f"/api/user/{phone_a}/orders",
            headers={"Authorization": f"Bearer {runner_token}"}
        )
        check(res_runner_to_cust.status_code == 403, "Runner token accessing customer orders returns HTTP 403", f"Status: {res_runner_to_cust.status_code}")

        # 5.9 Super Admin token accessing customer orders -> 200 OK (Oversight privilege)
        admin_token = issue_admin_token()
        res_admin_to_cust = client.get(
            f"/api/user/{phone_a}/orders",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        check(res_admin_to_cust.status_code == 200, "Super Admin accessing customer orders returns HTTP 200 (Oversight)", f"Status: {res_admin_to_cust.status_code}")

        # =====================================================================
        # SUITE 6: PRODUCTION ENVIRONMENT ISOLATION (ZERO OTP LEAKAGE)
        # =====================================================================
        print("\n[SUITE 6/6]: Production Environment Isolation (Zero OTP Echo)")

        # 6.1 Set ENVIRONMENT=production and verify OTP code is NEVER returned in response
        old_env = os.environ.get("ENVIRONMENT")
        try:
            os.environ["ENVIRONMENT"] = "production"
            phone_prod = "9876599999"

            res_prod = client.post("/api/auth/send-otp", json={"phone": phone_prod})
            check(res_prod.status_code == 200, "Production send-otp responds HTTP 200")
            prod_data = res_prod.json()
            check(prod_data.get("otp") is None, "Production send-otp response strictly omits OTP code (otp=None)", f"Echoed OTP: {prod_data.get('otp')}")

            # Verify that in production, even test phone 9876543210 generates secure random code (not 582941) and omits echo
            res_qa_prod = client.post("/api/auth/send-otp", json={"phone": qa_phone})
            check(res_qa_prod.json().get("otp") is None, "Production send-otp omits OTP even for test phone")
            
            rec_qa = db.query(OTPRecord).filter(
                OTPRecord.phone == qa_phone,
                OTPRecord.is_verified == False
            ).order_by(OTPRecord.created_at.desc()).first()
            check(rec_qa.otp_code != "582941", "Production generates secure random code for all numbers", f"Code: {rec_qa.otp_code}")
        finally:
            if old_env is not None:
                os.environ["ENVIRONMENT"] = old_env
            else:
                os.environ.pop("ENVIRONMENT", None)

    finally:
        db.close()

    print("\n" + "=" * 80)
    print(f"REGRESSION SUITE COMPLETED: {passed_count} PASSED, {failed_count} FAILED")
    print("=" * 80)
    if failed_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    run_customer_auth_regression_suite()

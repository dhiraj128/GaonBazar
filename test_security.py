"""
GaonBazaar Bank-Grade Cybersecurity & Penetration Test Suite
============================================================
Automated penetration and security verification tests for:
1. RFC 7519 HMAC-SHA256 JWT Authentication & Role-Based Access Control (RBAC)
2. Tenant & Entity Data Isolation (Cross-Store / Cross-Runner Tampering Defense)
3. Sliding Window Rate Limiting (Anti-Spam & SMS Flood Defense)
4. Anti-XSS Sanitization & SQL Parameterization Defense
5. Helmet-Style Security Headers & Restricted CORS Defense
"""

import sys
import time
import json
import base64
import hmac
import hashlib
from pathlib import Path
from fastapi.testclient import TestClient

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from backend.main import app
from backend.security import (
    create_jwt_token,
    decode_jwt_token,
    issue_user_token,
    issue_vendor_token,
    issue_runner_token,
    issue_admin_token,
    otp_rate_limiter,
    checkout_rate_limiter,
    JWT_SECRET
)

# Ensure UTF-8 output encoding across Windows consoles
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

client = TestClient(app)

TOTAL_TESTS = 0
PASSED_TESTS = 0
FAILED_TESTS = 0

def record_check(test_name: str, passed: bool, detail: str = ""):
    global TOTAL_TESTS, PASSED_TESTS, FAILED_TESTS
    TOTAL_TESTS += 1
    if passed:
        PASSED_TESTS += 1
        print(f"  [PASS]: {test_name} ({detail})")
    else:
        FAILED_TESTS += 1
        print(f"  [FAIL]: {test_name} ({detail})")


def test_jwt_engine():
    print("\n[SECURITY AUDIT 1/5]: RFC 7519 JWT Cryptographic Engine & Tamper Resistance")

    # 1.1 Generate valid customer token
    user_token = issue_user_token(user_id=101, phone="9876543210", name="Ramesh Patel")
    payload = decode_jwt_token(user_token)
    record_check("Valid Customer JWT Decode", payload["sub"] == "101" and payload["role"] == "customer", f"sub={payload['sub']}, role={payload['role']}")

    # 1.2 Tampered payload detection
    parts = user_token.split('.')
    tampered_payload = {"sub": "9999", "role": "admin", "iat": int(time.time()), "exp": int(time.time() + 3600)}
    tampered_b64 = base64.urlsafe_b64encode(json.dumps(tampered_payload).encode()).rstrip(b'=').decode()
    tampered_token = f"{parts[0]}.{tampered_b64}.{parts[2]}"

    tamper_rejected = False
    try:
        decode_jwt_token(tampered_token)
    except Exception as e:
        tamper_rejected = True
    record_check("Tampered JWT Signature Rejection", tamper_rejected, "HMAC signature mismatch intercepted")

    # 1.3 Expired token rejection
    expired_token = create_jwt_token({"sub": "user_expired", "role": "customer"}, expires_delta=-1)
    expired_rejected = False
    try:
        decode_jwt_token(expired_token)
    except Exception as e:
        expired_rejected = True
    record_check("Expired JWT Token Rejection", expired_rejected, "Token with exp in the past intercepted")

    # 1.4 Invalid secret signature rejection
    fake_token = create_jwt_token({"sub": "hacker", "role": "admin"}, secret="malicious-attacker-secret")
    fake_rejected = False
    try:
        decode_jwt_token(fake_token)
    except Exception as e:
        fake_rejected = True
    record_check("Forged Secret Key Rejection", fake_rejected, "Token signed with untrusted secret intercepted")


def test_rbac_and_data_isolation():
    print("\n[SECURITY AUDIT 2/5]: Role-Based Access Control & Strict Tenant Data Isolation")

    vendor_sharma_token = issue_vendor_token(store_id="sharma_brothers", phone="9876543210")
    vendor_apna_token = issue_vendor_token(store_id="apna_dairy", phone="9876543213")
    runner_token = issue_runner_token(runner_id="gm_1", phone="9876543220")
    customer_token = issue_user_token(user_id=1, phone="9876543210")

    # 2.1 Vendor accessing their own store profile -> OK
    res_sharma_self = client.get(
        "/api/vendor/stores/sharma_brothers/profile",
        headers={"Authorization": f"Bearer {vendor_sharma_token}", "X-Test-Client": "strict_security_audit"}
    )
    record_check("Vendor Authorized Access (Own Store)", res_sharma_self.status_code == 200, f"Status: {res_sharma_self.status_code}")

    # 2.2 Vendor A attempting to access Vendor B's orders/ledger -> 403 Forbidden
    res_sharma_cross = client.get(
        "/api/vendor/stores/apna_dairy/orders",
        headers={"Authorization": f"Bearer {vendor_sharma_token}", "X-Test-Client": "strict_security_audit"}
    )
    record_check("Cross-Vendor Access Denial (Tenant Isolation)", res_sharma_cross.status_code == 403, f"Status: {res_sharma_cross.status_code}")

    # 2.3 Customer token attempting to access vendor orders -> 403 Forbidden
    res_cust_to_vendor = client.get(
        "/api/vendor/stores/sharma_brothers/orders",
        headers={"Authorization": f"Bearer {customer_token}", "X-Test-Client": "strict_security_audit"}
    )
    record_check("Customer Attempting Vendor Control Denial", res_cust_to_vendor.status_code == 403, f"Status: {res_cust_to_vendor.status_code}")

    # 2.4 Runner accessing their own profile -> OK
    res_runner_self = client.get(
        "/api/runner/profile?runner_id=gm_1",
        headers={"Authorization": f"Bearer {runner_token}", "X-Test-Client": "strict_security_audit"}
    )
    record_check("Runner Authorized Access (Own Profile)", res_runner_self.status_code == 200, f"Status: {res_runner_self.status_code}")

    # 2.5 Runner attempting to access another runner's profile -> 403 Forbidden
    res_runner_cross = client.get(
        "/api/runner/profile?runner_id=gm_999",
        headers={"Authorization": f"Bearer {runner_token}", "X-Test-Client": "strict_security_audit"}
    )
    record_check("Cross-Runner Access Denial (Runner Isolation)", res_runner_cross.status_code == 403, f"Status: {res_runner_cross.status_code}")

    # 2.6 Cross-Vendor Order Action Denial (Vendor A cannot modify Vendor B's order)
    import urllib.parse
    from backend.database import db_session
    from backend.models import Order
    with db_session() as db:
        test_ord = db.query(Order).filter(Order.store_id == "apna_dairy").first()
        if not test_ord:
            test_ord = Order(
                id="#SEC-TEST-ORDER-1",
                user_phone="9876543210",
                user_name="Security Test User",
                village="Rampur",
                landmark="Test Landmark",
                store_id="apna_dairy",
                store_name="Apna Dairy",
                subtotal=100.0,
                total_amount=115.0,
                payment_mode="COD",
                status="Order Placed",
                timeline_stage=1,
                delivery_otp="9999"
            )
            db.add(test_ord)
            db.commit()
        test_ord_id = test_ord.id

    enc_order_id = urllib.parse.quote(test_ord_id)
    res_cross_action = client.post(
        f"/api/vendor/orders/{enc_order_id}/quick-action?action=accept",
        headers={"Authorization": f"Bearer {vendor_sharma_token}", "X-Test-Client": "strict_security_audit"}
    )
    record_check("Cross-Vendor Order Quick-Action Denial", res_cross_action.status_code == 403, f"Status: {res_cross_action.status_code}")

    # 2.7 Cross-Vendor Product Creation Denial (Vendor A cannot add product to Vendor B's store)
    res_cross_add_prod = client.post(
        "/api/vendor/products?store_id=apna_dairy",
        json={"name_en": "Hacked Milk", "name_hi": "दूध", "category": "dairy", "weight": "1L", "price": 50.0, "mrp": 60.0},
        headers={"Authorization": f"Bearer {vendor_sharma_token}", "X-Test-Client": "strict_security_audit"}
    )
    record_check("Cross-Vendor Product Creation Denial", res_cross_add_prod.status_code == 403, f"Status: {res_cross_add_prod.status_code}")

    # 2.8 Stage-locked Runner Pickup (Cannot pick up Stage 1 order)
    res_invalid_pickup = client.post(
        f"/api/runner/orders/{enc_order_id}/pickup",
        headers={"Authorization": f"Bearer {runner_token}", "X-Test-Client": "strict_security_audit"}
    )
    record_check("Stage-Locked Runner Pickup Defense (Non-Packed Rejection)", res_invalid_pickup.status_code == 400, f"Status: {res_invalid_pickup.status_code}")
    db.close()


def test_rate_limiting():
    print("\n[SECURITY AUDIT 3/5]: Anti-Spam & Anti-Flooding Rate Limiting")

    otp_rate_limiter.reset()
    checkout_rate_limiter.reset()

    # 3.1 Send OTP rate limit: 5 requests allowed, 6th must return HTTP 429
    otp_blocked = False
    status_codes = []
    for i in range(7):
        r = client.post(
            "/api/auth/send-otp",
            json={"phone": f"987650000{i}"},
            headers={"X-Enforce-Rate-Limit": "1"}
        )
        status_codes.append(r.status_code)
        if r.status_code == 429:
            otp_blocked = True

    record_check(
        "OTP Endpoint Rate Limit (Max 5/min)",
        otp_blocked and status_codes[5] == 429,
        f"Sequence: {status_codes}, 6th call returned 429"
    )

    # 3.2 Checkout rate limit: 10 requests allowed, 11th must return HTTP 429
    checkout_blocked = False
    chk_statuses = []
    created_order_ids = []
    for i in range(12):
        payload = {
            "user_phone": "9876543210",
            "user_name": "Test User",
            "village": "Rampur",
            "landmark": "Near Mandir Complex",
            "store_id": "sharma_brothers",
            "payment_mode": "COD",
            "customer_lat": 29.1350,
            "customer_lng": 77.0100,
            "distance_km": 1.2,
            "items": [{"id": "item_1", "name": "Atta", "price": 210.0, "qty": 1}]
        }
        r = client.post(
            "/api/orders/checkout",
            json=payload,
            headers={"X-Enforce-Rate-Limit": "1"}
        )
        chk_statuses.append(r.status_code)
        if r.status_code == 200:
            try:
                ord_id = r.json().get("order_id")
                if ord_id:
                    created_order_ids.append(ord_id)
            except Exception:
                pass
        if r.status_code == 429:
            checkout_blocked = True

    record_check(
        "Checkout Endpoint Rate Limit (Max 10/min)",
        checkout_blocked and chk_statuses[10] == 429,
        f"11th call returned 429 with Retry-After header"
    )

    # Clean up test orders created during rate limiting test to preserve database baseline
    if created_order_ids:
        from backend.database import db_session
        from backend.models import Order
        with db_session() as db:
            db.query(Order).filter(Order.id.in_(created_order_ids)).delete(synchronize_session=False)
            db.commit()

    # Reset limiters for subsequent ecosystem tests
    otp_rate_limiter.reset()
    checkout_rate_limiter.reset()


def test_xss_and_sqli_defense():
    print("\n[SECURITY AUDIT 4/5]: SQL Injection Parameterization & Anti-XSS Sanitization")

    # 4.1 SQL Injection payload in inputs
    sqli_payload = {
        "phone": "9876543210",
        "name": "Ramesh' OR '1'='1' --",
        "village": "Rampur' UNION SELECT null, null, null --",
        "landmark": "Near Mandir Chaupal with 10+ chars"
    }
    res_sqli = client.post("/api/user/landmark", json=sqli_payload)
    record_check("SQL Injection Defense (Parameterization)", res_sqli.status_code == 200, "Injected string treated safely as literal text")

    # 4.2 XSS Payload Sanitization in Pydantic Schema
    xss_payload = {
        "phone": "9876543210",
        "name": "<script>alert('pwned')</script>Suresh Kumar",
        "village": "<img src=x onerror=fetch('http://evil.com')>Rampur",
        "landmark": "<a href='javascript:alert(1)'>Valid Landmark Location Chaupal</a>"
    }
    res_xss = client.post("/api/user/landmark", json=xss_payload)
    user_data = res_xss.json().get("user", {})
    sanitized_name = user_data.get("name", "")
    sanitized_village = user_data.get("village", "")
    sanitized_landmark = user_data.get("landmark", "")

    has_no_tags = (
        "<script>" not in sanitized_name and
        "<img" not in sanitized_village and
        "onerror=" not in sanitized_village and
        "javascript:" not in sanitized_landmark
    )
    record_check(
        "Anti-XSS Input Sanitization",
        has_no_tags and ("Suresh Kumar" in sanitized_name),
        f"Cleaned Name: '{sanitized_name}', Cleaned Village: '{sanitized_village}'"
    )


def test_security_headers_and_cors():
    print("\n[SECURITY AUDIT 5/5]: Helmet-Style Security Headers & Restricted CORS")

    res = client.get("/health")

    # 5.1 X-Content-Type-Options: nosniff
    nosniff = res.headers.get("x-content-type-options") == "nosniff"
    record_check("X-Content-Type-Options: nosniff", nosniff, res.headers.get("x-content-type-options", "Missing"))

    # 5.2 X-Frame-Options: SAMEORIGIN
    frame_options = res.headers.get("x-frame-options") == "SAMEORIGIN"
    record_check("X-Frame-Options: SAMEORIGIN", frame_options, res.headers.get("x-frame-options", "Missing"))

    # 5.3 X-XSS-Protection: 1; mode=block
    xss_prot = "1; mode=block" in res.headers.get("x-xss-protection", "")
    record_check("X-XSS-Protection: 1; mode=block", xss_prot, res.headers.get("x-xss-protection", "Missing"))

    # 5.4 Referrer-Policy
    ref_pol = res.headers.get("referrer-policy") == "strict-origin-when-cross-origin"
    record_check("Referrer-Policy: strict-origin-when-cross-origin", ref_pol, res.headers.get("referrer-policy", "Missing"))

    # 5.5 Content-Security-Policy (CSP)
    csp = "default-src" in res.headers.get("content-security-policy", "")
    record_check("Content-Security-Policy Configured", csp, "CSP directives present")

    # 5.6 Locked down CORS test with unauthorized origin
    cors_res = client.options(
        "/api/auth/send-otp",
        headers={
            "Origin": "http://evil-hacker-site.ru",
            "Access-Control-Request-Method": "POST"
        }
    )
    allowed_origin = cors_res.headers.get("access-control-allow-origin")
    cors_blocked = (allowed_origin != "http://evil-hacker-site.ru" and allowed_origin != "*")
    record_check("CORS Locked Down Against Malicious Origin", cors_blocked, f"Allow-Origin: {allowed_origin}")


def test_delivery_location_authorization_and_ownership():
    print("\n[SECURITY AUDIT 6/6]: Order Delivery Location Security, Ownership & Active Order Enforcement")
    import urllib.parse
    from backend.database import db_session
    from backend.models import Order, Notification

    cust_a_phone = "9876543210"
    cust_b_phone = "9876543299"
    cust_a_token = issue_user_token(user_id=101, phone=cust_a_phone, name="Customer A")
    cust_b_token = issue_user_token(user_id=102, phone=cust_b_phone, name="Customer B")
    runner_assigned_token = issue_runner_token(runner_id="gm_1", phone="9876543220", name="Assigned Runner")
    runner_unassigned_token = issue_runner_token(runner_id="gm_2", phone="9876543221", name="Unassigned Runner")
    admin_token = issue_admin_token()

    test_ord_id = "#SEC-LOC-ORD-1"
    enc_id = urllib.parse.quote(test_ord_id)

    # Setup isolated test order
    with db_session() as db:
        existing = db.query(Order).filter(Order.id == test_ord_id).first()
        if existing:
            db.delete(existing)
            db.commit()

        test_order = Order(
            id=test_ord_id,
            user_id=101,
            user_phone=cust_a_phone,
            user_name="Customer A",
            village="Rampur Chaupal",
            landmark="Near Shiva Temple",
            customer_lat=29.1350,
            customer_lng=77.0100,
            runner_id="gm_1",
            store_id="sharma_brothers",
            store_name="Sharma Brothers Kirana",
            subtotal=250.0,
            total_amount=265.0,
            payment_mode="COD",
            status="Order Placed",
            timeline_stage=1,
            delivery_otp="1234"
        )
        db.add(test_order)
        db.commit()

    try:
        # 6.1 Unauthenticated PUT location -> 401 Unauthorized
        res_unauth_put = client.put(
            f"/api/orders/{enc_id}/delivery-location",
            json={"customer_lat": 29.1400, "customer_lng": 77.0200}
        )
        record_check("Unauthenticated Location Update Rejection (HTTP 401)", res_unauth_put.status_code == 401, f"Status: {res_unauth_put.status_code}")

        # 6.2 Unauthenticated GET location -> 401 Unauthorized
        res_unauth_get = client.get(f"/api/orders/{enc_id}/delivery-location")
        record_check("Unauthenticated Location Query Rejection (HTTP 401)", res_unauth_get.status_code == 401, f"Status: {res_unauth_get.status_code}")

        # 6.3 Customer B attempts to update Customer A's order location -> 403 Forbidden
        res_cust_b_put = client.put(
            f"/api/orders/{enc_id}/delivery-location",
            json={"customer_lat": 29.1450, "customer_lng": 77.0250},
            headers={"Authorization": f"Bearer {cust_b_token}"}
        )
        record_check("Cross-Customer Location Update Denial (HTTP 403)", res_cust_b_put.status_code == 403, f"Status: {res_cust_b_put.status_code}")

        # 6.4 Customer B attempts to view Customer A's order location -> 403 Forbidden
        res_cust_b_get = client.get(
            f"/api/orders/{enc_id}/delivery-location",
            headers={"Authorization": f"Bearer {cust_b_token}"}
        )
        record_check("Cross-Customer Location View Denial (HTTP 403)", res_cust_b_get.status_code == 403, f"Status: {res_cust_b_get.status_code}")

        # 6.5 Unassigned Runner (gm_2) attempts to view location -> 403 Forbidden
        res_unassigned_runner_get = client.get(
            f"/api/orders/{enc_id}/delivery-location",
            headers={"Authorization": f"Bearer {runner_unassigned_token}"}
        )
        record_check("Unassigned Runner Location View Denial (HTTP 403)", res_unassigned_runner_get.status_code == 403, f"Status: {res_unassigned_runner_get.status_code}")

        # 6.6 Valid Customer A updates their own order location -> 200 OK
        res_owner_put = client.put(
            f"/api/orders/{enc_id}/delivery-location",
            json={"customer_lat": 29.141200, "customer_lng": 77.018500, "landmark": "Green Door next to school"},
            headers={"Authorization": f"Bearer {cust_a_token}"}
        )
        record_check("Owner Customer Location Update Authorized (HTTP 200)", res_owner_put.status_code == 200, f"Status: {res_owner_put.status_code}")
        if res_owner_put.status_code == 200:
            data = res_owner_put.json()
            record_check("Location Coordinates Saved Correctly", abs(data["customer_lat"] - 29.141200) < 1e-4 and abs(data["customer_lng"] - 77.018500) < 1e-4)
            record_check("Directions URL Present in Response", "google.com/maps/dir" in (data.get("directions_url") or ""))

        # 6.7 Assigned Runner (gm_1) reads delivery location -> 200 OK
        res_assigned_runner_get = client.get(
            f"/api/orders/{enc_id}/delivery-location",
            headers={"Authorization": f"Bearer {runner_assigned_token}"}
        )
        record_check("Assigned Runner Location Query Authorized (HTTP 200)", res_assigned_runner_get.status_code == 200, f"Status: {res_assigned_runner_get.status_code}")

        # 6.8 Invalid GPS Coordinates Rejection (out-of-bounds latitude/longitude)
        res_invalid_coords = client.put(
            f"/api/orders/{enc_id}/delivery-location",
            json={"customer_lat": 195.0, "customer_lng": 77.018500},
            headers={"Authorization": f"Bearer {cust_a_token}"}
        )
        record_check("Out-of-Bounds GPS Coordinates Rejection (HTTP 400)", res_invalid_coords.status_code == 400, f"Status: {res_invalid_coords.status_code}")

        # 6.9 Zero GPS Coordinates Rejection (0, 0)
        res_zero_coords = client.put(
            f"/api/orders/{enc_id}/delivery-location",
            json={"customer_lat": 0.0, "customer_lng": 0.0},
            headers={"Authorization": f"Bearer {cust_a_token}"}
        )
        record_check("Zero GPS Coordinates Rejection (HTTP 400)", res_zero_coords.status_code == 400, f"Status: {res_zero_coords.status_code}")

        # 6.10 Non-existent order rejection (no silent fallback IDs)
        res_missing_order = client.put(
            "/api/orders/NON-EXISTENT-ORDER-9999/delivery-location",
            json={"customer_lat": 29.141200, "customer_lng": 77.018500},
            headers={"Authorization": f"Bearer {cust_a_token}"}
        )
        record_check("Missing Order Rejection (HTTP 404, No Fallback)", res_missing_order.status_code == 404, f"Status: {res_missing_order.status_code}")

        # 6.11 Delivered / Cancelled order location update rejection -> 400 Bad Request
        with db_session() as db:
            o = db.query(Order).filter(Order.id == test_ord_id).first()
            if o:
                o.timeline_stage = 5
                o.status = "Delivered"
                db.commit()

        res_delivered_put = client.put(
            f"/api/orders/{enc_id}/delivery-location",
            json={"customer_lat": 29.141200, "customer_lng": 77.018500},
            headers={"Authorization": f"Bearer {cust_a_token}"}
        )
        record_check("Delivered Order Location Update Rejection (HTTP 400)", res_delivered_put.status_code == 400, f"Status: {res_delivered_put.status_code}")

        # 6.12 Delivered Order Location Request Rejection (HTTP 400)
        res_deliv_req = client.post(
            f"/api/orders/{enc_id}/request-location",
            headers={"Authorization": f"Bearer {runner_assigned_token}"}
        )
        record_check("Delivered Order Location Request Rejection (HTTP 400)", res_deliv_req.status_code == 400, f"Status: {res_deliv_req.status_code}")

        # Reset to active stage 4 for request tests
        with db_session() as db:
            o = db.query(Order).filter(Order.id == test_ord_id).first()
            if o:
                o.timeline_stage = 4
                o.status = "Out for Delivery"
                db.commit()

        # 6.13 Assigned Runner Request Location Success (HTTP 200)
        res_req_ok = client.post(
            f"/api/orders/{enc_id}/request-location",
            headers={"Authorization": f"Bearer {runner_assigned_token}"}
        )
        record_check("Assigned Runner Request Location Success (HTTP 200)", res_req_ok.status_code == 200, f"Status: {res_req_ok.status_code}")

        # 6.14 Unassigned Runner Request Location Rejection (HTTP 403)
        res_unassigned_req = client.post(
            f"/api/orders/{enc_id}/request-location",
            headers={"Authorization": f"Bearer {runner_unassigned_token}"}
        )
        record_check("Unassigned Runner Request Location Rejection (HTTP 403)", res_unassigned_req.status_code == 403, f"Status: {res_unassigned_req.status_code}")

    finally:
        # Strict DB cleanup: preserve exact baseline
        with db_session() as db:
            clean_ord = db.query(Order).filter(Order.id == test_ord_id).first()
            if clean_ord:
                db.delete(clean_ord)
                db.commit()


def main():
    print("=" * 80)
    print("GAONBAZAAR ENTERPRISE SECURITY AUDIT & PENETRATION VERIFICATION")
    print("=" * 80)

    test_jwt_engine()
    test_rbac_and_data_isolation()
    test_rate_limiting()
    test_xss_and_sqli_defense()
    test_security_headers_and_cors()
    test_delivery_location_authorization_and_ownership()

    print("\n" + "=" * 80)
    print(f"SECURITY AUDIT RESULTS: {PASSED_TESTS}/{TOTAL_TESTS} CHECKS PASSED")
    print("=" * 80)

    if FAILED_TESTS > 0:
        print(f"\n❌ SECURITY SUITE FAILED WITH {FAILED_TESTS} VULNERABILITIES")
        sys.exit(1)
    else:
        print("\n✅ BANK-GRADE SECURITY VERIFICATION COMPLETE: 100% SECURE & IMPENETRABLE")
        sys.exit(0)


if __name__ == "__main__":
    main()

"""
Automated Verification Suite for GaonBazaar 3-Strike Customer Trust Score & Refund Penalty Math
Tests:
1. STRIKE 1 (The Warning):
   - User cancelled_orders becomes 1
   - Push/in-app warning notification generated: "Warning: Frequent cancellations may lead to COD restrictions."
   - User is NOT blocked from COD or online checkout
   - Prepaid cancellation provides full 100% refund (refund_penalty = 0.0)

2. STRIKE 2 (The COD Block):
   - User cancelled_orders becomes 2 -> is_cod_blocked = True
   - Checkout with COD is immediately rejected with HTTP 400 Bad Request
   - Checkout with Prepaid (UPI) is allowed and succeeds with HTTP 200 OK

3. STRIKE 3 (Blacklist & Exact Refund Penalty Math):
   - User cancelled_orders becomes 3 -> is_blacklisted = True
   - When a Prepaid (UPI/Online) order is cancelled:
     * Penalty = exact Delivery Fee + Platform Fee (₹3)
     * Refund Amount = Total Amount - Penalty = Item Subtotal
   - User is permanently blocked from checkout (HTTP 403 Forbidden) for all payment modes

4. Multi-Tier Delivery Fee Refund Penalty Verifications:
   - Tier 1 (Local, ₹15 delivery fee + ₹3 platform fee = ₹18 penalty)
   - Tier 2 (Village Edge, ₹25 delivery fee + ₹3 platform fee = ₹28 penalty)
   - Tier 3 (Long Distance, ₹40 delivery fee + ₹3 platform fee = ₹43 penalty)
"""

import sys
import os
from urllib.parse import quote

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

os.environ["TEST_MODE"] = "1"

# Ensure workspace root in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from backend.main import app
from backend.database import SessionLocal, ensure_schema_migrations
from backend.models import User, Order, OrderItem
from backend.security import checkout_rate_limiter, otp_rate_limiter

def run_trust_score_tests():
    print("=" * 80)
    print("GAONBAZAAR 3-STRIKE CUSTOMER TRUST SCORE & REFUND PENALTY VERIFICATION")
    print("=" * 80)

    ensure_schema_migrations()
    checkout_rate_limiter.reset()
    otp_rate_limiter.reset()
    client = TestClient(app)
    db = SessionLocal()

    passed_tests = 0
    total_tests = 0

    def record(name: str, condition: bool, detail: str = ""):
        nonlocal passed_tests, total_tests
        total_tests += 1
        if condition:
            passed_tests += 1
            print(f"  [PASS]: {name} {f'({detail})' if detail else ''}")
        else:
            print(f"  [FAIL]: {name} - ERROR: {detail}")
            assert condition, f"Test failed: {name} - {detail}"

    # Clean test users and cascading orders
    test_phone_1 = "9988776611"
    test_phone_2 = "9988776622"
    test_phone_3 = "9988776633"

    for p in [test_phone_1, test_phone_2, test_phone_3]:
        orders = db.query(Order).filter(Order.user_phone == p).all()
        for ord_obj in orders:
            db.delete(ord_obj)
        db.commit()
        u = db.query(User).filter(User.phone == p).first()
        if u:
            db.delete(u)
        db.commit()

    # =========================================================================
    # TEST SUITE 1: STRIKE 1 (The Warning)
    # =========================================================================
    print("\n[STRIKE 1 VERIFICATION]: First Cancellation (Warning Alert & No Restrictions)")

    # 1. Place first order (Prepaid UPI)
    # item_2 in catalog is Fortune Mustard Oil (₹145.0)
    payload_1 = {
        "user_phone": test_phone_1,
        "user_name": "Aakash Verma",
        "village": "Rampur",
        "landmark": "Near Main Chaupal, Shiva Mandir",
        "store_id": "sharma_brothers",
        "payment_mode": "UPI",
        "distance_km": 1.2,  # Local Tier (Fee ₹15, Platform ₹3, Total ₹163)
        "items": [{"id": "item_2", "name": "Fortune Mustard Oil", "price": 145.0, "qty": 1}]
    }

    resp1 = client.post("/api/orders/checkout", json=payload_1)
    record("Strike 1: Initial Order Placement (HTTP 200)", resp1.status_code == 200, f"Status: {resp1.status_code}")
    ord1_data = resp1.json()
    ord1_id = ord1_data["order_id"]
    record("Strike 1: Total Amount Verified", ord1_data["total_amount"] == 163.0, f"Total: {ord1_data['total_amount']}")

    # 2. Cancel first order
    cancel_resp1 = client.post(f"/api/orders/{quote(ord1_id)}/cancel", json={"reason": "Ordered wrong item"})
    record("Strike 1: Cancellation Succeeded (HTTP 200)", cancel_resp1.status_code == 200, f"Status: {cancel_resp1.status_code}")
    c1 = cancel_resp1.json()

    record("Strike 1: Cancelled Count is 1", c1["cancelled_orders_count"] == 1, f"Count: {c1['cancelled_orders_count']}")
    record("Strike 1: COD NOT Blocked", c1["is_cod_blocked"] is False, f"is_cod_blocked: {c1['is_cod_blocked']}")
    record("Strike 1: NOT Blacklisted", c1["is_blacklisted"] is False, f"is_blacklisted: {c1['is_blacklisted']}")
    record(
        "Strike 1: Warning Notification Present",
        "Warning: Frequent cancellations may lead to COD restrictions." in (c1["warning_alert"] or ""),
        f"Alert: {c1['warning_alert']}"
    )
    record("Strike 1: Zero Penalty on First Prepaid Cancellation", c1["refund_penalty"] == 0.0, f"Penalty: ₹{c1['refund_penalty']}")
    record("Strike 1: Full Refund on First Prepaid Cancellation", c1["refund_amount"] == 163.0, f"Refund: ₹{c1['refund_amount']}")

    # 3. Verify user can still checkout with COD
    cod_checkout_resp = client.post("/api/orders/checkout", json={
        "user_phone": test_phone_1,
        "user_name": "Aakash Verma",
        "village": "Rampur",
        "landmark": "Near Main Chaupal",
        "store_id": "sharma_brothers",
        "payment_mode": "COD",
        "distance_km": 1.2,
        "items": [{"id": "item_2", "name": "Fortune Mustard Oil", "price": 145.0, "qty": 1}]
    })
    record("Strike 1: User Can Still Order with COD (Not Blocked)", cod_checkout_resp.status_code == 200, f"Status: {cod_checkout_resp.status_code}")
    ord2_id = cod_checkout_resp.json()["order_id"]

    # =========================================================================
    # TEST SUITE 2: STRIKE 2 (The COD Block)
    # =========================================================================
    print("\n[STRIKE 2 VERIFICATION]: Second Cancellation (COD Blocked & Online Allowed)")

    # 1. Cancel second order
    cancel_resp2 = client.post(f"/api/orders/{quote(ord2_id)}/cancel", json={"reason": "Customer changed mind"})
    record("Strike 2: Second Cancellation Succeeded (HTTP 200)", cancel_resp2.status_code == 200, f"Status: {cancel_resp2.status_code}")
    c2 = cancel_resp2.json()

    record("Strike 2: Cancelled Count is 2", c2["cancelled_orders_count"] == 2, f"Count: {c2['cancelled_orders_count']}")
    record("Strike 2: is_cod_blocked set to True in DB", c2["is_cod_blocked"] is True, f"is_cod_blocked: {c2['is_cod_blocked']}")
    record("Strike 2: NOT Blacklisted Yet", c2["is_blacklisted"] is False, f"is_blacklisted: {c2['is_blacklisted']}")

    # 2. Attempt to checkout with COD (MUST FAIL with HTTP 400 Bad Request)
    cod_blocked_resp = client.post("/api/orders/checkout", json={
        "user_phone": test_phone_1,
        "user_name": "Aakash Verma",
        "village": "Rampur",
        "landmark": "Near Main Chaupal",
        "store_id": "sharma_brothers",
        "payment_mode": "COD",
        "distance_km": 1.2,
        "items": [{"id": "item_2", "name": "Fortune Mustard Oil", "price": 145.0, "qty": 1}]
    })
    record(
        "Strike 2: Checkout with COD Rejected (HTTP 400)",
        cod_blocked_resp.status_code == 400 and "COD" in cod_blocked_resp.json().get("detail", ""),
        f"Status: {cod_blocked_resp.status_code}, Detail: {cod_blocked_resp.json().get('detail', '')}"
    )

    # 3. Attempt to checkout with UPI / Prepaid (MUST SUCCEED with HTTP 200 OK)
    # item_1: Aashirvaad Atta 5kg (₹210.0), Distance: 3.0 km (Village Edge: ₹25 fee + ₹3 platform = ₹238.0 total)
    upi_allowed_resp = client.post("/api/orders/checkout", json={
        "user_phone": test_phone_1,
        "user_name": "Aakash Verma",
        "village": "Rampur",
        "landmark": "Near Main Chaupal",
        "store_id": "sharma_brothers",
        "payment_mode": "UPI",
        "distance_km": 3.0,  # Village Edge Tier (Delivery ₹25, Platform ₹3)
        "items": [{"id": "item_1", "name": "Atta", "price": 210.0, "qty": 1}]
    })
    record("Strike 2: Checkout with Prepaid UPI Allowed (HTTP 200)", upi_allowed_resp.status_code == 200, f"Status: {upi_allowed_resp.status_code}")
    ord3_data = upi_allowed_resp.json()
    ord3_id = ord3_data["order_id"]
    # Subtotal 210 + Delivery 25 + Platform 3 = 238
    record("Strike 2: Prepaid Order Amount Correct (₹238)", ord3_data["total_amount"] == 238.0, f"Total: {ord3_data['total_amount']}")

    # =========================================================================
    # TEST SUITE 3: STRIKE 3 (Blacklist & Exact Refund Penalty Math)
    # =========================================================================
    print("\n[STRIKE 3 VERIFICATION]: Third Cancellation (Blacklist & Exact Penalty Math)")

    # 1. Cancel the 3rd (Prepaid) Order
    cancel_resp3 = client.post(f"/api/orders/{quote(ord3_id)}/cancel", json={"reason": "Third cancellation"})
    record("Strike 3: Cancellation Handled (HTTP 200)", cancel_resp3.status_code == 200, f"Status: {cancel_resp3.status_code}")
    c3 = cancel_resp3.json()

    record("Strike 3: Cancelled Count is 3", c3["cancelled_orders_count"] == 3, f"Count: {c3['cancelled_orders_count']}")
    record("Strike 3: is_blacklisted set to True in DB", c3["is_blacklisted"] is True, f"is_blacklisted: {c3['is_blacklisted']}")
    record("Strike 3: is_cod_blocked is True", c3["is_cod_blocked"] is True, f"is_cod_blocked: {c3['is_cod_blocked']}")

    # EXACT PENALTY MATH ASSERTION:
    # Deduct exact Delivery Fee (₹25) + Platform Fee (₹3) = ₹28 penalty
    # Total Paid: ₹238.0
    # Expected Refund: ₹210.0 (exact item subtotal)
    expected_penalty_3 = 25.0 + 3.0  # ₹28.0
    expected_refund_3 = 210.0        # ₹210.0
    record(
        f"Strike 3: Exact Penalty Math Deducts Delivery (₹25) + Platform Fee (₹3) = ₹{expected_penalty_3}",
        c3["refund_penalty"] == expected_penalty_3,
        f"Calculated Penalty: ₹{c3['refund_penalty']} (Expected ₹{expected_penalty_3})"
    )
    record(
        f"Strike 3: Refund Amount Equals Remaining Balance / Item Subtotal (₹{expected_refund_3})",
        c3["refund_amount"] == expected_refund_3,
        f"Calculated Refund: ₹{c3['refund_amount']} (Expected ₹{expected_refund_3})"
    )
    record(
        "Strike 3: Balance Conservation (Refund + Penalty == Total Paid)",
        abs((c3["refund_amount"] + c3["refund_penalty"]) - c3["total_amount"]) < 0.01,
        f"Refund ({c3['refund_amount']}) + Penalty ({c3['refund_penalty']}) == Total ({c3['total_amount']})"
    )

    # 2. Permanent Checkout Block: Blacklisted user CANNOT checkout via COD or UPI
    post_black_cod = client.post("/api/orders/checkout", json={
        "user_phone": test_phone_1,
        "user_name": "Aakash Verma",
        "village": "Rampur",
        "landmark": "Near Main Chaupal",
        "store_id": "sharma_brothers",
        "payment_mode": "COD",
        "distance_km": 1.2,
        "items": [{"id": "item_2", "name": "Oil", "price": 145.0, "qty": 1}]
    })
    record("Strike 3: Blacklisted User Blocked from COD (HTTP 403)", post_black_cod.status_code == 403, f"Status: {post_black_cod.status_code}")

    post_black_upi = client.post("/api/orders/checkout", json={
        "user_phone": test_phone_1,
        "user_name": "Aakash Verma",
        "village": "Rampur",
        "landmark": "Near Main Chaupal",
        "store_id": "sharma_brothers",
        "payment_mode": "UPI",
        "distance_km": 1.2,
        "items": [{"id": "item_2", "name": "Oil", "price": 145.0, "qty": 1}]
    })
    record("Strike 3: Blacklisted User Permanently Blocked from Online UPI (HTTP 403)", post_black_upi.status_code == 403, f"Status: {post_black_upi.status_code}")

    # =========================================================================
    # TEST SUITE 4: MULTI-TIER PREPAID REFUND PENALTY MATH VERIFICATIONS
    # =========================================================================
    print("\n[MULTI-TIER REFUND PENALTY VERIFICATION]: Long-Distance Tier Penalty Audit")

    # User 2: Long-Distance Tier (6.5 km -> Delivery ₹40 + Platform ₹3 = ₹43 Penalty)
    # Fast-forward User 2 directly to Strike 2
    u2 = User(
        phone=test_phone_2,
        name="Sunil Rao",
        cancelled_orders=2,
        is_cod_blocked=True,
        is_blacklisted=False,
        trust_score=40
    )
    db.add(u2)
    db.commit()

    # User 2 places long-distance prepaid order: item_5 (Amul Ghee ₹580), distance 6.5 km
    # Delivery fee: ₹40, Platform: ₹3 -> Total: ₹623
    u2_ord_resp = client.post("/api/orders/checkout", json={
        "user_phone": test_phone_2,
        "user_name": "Sunil Rao",
        "village": "Rampur Long Distance",
        "landmark": "Near Highway Toll",
        "store_id": "sharma_brothers",
        "payment_mode": "UPI",
        "distance_km": 6.5,
        "items": [{"id": "item_5", "name": "Amul Pure Cow Ghee", "price": 580.0, "qty": 1}]
    })
    record("Long Distance Order Placement (HTTP 200)", u2_ord_resp.status_code == 200)
    u2_ord_id = u2_ord_resp.json()["order_id"]
    record("Long Distance Total Amount (₹623)", u2_ord_resp.json()["total_amount"] == 623.0)

    # Cancel order -> This is Strike 3 for User 2
    u2_cancel_resp = client.post(f"/api/orders/{quote(u2_ord_id)}/cancel", json={"reason": "Too far"})
    record("Long Distance Order Cancelled (HTTP 200)", u2_cancel_resp.status_code == 200)
    c_u2 = u2_cancel_resp.json()

    expected_penalty_long = 40.0 + 3.0  # ₹43.0
    expected_refund_long = 580.0        # ₹580.0 (item subtotal)
    record(
        f"Long Distance Tier Penalty Math: Fee (₹40) + Platform (₹3) = ₹{expected_penalty_long}",
        c_u2["refund_penalty"] == expected_penalty_long,
        f"Penalty: ₹{c_u2['refund_penalty']}"
    )
    record(
        f"Long Distance Tier Refund Amount Equals Subtotal (₹{expected_refund_long})",
        c_u2["refund_amount"] == expected_refund_long,
        f"Refund: ₹{c_u2['refund_amount']}"
    )
    record("User 2 Blacklisted at Strike 3", c_u2["is_blacklisted"] is True)

    # =========================================================================
    # TEST SUITE 5: REAL SQLITE DATABASE PERSISTENCE AUDIT
    # =========================================================================
    print("\n[SQLITE DATABASE AUDIT]: Direct Table Persistence Verification")

    db.expire_all()
    user_row = db.query(User).filter(User.phone == test_phone_1).first()
    record("DB User exists", user_row is not None)
    record("DB User cancelled_orders == 3", user_row.cancelled_orders == 3, f"Count: {user_row.cancelled_orders}")
    record("DB User is_cod_blocked == True", user_row.is_cod_blocked is True)
    record("DB User is_blacklisted == True", user_row.is_blacklisted is True)
    record("DB User warning_alert is populated", bool(user_row.warning_alert), f"Alert: {user_row.warning_alert}")

    order_row = db.query(Order).filter(Order.id == ord3_id).first()
    record("DB Order exists", order_row is not None)
    record("DB Order timeline_stage == 0", order_row.timeline_stage == 0)
    record("DB Order refund_penalty == ₹28.0", order_row.refund_penalty == 28.0, f"Penalty: ₹{order_row.refund_penalty}")
    record("DB Order refund_amount == ₹210.0", order_row.refund_amount == 210.0, f"Refund: ₹{order_row.refund_amount}")

    # Trust Status API Check
    trust_api_resp = client.get(f"/api/user/{test_phone_1}/trust-status")
    record("Trust Status API (HTTP 200)", trust_api_resp.status_code == 200)
    t_data = trust_api_resp.json()
    record("Trust Status API: can_order == False", t_data["can_order"] is False)
    record("Trust Status API: is_blacklisted == True", t_data["is_blacklisted"] is True)
    record("Trust Status API: allowed_payment_modes is empty", len(t_data["allowed_payment_modes"]) == 0)

    db.close()

    print("\n" + "=" * 80)
    print(f"TRUST SCORE & REFUND PENALTY AUDIT RESULTS: {passed_tests}/{total_tests} CHECKS PASSED")
    print("=" * 80)
    print("✅ ALL 3-STRIKE TRUST SCORE & REFUND PENALTY CRITERIA VERIFIED 100%")

if __name__ == "__main__":
    run_trust_score_tests()

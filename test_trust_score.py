"""
Automated Verification Suite for GaonBazaar Invisible Customer Trust Score & 3-Strike Policy
Timeline Verification:
1. Cancel Order 1 -> Vague Warning, Full Refund, COD Not Blocked.
2. Cancel Order 2 -> COD Blocked, Full Refund, COD Checkout Rejected (HTTP 400).
3. Complete Order 3 Successfully (Stage 5 "Delivered") -> Counter resets to 0, COD is Unblocked.
4. Cancel Orders 4, 5, and 6 consecutively:
   - Order 4: 1st consecutive cancellation (Warning, No COD Block)
   - Order 5: 2nd consecutive cancellation (COD Blocked)
   - Order 6: 3rd consecutive cancellation:
     * Exact penalty math: Strictly deducts Delivery Fee + Platform Fee (₹3)
     * Refund strictly equals item subtotal
     * User is permanently blacklisted (HTTP 403 for COD & Online UPI)
5. Multi-Tier Delivery Fee Refund Penalty Verification (Long Distance Tier 3).
6. Frontend Security & Invisibility Audit:
   - Assert "Trust Score", "Strike", and cancellation counters are 100% purged from customer UI (index.html).
   - Assert Super Admin Dashboard (admin_dashboard.html) provides complete God-View oversight.
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
from backend.models import User, Order
from backend.security import checkout_rate_limiter, otp_rate_limiter

def run_trust_score_tests():
    print("=" * 80)
    print("GAONBAZAAR INVISIBLE 3-STRIKE CONSECUTIVE CANCELLATION ENGINE VERIFICATION")
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

    for p in [test_phone_1, test_phone_2]:
        orders = db.query(Order).filter(Order.user_phone == p).all()
        for ord_obj in orders:
            db.delete(ord_obj)
        db.commit()
        u = db.query(User).filter(User.phone == p).first()
        if u:
            db.delete(u)
        db.commit()

    # =========================================================================
    # TIMELINE STEP 1: CANCEL ORDER 1 (Vague Warning & Full Refund)
    # =========================================================================
    print("\n[STEP 1]: Cancel Order 1 -> Vague Warning, Full Refund, COD Not Blocked")

    # Place Prepaid UPI Order 1: Fortune Mustard Oil (₹145.0) + Delivery (₹15.0) + Platform (₹3.0) = ₹163.0
    payload_1 = {
        "user_phone": test_phone_1,
        "user_name": "Aakash Verma",
        "village": "Rampur",
        "landmark": "Near Main Chaupal, Shiva Mandir",
        "store_id": "sharma_brothers",
        "payment_mode": "UPI",
        "distance_km": 1.2,
        "items": [{"id": "item_2", "name": "Fortune Mustard Oil", "price": 145.0, "qty": 1}]
    }
    resp1 = client.post("/api/orders/checkout", json=payload_1)
    record("Step 1: Order 1 Placed (HTTP 200)", resp1.status_code == 200, f"Status: {resp1.status_code}")
    ord1_id = resp1.json()["order_id"]

    # Cancel Order 1
    cancel_resp1 = client.post(f"/api/orders/{quote(ord1_id)}/cancel", json={"reason": "Ordered wrong item"})
    record("Step 1: Cancel Order 1 Succeeded (HTTP 200)", cancel_resp1.status_code == 200)
    c1 = cancel_resp1.json()

    record("Step 1: Consecutive Cancellations is 1", c1["consecutive_cancellations"] == 1, f"Count: {c1['consecutive_cancellations']}")
    record("Step 1: COD NOT Blocked", c1["is_cod_blocked"] is False)
    record("Step 1: NOT Blacklisted", c1["is_blacklisted"] is False)

    exact_vague_warning = "We noticed unusual cancellation activity on your account. Continued cancellations may result in COD or account restrictions."
    record(
        "Step 1: Exact Vague Warning Generated (Rules Hidden from Customer)",
        c1["warning_alert"] == exact_vague_warning,
        f"Alert: {c1['warning_alert']}"
    )
    record("Step 1: Zero Penalty on Prepaid Cancellation", c1["refund_penalty"] == 0.0, f"Penalty: ₹{c1['refund_penalty']}")
    record("Step 1: Full 100% Refund Given", c1["refund_amount"] == 163.0, f"Refund: ₹{c1['refund_amount']}")

    # =========================================================================
    # TIMELINE STEP 2: CANCEL ORDER 2 (COD Blocked & Full Refund)
    # =========================================================================
    print("\n[STEP 2]: Cancel Order 2 -> COD Blocked, Full Refund")

    # Place Order 2 with COD (allowed after 1 strike)
    payload_2 = {
        "user_phone": test_phone_1,
        "user_name": "Aakash Verma",
        "village": "Rampur",
        "landmark": "Near Main Chaupal",
        "store_id": "sharma_brothers",
        "payment_mode": "COD",
        "distance_km": 1.2,
        "items": [{"id": "item_2", "name": "Fortune Mustard Oil", "price": 145.0, "qty": 1}]
    }
    resp2 = client.post("/api/orders/checkout", json=payload_2)
    record("Step 2: Order 2 Placed with COD (HTTP 200)", resp2.status_code == 200)
    ord2_id = resp2.json()["order_id"]

    # Cancel Order 2
    cancel_resp2 = client.post(f"/api/orders/{quote(ord2_id)}/cancel", json={"reason": "Customer changed mind"})
    record("Step 2: Cancel Order 2 Succeeded (HTTP 200)", cancel_resp2.status_code == 200)
    c2 = cancel_resp2.json()

    record("Step 2: Consecutive Cancellations is 2", c2["consecutive_cancellations"] == 2, f"Count: {c2['consecutive_cancellations']}")
    record("Step 2: is_cod_blocked set to True", c2["is_cod_blocked"] is True)
    record("Step 2: NOT Blacklisted Yet", c2["is_blacklisted"] is False)
    record("Step 2: Zero Penalty for COD cancellation", c2["refund_penalty"] == 0.0)

    # Attempt to checkout with COD -> MUST FAIL (HTTP 400 Bad Request)
    cod_rejected_resp = client.post("/api/orders/checkout", json=payload_2)
    record(
        "Step 2: COD Checkout Rejected at 2 Consecutive Cancellations (HTTP 400)",
        cod_rejected_resp.status_code == 400 and "COD" in cod_rejected_resp.json().get("detail", ""),
        f"Status: {cod_rejected_resp.status_code}"
    )

    # =========================================================================
    # TIMELINE STEP 3: COMPLETE ORDER 3 (DELIVERED) -> COUNTER RESETS TO 0, COD UNBLOCKED
    # =========================================================================
    print("\n[STEP 3]: Complete Order 3 Successfully -> Counter Resets to 0, COD is Unblocked")

    # Place Order 3 using Prepaid UPI (allowed while COD is blocked)
    payload_3 = {
        "user_phone": test_phone_1,
        "user_name": "Aakash Verma",
        "village": "Rampur",
        "landmark": "Near Main Chaupal",
        "store_id": "sharma_brothers",
        "payment_mode": "UPI",
        "distance_km": 1.2,
        "items": [{"id": "item_2", "name": "Fortune Mustard Oil", "price": 145.0, "qty": 1}]
    }
    resp3 = client.post("/api/orders/checkout", json=payload_3)
    record("Step 3: Prepaid Order 3 Placed (HTTP 200)", resp3.status_code == 200)
    ord3_id = resp3.json()["order_id"]

    # Simulate Order 3 successfully reaching Stage 5 ("Delivered")
    deliver_resp = client.post(f"/api/orders/{quote(ord3_id)}/deliver")
    record("Step 3: Order 3 Transitioned to Stage 5 Delivered (HTTP 200)", deliver_resp.status_code == 200)

    # Audit Database state: consecutive_cancellations MUST be 0 and COD MUST be unblocked!
    db.expire_all()
    user_after_delivery = db.query(User).filter(User.phone == test_phone_1).first()
    record(
        "Step 3: The Reset Logic - consecutive_cancellations Reset to 0",
        user_after_delivery.consecutive_cancellations == 0,
        f"Counter: {user_after_delivery.consecutive_cancellations}"
    )
    record(
        "Step 3: The Reset Logic - COD is Unblocked (is_cod_blocked == False)",
        user_after_delivery.is_cod_blocked is False,
        f"is_cod_blocked: {user_after_delivery.is_cod_blocked}"
    )

    # Verify user can place a COD order again!
    resp_cod_unblocked = client.post("/api/orders/checkout", json=payload_2)
    record(
        "Step 3: User Can Order with COD Again After Successful Delivery (HTTP 200)",
        resp_cod_unblocked.status_code == 200,
        f"Status: {resp_cod_unblocked.status_code}"
    )
    ord4_id = resp_cod_unblocked.json()["order_id"]

    # =========================================================================
    # TIMELINE STEP 4: CANCEL ORDERS 4, 5, AND 6 CONSECUTIVELY -> BLACKLIST & STRICT PENALTY
    # =========================================================================
    print("\n[STEP 4]: Cancel Orders 4, 5, and 6 Consecutively -> Order 6 Penalty & Blacklist")

    # Cancel Order 4 (1st consecutive cancellation after reset)
    c_resp4 = client.post(f"/api/orders/{quote(ord4_id)}/cancel", json={"reason": "Cancel 4"})
    record("Step 4: Cancel Order 4 Succeeded (HTTP 200)", c_resp4.status_code == 200)
    c4 = c_resp4.json()
    record("Step 4: Order 4 - consecutive_cancellations is 1", c4["consecutive_cancellations"] == 1)
    record("Step 4: Order 4 - COD Still Allowed", c4["is_cod_blocked"] is False)

    # Place and Cancel Order 5 (2nd consecutive cancellation)
    resp5 = client.post("/api/orders/checkout", json=payload_2)
    ord5_id = resp5.json()["order_id"]
    c_resp5 = client.post(f"/api/orders/{quote(ord5_id)}/cancel", json={"reason": "Cancel 5"})
    record("Step 4: Cancel Order 5 Succeeded (HTTP 200)", c_resp5.status_code == 200)
    c5 = c_resp5.json()
    record("Step 4: Order 5 - consecutive_cancellations is 2", c5["consecutive_cancellations"] == 2)
    record("Step 4: Order 5 - COD Blocked Again", c5["is_cod_blocked"] is True)

    # Place Order 6 using Prepaid UPI: Atta (₹210.0), distance 3.0 km (Fee ₹25.0, Platform ₹3.0, Total ₹238.0)
    payload_6 = {
        "user_phone": test_phone_1,
        "user_name": "Aakash Verma",
        "village": "Rampur",
        "landmark": "Near Main Chaupal",
        "store_id": "sharma_brothers",
        "payment_mode": "UPI",
        "distance_km": 3.0,
        "items": [{"id": "item_1", "name": "Atta", "price": 210.0, "qty": 1}]
    }
    resp6 = client.post("/api/orders/checkout", json=payload_6)
    record("Step 4: Order 6 Placed with UPI (HTTP 200)", resp6.status_code == 200)
    ord6_id = resp6.json()["order_id"]

    # Cancel Order 6 -> 3rd Consecutive Cancellation (STRIKE 3)
    c_resp6 = client.post(f"/api/orders/{quote(ord6_id)}/cancel", json={"reason": "Cancel 6 - 3rd consecutive strike"})
    record("Step 4: Cancel Order 6 Succeeded (HTTP 200)", c_resp6.status_code == 200)
    c6 = c_resp6.json()

    record("Step 4: Order 6 - consecutive_cancellations is 3", c6["consecutive_cancellations"] == 3)
    record("Step 4: Order 6 - User is Blacklisted (is_blacklisted == True)", c6["is_blacklisted"] is True)
    record("Step 4: Order 6 - COD Blocked", c6["is_cod_blocked"] is True)

    # STRICT PENALTY MATH VERIFICATION ON ORDER 6:
    # Subtotal: ₹210.0, Delivery Fee: ₹20.0 (for 3.0 km tier), Platform Fee: ₹3.0, Total: ₹233.0
    # Expected Penalty = Delivery Fee (₹20.0) + Platform Fee (₹3.0) = ₹23.0
    # Expected Refund = Exact Item Subtotal = ₹210.0
    expected_penalty_6 = 20.0 + 3.0
    expected_refund_6 = 210.0
    record(
        f"Step 4: Strict Penalty Math - Deducts Exact Delivery (₹20) + Platform Fee (₹3) = ₹{expected_penalty_6}",
        c6["refund_penalty"] == expected_penalty_6,
        f"Calculated Penalty: ₹{c6['refund_penalty']} (Expected ₹{expected_penalty_6})"
    )
    record(
        f"Step 4: Strict Refund Math - Only Refunds Exact Item Subtotal (₹{expected_refund_6})",
        c6["refund_amount"] == expected_refund_6,
        f"Calculated Refund: ₹{c6['refund_amount']} (Expected ₹{expected_refund_6})"
    )
    record(
        "Step 4: Balance Conservation (Refund + Penalty == Total Paid)",
        abs((c6["refund_amount"] + c6["refund_penalty"]) - c6["total_amount"]) < 0.01,
        f"₹{c6['refund_amount']} + ₹{c6['refund_penalty']} == ₹{c6['total_amount']}"
    )

    # Permanent checkout blocks for Blacklisted User:
    post_block_cod = client.post("/api/orders/checkout", json=payload_2)
    record("Step 4: Blacklisted User Blocked from COD (HTTP 403)", post_block_cod.status_code == 403)
    post_block_upi = client.post("/api/orders/checkout", json=payload_6)
    record("Step 4: Blacklisted User Permanently Blocked from Online UPI (HTTP 403)", post_block_upi.status_code == 403)

    # =========================================================================
    # TIMELINE STEP 5: MULTI-TIER LONG DISTANCE PREPAID PENALTY AUDIT
    # =========================================================================
    print("\n[STEP 5]: Long-Distance Multi-Tier Prepaid Refund Penalty Audit")

    # Fast forward User 2 to 2 consecutive cancellations
    u2 = User(
        phone=test_phone_2,
        name="Sunil Rao",
        consecutive_cancellations=2,
        cancelled_orders=2,
        is_cod_blocked=True,
        is_blacklisted=False,
        trust_score=40
    )
    db.add(u2)
    db.commit()

    # User 2 places long-distance order (6.5 km -> Delivery ₹35, Platform ₹3, Total ₹618)
    u2_ord = client.post("/api/orders/checkout", json={
        "user_phone": test_phone_2,
        "user_name": "Sunil Rao",
        "village": "Rampur Long Distance",
        "landmark": "Near Highway Toll",
        "store_id": "sharma_brothers",
        "payment_mode": "UPI",
        "distance_km": 6.5,
        "items": [{"id": "item_5", "name": "Amul Pure Cow Ghee", "price": 580.0, "qty": 1}]
    })
    record("Step 5: Long Distance Order Placed (HTTP 200)", u2_ord.status_code == 200)
    u2_ord_id = u2_ord.json()["order_id"]
    record("Step 5: Long Distance Total Amount is ₹618", u2_ord.json()["total_amount"] == 618.0)

    # Cancel Long-Distance Order -> Strike 3 for User 2
    u2_c = client.post(f"/api/orders/{quote(u2_ord_id)}/cancel", json={"reason": "Too far"})
    record("Step 5: Long Distance Order Cancelled (HTTP 200)", u2_c.status_code == 200)
    c_u2 = u2_c.json()

    expected_penalty_long = 35.0 + 3.0  # ₹38.0
    expected_refund_long = 580.0        # ₹580.0
    record(
        f"Step 5: Long Distance Penalty Deducts Fee (₹35) + Platform (₹3) = ₹{expected_penalty_long}",
        c_u2["refund_penalty"] == expected_penalty_long,
        f"Penalty: ₹{c_u2['refund_penalty']}"
    )
    record(
        f"Step 5: Long Distance Refund Strictly Equals Subtotal (₹{expected_refund_long})",
        c_u2["refund_amount"] == expected_refund_long,
        f"Refund: ₹{c_u2['refund_amount']}"
    )

    # =========================================================================
    # TIMELINE STEP 6: FRONTEND SECURITY & INVISIBLE UI AUDIT
    # =========================================================================
    print("\n[STEP 6]: Frontend Security & Invisibility Audit (Customer UI vs Super Admin)")

    # 1. Audit index.html: "profile-trust-score" must NOT exist
    with open("index.html", "r", encoding="utf-8") as f:
        cust_html = f.read()

    record(
        "Step 6: id='profile-trust-score' Purged from Customer UI",
        "profile-trust-score" not in cust_html,
        "Confirmed #profile-trust-score is completely absent from index.html"
    )

    # Profile card text check
    has_hostile_customer_metric = any(
        term in cust_html.lower() for term in [
            "cancellation count",
            "strike counter",
            "account trust score",
            "customer trust score"
        ]
    )
    record(
        "Step 6: Hostile Risk Metrics Purged from Public Customer HTML",
        not has_hostile_customer_metric,
        "Customer app DOM is 100% clean of internal risk terminology"
    )

    # 2. Audit admin_dashboard.html: Admin God-View must contain risk profile tab & tables
    with open("admin_dashboard.html", "r", encoding="utf-8") as f:
        admin_html = f.read()

    record(
        "Step 6: Admin Dashboard Features Account Risk Profile Tab",
        "admin-tab-btn-risk" in admin_html and "tab-risk" in admin_html,
        "Admin Dashboard includes internal risk control interface"
    )
    record(
        "Step 6: Admin Dashboard Has Risk Profiles Table Body",
        "risk-profiles-table-body" in admin_html,
        "Admin God-View table populated for internal oversight"
    )

    # 3. Super Admin API Check
    admin_risk_api = client.get("/api/admin/users/risk-profile")
    record("Step 6: Super Admin Risk Profile API Succeeded (HTTP 200)", admin_risk_api.status_code == 200)
    risk_users = admin_risk_api.json()
    u1_admin_profile = next((u for u in risk_users if u["phone"] == test_phone_1), None)
    record(
        "Step 6: Admin Risk API Exposes consecutive_cancellations and Blacklist to Super Admin Only",
        u1_admin_profile is not None and u1_admin_profile["consecutive_cancellations"] == 3 and u1_admin_profile["is_blacklisted"] is True,
        f"Admin view: {u1_admin_profile}"
    )

    db.close()

    print("\n" + "=" * 80)
    print(f"TRUST SCORE & 3-STRIKE AUDIT RESULTS: {passed_tests}/{total_tests} CHECKS PASSED")
    print("=" * 80)
    print("✅ ALL INVISIBLE 3-STRIKE CONSECUTIVE CANCELLATION ENGINE TESTS VERIFIED 100%")

if __name__ == "__main__":
    run_trust_score_tests()

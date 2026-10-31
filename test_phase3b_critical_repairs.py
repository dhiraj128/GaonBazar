"""
GAONBAZAAR: PHASE 3B CRITICAL REPAIRS & ADVERSARIAL INTEGRITY TEST SUITE
Covers all Priority 0 security, financial, and multi-tenant access-control hardening.
"""

import os
import sys
sys.stdout.reconfigure(encoding="utf-8")
import uuid
import json
import hmac
import hashlib
from datetime import datetime, timezone

# Ensure backend can be imported
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from starlette.testclient import TestClient
from backend.main import (
    app,
    get_db,
    RAZORPAY_WEBHOOK_SECRET,
    RAZORPAY_LIVE_REFUNDS_ENABLED
)
from backend.security import create_jwt_token
from backend.models import (
    Base,
    User,
    Store,
    Product,
    Order,
    OrderItem,
    Runner,
    Replacement,
    RefundRecord,
    PaymentTransaction
)

client = TestClient(app)

PASSED_CHECKS = 0
TOTAL_CHECKS = 0

def check(description: str, condition: bool, details: str = ""):
    global PASSED_CHECKS, TOTAL_CHECKS
    TOTAL_CHECKS += 1
    if condition:
        PASSED_CHECKS += 1
        print(f"  [PASS] {description}")
    else:
        print(f"  [FAIL] {description} -> {details}")
        raise AssertionError(f"Check failed: {description} ({details})")


def run_critical_repair_tests():
    global PASSED_CHECKS, TOTAL_CHECKS
    print("\n" + "="*80)
    print("GAONBAZAAR: PHASE 3B CRITICAL REPAIRS ADVERSARIAL VERIFICATION")
    print("="*80)

    db = next(get_db())

    # Create test actors
    cust_phone = f"98{uuid.uuid4().hex[:8]}"
    other_cust_phone = f"99{uuid.uuid4().hex[:8]}"
    vendor_phone = f"97{uuid.uuid4().hex[:8]}"
    runner_phone = f"96{uuid.uuid4().hex[:8]}"
    other_runner_phone = f"95{uuid.uuid4().hex[:8]}"

    cust_token = create_jwt_token({"phone": cust_phone, "role": "customer"})
    other_cust_token = create_jwt_token({"phone": other_cust_phone, "role": "customer"})
    vendor_token = create_jwt_token({"phone": vendor_phone, "role": "vendor", "store_id": "store_test_3b"})
    runner_token = create_jwt_token({"phone": runner_phone, "role": "runner", "runner_id": "runner_test_3b"})
    other_runner_token = create_jwt_token({"phone": other_runner_phone, "role": "runner", "runner_id": "runner_other_3b"})
    admin_token = create_jwt_token({"phone": "9999999999", "role": "admin"})

    # Setup Product & Order
    prod = Product(
        id=f"prod_crit_{uuid.uuid4().hex[:6]}",
        name_en="Amul Gold Milk 500ml",
        name_hi="अमूल गोल्ड दूध 500ml",
        price=33.0,
        mrp=35.0,
        weight="500ml",
        stock_qty=50,
        in_stock=True,
        category="dairy",
        store_id="store_test_3b"
    )
    db.add(prod)

    test_order = Order(
        id=f"ORD-CRIT-{uuid.uuid4().hex[:6]}",
        user_id="user_test_crit",
        user_phone=cust_phone,
        user_name="Pooja Sharma",
        village="Goa Village",
        landmark="Near Church",
        store_id="store_test_3b",
        store_name="Goa Mart",
        subtotal=66.0,
        delivery_fee=20.0,
        platform_fee=5.0,
        total_amount=91.0,
        payment_mode="ONLINE",
        payment_status="PAID",
        delivery_otp="1234",
        status="Delivered",
        timeline_stage=5,
        created_at=datetime.now(timezone.utc)
    )
    db.add(test_order)
    db.flush()

    ord_item = OrderItem(
        order_id=test_order.id,
        product_id=prod.id,
        product_name=prod.name_en,
        price=33.0,
        quantity=2
    )
    db.add(ord_item)
    db.commit()

    # -------------------------------------------------------------------------
    # SUITE 1: Object-Level Authorization & OTP Suppression on Replacements
    # -------------------------------------------------------------------------
    print("\n--- 1. Object-Level Access & OTP Suppression (P0.2) ---")
    rep_obj = Replacement(
        replacement_id=f"REP-SEC-{uuid.uuid4().hex[:6]}",
        original_order_id=test_order.id,
        customer_phone=cust_phone,
        customer_name="Pooja Sharma",
        store_id="store_test_3b",
        runner_id="runner_test_3b",
        replacement_product_id=prod.id,
        product_name=prod.name_en,
        quantity=1,
        item_price=33.0,
        reason="damaged_item",
        delivery_verification="8844",
        status="OUT_FOR_DELIVERY",
        otp_attempts=0
    )
    db.add(rep_obj)
    db.commit()

    # 1.1 Unauthenticated request rejected
    r_unauth = client.get(f"/api/replacements/{rep_obj.replacement_id}")
    check("Unauthenticated request to replacement detail returns HTTP 401", r_unauth.status_code == 401)

    # 1.2 Unrelated customer rejected
    r_other_cust = client.get(
        f"/api/replacements/{rep_obj.replacement_id}",
        headers={"Authorization": f"Bearer {other_cust_token}"}
    )
    check("Unrelated customer viewing replacement returns HTTP 403", r_other_cust.status_code == 403)

    # 1.3 Customer owner can see OTP
    r_owner = client.get(
        f"/api/replacements/{rep_obj.replacement_id}",
        headers={"Authorization": f"Bearer {cust_token}"}
    )
    check("Customer owner retrieves replacement with HTTP 200", r_owner.status_code == 200)
    check("Customer owner sees delivery_verification OTP", r_owner.json().get("delivery_verification") == "8844")

    # 1.4 Vendor sees replacement but delivery OTP is suppressed
    r_ven = client.get(
        f"/api/replacements/{rep_obj.replacement_id}",
        headers={"Authorization": f"Bearer {vendor_token}"}
    )
    check("Assigned vendor retrieves replacement with HTTP 200", r_ven.status_code == 200)
    check("Assigned vendor GET view suppresses delivery OTP", r_ven.json().get("delivery_verification") is None)
    check("Customer phone masked for vendor", "******" in r_ven.json().get("customer_phone", ""))

    # 1.5 Runner sees replacement but delivery OTP is suppressed
    r_run = client.get(
        f"/api/replacements/{rep_obj.replacement_id}",
        headers={"Authorization": f"Bearer {runner_token}"}
    )
    check("Assigned runner retrieves replacement with HTTP 200", r_run.status_code == 200)
    check("Assigned runner GET view suppresses delivery OTP", r_run.json().get("delivery_verification") is None)

    # 1.6 Unassigned runner rejected
    r_other_run = client.get(
        f"/api/replacements/{rep_obj.replacement_id}",
        headers={"Authorization": f"Bearer {other_runner_token}"}
    )
    check("Unassigned runner viewing replacement returns HTTP 403", r_other_run.status_code == 403)

    # -------------------------------------------------------------------------
    # SUITE 2: OTP Brute-Force Rate Limiting (5 Attempts Max) (P0.6)
    # -------------------------------------------------------------------------
    print("\n--- 2. OTP Brute-Force Protection & Rate Limiting (P0.6) ---")
    for attempt in range(1, 6):
        r_fail = client.post(
            f"/api/runner/replacements/{rep_obj.replacement_id}/verify-otp",
            json={"otp": f"999{attempt}"},
            headers={"Authorization": f"Bearer {runner_token}"}
        )
        check(f"Incorrect OTP attempt {attempt} rejected with HTTP 400", r_fail.status_code == 400)

    # 6th attempt after 5 failed attempts should trigger lockout (HTTP 429)
    r_fail_6 = client.post(
        f"/api/runner/replacements/{rep_obj.replacement_id}/verify-otp",
        json={"otp": "0000"},
        headers={"Authorization": f"Bearer {runner_token}"}
    )
    check("6th attempt after 5 failed attempts triggers lockout with HTTP 429", r_fail_6.status_code == 429)

    # Subsequent attempt even with correct OTP remains locked
    r_locked = client.post(
        f"/api/runner/replacements/{rep_obj.replacement_id}/verify-otp",
        json={"otp": "8844"},
        headers={"Authorization": f"Bearer {runner_token}"}
    )
    check("Locked replacement rejects OTP verification with HTTP 429", r_locked.status_code == 429)

    # -------------------------------------------------------------------------
    # SUITE 3: Item-Level Strict Pricing & Anti-Overcompensation (P0.3)
    # -------------------------------------------------------------------------
    print("\n--- 3. Pricing Derivation & Anti-Overcompensation (P0.3) ---")
    # Fresh order for grievance tests
    test_ord2 = Order(
        id=f"ORD-ITEM-{uuid.uuid4().hex[:6]}",
        user_id="user_test_crit",
        user_phone=cust_phone,
        user_name="Pooja Sharma",
        village="Goa Village",
        landmark="Near Post Office",
        store_id="store_test_3b",
        store_name="Goa Mart",
        delivery_otp="5566",
        subtotal=66.0,
        delivery_fee=20.0,
        platform_fee=5.0,
        total_amount=91.0,
        payment_mode="ONLINE",
        payment_status="PAID",
        status="Delivered",
        timeline_stage=5,
        created_at=datetime.now(timezone.utc)
    )
    db.add(test_ord2)
    db.flush()

    ord2_item = OrderItem(
        order_id=test_ord2.id,
        product_id=prod.id,
        product_name=prod.name_en,
        price=33.0,
        quantity=2
    )
    db.add(ord2_item)
    db.commit()

    # 3.1 Unpurchased product rejection
    r_unpurchased = client.post(
        "/api/resolutions/issue",
        json={
            "order_id": test_ord2.id,
            "category": "damaged_item",
            "preferred_resolution": "refund",
            "message": "Damaged pack",
            "affected_items": [{"product_id": "fake_unpurchased_prod", "qty": 1}]
        },
        headers={"Authorization": f"Bearer {cust_token}"}
    )
    check("Unpurchased product rejected with HTTP 400", r_unpurchased.status_code == 400)

    # 3.2 Excess quantity rejection (requested 5, bought 2)
    r_excess_qty = client.post(
        "/api/resolutions/issue",
        json={
            "order_id": test_ord2.id,
            "category": "damaged_item",
            "preferred_resolution": "refund",
            "message": "Damaged pack",
            "affected_items": [{"product_id": prod.id, "qty": 5}]
        },
        headers={"Authorization": f"Bearer {cust_token}"}
    )
    check("Excess quantity request rejected with HTTP 400", r_excess_qty.status_code == 400)

    # 3.3 Valid item calculation (qty=1 -> ₹33.00, not arbitrary 50%)
    r_valid_claim = client.post(
        "/api/resolutions/issue",
        json={
            "order_id": test_ord2.id,
            "category": "damaged_item",
            "preferred_resolution": "refund",
            "message": "1 bottle leaked",
            "affected_items": [{"product_id": prod.id, "qty": 1}]
        },
        headers={"Authorization": f"Bearer {cust_token}"}
    )
    check("Valid item-level claim registered with HTTP 200", r_valid_claim.status_code == 200)
    claim_refund_id = r_valid_claim.json().get("refund_id")
    check("Refund amount strictly derived from item price (₹33.00)", r_valid_claim.json().get("refund_amount") == 33.0)

    # 3.4 Anti-overcompensation: refund remainder of order
    ref_rec1 = db.query(RefundRecord).filter(RefundRecord.refund_id == claim_refund_id).first()
    ref_rec1.status = "APPROVED"
    db.commit()

    # Second claim for remaining amount (₹91.00 - ₹33.00 = ₹58.00)
    r_claim2 = client.post(
        "/api/resolutions/issue",
        json={
            "order_id": test_ord2.id,
            "category": "order_not_delivered",
            "preferred_resolution": "refund",
            "message": "Rest of order never arrived"
        },
        headers={"Authorization": f"Bearer {cust_token}"}
    )
    check("Second claim for remaining balance accepted with HTTP 200", r_claim2.status_code == 200)
    check("Remaining balance capped at ₹58.00 (₹91 - ₹33)", r_claim2.json().get("refund_amount") == 58.0)

    # Third claim when order is fully exhausted should fail
    ref_rec2 = db.query(RefundRecord).filter(RefundRecord.refund_id == r_claim2.json().get("refund_id")).first()
    ref_rec2.status = "APPROVED"
    db.commit()

    r_claim_over = client.post(
        "/api/resolutions/issue",
        json={
            "order_id": test_ord2.id,
            "category": "order_not_delivered",
            "preferred_resolution": "refund",
            "message": "Try to get more money"
        },
        headers={"Authorization": f"Bearer {cust_token}"}
    )
    check("Claim exceeding order total balance rejected with HTTP 400", r_claim_over.status_code == 400)

    # -------------------------------------------------------------------------
    # SUITE 4: Cancellation Policy Overhaul & Zero 3-Strike Penalties (P0.4)
    # -------------------------------------------------------------------------
    print("\n--- 4. Cancellation Policy & Zero 3-Strike Penalty (P0.4) ---")
    cancel_ord = Order(
        id=f"ORD-CANC-{uuid.uuid4().hex[:6]}",
        user_id="user_test_crit",
        user_phone=cust_phone,
        user_name="Pooja Sharma",
        village="Goa Village",
        landmark="Near Post Office",
        store_id="store_test_3b",
        store_name="Goa Mart",
        delivery_otp="5566",
        subtotal=100.0,
        delivery_fee=20.0,
        platform_fee=5.0,
        total_amount=125.0,
        payment_mode="UPI",
        payment_status="PAID",
        status="Placed",
        timeline_stage=1,
        created_at=datetime.now(timezone.utc)
    )
    db.add(cancel_ord)
    db.commit()

    r_cancel = client.post(
        f"/api/orders/{cancel_ord.id}/cancel",
        json={"reason": "Ordered by mistake"},
        headers={"Authorization": f"Bearer {cust_token}"}
    )
    check("Stage 1 order cancellation succeeds with HTTP 200", r_cancel.status_code == 200)
    cancel_data = r_cancel.json()
    check("Refund amount is 100% of total (₹125.00)", cancel_data.get("refund_amount") == 125.0)
    check("Penalty is strictly ₹0.00 (Zero 3-strike penalty)", cancel_data.get("refund_penalty") == 0.0)

    db.refresh(cancel_ord)
    check("Order status marked as Cancelled", cancel_ord.status == "Cancelled")
    check("Inventory restoration flag set to True", cancel_ord.inventory_restored is True)
    check("Refund record created for cancellation", cancel_ord.refund_id is not None)

    # -------------------------------------------------------------------------
    # SUITE 5: Truthful Gateway Execution & Financial Settlements (P0.1, P0.6)
    # -------------------------------------------------------------------------
    print("\n--- 5. Truthful Refund Status & Runner Delivery Payout (P0.1, P0.6) ---")
    check(f"RAZORPAY_LIVE_REFUNDS_ENABLED is disabled by default ({RAZORPAY_LIVE_REFUNDS_ENABLED})", RAZORPAY_LIVE_REFUNDS_ENABLED is False)

    # Admin approval on refund record
    r_admin_appr = client.post(
        f"/api/admin/resolutions/{cancel_ord.refund_id}/action",
        json={"action": "approve_refund", "responsible_party": "platform"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    check("Admin refund action returns HTTP 200", r_admin_appr.status_code == 200)
    appr_json = r_admin_appr.json()
    check("Status truthfully stays APPROVED without fake rfnd_ generation", appr_json.get("status") == "APPROVED")

    canc_ref_rec = db.query(RefundRecord).filter(RefundRecord.refund_id == cancel_ord.refund_id).first()
    check("No fabricated Razorpay refund ID in database", canc_ref_rec.razorpay_refund_id is None)

    # Successful Runner replacement delivery settlement test
    rep_settle = Replacement(
        replacement_id=f"REP-SETTLE-{uuid.uuid4().hex[:6]}",
        original_order_id=test_order.id,
        customer_phone=cust_phone,
        customer_name="Pooja Sharma",
        store_id="store_test_3b",
        runner_id="runner_test_3b",
        replacement_product_id=prod.id,
        product_name=prod.name_en,
        quantity=1,
        item_price=33.0,
        reason="damaged_item",
        delivery_verification="9988",
        status="OUT_FOR_DELIVERY",
        otp_attempts=0
    )
    db.add(rep_settle)
    db.commit()

    r_otp_success = client.post(
        f"/api/runner/replacements/{rep_settle.replacement_id}/verify-otp",
        json={"otp": "9988"},
        headers={"Authorization": f"Bearer {runner_token}"}
    )
    check("Runner completes delivery with correct OTP (HTTP 200)", r_otp_success.status_code == 200)
    db.refresh(rep_settle)
    check("Replacement status updated to REPLACED", rep_settle.status == "REPLACED")

    # Verify Runner Payout transaction record in database
    payout_tx = db.query(PaymentTransaction).filter(
        PaymentTransaction.payment_mode == "RUNNER_PAYOUT",
        PaymentTransaction.razorpay_order_id == f"PAYOUT-REP-{rep_settle.replacement_id}"
    ).first()
    check("Runner delivery payout transaction created in payment_transactions", payout_tx is not None)
    if payout_tx:
        check("Runner payout amount is ₹20.00", payout_tx.amount == 20.0)
        check("Runner payout status is EARNED", payout_tx.status == "EARNED")
        check("Runner payout route transfer is payable", payout_tx.route_transfer_status == "payable")

    # -------------------------------------------------------------------------
    # SUITE 6: Webhook Handling for refund.failed (P0.1)
    # -------------------------------------------------------------------------
    print("\n--- 6. Webhook Reconciliation for refund.failed (P0.1) ---")
    fail_webhook_payload = {
        "event": "refund.failed",
        "payload": {
            "refund": {
                "entity": {
                    "id": "rfnd_test_failed_888",
                    "payment_id": "pay_test_online_456",
                    "amount": 12500,
                    "status": "failed",
                    "error_description": "Bank servers unavailable",
                    "notes": {
                        "refund_id": canc_ref_rec.refund_id
                    }
                }
            }
        }
    }
    raw_wh_fail_bytes = json.dumps(fail_webhook_payload).encode("utf-8")
    sig_fail = hmac.new(
        key=RAZORPAY_WEBHOOK_SECRET.encode("utf-8"),
        msg=raw_wh_fail_bytes,
        digestmod=hashlib.sha256
    ).hexdigest()

    r_wh_fail = client.post(
        "/api/payments/webhook",
        content=raw_wh_fail_bytes,
        headers={
            "Content-Type": "application/json",
            "X-Razorpay-Signature": sig_fail
        }
    )
    check("refund.failed webhook accepted with HTTP 200", r_wh_fail.status_code == 200)
    db.refresh(canc_ref_rec)
    check("RefundRecord status transitioned to FAILED", canc_ref_rec.status == "FAILED")
    check("Failure reason captured in database", "Bank servers unavailable" in (canc_ref_rec.failure_reason or ""))

    print("\n" + "="*80)
    print(f"PHASE 3B CRITICAL REPAIRS TEST COMPLETE: {PASSED_CHECKS}/{TOTAL_CHECKS} CHECKS PASSED (100%)")
    print("="*80 + "\n")


if __name__ == "__main__":
    run_critical_repair_tests()
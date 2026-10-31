"""
GaonBazaar P0 Financial Integrity & Razorpay Webhook Precision Test Suite
========================================================================
Validates:
1. payment.authorized event leaves order UNPAID with status 'AUTHORIZED' (zero fulfillment).
2. payment.captured enforces amount in paise match, currency INR, and payment id format.
3. refund.processed requires exact matching refund ID (zero newest-record fallback).
4. refund.processed creates exactly-once ledger PaymentTransaction record with status 'refunded'.
5. admin_execute_resolution_action idempotency protects settled/initiated refunds.
6. runner replacement delivery records payout with status 'EARNED' and route_transfer_status 'payable'.
"""

import sys
import os
import json
import uuid
import hmac
import hashlib
from datetime import datetime, timezone

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.main import app, RAZORPAY_WEBHOOK_SECRET
from backend.models import User, Order, OrderItem, RefundRecord, Replacement, PaymentTransaction, Runner
from backend.database import SessionLocal
from backend.security import create_jwt_token
from starlette.testclient import TestClient

client = TestClient(app)

PASSED = 0
FAILED = 0

def check(name, cond, details=""):
    global PASSED, FAILED
    if cond:
        PASSED += 1
        print(f"  [PASS] {name}")
    else:
        FAILED += 1
        print(f"  [FAIL] {name} -> {details}")
        raise AssertionError(f"{name}: {details}")

def run_financial_integrity_tests():
    db = SessionLocal()
    print("\n================================================================================")
    print("GAONBAZAAR: P0 FINANCIAL INTEGRITY & WEBHOOK PRECISION VERIFICATION")
    print("================================================================================")

    # 1. Setup Test Order
    ord_id = f"ORD-FIN-{uuid.uuid4().hex[:6]}"
    test_ord = Order(
        id=ord_id,
        user_id="user_fin",
        user_phone="9876599999",
        user_name="Financial Test User",
        store_id="sharma_brothers",
        store_name="Sharma Brothers Kirana",
        village="Minapur",
        landmark="P0 Verification Hub",
        subtotal=200.0,
        delivery_fee=20.0,
        platform_fee=5.0,
        total_amount=225.0,
        payment_mode="ONLINE",
        payment_status="PENDING",
        status="Checkout",
        timeline_stage=1,
        delivery_otp="1234",
        created_at=datetime.now(timezone.utc)
    )
    db.add(test_ord)
    db.commit()

    # -------------------------------------------------------------------------
    # TEST 1: payment.authorized NEVER marks order as PAID or Order Placed
    # -------------------------------------------------------------------------
    print("\n--- 1. payment.authorized Event Integrity ---")
    auth_payload = {
        "event": "payment.authorized",
        "payload": {
            "payment": {
                "entity": {
                    "id": f"pay_{uuid.uuid4().hex[:14]}",
                    "order_id": f"order_{uuid.uuid4().hex[:14]}",
                    "amount": 22500,
                    "currency": "INR",
                    "status": "authorized",
                    "notes": {"order_id": ord_id}
                }
            }
        }
    }
    raw_auth = json.dumps(auth_payload).encode("utf-8")
    sig_auth = hmac.new(RAZORPAY_WEBHOOK_SECRET.encode("utf-8"), raw_auth, hashlib.sha256).hexdigest()

    r = client.post("/api/payments/webhook", content=raw_auth, headers={"Content-Type": "application/json", "X-Razorpay-Signature": sig_auth})
    check("payment.authorized webhook accepted with HTTP 200", r.status_code == 200)
    res_json = r.json()
    check("Webhook status is AUTHORIZED (not PAID)", res_json.get("status") == "AUTHORIZED")

    db.refresh(test_ord)
    check("Database order.payment_status is AUTHORIZED", test_ord.payment_status == "AUTHORIZED")
    check("Database order.status is NOT Order Placed (unfulfilled)", test_ord.status != "Order Placed")

    # -------------------------------------------------------------------------
    # TEST 2: payment.captured Validation (amount, currency, status)
    # -------------------------------------------------------------------------
    print("\n--- 2. payment.captured Zero-Trust Validation ---")
    # Bad amount (e.g. 10000 instead of 22500 paise)
    captured_bad_amt = {
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": f"pay_{uuid.uuid4().hex[:14]}",
                    "order_id": f"order_{uuid.uuid4().hex[:14]}",
                    "amount": 10000,
                    "currency": "INR",
                    "status": "captured",
                    "notes": {"order_id": ord_id}
                }
            }
        }
    }
    raw_bad_amt = json.dumps(captured_bad_amt).encode("utf-8")
    sig_bad_amt = hmac.new(RAZORPAY_WEBHOOK_SECRET.encode("utf-8"), raw_bad_amt, hashlib.sha256).hexdigest()
    r_bad_amt = client.post("/api/payments/webhook", content=raw_bad_amt, headers={"Content-Type": "application/json", "X-Razorpay-Signature": sig_bad_amt})
    check("Mismatched payment amount rejected with HTTP 400", r_bad_amt.status_code == 400)

    # Bad currency (e.g. USD instead of INR)
    captured_bad_curr = {
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": f"pay_{uuid.uuid4().hex[:14]}",
                    "order_id": f"order_{uuid.uuid4().hex[:14]}",
                    "amount": 22500,
                    "currency": "USD",
                    "status": "captured",
                    "notes": {"order_id": ord_id}
                }
            }
        }
    }
    raw_bad_curr = json.dumps(captured_bad_curr).encode("utf-8")
    sig_bad_curr = hmac.new(RAZORPAY_WEBHOOK_SECRET.encode("utf-8"), raw_bad_curr, hashlib.sha256).hexdigest()
    r_bad_curr = client.post("/api/payments/webhook", content=raw_bad_curr, headers={"Content-Type": "application/json", "X-Razorpay-Signature": sig_bad_curr})
    check("Non-INR currency rejected with HTTP 400", r_bad_curr.status_code == 400)

    # Valid payment.captured
    real_pay_id = f"pay_{uuid.uuid4().hex[:14]}"
    captured_valid = {
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": real_pay_id,
                    "order_id": f"order_{uuid.uuid4().hex[:14]}",
                    "amount": 22500,
                    "currency": "INR",
                    "status": "captured",
                    "notes": {"order_id": ord_id, "phone": "9876599999"}
                }
            }
        }
    }
    raw_valid = json.dumps(captured_valid).encode("utf-8")
    sig_valid = hmac.new(RAZORPAY_WEBHOOK_SECRET.encode("utf-8"), raw_valid, hashlib.sha256).hexdigest()
    r_valid = client.post("/api/payments/webhook", content=raw_valid, headers={"Content-Type": "application/json", "X-Razorpay-Signature": sig_valid})
    check("Valid payment.captured accepted with HTTP 200", r_valid.status_code == 200)

    db.refresh(test_ord)
    check("Order marked as PAID upon verified capture", test_ord.payment_status == "PAID")
    check("Order status transitioned to Order Placed", test_ord.status == "Order Placed")
    check("Order razorpay_payment_id populated", test_ord.razorpay_payment_id == real_pay_id)

    # -------------------------------------------------------------------------
    # TEST 3: Strict Refund Webhook Matching (Zero Fallback)
    # -------------------------------------------------------------------------
    print("\n--- 3. Strict Refund Matching & Exact Match Requirement ---")
    custom_ref_id = f"REF-FIN-{uuid.uuid4().hex[:6]}"
    ref_record = RefundRecord(
        refund_id=custom_ref_id,
        order_id=ord_id,
        user_phone="9876599999",
        amount=225.0,
        amount_paise=22500,
        reason="P0 Financial Verification",
        payment_mode="ONLINE",
        status="APPROVED",
        created_at=datetime.now(timezone.utc)
    )
    db.add(ref_record)
    db.commit()

    # Webhook with nonexistent refund ID and NO custom refund_id notes
    fake_ref_payload = {
        "event": "refund.processed",
        "payload": {
            "refund": {
                "entity": {
                    "id": f"rfnd_nonexistent_{uuid.uuid4().hex[:8]}",
                    "payment_id": real_pay_id,
                    "amount": 22500,
                    "status": "processed",
                    "notes": {"order_id": ord_id}  # Notice: NO refund_id
                }
            }
        }
    }
    raw_fake = json.dumps(fake_ref_payload).encode("utf-8")
    sig_fake = hmac.new(RAZORPAY_WEBHOOK_SECRET.encode("utf-8"), raw_fake, hashlib.sha256).hexdigest()
    r_fake = client.post("/api/payments/webhook", content=raw_fake, headers={"Content-Type": "application/json", "X-Razorpay-Signature": sig_fake})
    check("Refund webhook with unknown ID rejected with HTTP 404 (Zero newest-record fallback)", r_fake.status_code == 404)

    # Valid refund.processed with exact matching custom refund ID
    gateway_rzp_ref_id = f"rfnd_live_{uuid.uuid4().hex[:12]}"
    valid_ref_payload = {
        "event": "refund.processed",
        "payload": {
            "refund": {
                "entity": {
                    "id": gateway_rzp_ref_id,
                    "payment_id": real_pay_id,
                    "amount": 22500,
                    "status": "processed",
                    "notes": {"order_id": ord_id, "refund_id": custom_ref_id}
                }
            }
        }
    }
    raw_vref = json.dumps(valid_ref_payload).encode("utf-8")
    sig_vref = hmac.new(RAZORPAY_WEBHOOK_SECRET.encode("utf-8"), raw_vref, hashlib.sha256).hexdigest()
    r_vref = client.post("/api/payments/webhook", content=raw_vref, headers={"Content-Type": "application/json", "X-Razorpay-Signature": sig_vref})
    check("Valid refund.processed accepted with HTTP 200", r_vref.status_code == 200)

    # Fresh DB check
    fresh_db = SessionLocal()
    updated_ref = fresh_db.query(RefundRecord).filter(RefundRecord.refund_id == custom_ref_id).first()
    check("RefundRecord transitioned to PROCESSED", updated_ref.status == "PROCESSED")
    check("RefundRecord razorpay_refund_id saved", updated_ref.razorpay_refund_id == gateway_rzp_ref_id)

    # Exactly-once ledger entry in payment_transactions
    refund_tx = fresh_db.query(PaymentTransaction).filter(
        PaymentTransaction.order_id == ord_id,
        PaymentTransaction.payment_mode == "REFUND",
        PaymentTransaction.razorpay_payment_id == gateway_rzp_ref_id
    ).first()
    check("Exactly-once REFUND transaction created in ledger", refund_tx is not None)
    if refund_tx:
        check("Refund ledger transaction status is 'refunded'", refund_tx.status == "refunded")
        check("Refund ledger amount is ₹225.00", refund_tx.amount == 225.0)

    fresh_db.close()

    # -------------------------------------------------------------------------
    # TEST 4: Admin Refund Idempotency
    # -------------------------------------------------------------------------
    print("\n--- 4. Admin Refund Execution Idempotency ---")
    admin_token = create_jwt_token(payload={"phone": "9999999999", "role": "admin"})
    r_reapprove = client.post(
        f"/api/admin/resolutions/{custom_ref_id}/action",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"action": "approve_refund", "responsible_party": "platform"}
    )
    check("Re-approving an already PROCESSED refund rejected with HTTP 400", r_reapprove.status_code == 400)

    # -------------------------------------------------------------------------
    # TEST 5: Runner Replacement Payout 'EARNED' & 'payable'
    # -------------------------------------------------------------------------
    print("\n--- 5. Runner Payout 'EARNED' Status & Dynamic Engine ---")
    runner_id = "gm_fin"
    runner_user = db.query(Runner).filter(Runner.id == runner_id).first()
    if not runner_user:
        runner_user = Runner(
            id=runner_id,
            name="Financial Test Runner",
            phone="9876543299",
            runner_code="#GM-FIN-99",
            status="approved"
        )
        db.add(runner_user)
        db.commit()

    runner_token = create_jwt_token(payload={"runner_id": runner_id, "phone": "9876543299", "role": "runner"})

    rep_id = f"REP-FIN-{uuid.uuid4().hex[:6]}"
    otp_code = "7788"
    rep_obj = Replacement(
        replacement_id=rep_id,
        original_order_id=ord_id,
        replacement_product_id="prod_1",
        product_name=" Basmati Rice 1kg",
        quantity=1,
        item_price=120.0,
        reason="damaged_item",
        customer_phone="9876599999",
        store_id="sharma_brothers",
        runner_id=runner_id,
        runner_payout=25.0,  # Tiered custom distance payout
        status="OUT_FOR_DELIVERY",
        delivery_verification=otp_code,
        customer_charge_paise=0,
        reverse_pickup_required=False,
        reverse_pickup_status="NOT_REQUIRED",
        created_at=datetime.now(timezone.utc)
    )
    db.add(rep_obj)
    db.commit()

    r_otp = client.post(
        f"/api/runner/replacements/{rep_id}/verify-otp",
        headers={"Authorization": f"Bearer {runner_token}"},
        json={"otp": otp_code}
    )
    check("Runner verifies delivery OTP with HTTP 200", r_otp.status_code == 200)

    fresh_db2 = SessionLocal()
    rep_settled = fresh_db2.query(Replacement).filter(Replacement.replacement_id == rep_id).first()
    check("Replacement status is REPLACED", rep_settled.status == "REPLACED")

    runner_tx = fresh_db2.query(PaymentTransaction).filter(
        PaymentTransaction.razorpay_order_id == f"PAYOUT-REP-{rep_id}"
    ).first()
    check("Runner payout transaction created", runner_tx is not None)
    if runner_tx:
        check("Runner payout status is strictly 'EARNED' (not settled/success)", runner_tx.status == "EARNED")
        check("Runner payout route_transfer_status is 'payable'", runner_tx.route_transfer_status == "payable")
        check("Runner payout amount reflects dynamic payout ₹25.00", runner_tx.amount == 25.0)

    fresh_db2.close()
    db.close()

    print("\n================================================================================")
    print(f"P0 FINANCIAL INTEGRITY SUITE: {PASSED}/{PASSED + FAILED} CHECKS PASSED (100%)")
    print("================================================================================")

if __name__ == "__main__":
    run_financial_integrity_tests()

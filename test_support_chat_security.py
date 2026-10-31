"""
test_support_chat_security.py - Comprehensive Adversarial Security & Authorization Test Suite
Validates Priority A (Security Overhaul of /api/support/chat & /api/support/ticket):
1. Anonymous requests -> 401 Unauthorized
2. Expired / forged JWT tokens -> 401 Unauthorized
3. Cross-role boundary defense: Runner / Vendor tokens calling customer chat -> 403 Forbidden
4. Cross-tenant order isolation: Customer A probing Customer B's order -> 403 Forbidden
5. Phone forgery defense: Customer A providing Customer B's phone in payload -> 403 Forbidden
6. Non-existent order probing -> 404 Not Found
7. Delivery OTP leakage prevention:
   - Order at Stage 1/2/3 -> OTP is strictly masked / suppressed
   - Order at Stage 4 -> OTP disclosed ONLY to the verified order owner
8. Truthful refund policy verification: 5-7 business days, never 2 hours
9. Ticket creation & retrieval isolation: tenant isolation per customer phone
10. Preserves DB baseline: cleans up all test fixtures in finally block
"""

import sys
import io
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import SessionLocal
from backend.models import Order, SupportTicket
from backend.security import create_jwt_token

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

client = TestClient(app)

def run_adversarial_security_suite():
    print("=" * 70)
    print("GAONBAZAAR PRIORITY A: SUPPORT CHAT & TICKET ADVERSARIAL SECURITY AUDIT")
    print("=" * 70)

    passed = 0
    total = 0

    def check(name, condition, details=""):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"  ✓ PASS: {name} {details}")
        else:
            print(f"  ✗ FAIL: {name} {details}")
            assert False, f"Test failed: {name} - {details}"

    db = SessionLocal()
    created_orders = []
    created_tickets = []
    try:
        cust_a_phone = "9876500001"
        cust_b_phone = "9876500002"
        runner_phone = "9988776655"
        vendor_store = "sharma_brothers"

        # Tokens
        token_cust_a = create_jwt_token({"role": "customer", "phone": cust_a_phone, "sub": cust_a_phone})
        token_cust_b = create_jwt_token({"role": "customer", "phone": cust_b_phone, "sub": cust_b_phone})
        token_runner = create_jwt_token({"role": "runner", "phone": runner_phone, "runner_id": "RUN-001", "sub": runner_phone})
        token_vendor = create_jwt_token({"role": "vendor", "store_id": vendor_store, "sub": "vendor_user"})
        token_expired = create_jwt_token(
            {"role": "customer", "phone": cust_a_phone, "sub": cust_a_phone},
            expires_delta=timedelta(seconds=-3600)
        )

        headers_a = {"Authorization": f"Bearer {token_cust_a}"}
        headers_b = {"Authorization": f"Bearer {token_cust_b}"}
        headers_runner = {"Authorization": f"Bearer {token_runner}"}
        headers_vendor = {"Authorization": f"Bearer {token_vendor}"}
        headers_expired = {"Authorization": f"Bearer {token_expired}"}

        # Create temporary isolated test orders
        order_a_st2 = Order(
            id="ORD-SEC-A-01",
            user_phone=cust_a_phone,
            user_name="Customer A",
            village="Rampur",
            landmark="Near Old Well",
            store_id=vendor_store,
            store_name="Sharma Brothers Kirana",
            subtotal=234.0,
            total_amount=250.0,
            status="packing",
            timeline_stage=2,
            delivery_otp="4821",
            payment_mode="COD"
        )
        db.add(order_a_st2)
        created_orders.append(order_a_st2)

        order_b_st4 = Order(
            id="ORD-SEC-B-02",
            user_phone=cust_b_phone,
            user_name="Customer B",
            village="Rampur",
            landmark="Near Primary School",
            store_id=vendor_store,
            store_name="Sharma Brothers Kirana",
            subtotal=484.0,
            total_amount=500.0,
            status="out_for_delivery",
            timeline_stage=4,
            delivery_otp="7793",
            payment_mode="UPI"
        )
        db.add(order_b_st4)
        created_orders.append(order_b_st4)

        db.commit()

        # -------------------------------------------------------------
        # TEST 1: ANONYMOUS REQUEST TO /api/support/chat -> 401
        # -------------------------------------------------------------
        print("\n--- 1. Unauthenticated Request Blocking ---")
        res = client.post("/api/support/chat", json={"message": "Where is my order?"})
        check("Anonymous request rejected with 401", res.status_code == 401, f"got {res.status_code}")

        # -------------------------------------------------------------
        # TEST 2: EXPIRED TOKEN -> 401
        # -------------------------------------------------------------
        print("\n--- 2. Expired JWT Token Handling ---")
        res = client.post("/api/support/chat", json={"message": "Where is my order?"}, headers=headers_expired)
        check("Expired token rejected with 401", res.status_code == 401, f"got {res.status_code}")

        # -------------------------------------------------------------
        # TEST 3: MALFORMED TOKEN -> 401
        # -------------------------------------------------------------
        print("\n--- 3. Tampered / Malformed Token Handling ---")
        res = client.post("/api/support/chat", json={"message": "Where is my order?"}, headers={"Authorization": "Bearer invalid.token.xyz"})
        check("Malformed token rejected with 401", res.status_code == 401, f"got {res.status_code}")

        # -------------------------------------------------------------
        # TEST 4: ROLE BOUNDARIES: RUNNER & VENDOR CALLING CUSTOMER CHAT -> 403
        # -------------------------------------------------------------
        print("\n--- 4. Cross-Role Boundary Protection ---")
        res_r = client.post("/api/support/chat", json={"message": "Where is order ORD-SEC-B-02?"}, headers=headers_runner)
        check("Runner token denied customer chat with 403", res_r.status_code == 403, f"got {res_r.status_code}")

        res_v = client.post("/api/support/chat", json={"message": "Where is order ORD-SEC-B-02?"}, headers=headers_vendor)
        check("Vendor token denied customer chat with 403", res_v.status_code == 403, f"got {res_v.status_code}")

        # -------------------------------------------------------------
        # TEST 5: CROSS-TENANT ORDER PROBING: CUSTOMER A QUERIES CUSTOMER B'S ORDER
        # -------------------------------------------------------------
        print("\n--- 5. Cross-Tenant Order Access Enforcement ---")
        res = client.post(
            "/api/support/chat",
            json={"order_id": order_b_st4.id, "message": "Where is my order?"},
            headers=headers_a
        )
        check("Customer A forbidden from accessing Customer B's order ID (403)", res.status_code == 403, f"got {res.status_code}")

        # -------------------------------------------------------------
        # TEST 6: FORGED PHONE NUMBER IN PAYLOAD
        # -------------------------------------------------------------
        print("\n--- 6. Phone Forgery Defense ---")
        res = client.post(
            "/api/support/chat",
            json={"user_phone": cust_b_phone, "message": "Where is my order?"},
            headers=headers_a
        )
        check("Customer A cannot spoof Customer B's phone (403)", res.status_code == 403, f"got {res.status_code}")

        # -------------------------------------------------------------
        # TEST 7: PROBING ARBITRARY NON-EXISTENT ORDER ID -> 404
        # -------------------------------------------------------------
        print("\n--- 7. Non-Existent Order Probing ---")
        res = client.post(
            "/api/support/chat",
            json={"order_id": "ORD-NONEXISTENT-9999", "message": "Where is my order?"},
            headers=headers_a
        )
        check("Probing non-existent order ID returns 404", res.status_code == 404, f"got {res.status_code}")

        # -------------------------------------------------------------
        # TEST 8: LEGITIMATE CUSTOMER A TRACKS OWN ORDER AT STAGE 2
        # (Must succeed, but MUST NOT leak delivery OTP)
        # -------------------------------------------------------------
        print("\n--- 8. Legitimate Customer Order Tracking & OTP Suppression at Stage 2 ---")
        res = client.post(
            "/api/support/chat",
            json={"order_id": order_a_st2.id, "message": "Where is my order?", "lang": "en"},
            headers=headers_a
        )
        check("Customer A tracks own order at stage 2 -> 200 OK", res.status_code == 200, f"got {res.status_code}")
        body = res.json()
        reply = body.get("reply", "")
        check("Stage 2 reply does NOT disclose OTP", "4821" not in reply, f"reply: {reply[:60]}...")
        check("Stage 2 indicates packing progress", "packing" in reply.lower() or "store" in reply.lower(), f"reply: {reply}")

        # -------------------------------------------------------------
        # TEST 9: LEGITIMATE CUSTOMER B TRACKS OWN ORDER AT STAGE 4
        # (Must succeed, and DOES securely provide OTP to verified owner)
        # -------------------------------------------------------------
        print("\n--- 9. Verified Customer B Tracking Own Order at Stage 4 (OTP Disclosure) ---")
        res = client.post(
            "/api/support/chat",
            json={"order_id": order_b_st4.id, "message": "Where is my order?", "lang": "en"},
            headers=headers_b
        )
        check("Customer B tracks own order at stage 4 -> 200 OK", res.status_code == 200, f"got {res.status_code}")
        body = res.json()
        reply = body.get("reply", "")
        check("Stage 4 reply securely reveals OTP to verified owner", "7793" in reply, f"reply: {reply}")
        check("Stage 4 indicates out for delivery", "out for delivery" in reply.lower(), f"reply: {reply}")

        # -------------------------------------------------------------
        # TEST 10: REFUND TIMELINE TRUTHFULNESS: NEVER 2 HOURS, ALWAYS 5-7 BUSINESS DAYS
        # -------------------------------------------------------------
        print("\n--- 10. Truthful Refund Policy Verification (Priority G) ---")
        res_ref_en = client.post(
            "/api/support/chat",
            json={"message": "What is the refund timeline?", "lang": "en"},
            headers=headers_a
        )
        check("Refund query 200 OK", res_ref_en.status_code == 200, f"got {res_ref_en.status_code}")
        reply_en = res_ref_en.json().get("reply", "")
        check("Refund reply states 5-7 business days", "5-7 business days" in reply_en, f"reply: {reply_en}")
        check("Refund reply does NOT claim 2 hours", "2 hour" not in reply_en.lower(), f"reply: {reply_en}")

        res_ref_hi = client.post(
            "/api/support/chat",
            json={"message": "रिफंड कब आएगा?", "lang": "hi"},
            headers=headers_a
        )
        check("Hindi refund query 200 OK", res_ref_hi.status_code == 200, f"got {res_ref_hi.status_code}")
        reply_hi = res_ref_hi.json().get("reply", "")
        check("Hindi refund reply states 5-7 कार्य दिवस", "5-7 कार्य दिवस" in reply_hi, f"reply: {reply_hi}")
        check("Hindi refund reply does NOT claim 2 घंटे", "2 घंटे" not in reply_hi, f"reply: {reply_hi}")

        # -------------------------------------------------------------
        # TEST 11: CANCELLED ORDER REPLY TRUTHFULNESS
        # -------------------------------------------------------------
        print("\n--- 11. Cancelled Order Refund Honesty ---")
        order_a_st2.status = "cancelled"
        db.commit()
        res_canc = client.post(
            "/api/support/chat",
            json={"order_id": order_a_st2.id, "message": "Order status?", "lang": "en"},
            headers=headers_a
        )
        check("Cancelled order query 200 OK", res_canc.status_code == 200, f"got {res_canc.status_code}")
        canc_reply = res_canc.json().get("reply", "")
        check("Cancelled reply specifies banking cycles (5-7 business days)", "5-7 business days" in canc_reply, f"reply: {canc_reply}")
        check("Cancelled reply does NOT claim 2 hours", "2 hour" not in canc_reply.lower(), f"reply: {canc_reply}")

        # -------------------------------------------------------------
        # TEST 12: SUPPORT TICKET ACCOUNT ISOLATION
        # -------------------------------------------------------------
        print("\n--- 12. Support Ticket Authentication & Isolation ---")
        # Anonymous ticket creation -> 401
        res = client.post("/api/support/ticket", json={"message": "Package arrived damaged"})
        check("Anonymous ticket creation rejected with 401", res.status_code == 401, f"got {res.status_code}")

        # Customer A creating ticket -> 200 OK
        res = client.post(
            "/api/support/ticket",
            json={"message": "Package arrived damaged", "category": "damage"},
            headers=headers_a
        )
        check("Customer A ticket creation 200 OK", res.status_code == 200, f"got {res.status_code}")
        tkt_id = res.json().get("ticket_id")
        created_tickets.append(tkt_id)
        check("Ticket ID generated", bool(tkt_id and tkt_id.startswith("TKT-")), f"ID: {tkt_id}")

        # Customer A attempting to create ticket for Customer B's phone -> 403
        res = client.post(
            "/api/support/ticket",
            json={"message": "Spoofed complaint", "user_phone": cust_b_phone},
            headers=headers_a
        )
        check("Ticket creation phone forgery rejected with 403", res.status_code == 403, f"got {res.status_code}")

        # Customer listing tickets: Customer B cannot see Customer A's ticket
        res = client.get("/api/support/tickets", headers=headers_b)
        check("Customer B listing tickets 200 OK", res.status_code == 200, f"got {res.status_code}")
        b_tickets = res.json()
        check("Customer B cannot see Customer A's ticket", not any(t["ticket_id"] == tkt_id for t in b_tickets), f"ticket count: {len(b_tickets)}")

        # Customer A listing tickets: Customer A sees their own ticket
        res = client.get("/api/support/tickets", headers=headers_a)
        check("Customer A listing tickets 200 OK", res.status_code == 200, f"got {res.status_code}")
        a_tickets = res.json()
        check("Customer A sees their own ticket", any(t["ticket_id"] == tkt_id for t in a_tickets), f"found in {len(a_tickets)} tickets")

        print("\n" + "=" * 70)
        print(f"SECURITY AUDIT COMPLETE: {passed}/{total} ADVERSARIAL TESTS PASSED ({(passed/total)*100:.1f}%)")
        print("=" * 70)

    finally:
        # Clean up all created fixtures to preserve database baseline
        try:
            db.rollback()
        except Exception:
            pass
        for ord_obj in created_orders:
            try:
                db.delete(ord_obj)
            except Exception:
                pass
        for tid in created_tickets:
            try:
                db.query(SupportTicket).filter(SupportTicket.ticket_id == tid).delete()
            except Exception:
                pass
        try:
            db.commit()
        except Exception:
            pass
        db.close()

if __name__ == "__main__":
    run_adversarial_security_suite()

import sys
import io
from fastapi.testclient import TestClient
from backend.main import app
from backend.security import create_jwt_token
from backend.database import SessionLocal
from backend.models import SupportTicket

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

client = TestClient(app)

def test_backend_endpoints():
    print("======================================================================")
    print("BACKEND AI & SUPPORT ENDPOINTS VERIFICATION")
    print("======================================================================")
    
    passed = 0
    total = 0
    def check(name, cond, details=""):
        nonlocal passed, total
        total += 1
        if cond:
            passed += 1
            print(f"  ✓ PASS: {name} - {details}")
        else:
            print(f"  ✗ FAIL: {name} - {details}")

    # Generate customer Bearer token
    customer_phone = "9876543210"
    token = create_jwt_token({"role": "customer", "phone": customer_phone, "sub": customer_phone})
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Test Single Smart AI Backend: Commerce Assistant Endpoint
    print("\n--- 1. POST /api/ai/commerce-assistant ---")
    payload = {"query": "I want 1kg Aata and 1 packet Milk", "lang": "en"}
    res = client.post("/api/ai/commerce-assistant", json=payload)
    check("Endpoint 200 OK", res.status_code == 200, f"Status: {res.status_code}")
    data = res.json()
    check("Parsed Multiple Items", len(data.get("parsed_items", [])) >= 2, f"Items: {data.get('parsed_items')}")
    check("Returned Matched Products", len(data.get("products", [])) >= 2, f"Found {len(data.get('products', []))} products")
    prod_names = [p["name_en"] for p in data.get("products", [])]
    check("Aashirvaad Atta Found", any("Atta" in n for n in prod_names), f"Products: {prod_names}")
    check("Milk / Dairy Found", any("Milk" in n for n in prod_names), f"Products: {prod_names}")

    # 2. Test Support AI Chat: Post-order queries only
    print("\n--- 2. POST /api/support/chat ---")
    order_payload = {"user_phone": customer_phone, "message": "Where is my order?", "lang": "en"}
    res_chat = client.post("/api/support/chat", json=order_payload, headers=headers)
    check("Chat Endpoint 200 OK", res_chat.status_code == 200, f"Status: {res_chat.status_code}")
    chat_data = res_chat.json()
    check("Provides Order Tracking Info", "order" in chat_data.get("reply", "").lower() or "reach" in chat_data.get("reply", "").lower() or "delivery" in chat_data.get("reply", "").lower() or "found" in chat_data.get("reply", "").lower(), 
          f"Reply: {chat_data.get('reply')[:70]}...")
    check("Action is order tracking or help", chat_data.get("action") in ["order_tracking", "order_in_progress", "order_cancelled", "no_order_found", "general_help"], 
          f"Action: {chat_data.get('action')}")

    # 3. Test Traditional Support Ticket Creation: POST /api/support/ticket
    print("\n--- 3. POST /api/support/ticket ---")
    tkt_payload = {
        "user_phone": customer_phone,
        "order_id": "ORD-9482",
        "category": "damaged_item",
        "message": "[Damaged Goods] Atta package was damaged during delivery",
        "subject": "Damaged Goods"
    }
    res_tkt = client.post("/api/support/ticket", json=tkt_payload, headers=headers)
    check("Ticket Creation 200 OK", res_tkt.status_code == 200, f"Status: {res_tkt.status_code}")
    tkt_data = res_tkt.json()
    check("Generated Ticket ID", tkt_data.get("ticket_id", "").startswith("TKT-"), f"ID: {tkt_data.get('ticket_id')}")
    check("Status is open", tkt_data.get("status") == "open", f"Status: {tkt_data.get('status')}")

    # 4. Test Support Tickets List: GET /api/support/tickets
    print("\n--- 4. GET /api/support/tickets ---")
    res_list = client.get(f"/api/support/tickets?user_phone={customer_phone}", headers=headers)
    check("Ticket Listing 200 OK", res_list.status_code == 200, f"Status: {res_list.status_code}")
    list_data = res_list.json()
    check("Contains Logged Ticket", len(list_data) >= 1, f"Found {len(list_data)} tickets")
    check("Ticket Details Persisted in DB", any(t["ticket_id"] == tkt_data["ticket_id"] for t in list_data), 
          f"Found matching ticket ID {tkt_data['ticket_id']}")

    # Clean up ticket to preserve DB cleanliness
    db = SessionLocal()
    try:
        db.query(SupportTicket).filter(SupportTicket.ticket_id == tkt_data["ticket_id"]).delete()
        db.commit()
    finally:
        db.close()

    print("\n======================================================================")
    print(f"RESULTS: {passed}/{total} BACKEND AUDITS PASSED ({(passed/total)*100:.1f}%)")
    print("======================================================================")

if __name__ == "__main__":
    test_backend_endpoints()

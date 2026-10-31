import os
import sys
from urllib.parse import quote
import pytest
from fastapi.testclient import TestClient

sys.stdout.reconfigure(encoding="utf-8")
os.environ["ENVIRONMENT"] = "development"

from backend.main import app
from backend.database import db_session
from backend.models import Order, Store, User, SupportTicket, AuditLog, OTPRecord
from backend.security import issue_user_token, issue_vendor_token, issue_runner_token, issue_admin_token

client = TestClient(app)


def test_01_customer_otp_and_landmark_profile():
    """Customer receives OTP, verifies login, and saves rural village landmark."""
    test_phone = "9876543220"
    
    # 1. Send OTP
    r_otp = client.post("/api/auth/send-otp", json={"phone": test_phone})
    assert r_otp.status_code == 200
    assert r_otp.json()["success"] is True

    # 2. Verify OTP
    with db_session() as db:
        otp_row = db.query(OTPRecord).filter(OTPRecord.phone == test_phone).order_by(OTPRecord.id.desc()).first()
        valid_otp = otp_row.otp_code if otp_row else "123456"
    r_verify = client.post("/api/auth/verify-otp", json={"phone": test_phone, "otp": valid_otp})
    assert r_verify.status_code == 200
    auth_data = r_verify.json()
    token = auth_data["token"]
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Save rural landmark
    r_lm = client.post(
        "/api/user/landmark",
        headers=headers,
        json={
            "phone": test_phone,
            "name": "Rameshwar Prasad",
            "village": "Minapur",
            "block": "Minapur",
            "district": "Muzaffarpur",
            "landmark": "Near Gram Panchayat Bhavan, Purani Masjid Chowk",
            "lat": 26.1775,
            "lng": 85.3410
        }
    )
    assert r_lm.status_code == 200
    lm_data = r_lm.json()
    assert lm_data["success"] is True
    assert lm_data["user"]["name"] == "Rameshwar Prasad"


def test_02_location_serviceability_and_pilot_geofence():
    """Validates pilot geofencing: Minapur pilot villages are serviceable, far locations rejected."""
    # 1. Pilot village in Minapur block -> Serviceable
    r_pilot = client.get("/api/location/serviceability?village=Minapur&district=Muzaffarpur&block=Minapur")
    assert r_pilot.status_code == 200
    assert r_pilot.json()["serviceable"] is True
    assert r_pilot.json()["max_radius_km"] == 8.0

    # 2. Coordinates within Minapur HQ (< 8 km) -> Serviceable
    r_coords_in = client.get("/api/location/serviceability?lat=26.1780&lng=85.3420")
    assert r_coords_in.status_code == 200
    assert r_coords_in.json()["serviceable"] is True

    # 3. Distant coordinates (Patna or Delhi > 50 km away) -> Unserviceable
    r_coords_out = client.get("/api/location/serviceability?lat=28.7041&lng=77.1025")
    assert r_coords_out.status_code == 200
    assert r_coords_out.json()["serviceable"] is False
    assert "exceeds pilot limit" in r_coords_out.json().get("reason", "")


def test_03_cart_pricing_rules():
    """Delivery fee tiers: Platform handling fee \u20b93.00, dynamic distance tiers, and \u20b9299 promotion."""
    from backend.pricing import calculate_order_pricing
    
    # 1. Standard tier (subtotal \u20b9100, 2.0 km) -> Base fee \u20b915, platform fee \u20b93
    pricing_std = calculate_order_pricing(subtotal_in_rupees=100.0, distance_km=2.0)
    assert pricing_std.platform_fee == 3.0
    assert pricing_std.base_delivery_fee == 15.0
    assert pricing_std.delivery_discount == 0.0
    assert pricing_std.delivery_fee == 15.0
    assert pricing_std.total_amount == 118.0

    # 2. Promotional tier (subtotal \u20b9300 >= \u20b9299, 2.0 km) -> \u20b910 platform discount applied
    pricing_promo = calculate_order_pricing(subtotal_in_rupees=300.0, distance_km=2.0)
    assert pricing_promo.platform_fee == 3.0
    assert pricing_promo.base_delivery_fee == 15.0
    assert pricing_promo.delivery_discount == 10.0
    assert pricing_promo.delivery_fee == 5.0
    assert pricing_promo.total_amount == 308.0

    # 3. Geofence violation (> 8.0 km) -> raises ValueError
    with pytest.raises(ValueError):
        calculate_order_pricing(subtotal_in_rupees=150.0, distance_km=9.5, bypass_geofence=False)


def test_04_precise_delivery_location_sharing_and_isolation():
    """Customer can update their active order delivery GPS, but cross-customer access is forbidden."""
    cust_phone = "9876543230"
    cust_token = issue_user_token(101, cust_phone, "Customer One")
    headers_cust = {"Authorization": f"Bearer {cust_token}"}

    attacker_phone = "9876543231"
    attacker_token = issue_user_token(102, attacker_phone, "Attacker")
    headers_attacker = {"Authorization": f"Bearer {attacker_token}"}

    # Find an active order owned by someone or use existing order
    with db_session() as db:
        order = db.query(Order).filter(Order.timeline_stage < 5).first()
        assert order is not None
        target_order_id = order.id
        owner_phone = order.user_phone

    owner_token = issue_user_token(order.user_id or 1, owner_phone or "9876543210")
    headers_owner = {"Authorization": f"Bearer {owner_token}"}

    encoded_id = quote(target_order_id)

    # 1. Owner updates exact delivery GPS -> 200
    r_update = client.put(
        f"/api/orders/{encoded_id}/delivery-location",
        headers=headers_owner,
        json={
            "customer_lat": 26.1785,
            "customer_lng": 85.3425,
            "landmark": "Near Minapur Middle School Gate"
        }
    )
    assert r_update.status_code == 200
    assert r_update.json()["success"] is True
    assert r_update.json()["customer_lat"] == 26.1785

    # 2. Owner reads precise delivery GPS -> 200
    r_read_owner = client.get(f"/api/orders/{encoded_id}/delivery-location", headers=headers_owner)
    assert r_read_owner.status_code == 200
    assert r_read_owner.json()["customer_lat"] == 26.1785

    # 3. Attacker (unauthorized customer) reads location -> 403 Forbidden
    r_read_attacker = client.get(f"/api/orders/{encoded_id}/delivery-location", headers=headers_attacker)
    assert r_read_attacker.status_code == 403, f"Expected 403 for attacker, got {r_read_attacker.status_code}"

    # 4. Attacker attempts to modify location -> 403 Forbidden
    r_update_attacker = client.put(
        f"/api/orders/{encoded_id}/delivery-location",
        headers=headers_attacker,
        json={"customer_lat": 26.1800, "customer_lng": 85.3500}
    )
    assert r_update_attacker.status_code == 403


def test_05_customer_support_grievance_submission():
    """Customer submits grievance ticket and tracks real status."""
    cust_phone = "9876543240"
    cust_token = issue_user_token(105, cust_phone, "Grievance User")
    headers = {"Authorization": f"Bearer {cust_token}"}

    # Submit grievance
    r_ticket = client.post(
        "/api/support/ticket",
        headers=headers,
        json={
            "user_phone": cust_phone,
            "category": "delivery_delay",
            "message": "Runner delayed beyond estimated delivery window for Rampur order."
        }
    )
    assert r_ticket.status_code == 200
    t_data = r_ticket.json()
    assert t_data["success"] is True
    assert "ticket_id" in t_data
    ticket_id = t_data["ticket_id"]

    # Verify ticket appears in Super Admin support desk
    admin_token = issue_admin_token()
    r_admin_list = client.get("/api/admin/support/tickets", headers={"Authorization": f"Bearer {admin_token}"})
    assert r_admin_list.status_code == 200
    all_tickets = r_admin_list.json()
    assert any(t["ticket_id"] == ticket_id for t in all_tickets)

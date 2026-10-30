import os
import sys
from urllib.parse import quote
import pytest
from fastapi.testclient import TestClient

sys.stdout.reconfigure(encoding="utf-8")
os.environ["ENVIRONMENT"] = "development"

from backend.main import app
from backend.database import db_session
from backend.models import Order, Runner, Store, AuditLog
from backend.security import issue_runner_token, issue_user_token, issue_vendor_token, issue_admin_token

client = TestClient(app)


def test_01_runner_auth_and_shift_toggle():
    """Runner authenticates with JWT and toggles shift status between online and offline."""
    runner_token = issue_runner_token("gm_1", "9876543212", "Kamal Singh")
    headers = {"Authorization": f"Bearer {runner_token}"}

    # 1. Toggle Online
    r_on = client.post("/api/runner/shift", headers=headers, json={"runner_id": "gm_1", "is_online": True})
    assert r_on.status_code == 200
    assert r_on.json()["is_online"] is True

    # 2. Verify in DB
    with db_session() as db:
        runner = db.query(Runner).filter(Runner.id == "gm_1").first()
        assert runner is not None
        assert runner.is_online is True

    # 3. Toggle Offline
    r_off = client.post("/api/runner/shift", headers=headers, json={"runner_id": "gm_1", "is_online": False})
    assert r_off.status_code == 200
    assert r_off.json()["is_online"] is False


def test_02_runner_mission_queue_and_pickup():
    """Runner inspects active delivery missions and confirms package pickup from vendor store."""
    runner_token = issue_runner_token("gm_1", "9876543212", "Kamal Singh")
    headers = {"Authorization": f"Bearer {runner_token}"}

    # 1. Missions queue
    r_missions = client.get("/api/runner/missions", headers=headers)
    assert r_missions.status_code == 200
    missions = r_missions.json()
    assert isinstance(missions, list)

    # 2. Stage 3 -> Stage 4 Pickup
    # Setup test order at Stage 3
    with db_session() as db:
        test_order = db.query(Order).filter(Order.timeline_stage < 5).first()
        assert test_order is not None
        order_id = test_order.id
        test_order.timeline_stage = 3
        test_order.status = "Packed & Ready"
        test_order.runner_id = "gm_1"
        db.commit()

    encoded_id = quote(order_id)
    r_pickup = client.post(f"/api/runner/orders/{encoded_id}/pickup", headers=headers)
    assert r_pickup.status_code == 200
    p_data = r_pickup.json()
    assert p_data["status"] == "Out for Delivery"

    # Verify audit log
    with db_session() as db:
        audit = db.query(AuditLog).filter(
            AuditLog.action == "RUNNER_ORDER_PICKUP",
            AuditLog.target_id == order_id
        ).first()
        assert audit is not None


def test_03_doorstep_otp_handover_verification():
    """Runner verifies 4-digit doorstep delivery OTP to complete mission. Rejection on invalid OTP."""
    runner_token = issue_runner_token("gm_1", "9876543212", "Kamal Singh")
    headers = {"Authorization": f"Bearer {runner_token}"}

    with db_session() as db:
        test_order = db.query(Order).filter(Order.timeline_stage < 5).first()
        assert test_order is not None
        order_id = test_order.id
        delivery_otp = test_order.delivery_otp or "4821"
        test_order.timeline_stage = 4
        test_order.status = "Out for Delivery"
        test_order.delivery_otp = delivery_otp
        test_order.runner_id = "gm_1"
        db.commit()

    encoded_id = quote(order_id)

    # 1. Invalid OTP -> 400
    r_bad_otp = client.post(
        f"/api/runner/orders/{encoded_id}/verify-otp",
        headers=headers,
        json={"otp": "0000"}
    )
    assert r_bad_otp.status_code == 400
    assert "Invalid OTP" in r_bad_otp.json().get("detail", "") or "अमान्य" in r_bad_otp.json().get("detail", "")

    # 2. Valid OTP -> 200 Handover Complete (Stage 5)
    r_good_otp = client.post(
        f"/api/runner/orders/{encoded_id}/verify-otp",
        headers=headers,
        json={"otp": delivery_otp}
    )
    assert r_good_otp.status_code == 200
    assert r_good_otp.json()["status"] == "Delivered"
    assert r_good_otp.json()["timeline_stage"] == 5

    # 3. OTP Replay rejection -> 400 (Already delivered)
    r_replay = client.post(
        f"/api/runner/orders/{encoded_id}/verify-otp",
        headers=headers,
        json={"otp": delivery_otp}
    )
    assert r_replay.status_code == 400
    assert "already been delivered" in r_replay.json().get("detail", "")


def test_04_runner_ledger_and_payout_settings():
    """Runner can view trip earnings ledger and manage payout bank details."""
    runner_token = issue_runner_token("gm_1", "9876543212", "Kamal Singh")
    headers = {"Authorization": f"Bearer {runner_token}"}

    # 1. Ledger view
    r_ledger = client.get("/api/runner/ledger", headers=headers)
    assert r_ledger.status_code == 200
    ledger = r_ledger.json()
    assert "runner_id" in ledger
    assert "completed_today" in ledger
    assert "total_earnings" in ledger

    # 2. Payout bank details update
    r_bank = client.put(
        "/api/runner/bank?runner_id=gm_1",
        headers=headers,
        json={
            "payout_mode": "bank",
            "account_holder": "Kamal Singh",
            "account_number": "601928374655",
            "ifsc": "PUNB0123400"
        }
    )
    assert r_bank.status_code == 200
    assert r_bank.json()["success"] is True

    # 3. Masked account verification
    r_settings = client.get("/api/runner/gm_1/payout-settings", headers=headers)
    assert r_settings.status_code == 200
    settings = r_settings.json()
    acc_masked = settings.get("account_number_masked", "")
    assert "••••" in acc_masked or "XXXX" in acc_masked or "..." in acc_masked


def test_05_runner_vehicle_documentation_rules():
    """Bicycle partners do not require driving licence; motorized vehicles require registration."""
    runner_token = issue_runner_token("gm_1", "9876543212", "Kamal Singh")
    headers = {"Authorization": f"Bearer {runner_token}"}

    # 1. Update as Bicycle
    r_bike = client.post(
        "/api/runner/kyc/submit?runner_id=gm_1",
        headers=headers,
        json={
            "document_type": "Aadhaar",
            "document_number": "XXXX-XXXX-4821",
            "vehicle_type": "Bicycle"
        }
    )
    assert r_bike.status_code == 200
    with db_session() as db:
        r_obj = db.query(Runner).filter(Runner.id == "gm_1").first()
        assert r_obj.vehicle_type == "Bicycle"
        assert r_obj.driving_licence_number is None

    # 2. Update as Motorcycle
    r_moto = client.post(
        "/api/runner/kyc/submit?runner_id=gm_1",
        headers=headers,
        json={
            "document_type": "Aadhaar",
            "document_number": "XXXX-XXXX-4821",
            "vehicle_type": "Motorcycle",
            "vehicle_reg_number": "BR-06-AB-1234",
            "driving_licence_number": "DL-BR06-2022001"
        }
    )
    assert r_moto.status_code == 200
    with db_session() as db:
        r_obj2 = db.query(Runner).filter(Runner.id == "gm_1").first()
        assert r_obj2.vehicle_type == "Motorcycle"
        assert r_obj2.vehicle_reg_number == "BR-06-AB-1234"

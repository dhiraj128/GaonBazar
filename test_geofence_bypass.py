import os
import sys
import unittest
from fastapi.testclient import TestClient
from backend.main import app, is_geofence_bypass_enabled, calculate_haversine_km
from backend.database import get_db, Base, engine
from backend.models import Product, Store

client = TestClient(app)

HEADERS = {"X-Test-Bypass": "1"}

class TestGeofenceBypassSuite(unittest.TestCase):
    def setUp(self):
        # Ensure test database tables exist
        Base.metadata.create_all(bind=engine)

    def test_haversine_math_preserved(self):
        """Verify the Haversine distance formula is untouched and accurate."""
        # Distance between Sharma Brothers (29.1350, 77.0100) and Kisan Seva (29.1450, 77.0200)
        dist = calculate_haversine_km(29.1350, 77.0100, 29.1450, 77.0200)
        self.assertAlmostEqual(dist, 1.48, delta=0.1)
        # Identical coordinates must be 0.0 km
        self.assertEqual(calculate_haversine_km(29.1350, 77.0100, 29.1350, 77.0100), 0.0)

    def test_geofence_enforced_when_false(self):
        """When BYPASS_GEOFENCE=False, distance > 8.0 km must return HTTP 400."""
        os.environ["BYPASS_GEOFENCE"] = "False"
        self.assertFalse(is_geofence_bypass_enabled())

        payload = {
            "items": [{"id": "item_1", "qty": 1, "name": "Aashirvaad Shudh Chakki Atta", "price": 210.0}],
            "user_name": "Ramesh Kumar",
            "user_phone": "9876543210",
            "village": "Rampur",
            "landmark": "Near Mandir",
            "store_id": "sharma_brothers",
            "distance_km": 9.5,
            "payment_mode": "COD"
        }
        resp = client.post("/api/orders/checkout", json=payload, headers=HEADERS)
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Outside delivery zone", resp.json()["detail"])
        self.assertIn("exceeds 8.0 km", resp.json()["detail"])

    def test_geofence_enforced_when_missing(self):
        """When BYPASS_GEOFENCE is missing, default must be False and strictly enforce 8.0 km."""
        if "BYPASS_GEOFENCE" in os.environ:
            del os.environ["BYPASS_GEOFENCE"]
        self.assertFalse(is_geofence_bypass_enabled())

        payload = {
            "items": [{"id": "item_1", "qty": 1, "name": "Aashirvaad Shudh Chakki Atta", "price": 210.0}],
            "user_name": "Ramesh Kumar",
            "user_phone": "9876543210",
            "village": "Rampur",
            "landmark": "Near Mandir",
            "store_id": "sharma_brothers",
            "distance_km": 11.2,
            "payment_mode": "COD"
        }
        resp = client.post("/api/orders/checkout", json=payload, headers=HEADERS)
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Outside delivery zone", resp.json()["detail"])

    def test_geofence_bypassed_when_true(self):
        """When BYPASS_GEOFENCE=True, distance > 8.0 km is permitted for testing."""
        os.environ["BYPASS_GEOFENCE"] = "True"
        self.assertTrue(is_geofence_bypass_enabled())

        payload = {
            "items": [{"id": "item_1", "qty": 1, "name": "Aashirvaad Shudh Chakki Atta", "price": 210.0}],
            "user_name": "Ramesh Test",
            "user_phone": "9876543211",
            "village": "Rampur",
            "landmark": "Near Mandir",
            "store_id": "sharma_brothers",
            "distance_km": 12.5,
            "payment_mode": "COD"
        }
        resp = client.post("/api/orders/checkout", json=payload, headers=HEADERS)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertTrue(data["order_id"].startswith("#RUR-"))
        # Verify base fee applied for long distance is 40.0
        self.assertEqual(data["delivery_fee"], 40.0)

    def test_razorpay_order_geofence_bypass(self):
        """Verify Razorpay payment order endpoint also respects BYPASS_GEOFENCE."""
        # 1. Enforced when False
        os.environ["BYPASS_GEOFENCE"] = "False"
        payload = {
            "amount": 253.0,
            "user_phone": "9876543210",
            "user_name": "Ramesh Kumar",
            "village": "Rampur",
            "landmark": "Near Mandir",
            "distance_km": 9.2,
            "items": [{"id": "item_1", "qty": 1, "price": 210.0}]
        }
        resp = client.post("/api/payments/create-order", json=payload, headers=HEADERS)
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Outside delivery zone", resp.json()["detail"])

        # 2. Bypassed when True
        os.environ["BYPASS_GEOFENCE"] = "True"
        resp = client.post("/api/payments/create-order", json=payload, headers=HEADERS)
        if resp.status_code == 400:
            self.assertNotIn("Outside delivery zone", resp.json().get("detail", ""))

    def tearDown(self):
        # Restore safe default
        os.environ["BYPASS_GEOFENCE"] = "False"

if __name__ == "__main__":
    unittest.main()

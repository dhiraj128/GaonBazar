"""
Verification test for Vendor & Runner frontend HTML response routes and Static Asset mounts.
Tests FastAPI routes:
- GET /vendor and /vendor/
- GET /runner and /runner/
- GET /static and /assets mounts
- Static root assets (.png, .js, .json)
"""

import sys
import os
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from backend.main import app, ROOT_DIR

class TestFrontendRoutesAndStaticAssets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_vendor_route(self):
        res = self.client.get("/vendor")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/html", res.headers.get("content-type", ""))
        self.assertIn("दुकानदार पोर्टल", res.text)
        print("  ✓ GET /vendor returned 200 OK with vendor_dashboard.html")

    def test_vendor_trailing_slash_route(self):
        res = self.client.get("/vendor/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/html", res.headers.get("content-type", ""))
        self.assertIn("दुकानदार पोर्टल", res.text)
        print("  ✓ GET /vendor/ returned 200 OK with vendor_dashboard.html")

    def test_runner_route(self):
        res = self.client.get("/runner")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/html", res.headers.get("content-type", ""))
        self.assertIn("गाँव मित्र", res.text)
        print("  ✓ GET /runner returned 200 OK with runner_dashboard.html")

    def test_runner_trailing_slash_route(self):
        res = self.client.get("/runner/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/html", res.headers.get("content-type", ""))
        self.assertIn("गाँव मित्र", res.text)
        print("  ✓ GET /runner/ returned 200 OK with runner_dashboard.html")

    def test_static_mounts(self):
        test_file = ROOT_DIR / "static" / "test_asset.css"
        test_file.write_text("body { background: #000; }", encoding="utf-8")
        try:
            res = self.client.get("/static/test_asset.css")
            self.assertEqual(res.status_code, 200)
            self.assertIn("body { background: #000; }", res.text)
            print("  ✓ GET /static/test_asset.css returned 200 OK via StaticFiles mount")
        finally:
            if test_file.exists():
                test_file.unlink()

    def test_assets_mount(self):
        test_file = ROOT_DIR / "assets" / "test_img.svg"
        test_file.write_text("<svg></svg>", encoding="utf-8")
        try:
            res = self.client.get("/assets/test_img.svg")
            self.assertEqual(res.status_code, 200)
            print("  ✓ GET /assets/test_img.svg returned 200 OK via StaticFiles mount")
        finally:
            if test_file.exists():
                test_file.unlink()

    def test_root_image_asset(self):
        res = self.client.get("/galaxys22_step1_01_login_initial.png")
        self.assertEqual(res.status_code, 200)
        self.assertIn("image/png", res.headers.get("content-type", ""))
        print("  ✓ Root image asset galaxys22_step1_01_login_initial.png returned 200 image/png")

    def test_manifest_route(self):
        res = self.client.get("/manifest.json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json().get("name"), "GaonBazaar")
        print("  ✓ GET /manifest.json returned 200 OK with manifest JSON")

    def test_sw_route(self):
        res = self.client.get("/sw.js")
        self.assertEqual(res.status_code, 200)
        self.assertIn("javascript", res.headers.get("content-type", ""))
        print("  ✓ GET /sw.js returned 200 OK with application/javascript")

    def test_security_traversal_blocked(self):
        res = self.client.get("/backend/main.py")
        self.assertIn(res.status_code, [403, 404])
        print(f"  ✓ Sensitive python file request blocked with status {res.status_code}")

if __name__ == "__main__":
    unittest.main()

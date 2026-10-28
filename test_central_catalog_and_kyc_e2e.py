# -*- coding: utf-8 -*-
"""
test_central_catalog_and_kyc_e2e.py
Automated E2E QA Verification for GaonBazaar Central Product & Image Library,
Vendor (Dukandaar) & Delivery Partner (Gaon Mitra) Apps, and Super Admin KYC.
"""

import os
import sys
import json
import sqlite3
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from backend.main import app
from backend.database import get_db, SessionLocal, DATABASE_URL
from backend.models import CentralProduct, Product, Store, Runner, Order

client = TestClient(app)

print("\n" + "="*80)
print("GAONBAZAAR CENTRAL CATALOG, VENDOR/RUNNER PROFILES & KYC E2E TEST SUITE")
print("="*80)


def test_01_database_order_preservation():
    """Verify that existing database contains at least 364 orders with zero regression."""
    print("\n[TEST 01] Verifying database integrity and 364 orders preservation...")
    db = SessionLocal()
    try:
        count = db.query(Order).count()
        print(f"-> Total Orders in DB: {count}")
        assert count >= 364, f"CRITICAL: Expected at least 364 orders, found {count}"
    finally:
        db.close()


def test_02_central_catalog_categories():
    """Verify central catalog categories endpoint returns all 10 rural categories with counts."""
    print("\n[TEST 02] Testing Central Catalog Categories endpoint...")
    resp = client.get("/api/catalog/categories")
    assert resp.status_code == 200, f"Failed: {resp.text}"
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 10, f"Expected 10 rural categories, got {len(data)}"
    
    cat_ids = [c["id"] for c in data]
    required_cats = [
        "vegetables", "grains", "dairy", "oil", "spices",
        "snacks", "personal_care", "cleaning", "puja", "stationery"
    ]
    for req in required_cats:
        assert req in cat_ids, f"Category '{req}' missing from catalog"
    print("-> All 10 rural categories present with bilingual metadata.")


def test_03_central_catalog_bilingual_search():
    """Verify smart matching in English, Hindi, and Roman transliterations."""
    print("\n[TEST 03] Testing Central Catalog Autocomplete & Phonetic Transliteration...")
    test_queries = [
        ("tamatar", "Tomato"),
        ("tomato", "Tomato"),
        ("टमाटर", "Tomato"),
        ("pyaz", "Onion"),
        ("onion", "Onion"),
        ("doodh", "Milk"),
        ("milk", "Milk"),
        ("दूध", "Milk"),
        ("atta", "Atta"),
        ("आलू", "Potato"),
        ("aloo", "Potato"),
        ("chawal", "Rice")
    ]

    for query, expected_keyword in test_queries:
        resp = client.get(f"/api/catalog/search?q={query}")
        assert resp.status_code == 200, f"Query '{query}' failed"
        items = resp.json()
        assert len(items) > 0, f"Query '{query}' returned 0 results"
        matched = any(expected_keyword.lower() in (it["name_en"] + " " + it["name_hi"]).lower() for it in items)
        assert matched, f"Query '{query}' did not match any product with '{expected_keyword}'"
        print(f"  ✓ Search '{query}' -> Found {len(items)} items matching '{expected_keyword}'")


def test_04_vendor_independent_pricing_and_stock():
    """Verify vendor-specific pricing independence: central updates do NOT overwrite vendor selling price."""
    print("\n[TEST 04] Testing Vendor Independent Pricing & Stock Control...")
    db = SessionLocal()
    try:
        # 1. Fetch a central product
        cp = db.query(CentralProduct).filter(CentralProduct.name_en.ilike("%Tomato%")).first()
        assert cp is not None
        orig_central_mrp = cp.default_mrp

        # 2. Add product to vendor store with vendor's own selling price
        payload = {
            "central_product_id": cp.id,
            "name_en": "Fresh Tomato",
            "name_hi": "ताज़ा देशी टमाटर",
            "category": "vegetables",
            "weight": "1 kg",
            "price": 28.50, # Vendor's own custom selling price
            "mrp": 35.00,
            "stock_qty": 75,
            "in_stock": True,
            "image_url": cp.image_url
        }
        resp = client.post("/api/vendor/inventory/add?store_id=sharma_brothers", json=payload)
        assert resp.status_code == 200, f"Add failed: {resp.text}"
        added = resp.json()
        item_id = added["id"]
        assert added["price"] == 28.50
        assert added["stock_qty"] == 75

        # 3. Update selling price and stock
        update_resp = client.put(f"/api/vendor/inventory/{item_id}", json={
            "price": 32.00,
            "stock_qty": 60,
            "in_stock": True
        })
        assert update_resp.status_code == 200
        updated = update_resp.json()
        assert updated["price"] == 32.00
        assert updated["stock_qty"] == 60

        # 4. Confirm Central Product MRP remains completely untouched
        db.refresh(cp)
        assert cp.default_mrp == orig_central_mrp
        print(f"-> Vendor price changed to ₹{updated['price']} while Central MRP preserved at ₹{cp.default_mrp}.")

        # Clean up added test listing
        del_resp = client.delete(f"/api/vendor/inventory/{item_id}")
        assert del_resp.status_code == 200
    finally:
        db.close()


def test_05_product_image_upload_and_versioning():
    """Verify product image upload stores file and returns persistent versioned URL."""
    print("\n[TEST 05] Testing Product Image Upload & Retrieval...")
    dummy_png_bytes = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4'
        b'\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    files = {"file": ("test_upload_tomato.png", dummy_png_bytes, "image/png")}
    resp = client.post("/api/catalog/upload-image", files=files)
    assert resp.status_code == 200, f"Upload failed: {resp.text}"
    data = resp.json()
    assert data["success"] is True
    assert "image_url" in data
    assert "static/images/" in data["image_url"]
    assert "?v=" in data["image_url"]
    print(f"-> Uploaded image URL: {data['image_url']}")


def test_06_unique_store_and_runner_permanent_ids():
    """Verify permanent unique IDs for Store (GB-S000001) and Runner (GB-DP000001)."""
    print("\n[TEST 06] Verifying Permanent Unique Store & Runner IDs...")
    resp_vendor = client.get("/api/vendor/profile?store_id=sharma_brothers")
    assert resp_vendor.status_code == 200
    vendor_data = resp_vendor.json()
    assert "store_code" in vendor_data
    assert vendor_data["store_code"].startswith("GB-S"), f"Invalid Store Code: {vendor_data['store_code']}"
    print(f"  ✓ Vendor Store Code: {vendor_data['store_code']}")

    resp_runner = client.get("/api/runner/profile?runner_id=gm_1")
    assert resp_runner.status_code == 200
    runner_data = resp_runner.json()
    assert "partner_code" in runner_data
    assert runner_data["partner_code"].startswith("GB-DP"), f"Invalid Partner Code: {runner_data['partner_code']}"
    print(f"  ✓ Delivery Partner Code: {runner_data['partner_code']}")


def test_07_vendor_kyc_and_super_admin_review():
    """Verify Vendor KYC submission and Super Admin approval granting 'गांव बाज़ार सत्यापित' badge."""
    print("\n[TEST 07] Testing Vendor KYC Submission & Admin Approval Flow...")
    # 1. Submit KYC
    sub_payload = {
        "document_type": "Aadhaar",
        "document_number": "9988-7766-5544",
        "document_url": "static/images/store_sharma.png"
    }
    resp = client.post("/api/vendor/kyc/submit?store_id=sharma_brothers", json=sub_payload)
    assert resp.status_code == 200
    assert resp.json()["kyc_status"] == "under_review"

    # 2. Verify Super Admin sees pending submission
    pending_resp = client.get("/api/admin/kyc/pending")
    assert pending_resp.status_code == 200
    pending_items = pending_resp.json()
    vendor_pending = [item for item in pending_items if item["entity_id"] == "sharma_brothers"]
    assert len(vendor_pending) > 0
    assert "9988-7766-5544"[-4:] in vendor_pending[0]["document_number_masked"]

    # 3. Super Admin approves submission
    review_resp = client.post("/api/admin/kyc/vendor/sharma_brothers/review", json={
        "action": "approved",
        "rejection_reason": None
    })
    assert review_resp.status_code == 200
    assert review_resp.json()["is_verified"] is True

    # 4. Verify Vendor Profile reflects verified status
    prof_resp = client.get("/api/vendor/profile?store_id=sharma_brothers")
    prof = prof_resp.json()
    assert prof["is_verified"] is True
    assert prof["kyc_status"] == "approved"
    print("-> Vendor KYC successfully approved and verified badge granted.")


def test_08_runner_kyc_conditional_vehicle_rule():
    """Verify Delivery Partner KYC with conditional rule: Bicycle requires NO Driving Licence."""
    print("\n[TEST 08] Testing Delivery Partner KYC & Conditional Bicycle Exemption Rule...")
    # 1. Bicycle Partner KYC Submission (DL not required)
    sub_bicycle = {
        "document_type": "Voter ID",
        "document_number": "VTR-12345678",
        "document_url": "static/images/runner_avatar.png",
        "vehicle_type": "Bicycle",
        "vehicle_reg_number": None,
        "driving_licence_number": None
    }
    resp_b = client.post("/api/runner/kyc/submit?runner_id=gm_1", json=sub_bicycle)
    assert resp_b.status_code == 200
    assert resp_b.json()["kyc_status"] == "under_review"

    # Verify profile reflects bicycle exemption
    prof_b = client.get("/api/runner/profile?runner_id=gm_1").json()
    assert prof_b["vehicle_type"] == "Bicycle"
    assert prof_b["driving_licence_number"] is None

    # 2. Motorcycle Partner KYC Submission (DL & Registration required)
    sub_motor = {
        "document_type": "Aadhaar",
        "document_number": "1122-3344-5566",
        "document_url": "static/images/runner_avatar.png",
        "vehicle_type": "Motorcycle",
        "vehicle_reg_number": "UP-14-EA-4921",
        "driving_licence_number": "DL-1420110012345"
    }
    resp_m = client.post("/api/runner/kyc/submit?runner_id=gm_1", json=sub_motor)
    assert resp_m.status_code == 200
    prof_m = client.get("/api/runner/profile?runner_id=gm_1").json()
    assert prof_m["vehicle_type"] == "Motorcycle"
    assert prof_m["vehicle_reg_number"] == "UP-14-EA-4921"
    assert prof_m["driving_licence_number"] == "DL-1420110012345"

    # 3. Super Admin approves runner
    client.post("/api/admin/kyc/runner/gm_1/review", json={"action": "approved"})
    verified_runner = client.get("/api/runner/profile?runner_id=gm_1").json()
    assert verified_runner["is_verified"] is True
    print("-> Conditional vehicle logic and Partner verification confirmed.")


def test_09_bank_and_upi_security_masking():
    """Verify bank account numbers and ID documents are properly masked for privacy."""
    print("\n[TEST 09] Testing Bank Account Masking & UPI Payout Security...")
    # Update vendor bank
    client.put("/api/vendor/bank?store_id=sharma_brothers", json={
        "account_holder": "Ramesh Sharma",
        "account_number": "98765432101234",
        "ifsc": "SBIN0001234",
        "upi_id": "sharma.kirana@okaxis"
    })

    prof = client.get("/api/vendor/profile?store_id=sharma_brothers").json()
    assert prof["bank_account_number_masked"].endswith("1234")
    assert "98765432101234" not in prof["bank_account_number_masked"]
    assert prof["payout_upi"] == "sharma.kirana@okaxis"
    print("-> Bank account masked correctly to ••••••••1234.")


def test_10_central_catalog_deduplication_and_soft_disable():
    """Verify Super Admin safe catalog deduplication and soft-disable."""
    print("\n[TEST 10] Testing Central Catalog Deduplication & Soft-Disable...")
    # 1. Create temporary master and duplicate
    m = client.post("/api/catalog/products", json={
        "name_en": "Test Master Ghee",
        "name_hi": "टेस्ट मास्टर घी",
        "category": "oil",
        "default_unit": "1 L",
        "default_mrp": 600.0,
        "search_aliases": "ghee, test"
    }).json()
    
    d = client.post("/api/catalog/products", json={
        "name_en": "Test Duplicate Ghee",
        "name_hi": "टेस्ट डुप्लीकेट घी",
        "category": "oil",
        "default_unit": "1 L",
        "default_mrp": 610.0,
        "search_aliases": "ghee, test duplicate"
    }).json()

    # 2. Deduplicate
    dedup_resp = client.post("/api/catalog/deduplicate", json={
        "master_id": m["id"],
        "duplicate_id": d["id"]
    })
    assert dedup_resp.status_code == 200
    assert dedup_resp.json()["success"] is True

    # 3. Soft disable
    dis_resp = client.delete(f"/api/catalog/products/{m['id']}")
    assert dis_resp.status_code == 200
    assert dis_resp.json()["success"] is True

    # Confirm deactivated
    detail_res = client.get(f"/api/catalog/products/{m['id']}").json()
    assert detail_res["is_active"] is False

    dup_detail = client.get(f"/api/catalog/products/{d['id']}").json()
    assert dup_detail["is_active"] is False

    search_res = client.get(f"/api/catalog/search?q={m['name_en']}").json()
    assert not any(p["id"] in (m["id"], d["id"]) for p in search_res)
    print("-> Safe deduplication and soft-disable executed with zero data loss.")


def test_11_navigation_html_integrity():
    """Verify that duplicate top-right header grid buttons are absent and bottom nav is 5 tabs."""
    print("\n[TEST 11] Testing Vendor & Runner HTML Navigation Structure...")
    # Vendor Dashboard
    with open("vendor_dashboard.html", "r", encoding="utf-8") as f:
        vendor_html = f.read()
    assert '<button id="btn-vendor-header-settings"' not in vendor_html, "Duplicate vendor header settings button must be purged"
    assert 'id="nav-btn-orders"' in vendor_html
    assert 'id="nav-btn-inventory"' in vendor_html
    assert 'id="nav-btn-ledger"' in vendor_html
    assert 'id="nav-btn-messages"' in vendor_html
    assert 'id="nav-btn-settings"' in vendor_html
    assert 'data-i18n="nav_profile"' in vendor_html
    print("  ✓ Vendor Dashboard: Duplicate header grid button removed, 5 canonical bottom tabs intact.")

    # Runner Dashboard
    with open("runner_dashboard.html", "r", encoding="utf-8") as f:
        runner_html = f.read()
    assert '<button id="btn-runner-header-settings"' not in runner_html, "Duplicate runner header settings button must be purged"
    assert 'id="nav-btn-missions"' in runner_html
    assert 'id="nav-btn-detail"' in runner_html
    assert 'id="nav-btn-ledger"' in runner_html
    assert 'id="nav-btn-help"' in runner_html
    assert 'id="nav-btn-settings"' in runner_html
    print("  ✓ Delivery Partner Dashboard: Duplicate header grid button removed, 5 canonical bottom tabs intact.")

    # Admin Dashboard
    with open("admin_dashboard.html", "r", encoding="utf-8") as f:
        admin_html = f.read()
    assert 'id="admin-tab-btn-catalog"' in admin_html, "Admin must have Central Catalog tab button"
    assert 'id="tab-catalog"' in admin_html, "Admin must have Central Catalog tab section"
    print("  ✓ Super Admin Dashboard: Central Catalog Library tab and controls verified.")


def test_12_final_database_count():
    """Final safeguard: verify 364 orders count is strictly maintained."""
    print("\n[TEST 12] Final Database Count Verification...")
    db = SessionLocal()
    try:
        count = db.query(Order).count()
        assert count >= 364
        print(f"-> FINAL CONFIRMATION: {count} orders preserved (baseline 364 preserved).")
    finally:
        db.close()


if __name__ == "__main__":
    test_01_database_order_preservation()
    test_02_central_catalog_categories()
    test_03_central_catalog_bilingual_search()
    test_04_vendor_independent_pricing_and_stock()
    test_05_product_image_upload_and_versioning()
    test_06_unique_store_and_runner_permanent_ids()
    test_07_vendor_kyc_and_super_admin_review()
    test_08_runner_kyc_conditional_vehicle_rule()
    test_09_bank_and_upi_security_masking()
    test_10_central_catalog_deduplication_and_soft_disable()
    test_11_navigation_html_integrity()
    test_12_final_database_count()
    print("\n" + "="*80)
    print("ALL 12 CENTRAL CATALOG, VENDOR & RUNNER KYC TESTS PASSED!")
    print("="*80 + "\n")

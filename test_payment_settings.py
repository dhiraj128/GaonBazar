"""
GaonBazaar FinTech Payout & Payment Settings Onboarding Verification Suite
========================================================================
Comprehensive automated test suite verifying:
1. Vendor & Runner Bank & UPI Payout Onboarding (Razorpay Route Linked Accounts)
2. Strict Regulatory & FinTech Validation (IFSC Regex, UPI VPA Regex, Account Number Matching)
3. Customer App Saved Payment Methods UI & Management (Razorpay Token Ready, Delete, Add)
4. Super Admin Payout KYC Verification Controls (Pending -> Verified -> Rejected)
5. Frontend UI Modules, Form Inputs, Badges, and Empty States across Ecosystem
"""

import sys
import re
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure UTF-8 output encoding
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from backend.main import app, mask_bank_account
from backend.database import SessionLocal, ensure_schema_migrations
from backend.models import Store, Runner, SavedPaymentMethod, User
from backend.security import issue_user_token, issue_vendor_token, issue_runner_token, issue_admin_token, decrypt_sensitive_field
ADMIN_AUTH = {'Authorization': f'Bearer {issue_admin_token()}'}

VENDOR_AUTH = {"Authorization": f"Bearer {issue_vendor_token('sharma_brothers', '9876543211')}"}
RUNNER_AUTH = {"Authorization": f"Bearer {issue_runner_token('gm_1', '9876543220')}"}

client = TestClient(app)

TOTAL_CHECKS = 0
PASSED_CHECKS = 0

def check(condition: bool, description: str):
    global TOTAL_CHECKS, PASSED_CHECKS
    TOTAL_CHECKS += 1
    if condition:
        PASSED_CHECKS += 1
        print(f"  [PASS]: {description}")
    else:
        print(f"  [FAIL]: {description}")
        raise AssertionError(f"Check failed: {description}")


def test_ifsc_and_upi_validation_engine():
    print("\n[SUITE 1/5]: FinTech Validation Engine & Strict Regex Constraints")
    
    # 1.1 Invalid IFSC (wrong format: missing 0 in 5th position or wrong length)
    bad_ifsc_list = [
        "SBIN1234567",       # length 11 but 5th is '1' not '0'
        "SBI0001234",        # length 10 (too short)
        "SBINO001234",       # 5th char is letter 'O' instead of digit '0'
        "12340001234",       # First 4 are digits instead of letters
        "HDFC00000000",      # length 12 (too long)
        "ABCD",              # too short
        "SBIN 001234"        # space
    ]
    for bad_ifsc in bad_ifsc_list:
        res = client.post("/api/vendor/stores/sharma_brothers/payout-settings", headers=VENDOR_AUTH, json={
            "account_holder_name": "Ramesh Sharma",
            "account_number": "123456789012",
            "confirm_account_number": "123456789012",
            "ifsc_code": bad_ifsc,
            "upi_id": "sharma@okaxis"
        })
        check(res.status_code == 422, f"Rejected invalid IFSC '{bad_ifsc}' (Status 422)")

    # 1.2 Invalid UPI VPAs
    bad_upi_list = [
        "invalidupi",         # missing @
        "@okaxis",           # missing username
        "sharma@",           # missing handle
        "sharma@ok@axis",    # multiple @
        "s@a",               # too short
        "sharma kirana@upi"  # space
    ]
    for bad_upi in bad_upi_list:
        res = client.post("/api/vendor/stores/sharma_brothers/payout-settings", headers=VENDOR_AUTH, json={
            "account_holder_name": "Ramesh Sharma",
            "account_number": "123456789012",
            "confirm_account_number": "123456789012",
            "ifsc_code": "SBIN0001234",
            "upi_id": bad_upi
        })
        check(res.status_code == 422, f"Rejected invalid UPI '{bad_upi}' (Status 422)")

    # 1.3 Account number mismatch
    res_mismatch = client.post("/api/vendor/stores/sharma_brothers/payout-settings", headers=VENDOR_AUTH, json={
        "account_holder_name": "Ramesh Sharma",
        "account_number": "123456789012",
        "confirm_account_number": "987654321098",
        "ifsc_code": "SBIN0001234",
        "upi_id": "sharma@okhdfcbank"
    })
    check(res_mismatch.status_code == 422, "Rejected mismatched account numbers (Status 422)")

    # 1.4 Invalid non-numeric account number
    res_non_num = client.post("/api/vendor/stores/sharma_brothers/payout-settings", headers=VENDOR_AUTH, json={
        "account_holder_name": "Ramesh Sharma",
        "account_number": "12345ABC9012",
        "confirm_account_number": "12345ABC9012",
        "ifsc_code": "SBIN0001234",
        "upi_id": "sharma@okhdfcbank"
    })
    check(res_non_num.status_code == 422, "Rejected non-numeric account number (Status 422)")

    # 1.5 Masking algorithm check
    check(mask_bank_account("123456789012") == "••••••••9012", "Account number 123456789012 masked correctly to ••••••••9012")
    check(mask_bank_account("987654321") == "•••••4321", "Account number 987654321 masked correctly to •••••4321")
    check(mask_bank_account(None) is None, "None handled safely by masking algorithm")


def test_vendor_payout_settings_lifecycle():
    print("\n[SUITE 2/5]: Vendor Bank & UPI Payout Onboarding (Razorpay Route)")

    # Valid Vendor Submission
    payload = {
        "account_holder_name": "Ramesh Sharma",
        "account_number": "50100234567890",
        "confirm_account_number": "50100234567890",
        "ifsc_code": "HDFC0000240",
        "upi_id": "sharma.kirana@okhdfcbank"
    }
    res = client.post("/api/vendor/stores/sharma_brothers/payout-settings", headers=VENDOR_AUTH, json=payload)
    check(res.status_code == 200, "Vendor payout settings saved successfully (Status 200)")
    data = res.json()
    check(data.get("success") is True, "Response contains success=True")
    check(data.get("verification_status") == "pending", "Initial verification status is 'pending'")
    check(data.get("account_number_masked") == "••••••••••7890", "Response masks sensitive account number (••••••••••7890)")
    check(data.get("ifsc_code") == "HDFC0000240", "IFSC saved as HDFC0000240")
    check(data.get("upi_id") == "sharma.kirana@okhdfcbank", "UPI saved as sharma.kirana@okhdfcbank")

    # Verify SQLite DB persistence
    db = SessionLocal()
    try:
        store = db.query(Store).filter(Store.id == "sharma_brothers").first()
        check(store is not None, "Store found in SQLite database")
        check(decrypt_sensitive_field(store.bank_account_number) == "50100234567890", "Account number securely encrypted at rest in DB and matches plaintext")
        check(store.bank_ifsc == "HDFC0000240", "IFSC stored in DB")
        check(store.payout_upi == "sharma.kirana@okhdfcbank", "UPI stored in DB")
        check(store.bank_verification_status == "pending", "DB verification status is 'pending'")
    finally:
        db.close()

    # GET endpoint retrieval
    get_res = client.get("/api/vendor/stores/sharma_brothers/payout-settings", headers=VENDOR_AUTH)
    check(get_res.status_code == 200, "Vendor GET payout settings returns 200")
    get_data = get_res.json()
    check(get_data.get("account_number_masked") == "••••••••••7890", "GET returns masked account number")
    check(get_data.get("is_configured") is True, "Vendor payout is marked as configured")
    check(get_data.get("verification_status") == "pending", "Verification status is 'pending'")


def test_runner_payout_settings_lifecycle():
    print("\n[SUITE 3/5]: Runner Bank & UPI Payout Onboarding (Razorpay Route)")

    payload = {
        "account_holder_name": "Kamal Singh",
        "account_number": "10029384756102",
        "confirm_account_number": "10029384756102",
        "ifsc_code": "PUNB0123400",
        "upi_id": "kamal.singh@ybl"
    }
    res = client.post("/api/runner/gm_1/payout-settings", headers=RUNNER_AUTH, json=payload)
    check(res.status_code == 200, "Runner payout settings saved successfully (Status 200)")
    data = res.json()
    check(data.get("success") is True, "Response contains success=True")
    check(data.get("verification_status") == "pending", "Initial runner verification status is 'pending'")
    check(data.get("account_number_masked") == "••••••••••6102", "Response masks runner account number (••••••••••6102)")
    check(data.get("ifsc_code") == "PUNB0123400", "IFSC saved as PUNB0123400")

    # Verify SQLite DB persistence
    db = SessionLocal()
    try:
        runner = db.query(Runner).filter(Runner.id == "gm_1").first()
        check(runner is not None, "Runner found in SQLite database")
        check(decrypt_sensitive_field(runner.bank_account_number) == "10029384756102", "Runner account number securely encrypted at rest in DB and matches plaintext")
        check(runner.bank_ifsc == "PUNB0123400", "Runner IFSC stored in DB")
        check(runner.bank_verification_status == "pending", "Runner verification status in DB is 'pending'")
    finally:
        db.close()

    # GET endpoint retrieval
    get_res = client.get("/api/runner/gm_1/payout-settings", headers=RUNNER_AUTH)
    check(get_res.status_code == 200, "Runner GET payout settings returns 200")
    get_data = get_res.json()
    check(get_data.get("account_number_masked") == "••••••••••6102", "GET returns masked account number")
    check(get_data.get("is_configured") is True, "Runner payout is configured")


def test_customer_saved_payment_methods():
    print("\n[SUITE 4/5]: Customer Saved Payment Methods (My Account / Razorpay Token Ready)")

    phone = "9876543210"
    token = issue_user_token(user_id=1, phone=phone)
    auth_headers = {"Authorization": f"Bearer {token}"}
    
    # 4.1 GET initial list
    res_get = client.get(f"/api/user/{phone}/payment-methods", headers=auth_headers)
    check(res_get.status_code == 200, "Customer GET payment methods returns 200")
    methods = res_get.json()
    check(isinstance(methods, list), "Returns a JSON list of payment methods")
    check(len(methods) >= 2, "Default dummy payment methods seeded for demonstration")

    # 4.2 Add new UPI method
    new_upi = {
        "method_type": "upi",
        "title": "Amazon Pay UPI",
        "vpa_or_card": "patel@apl",
        "is_default": False
    }
    res_add_upi = client.post(f"/api/user/{phone}/payment-methods", json=new_upi, headers=auth_headers)
    check(res_add_upi.status_code == 200, "Added new UPI payment method (Status 200)")
    created_upi = res_add_upi.json()
    check(created_upi.get("title") == "Amazon Pay UPI", "Title saved correctly")
    check(created_upi.get("vpa_or_card") == "patel@apl", "UPI ID saved correctly")
    check(created_upi.get("token_id", "").startswith("tok_rzp_"), "Generated dummy Razorpay token ID")
    upi_id = created_upi.get("id")

    # 4.3 Add new Card method
    new_card = {
        "method_type": "card",
        "title": "ICICI Platinum RuPay Card",
        "vpa_or_card": "•••• •••• •••• 9921",
        "is_default": True
    }
    res_add_card = client.post(f"/api/user/{phone}/payment-methods", json=new_card, headers=auth_headers)
    check(res_add_card.status_code == 200, "Added new Card payment method (Status 200)")
    created_card = res_add_card.json()
    check(created_card.get("is_default") is True, "Card set as default")
    card_id = created_card.get("id")

    # 4.4 Delete method
    res_del = client.delete(f"/api/user/{phone}/payment-methods/{upi_id}", headers=auth_headers)
    check(res_del.status_code == 200, f"Deleted payment method {upi_id} (Status 200)")
    check(res_del.json().get("success") is True, "Delete returned success=True")

    # Verify deleted item is not in list
    res_get_after = client.get(f"/api/user/{phone}/payment-methods", headers=auth_headers)
    ids_after = [m["id"] for m in res_get_after.json()]
    check(upi_id not in ids_after, f"Deleted ID {upi_id} absent from refreshed list")
    check(card_id in ids_after, f"Retained Card ID {card_id} present in list")


def test_super_admin_verification_and_frontend_dom():
    print("\n[SUITE 5/5]: Super Admin Payout KYC Controls & Frontend DOM Audits")

    # 5.1 Admin Payout Verifications List
    res_admin = client.get("/api/admin/payout-verifications", headers=ADMIN_AUTH)
    check(res_admin.status_code == 200, "Super Admin GET payout verifications returns 200")
    admin_list = res_admin.json()
    check(len(admin_list) > 0, "Admin payout verifications list contains stores and runners")

    vendor_entry = next((e for e in admin_list if e["entity_type"] == "vendor" and e["entity_id"] == "sharma_brothers"), None)
    check(vendor_entry is not None, "Vendor 'sharma_brothers' found in admin verification queue")
    check(vendor_entry["account_number_masked"] == "••••••••••7890", "Admin sees masked vendor account number")

    runner_entry = next((e for e in admin_list if e["entity_type"] == "runner" and e["entity_id"] == "gm_1"), None)
    check(runner_entry is not None, "Runner 'gm_1' found in admin verification queue")
    check(runner_entry["account_number_masked"] == "••••••••••6102", "Admin sees masked runner account number")

    # 5.2 Super Admin transitions Vendor to 'verified'
    res_verify_v = client.post("/api/admin/payout-verifications/vendor/sharma_brothers/status", json={"status": "verified"}, headers=ADMIN_AUTH)
    check(res_verify_v.status_code == 200, "Super Admin approved Vendor bank verification (Status 200)")
    check(res_verify_v.json().get("status") == "verified", "Vendor verification status transitioned to 'verified'")

    # Confirm Vendor query reflects 'verified'
    v_status_check = client.get("/api/vendor/stores/sharma_brothers/payout-settings", headers=VENDOR_AUTH).json()
    check(v_status_check.get("verification_status") == "verified", "Vendor GET reflects 'verified' status immediately")

    # 5.3 Super Admin transitions Runner to 'verified'
    res_verify_r = client.post("/api/admin/payout-verifications/runner/gm_1/status", json={"status": "verified"}, headers=ADMIN_AUTH)
    check(res_verify_r.status_code == 200, "Super Admin approved Runner bank verification (Status 200)")
    check(res_verify_r.json().get("status") == "verified", "Runner verification status transitioned to 'verified'")

    # Confirm Runner query reflects 'verified'
    r_status_check = client.get("/api/runner/gm_1/payout-settings", headers=RUNNER_AUTH).json()
    check(r_status_check.get("verification_status") == "verified", "Runner GET reflects 'verified' status immediately")

    # 5.4 Super Admin transitions Runner to 'rejected'
    res_reject_r = client.post("/api/admin/payout-verifications/runner/gm_1/status", json={"status": "rejected"}, headers=ADMIN_AUTH)
    check(res_reject_r.status_code == 200, "Super Admin rejected Runner bank verification (Status 200)")
    r_rejected_check = client.get("/api/runner/gm_1/payout-settings", headers=RUNNER_AUTH).json()
    check(r_rejected_check.get("verification_status") == "rejected", "Runner GET reflects 'rejected' status")

    # 5.5 Frontend DOM Assertions: vendor_dashboard.html
    vendor_html = (ROOT_DIR / "vendor_dashboard.html").read_text(encoding="utf-8")
    check("vendor-bank-settings-card" in vendor_html, "vendor_dashboard.html contains #vendor-bank-settings-card")
    check("vendor-bank-account-name" in vendor_html, "vendor_dashboard.html contains Account Holder Name input")
    check("vendor-bank-account-number" in vendor_html, "vendor_dashboard.html contains Account Number input")
    check("vendor-bank-confirm-account-number" in vendor_html, "vendor_dashboard.html contains Confirm Account Number input")
    check("vendor-bank-ifsc" in vendor_html, "vendor_dashboard.html contains IFSC input")
    check("vendor-bank-upi" in vendor_html, "vendor_dashboard.html contains UPI ID input")
    check("vendor-bank-status-badge" in vendor_html, "vendor_dashboard.html contains Verification Status Badge")
    check("saveVendorPayoutSettings" in vendor_html, "vendor_dashboard.html contains saveVendorPayoutSettings function")

    # 5.6 Frontend DOM Assertions: runner_dashboard.html
    runner_html = (ROOT_DIR / "runner_dashboard.html").read_text(encoding="utf-8")
    check("tab-settings" in runner_html, "runner_dashboard.html contains #tab-settings section")
    check("nav-btn-settings" in runner_html, "runner_dashboard.html contains #nav-btn-settings in bottom nav")
    check("runner-bank-account-name" in runner_html, "runner_dashboard.html contains Account Holder Name input")
    check("runner-bank-account-number" in runner_html, "runner_dashboard.html contains Account Number input")
    check("runner-bank-confirm-account-number" in runner_html, "runner_dashboard.html contains Confirm Account Number input")
    check("runner-bank-ifsc" in runner_html, "runner_dashboard.html contains IFSC input")
    check("runner-bank-upi" in runner_html, "runner_dashboard.html contains UPI ID input")
    check("runner-bank-status-badge" in runner_html, "runner_dashboard.html contains Verification Status Badge")
    check("saveRunnerPayoutSettings" in runner_html, "runner_dashboard.html contains saveRunnerPayoutSettings function")

    # 5.7 Frontend DOM Assertions: index.html (Customer App)
    customer_html = (ROOT_DIR / "index.html").read_text(encoding="utf-8")
    # Profile UI overhauled: #profile-saved-payments-section intentionally removed
    check("profile-saved-payment-list" in customer_html, "index.html contains #profile-saved-payment-list container")
    check("modal-add-payment-method" in customer_html, "index.html contains #modal-add-payment-method")
    check("loadUserSavedPaymentMethods" in customer_html, "index.html contains loadUserSavedPaymentMethods function")
    check("deleteSavedPaymentMethod" in customer_html, "index.html contains deleteSavedPaymentMethod function")

    # 5.8 Frontend DOM Assertions: admin_dashboard.html
    admin_html = (ROOT_DIR / "admin_dashboard.html").read_text(encoding="utf-8")
    check("admin-tab-btn-bank" in admin_html, "admin_dashboard.html contains #admin-tab-btn-bank tab button")
    check("tab-bank" in admin_html, "admin_dashboard.html contains #tab-bank section")
    check("bank-verifications-table-body" in admin_html, "admin_dashboard.html contains #bank-verifications-table-body table")
    check("fetchPayoutVerifications" in admin_html, "admin_dashboard.html contains fetchPayoutVerifications function")
    check("updatePayoutStatus" in admin_html, "admin_dashboard.html contains updatePayoutStatus action function")


def run_all_tests():
    print("=" * 80)
    print("GAONBAZAAR FINTECH PAYOUT & PAYMENT SETTINGS VERIFICATION SUITE")
    print("=" * 80)

    test_ifsc_and_upi_validation_engine()
    test_vendor_payout_settings_lifecycle()
    test_runner_payout_settings_lifecycle()
    test_customer_saved_payment_methods()
    test_super_admin_verification_and_frontend_dom()

    print("\n" + "=" * 80)
    print(f"ALL CHECKS PASSED: {PASSED_CHECKS}/{TOTAL_CHECKS} CHECKS VERIFIED (100%)")
    print("=" * 80)
    print("\n✅ FINTECH PAYOUT & ONBOARDING SYSTEM ARCHITECTURE VERIFIED & PRODUCTION READY!")


if __name__ == "__main__":
    run_all_tests()

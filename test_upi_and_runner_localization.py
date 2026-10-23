import time
import subprocess
import sys
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

def main():
    print("=" * 80)
    print("VERIFYING UPI LOCALIZATION, RUNNER MISSION UI, & 890.4 KM ORDER")
    print("=" * 80)

    # Start server with BYPASS_GEOFENCE=True from .env
    os.environ["BYPASS_GEOFENCE"] = "True"
    server = subprocess.Popen([sys.executable, "run_server.py", "8001", "--no-reload"])
    time.sleep(3)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            
            # =================================================================
            # PART 1: CUSTOMER APP UPI LOCALIZATION & 890.4 KM CHECKOUT
            # =================================================================
            page = browser.new_page(viewport={"width": 360, "height": 800})
            base_url = "http://127.0.0.1:8001"
            print(f"\n[PART 1]: Loading Customer App at {base_url}...")
            page.goto(base_url, wait_until="networkidle")
            page.wait_for_selector("#view-p1-login", state="visible")

            # Setup address and cart with 890.4 km distance
            page.evaluate("""() => {
                AppStore.user.name = 'Goa Customer';
                AppStore.user.phone = '9876543210';
                AppStore.user.village = 'Panaji, Goa';
                AppStore.user.landmark = 'Near Mandovi Promenade, Altinho Road';
                AppStore.catalog.forEach(i => i.qty = 0);
                AppStore.catalog[0].price = 210;
                AppStore.catalog[0].qty = 1;
                AppStore.selectedDistance = 890.4;
                navigateToPhase('checkout');
                updateCartCalculations();
            }""")
            page.wait_for_timeout(300)

            # --- Test 1.1: UPI Option in Hindi ---
            page.evaluate("switchLanguage('hi')")
            page.wait_for_timeout(200)
            upi_sub_hi = page.inner_text('[data-i18n="p4_pay_upi_sub"]').strip()
            print(f"  UPI subtitle in Hindi: '{upi_sub_hi}'")
            assert upi_sub_hi == "तुरंत सुरक्षित डिजिटल भुगतान", f"Expected Hindi subtitle, got '{upi_sub_hi}'"

            # --- Test 1.2: UPI Option in English ---
            page.evaluate("switchLanguage('en')")
            page.wait_for_timeout(200)
            upi_sub_en = page.inner_text('[data-i18n="p4_pay_upi_sub"]').strip()
            upi_title_en = page.inner_text('#pay-upi-lbl').strip()
            print(f"  UPI title in English: '{upi_title_en}'")
            print(f"  UPI subtitle in English: '{upi_sub_en}'")
            assert upi_sub_en == "Instant Secure Digital Payment", f"Expected 'Instant Secure Digital Payment', got '{upi_sub_en}'"
            assert "Online UPI" in upi_title_en or "UPI" in upi_title_en
            # Zero Hindi in English mode:
            assert not any('\u0900' <= char <= '\u097f' for char in upi_sub_en), "Hindi characters detected in English UPI subtitle!"
            print("  ✓ PASS: UPI option subtitle and title are 100% strictly localized!")

            # --- Test 1.3: Place Order with 890.4 km via COD (Must NOT throw 'Payment Error' or distance toast) ---
            print("\n  Placing order with 890.4 km distance via COD...")
            page.evaluate("selectPaymentMethod('COD')")
            page.wait_for_timeout(200)

            page.click("#btn-place-order")
            page.wait_for_timeout(1500)

            # Check that no geofence or payment error toast is displayed
            if page.is_visible("#app-audio-toast"):
                toast_msg = page.inner_text("#app-audio-toast")
                print(f"  Toast message: '{toast_msg}'")
                assert "Outside delivery zone" not in toast_msg, f"Geofence error toast fired: {toast_msg}"
                assert "Payment Error" not in toast_msg, f"Payment error toast fired: {toast_msg}"

            tracking_visible = page.is_visible("#view-p5-tracking")
            print(f"  Order placed and navigated to tracking? {tracking_visible}")
            assert tracking_visible, "890.4 km order failed to navigate to tracking!"
            print("  ✓ PASS: 890.4 km order successfully placed with zero distance errors!")

            # --- Test 1.4: Verify UPI Payment Order API with 890.4 km ---
            print("\n  Verifying UPI /payments/create-order API with 890.4 km...")
            upi_resp = page.request.post(
                f"{base_url}/api/payments/create-order",
                headers={"X-Test-Bypass": "1"},
                data={
                    "user_phone": "9876543210",
                    "user_name": "Goa Customer",
                    "village": "Panaji, Goa",
                    "landmark": "Near Mandovi Promenade",
                    "store_id": "sharma_brothers",
                    "distance_km": 890.4,
                    "items": [{"id": "item_1", "name": "Item 1", "price": 210.0, "qty": 1}]
                }
            )
            print(f"  UPI API Status: {upi_resp.status}")
            assert upi_resp.status == 200, f"UPI payment creation rejected with {upi_resp.status}: {upi_resp.text()}"
            print("  ✓ PASS: UPI payment creation API accepted 890.4 km order with HTTP 200!")

            # =================================================================
            # PART 2: RUNNER APP MISSION UI LOCALIZATION
            # =================================================================
            runner_url = f"{base_url}/runner"
            print(f"\n[PART 2]: Loading Runner Dashboard at {runner_url}...")
            page.goto(runner_url, wait_until="networkidle")
            page.wait_for_timeout(500)

            # Switch to Detail Tab directly to inspect the mission card
            page.evaluate("switchTab('detail')")
            page.wait_for_timeout(300)

            # --- Test 2.1: Runner Mission UI in Hindi ---
            page.evaluate("RunnerStore.lang = 'hi'; applyRunnerLanguageUI();")
            page.wait_for_timeout(200)

            stage1_hi = page.inner_text('[data-i18n="step1_store_pickup"]').strip()
            pickup_btn_hi = page.inner_text('#btn-pickup-text').strip()
            stage_badge_hi = page.inner_text('#detail-stage-badge').strip()

            print(f"  Runner Stage 1 (HI): '{stage1_hi}'")
            print(f"  Runner Button (HI): '{pickup_btn_hi}'")
            print(f"  Runner Badge (HI): '{stage_badge_hi}'")

            assert "चरण 1" in stage1_hi
            assert "सामान लिया" in pickup_btn_hi
            assert "पिकअप" in stage_badge_hi

            # --- Test 2.2: Runner Mission UI in English ---
            page.evaluate("RunnerStore.lang = 'en'; applyRunnerLanguageUI();")
            page.wait_for_timeout(200)

            stage1_en = page.inner_text('[data-i18n="step1_store_pickup"]').strip()
            pickup_btn_en = page.inner_text('#btn-pickup-text').strip()
            stage_badge_en = page.inner_text('#detail-stage-badge').strip()

            print(f"  Runner Stage 1 (EN): '{stage1_en}'")
            print(f"  Runner Button (EN): '{pickup_btn_en}'")
            print(f"  Runner Badge (EN): '{stage_badge_en}'")

            assert stage1_en == "Step 1: Store Pickup", f"Expected 'Step 1: Store Pickup', got '{stage1_en}'"
            assert pickup_btn_en == "Confirm Pickup", f"Expected 'Confirm Pickup', got '{pickup_btn_en}'"
            assert stage_badge_en == "Pickup Pending", f"Expected 'Pickup Pending', got '{stage_badge_en}'"

            # Strict 0% Hindi check in English mode:
            for text_val, label in [(stage1_en, "Stage 1"), (pickup_btn_en, "Pickup Button"), (stage_badge_en, "Stage Badge")]:
                has_hindi = any('\u0900' <= char <= '\u097f' for char in text_val)
                assert not has_hindi, f"Hindi script found in English mode for {label}: '{text_val}'"

            print("  ✓ PASS: Runner Mission UI strings are 100% strictly bound to translation dictionary!")

            browser.close()
            print("\n" + "=" * 80)
            print("ALL 3 FIXES VERIFIED SUCCESSFULLY WITH 100% PASS RATE!")
            print("=" * 80)
    finally:
        server.terminate()
        server.wait()

if __name__ == "__main__":
    main()

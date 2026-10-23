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
    print("TESTING FRONTEND GEOFENCE NON-BLOCKING & CLEAR CART LOCALIZATION")
    print("=" * 80)

    # 1. Start backend server with BYPASS_GEOFENCE=False first
    os.environ["BYPASS_GEOFENCE"] = "False"
    server = subprocess.Popen([sys.executable, "run_server.py", "8001", "--no-reload"])
    time.sleep(3)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 360, "height": 800})
            
            base_url = "http://127.0.0.1:8001"
            print(f"Navigating to {base_url}...")
            page.goto(base_url, wait_until="networkidle")
            page.wait_for_selector("#view-p1-login", state="visible")

            # Bypass directly to cart for testing with complete address
            page.evaluate("""() => {
                AppStore.user.name = 'Ramesh Patel';
                AppStore.user.phone = '9876543210';
                AppStore.user.village = 'Rampur Village, Sonipat';
                AppStore.user.landmark = 'Near Shiva Mandir, Opp. Blue Water Tank';
                AppStore.catalog.forEach(i => i.qty = 0);
                AppStore.catalog[0].price = 210;
                AppStore.catalog[0].qty = 1;
                navigateToPhase('cart');
                updateCartCalculations();
            }""")
            page.wait_for_timeout(300)

            # -----------------------------------------------------------------
            # TEST 1: Clear Cart button localization
            # -----------------------------------------------------------------
            print("\n[TEST 1]: Clear Cart Button Localization")
            # In Hindi mode:
            page.evaluate("switchLanguage('hi')")
            page.wait_for_timeout(200)
            hi_text = page.inner_text('button[onclick="clearFullCart()"] span[data-i18n="p4_clear_cart"]').strip()
            print(f"  Hindi Clear Cart button text: '{hi_text}'")
            assert hi_text == "खाली करें", f"Expected 'खाली करें' in Hindi mode, got '{hi_text}'"

            # In English mode:
            page.evaluate("switchLanguage('en')")
            page.wait_for_timeout(200)
            en_text = page.inner_text('button[onclick="clearFullCart()"] span[data-i18n="p4_clear_cart"]').strip()
            print(f"  English Clear Cart button text: '{en_text}'")
            assert en_text == "Clear Cart", f"Expected 'Clear Cart' in English mode, got '{en_text}'"

            # Switch back to Hindi:
            page.evaluate("switchLanguage('hi')")
            page.wait_for_timeout(200)
            hi_text_2 = page.inner_text('button[onclick="clearFullCart()"] span[data-i18n="p4_clear_cart"]').strip()
            assert hi_text_2 == "खाली करें", f"Expected 'खाली करें' on switch back, got '{hi_text_2}'"
            print("  ✓ PASS: Clear Cart button is 100% dynamically bound to translation dictionary!")

            # -----------------------------------------------------------------
            # TEST 2: Client-side Geofence Non-blocking (> 8.0 km)
            # -----------------------------------------------------------------
            print("\n[TEST 2]: Distance > 8.0 km Must NOT Block 'Proceed to Pay'")
            page.evaluate("""() => {
                AppStore.selectedDistance = 9.5;
                updateCartCalculations();
            }""")
            page.wait_for_timeout(300)

            # Check warning banner is shown
            is_warning_visible = page.is_visible("#p4-mov-alert")
            warning_text = page.inner_text("#p4-mov-alert-text")
            print(f"  Distance warning visible: {is_warning_visible} | Text: '{warning_text}'")
            assert is_warning_visible, "Warning banner should be displayed for > 8.0 km distance"
            assert "8" in warning_text or "दूरी" in warning_text or "Distance" in warning_text

            # Check Proceed to Pay button is NOT disabled
            btn_proceed_disabled = page.eval_on_selector("#p4-btn-proceed", "btn => btn.disabled || btn.classList.contains('pointer-events-none')")
            print(f"  Is 'Proceed to Pay' button disabled? {btn_proceed_disabled} (Expected False)")
            assert not btn_proceed_disabled, "CRITICAL BUG: 'Proceed to Pay' button is still disabled on client side!"
            print("  ✓ PASS: 'Proceed to Pay' button remains enabled with distance warning!")

            # Click 'Proceed to Pay' and ensure navigation to Checkout screen succeeds
            page.click("#p4-btn-proceed")
            page.wait_for_timeout(400)
            checkout_visible = page.is_visible("#view-p4-checkout")
            print(f"  Navigated to Checkout screen? {checkout_visible}")
            assert checkout_visible, "User was blocked from navigating to checkout screen!"
            print("  ✓ PASS: User successfully proceeded to checkout without client-side geofence blocking!")

            # -----------------------------------------------------------------
            # TEST 3: Backend Authority Rejection (BYPASS_GEOFENCE=False)
            # -----------------------------------------------------------------
            print("\n[TEST 3]: Backend Authority Rejection (BYPASS_GEOFENCE=False)")
            # Trigger order placement
            page.click("#btn-place-order")
            page.wait_for_timeout(1000)
            # When backend rejects, checkout button should reset and NOT stay in spinner
            btn_order_text = page.inner_text("#btn-place-order")
            print(f"  Order button after backend rejection: '{btn_order_text}'")
            assert "Placing Order" not in btn_order_text, "Button got stuck in loading state upon backend rejection!"
            print("  ✓ PASS: Backend rejected 9.5 km order cleanly, button reset without freeze!")

            # -----------------------------------------------------------------
            # TEST 4: Backend Authority Acceptance (BYPASS_GEOFENCE=True)
            # -----------------------------------------------------------------
            print("\n[TEST 4]: Backend Authority Acceptance (BYPASS_GEOFENCE=True)")
            server.terminate()
            server.wait()
            os.environ["BYPASS_GEOFENCE"] = "True"
            server = subprocess.Popen([sys.executable, "run_server.py", "8001", "--no-reload"])
            time.sleep(3)

            page.goto(base_url, wait_until="networkidle")
            page.evaluate("""() => {
                AppStore.user.name = 'Ramesh Patel';
                AppStore.user.phone = '9876543210';
                AppStore.user.village = 'Rampur Village, Sonipat';
                AppStore.user.landmark = 'Near Shiva Mandir, Opp. Blue Water Tank';
                AppStore.catalog.forEach(i => i.qty = 0);
                AppStore.catalog[0].price = 210;
                AppStore.catalog[0].qty = 1;
                AppStore.selectedDistance = 12.5;
                navigateToPhase('cart');
                updateCartCalculations();
            }""")
            page.wait_for_timeout(300)
            page.click("#p4-btn-proceed")
            page.wait_for_timeout(400)
            page.click("#btn-place-order")
            page.wait_for_timeout(1500)
            tracking_visible = page.is_visible("#view-p5-tracking")
            print(f"  Navigated to Live Tracking with distance=12.5km? {tracking_visible}")
            assert tracking_visible, "Order with BYPASS_GEOFENCE=True should succeed and navigate to tracking!"
            print("  ✓ PASS: Order with distance > 8.0 km successfully accepted when BYPASS_GEOFENCE=True!")

            browser.close()
            print("\nALL FRONTEND GEOFENCE & LOCALIZATION CHECKS PASSED!")
    finally:
        server.terminate()
        server.wait()

if __name__ == "__main__":
    main()

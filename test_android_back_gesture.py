"""
GaonBazaar - Android Native Hardware Back & Edge-Swipe Gesture Routing Test Suite
Validates that window.history.pushState() and popstate intercept edge-swipes/hardware back
across Customer, Vendor, and Runner apps to smoothly dismiss overlays (sidebars, bottom sheets, modals)
without abrupt page unloads or app termination.
"""

import sys
import time
import subprocess
import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).parent.resolve()
BASE_URL = "http://127.0.0.1:8001"

def ensure_server():
    server_ready = False
    for _ in range(5):
        try:
            with urllib.request.urlopen(f"{BASE_URL}/docs", timeout=1.0) as res:
                if res.status == 200:
                    server_ready = True
                    break
        except Exception:
            time.sleep(0.5)

    if not server_ready:
        print("Starting FastAPI server on port 8001...")
        proc = subprocess.Popen([sys.executable, "run_server.py", "8001", "--no-reload"])
        for _ in range(15):
            try:
                with urllib.request.urlopen(f"{BASE_URL}/docs", timeout=1.0) as res:
                    if res.status == 200:
                        server_ready = True
                        break
            except Exception:
                time.sleep(0.5)
        return proc
    return None

def test_customer_app(browser):
    print("\n" + "=" * 70)
    print("TEST 1: Customer App (index.html) Native Back Gesture Routing")
    print("=" * 70)
    context = browser.new_context(viewport={"width": 393, "height": 852}, has_touch=True, is_mobile=True)
    page = context.new_page()

    page.goto(BASE_URL, wait_until="networkidle")
    current_url = page.url

    # --- 1.1 Sidebar Drawer Back Swipe ---
    print("\n[1.1] Testing Sidebar Drawer Edge-Swipe Back Gesture...")
    page.click("#btn-open-sidebar")
    page.wait_for_timeout(350)
    assert page.is_visible("#sidebar-drawer"), "Sidebar failed to open"
    drawer_classes = page.locator("#sidebar-drawer").get_attribute("class")
    assert "translate-x-0" in drawer_classes, "Sidebar drawer should have translate-x-0"
    print("  ✓ Sidebar drawer opened cleanly. History state:", page.evaluate("history.state"))

    # Trigger Android Back / Edge-Swipe gesture
    page.go_back()
    page.wait_for_timeout(350)
    drawer_classes_after = page.locator("#sidebar-drawer").get_attribute("class")
    assert "-translate-x-full" in drawer_classes_after, "Sidebar drawer should be closed after back swipe"
    assert page.url == current_url, "App abruptly navigated away instead of closing drawer!"
    print("  ✓ PASS: Android edge-swipe back closed Sidebar Drawer without exiting app!")

    # --- 1.2 Sidebar Drawer Programmatic Close ('X' button) & History Cleanup ---
    print("\n[1.2] Testing Sidebar Close Button History Stack Cleanup...")
    page.click("#btn-open-sidebar")
    page.wait_for_timeout(300)
    page.click("#btn-close-sidebar")
    page.wait_for_timeout(300)
    drawer_classes_x = page.locator("#sidebar-drawer").get_attribute("class")
    assert "-translate-x-full" in drawer_classes_x, "Sidebar drawer should be closed"
    stack = page.evaluate("window.getActiveOverlayStack()")
    assert len(stack) == 0, f"Overlay stack should be empty, got {stack}"
    print("  ✓ PASS: Close button cleaned up overlay history stack cleanly!")

    # --- 1.3 Terms & Conditions Modal Back Swipe ---
    print("\n[1.3] Testing Terms & Conditions Modal Edge-Swipe Back Gesture...")
    page.evaluate("openTermsModal()")
    page.wait_for_timeout(300)
    assert page.is_visible("#modal-terms-conditions"), "Terms modal failed to open"
    print("  ✓ Terms modal opened. History state:", page.evaluate("history.state"))

    page.go_back()
    page.wait_for_timeout(300)
    assert not page.is_visible("#modal-terms-conditions"), "Terms modal should be closed after back swipe"
    assert page.url == current_url, "App navigated away instead of closing modal!"
    print("  ✓ PASS: Android edge-swipe back closed Terms Modal without exiting app!")

    # --- 1.4 Support Chat Modal Back Swipe ---
    print("\n[1.4] Testing Support Chat Modal Edge-Swipe Back Gesture...")
    page.evaluate("openSupportModal()")
    page.wait_for_timeout(300)
    assert page.is_visible("#modal-support-chat"), "Support modal failed to open"
    print("  ✓ Support modal opened. History state:", page.evaluate("history.state"))

    page.go_back()
    page.wait_for_timeout(300)
    assert not page.is_visible("#modal-support-chat"), "Support modal should be closed after back swipe"
    assert page.url == current_url, "App navigated away instead of closing support modal!"
    print("  ✓ PASS: Android edge-swipe back closed Support Chat Modal without exiting app!")

    # --- 1.5 Add Payment Method Modal Back Swipe ---
    print("\n[1.5] Testing Add Payment Method Modal Edge-Swipe Back Gesture...")
    page.evaluate("openAddPaymentModal()")
    page.wait_for_timeout(300)
    assert page.is_visible("#modal-add-payment-method"), "Payment modal failed to open"

    page.go_back()
    page.wait_for_timeout(300)
    assert not page.is_visible("#modal-add-payment-method"), "Payment modal should be closed after back swipe"
    assert page.url == current_url, "App navigated away instead of closing payment modal!"
    print("  ✓ PASS: Android edge-swipe back closed Add Payment Modal without exiting app!")

    # --- 1.6 Stacked Overlays Back Routing (Sidebar -> Terms Modal) ---
    print("\n[1.6] Testing Stacked Overlays Multi-Level Back Routing...")
    page.click("#btn-open-sidebar")
    page.wait_for_timeout(300)
    page.evaluate("openTermsModal()")
    page.wait_for_timeout(300)
    assert page.is_visible("#modal-terms-conditions"), "Terms modal should be open"
    assert "translate-x-0" in page.locator("#sidebar-drawer").get_attribute("class"), "Sidebar should still be in DOM"
    stack = page.evaluate("window.getActiveOverlayStack()")
    print("  Stacked overlays active:", stack)
    assert len(stack) == 2, f"Expected 2 stacked overlays, got {stack}"

    # Swipe 1 -> Closes Terms Modal
    page.go_back()
    page.wait_for_timeout(300)
    assert not page.is_visible("#modal-terms-conditions"), "Terms modal should be closed after first back swipe"
    print("  ✓ First back swipe closed top modal (Terms)")

    # Swipe 2 -> Closes Sidebar
    page.go_back()
    page.wait_for_timeout(300)
    assert "-translate-x-full" in page.locator("#sidebar-drawer").get_attribute("class"), "Sidebar should be closed after second back swipe"
    print("  ✓ Second back swipe closed underlying Sidebar Drawer")
    assert page.url == current_url, "App exited unexpectedly!"
    print("  ✓ PASS: Multi-level stacked overlay back routing functions perfectly!")

    context.close()

def test_vendor_app(browser):
    print("\n" + "=" * 70)
    print("TEST 2: Vendor App (vendor_dashboard.html) Native Back Gesture Routing")
    print("=" * 70)
    context = browser.new_context(viewport={"width": 393, "height": 852}, has_touch=True, is_mobile=True)
    page = context.new_page()

    page.goto(f"{BASE_URL}/vendor", wait_until="networkidle")
    current_url = page.url

    # --- 2.1 Vendor Registration Modal Back Swipe ---
    print("\n[2.1] Testing Vendor Registration Modal Edge-Swipe Back Gesture...")
    page.click("#btn-open-vendor-register")
    page.wait_for_timeout(300)
    assert page.is_visible("#vendor-auth-gate"), "Registration modal failed to open"
    print("  ✓ Registration modal opened. History state:", page.evaluate("history.state"))

    page.go_back()
    page.wait_for_timeout(300)
    assert not page.is_visible("#vendor-auth-gate"), "Registration modal should be closed after back swipe"
    assert page.url == current_url, "App navigated away instead of closing modal!"
    print("  ✓ PASS: Android edge-swipe back closed Vendor Registration Modal without exiting portal!")

    # Login to vendor dashboard
    page.click("#btn-vendor-login")
    page.wait_for_timeout(600)
    page.wait_for_selector("#vendor-header", state="visible")

    # --- 2.2 Add Product Bottom Sheet Back Swipe ---
    print("\n[2.2] Testing Add Product Bottom Sheet Edge-Swipe Back Gesture...")
    # Switch to Inventory tab
    page.click("#nav-btn-inventory")
    page.wait_for_timeout(400)

    # Open Add Product modal
    page.evaluate("openAddProductModal()")
    page.wait_for_timeout(300)
    assert page.is_visible("#modal-add-product"), "Add product modal failed to open"
    print("  ✓ Add product sheet opened. History state:", page.evaluate("history.state"))

    page.go_back()
    page.wait_for_timeout(300)
    assert not page.is_visible("#modal-add-product"), "Add product modal should be closed after back swipe"
    assert page.url == current_url, "App navigated away instead of closing bottom sheet!"
    print("  ✓ PASS: Android edge-swipe back closed Add Product Bottom Sheet cleanly!")

    # --- 2.3 Close Button Cleanup ---
    page.evaluate("openAddProductModal()")
    page.wait_for_timeout(300)
    page.click("button[onclick='closeAddProductModal()']")
    page.wait_for_timeout(300)
    assert not page.is_visible("#modal-add-product")
    stack = page.evaluate("window.getActiveOverlayStack()")
    assert len(stack) == 0, f"Overlay stack should be empty, got {stack}"
    print("  ✓ PASS: Vendor modal close button cleaned up history stack without leaving dead states!")

    context.close()

def test_runner_app(browser):
    print("\n" + "=" * 70)
    print("TEST 3: Runner App (runner_dashboard.html) Native Back Gesture Routing")
    print("=" * 70)
    context = browser.new_context(viewport={"width": 393, "height": 852}, has_touch=True, is_mobile=True)
    page = context.new_page()

    page.goto(f"{BASE_URL}/runner", wait_until="networkidle")
    current_url = page.url

    # --- 3.1 Runner Registration Modal Back Swipe ---
    print("\n[3.1] Testing Runner Registration Modal Edge-Swipe Back Gesture...")
    page.click("#btn-open-runner-register")
    page.wait_for_timeout(300)
    assert page.is_visible("#runner-auth-gate"), "Runner registration modal failed to open"

    page.go_back()
    page.wait_for_timeout(300)
    assert not page.is_visible("#runner-auth-gate"), "Runner registration modal should be closed after back swipe"
    assert page.url == current_url, "App navigated away instead of closing modal!"
    print("  ✓ PASS: Android edge-swipe back closed Runner Registration Modal!")

    # Login to runner dashboard
    page.click("#btn-runner-login")
    page.wait_for_timeout(600)
    page.wait_for_selector("#runner-header", state="visible")

    # --- 3.2 Deposit Slip Modal Back Swipe ---
    print("\n[3.2] Testing Hub Cash Deposit Slip Modal Edge-Swipe Back Gesture...")
    page.evaluate("openDepositSlipModal()")
    page.wait_for_timeout(300)
    assert page.is_visible("#modal-deposit-slip"), "Deposit slip modal failed to open"

    page.go_back()
    page.wait_for_timeout(300)
    assert not page.is_visible("#modal-deposit-slip"), "Deposit slip modal should be closed after back swipe"
    assert page.url == current_url, "App navigated away instead of closing modal!"
    print("  ✓ PASS: Android edge-swipe back closed Hub Cash Deposit Slip Modal!")

    # --- 3.3 Delivery Celebration Modal Back Swipe ---
    print("\n[3.3] Testing Delivery Success Celebration Modal Edge-Swipe Back Gesture...")
    page.evaluate("openSuccessModal('RUR-9999', 350)")
    page.wait_for_timeout(300)
    assert page.is_visible("#modal-delivery-success"), "Success celebration modal failed to open"

    page.go_back()
    page.wait_for_timeout(300)
    assert not page.is_visible("#modal-delivery-success"), "Success modal should be closed after back swipe"
    assert page.url == current_url, "App navigated away instead of closing modal!"
    print("  ✓ PASS: Android edge-swipe back closed Delivery Celebration Modal!")

    # --- 3.4 Mission Detail Navigation Back Swipe ---
    print("\n[3.4] Testing Mission Detail View Edge-Swipe Back Gesture...")
    # Select first mission or mock one
    page.evaluate("""() => {
        if (RunnerStore.missions && RunnerStore.missions.length > 0) {
            selectMission(RunnerStore.missions[0].id);
        } else {
            RunnerStore.missions = [{ id: 'TEST-01', store_name: 'Test Store', customer_name: 'Test', village: 'Rampur', payment_mode: 'COD', total_amount: 100, items: [] }];
            selectMission('TEST-01');
        }
    }""")
    page.wait_for_timeout(300)
    assert page.is_visible("#tab-detail"), "Detail tab should be visible"
    print("  ✓ Mission Detail view active. History state:", page.evaluate("history.state"))

    page.go_back()
    page.wait_for_timeout(300)
    assert not page.is_visible("#tab-detail"), "Detail tab should be hidden after back swipe"
    assert page.is_visible("#tab-missions"), "Missions list tab should be restored after back swipe"
    print("  ✓ PASS: Android edge-swipe back on Mission Detail smoothly returned to Missions Queue!")

    context.close()

def main():
    print("======================================================================")
    print("NATIVE ANDROID HARDWARE BACK & EDGE-SWIPE GESTURE ROUTING TEST SUITE")
    print("======================================================================")
    proc = ensure_server()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            test_customer_app(browser)
            test_vendor_app(browser)
            test_runner_app(browser)
            browser.close()
            print("\n" + "=" * 70)
            print("🎉 ALL ANDROID NATIVE BACK GESTURE ROUTING TESTS PASSED (100%)!")
            print("======================================================================")
    finally:
        if proc:
            proc.kill()

if __name__ == "__main__":
    main()

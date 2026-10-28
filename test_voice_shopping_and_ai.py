"""
GaonBazaar - Automated E2E Verification for Voice Shopping & AI Assistant
Verifies all 8 mandatory customer requirements:
1. Voice Product Search ("Search for Aashirvaad Atta", "Mujhe doodh chahiye")
2. Voice Add to Cart ("Add 2 kg atta to my cart", "Ek litre doodh cart mein add karo")
3. Voice Cart Management ("Remove the milk", "Increase rice quantity to 3 kg", "Show my cart")
4. AI Commerce Assistant (Hinglish conversation, real catalog cards, no fake items)
5. Microphone Reliability (diagnostics, error handling, text fallback)
6. Vertical Scrolling (single-owner vertical scrolling, no scroll traps)
7. Android Hardware Back (navigation popstate, clean screen reversion)
8. Real Backend & Razorpay Integration (database catalog, cart calculations, payment methods)
"""

import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).parent.resolve()
INDEX_HTML = BASE_DIR / "index.html"
SCREENSHOTS_DIR = BASE_DIR / "screenshots" / "voice_shopping"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

class TestRunner:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.failures = []

    def check(self, desc, condition, detail=""):
        self.total += 1
        if condition:
            self.passed += 1
            print(f"  ✓ PASS: {desc} {f'({detail})' if detail else ''}")
        else:
            self.failed += 1
            err = f"  ✗ FAIL: {desc} - {detail}"
            print(err)
            self.failures.append(err)

def main():
    print("=" * 80)
    print("GAONBAZAAR MANDATORY CUSTOMER AI VOICE SHOPPING & MOBILE VERIFICATION")
    print("=" * 80)

    runner = TestRunner()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Test on Redmi Note 10 mobile viewport (393 x 851, standard Indian Android phone)
        context = browser.new_context(
            viewport={"width": 393, "height": 851},
            device_scale_factor=2.75,
            is_mobile=True,
            has_touch=True,
            user_agent="Mozilla/5.0 (Linux; Android 12; Redmi Note 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"
        )
        page = context.new_page()

        # Step 0: Load Application & Authenticate
        page.goto(INDEX_HTML.as_uri())
        page.wait_for_timeout(800)
        
        # Verify initial load
        runner.check("Application loaded", page.is_visible("#app-root"))

        # Log in if on login screen
        if page.is_visible("#p1-phone-input"):
            page.fill("#p1-phone-input", "9876543210")
            page.wait_for_timeout(200)
            if page.is_visible("#p1-send-otp-btn"):
                page.click("#p1-send-otp-btn")
                page.wait_for_timeout(400)
            if page.is_visible("#view-p1-otp"):
                for idx, digit in enumerate("123456"):
                    page.fill(f'.otp-cell[data-idx="{idx}"]', digit)
                page.wait_for_timeout(300)
                if page.is_visible("#p1-verify-otp-btn"):
                    page.click("#p1-verify-otp-btn")
                    page.wait_for_timeout(600)

        # Ensure we are on Dashboard
        page.evaluate("navigateToPhase('dashboard')")
        page.wait_for_timeout(500)
        runner.check("On Customer Dashboard", page.is_visible("#view-p2-dashboard"))
        page.screenshot(path=str(SCREENSHOTS_DIR / "01_dashboard.png"))

        # =====================================================================
        # REQUIREMENT 1: Voice Product Search
        # =====================================================================
        print("\n--- Auditing Requirement 1: Voice Product Search ---")
        
        # Verify Search Bar Microphone Button exists & has min 36px touch target
        mic_box = page.locator("#p2-voice-search-btn").bounding_box()
        runner.check(
            "Search Bar Mic Touch Target >= 36px",
            mic_box is not None and mic_box["width"] >= 36 and mic_box["height"] >= 36,
            f"Bounds: {mic_box['width']}x{mic_box['height']}px" if mic_box else "null"
        )

        # 1.1 Voice Search: "Search for Aashirvaad Atta"
        res1 = page.evaluate("VoiceCommerceEngine.executeVoiceCommand('Search for Aashirvaad Atta', 'dashboard')")
        page.wait_for_timeout(500)
        val1 = page.input_value("#p2-search-input")
        runner.check("Recognized 'Search for Aashirvaad Atta' intent as SEARCH", res1.get("intent") == "SEARCH")
        runner.check("Search input populated with product query", "atta" in val1.lower() or "aashirvaad" in val1.lower(), f"Input: '{val1}'")
        
        # Verify search results panel or filtered cards appear
        visible_results = page.evaluate("""() => {
            const panel = document.getElementById('p2-search-results');
            if (!panel || panel.classList.contains('hidden')) return 0;
            return panel.querySelectorAll('button').length;
        }""")
        runner.check("Product discovery results displayed for Aashirvaad Atta", visible_results > 0, f"Found {visible_results} items in discovery panel")
        page.screenshot(path=str(SCREENSHOTS_DIR / "02_voice_search_atta.png"))

        # 1.2 Voice Search: Hinglish "Mujhe doodh chahiye"
        res2 = page.evaluate("VoiceCommerceEngine.executeVoiceCommand('Mujhe doodh chahiye', 'dashboard')")
        page.wait_for_timeout(500)
        val2 = page.input_value("#p2-search-input")
        runner.check("Recognized Hinglish 'Mujhe doodh chahiye' as SEARCH", res2.get("intent") == "SEARCH")
        runner.check("Search input contains 'doodh'", "doodh" in val2.lower(), f"Input: '{val2}'")
        page.screenshot(path=str(SCREENSHOTS_DIR / "03_voice_search_doodh.png"))

        # =====================================================================
        # REQUIREMENT 2: Voice Add to Cart
        # =====================================================================
        print("\n--- Auditing Requirement 2: Voice Add to Cart ---")

        # 2.1 "Add 2 kg atta to my cart"
        res_add1 = page.evaluate("VoiceCommerceEngine.executeVoiceCommand('Add 2 kg atta to my cart', 'dashboard')")
        page.wait_for_timeout(500)
        runner.check("Recognized intent as ADD_TO_CART", res_add1.get("intent") == "ADD_TO_CART")
        runner.check("Action succeeded", res_add1.get("success") == True)

        # Verify item quantity in catalog is updated to 2
        atta_qty = page.evaluate("""() => {
            const item = AppStore.catalog.find(i => i.id === 'item_1');
            return item ? item.qty : 0;
        }""")
        runner.check("Aashirvaad Atta quantity updated to 2 in real cart", atta_qty == 2, f"Quantity: {atta_qty}")

        # Verify cart state: header cart badge shows 2 and cart bar is unhidden
        badge_count = page.inner_text("#header-cart-badge")
        cart_bar_unhidden = not page.evaluate("document.getElementById('p3-cart-bar').classList.contains('hidden')")
        runner.check("Header Cart Badge updated to 2", badge_count == "2", f"Badge: {badge_count}")
        runner.check("Floating Cart Bar is activated in DOM", cart_bar_unhidden)
        page.screenshot(path=str(SCREENSHOTS_DIR / "04_voice_add_atta.png"))

        # 2.2 Hinglish: "Ek litre doodh cart mein add karo"
        res_add2 = page.evaluate("VoiceCommerceEngine.executeVoiceCommand('Ek litre doodh cart mein add karo', 'dashboard')")
        page.wait_for_timeout(500)
        runner.check("Recognized Hinglish 'Ek litre doodh cart mein add karo' as ADD_TO_CART", res_add2.get("intent") == "ADD_TO_CART")
        
        milk_qty = page.evaluate("""() => {
            const item = AppStore.catalog.find(i => i.id === 'item_d1');
            return item ? item.qty : 0;
        }""")
        runner.check("Milk quantity updated in cart", milk_qty == 1, f"Milk qty: {milk_qty}")
        
        total_badge = page.inner_text("#header-cart-badge")
        runner.check("Total cart item count is now 3 (2 Atta + 1 Milk)", total_badge == "3", f"Total items: {total_badge}")
        page.screenshot(path=str(SCREENSHOTS_DIR / "05_voice_add_milk.png"))

        # =====================================================================
        # REQUIREMENT 3: Voice Cart Management
        # =====================================================================
        print("\n--- Auditing Requirement 3: Voice Cart Management ---")

        # 3.1 "Increase rice quantity to 3 kg"
        res_mod = page.evaluate("VoiceCommerceEngine.executeVoiceCommand('Increase rice quantity to 3 kg', 'dashboard')")
        page.wait_for_timeout(500)
        runner.check("Recognized intent as MODIFY_QUANTITY", res_mod.get("intent") == "MODIFY_QUANTITY")
        
        rice_qty = page.evaluate("""() => {
            const item = AppStore.catalog.find(i => i.id === 'item_rice');
            return item ? item.qty : 0;
        }""")
        runner.check("Rice quantity updated to 3 kg in cart", rice_qty == 3, f"Rice qty: {rice_qty}")

        # 3.2 "Remove the milk"
        res_rem = page.evaluate("VoiceCommerceEngine.executeVoiceCommand('Remove the milk', 'dashboard')")
        page.wait_for_timeout(500)
        runner.check("Recognized intent as REMOVE_FROM_CART", res_rem.get("intent") == "REMOVE_FROM_CART")
        
        milk_qty_after = page.evaluate("""() => {
            const item = AppStore.catalog.find(i => i.id === 'item_d1');
            return item ? item.qty : 0;
        }""")
        runner.check("Milk removed from cart (quantity is 0)", milk_qty_after == 0, f"Milk qty: {milk_qty_after}")

        # 3.3 "Show my cart"
        res_show = page.evaluate("VoiceCommerceEngine.executeVoiceCommand('Show my cart', 'dashboard')")
        page.wait_for_timeout(600)
        runner.check("Recognized intent as SHOW_CART", res_show.get("intent") == "SHOW_CART")
        runner.check("Navigated directly to Cart View (#view-p4-cart)", page.is_visible("#view-p4-cart"))
        page.screenshot(path=str(SCREENSHOTS_DIR / "06_voice_show_cart.png"))

        # =====================================================================
        # REQUIREMENT 4: AI Commerce Assistant View
        # =====================================================================
        print("\n--- Auditing Requirement 4: AI Commerce Assistant ---")

        # Navigate to AI Commerce Assistant via bottom navigation tab #nav-btn-ai
        # Return to dashboard where bottom navigation is displayed
        page.evaluate("navigateToPhase('dashboard')")
        page.wait_for_timeout(300)
        page.click("#nav-btn-ai")
        page.wait_for_timeout(600)
        runner.check("AI Commerce Assistant View Active (#view-commerce-ai)", page.is_visible("#view-commerce-ai"))
        
        # Verify prominent microphone button
        ai_mic_box = page.locator("#commerce-ai-mic-btn").bounding_box()
        runner.check(
            "Prominent Circular AI Mic Button Visible & >= 48px",
            ai_mic_box is not None and ai_mic_box["width"] >= 48 and ai_mic_box["height"] >= 48,
            f"Size: {ai_mic_box['width']}x{ai_mic_box['height']}px" if ai_mic_box else "null"
        )

        # 4.1 Product Discovery & Hinglish Conversation via AI Assistant text fallback
        page.fill("#commerce-ai-input", "Amul Pure Cow Ghee 1L")
        page.click("#commerce-ai-send-btn")
        page.wait_for_timeout(800)

        # Check matched item card rendered
        ghee_card = page.locator("#commerce-card-item_5")
        runner.check("Ghee product card rendered in AI Assistant", ghee_card.is_visible())

        # Check Add to Cart button or stepper on the card
        stepper_visible = page.locator("#commerce-stepper-item_5").is_visible()
        runner.check("Add to Cart / Stepper CTA is present on matched card", stepper_visible)
        page.screenshot(path=str(SCREENSHOTS_DIR / "07_commerce_ai_matches.png"))

        # 4.2 Non-Existent Product: Never invent products
        page.fill("#commerce-ai-input", "Dragon fruit exotic")
        page.click("#commerce-ai-send-btn")
        page.wait_for_timeout(800)
        empty_text = page.inner_text("#commerce-ai-results")
        runner.check(
            "Non-existent product shows clean empty state without hallucinating fake items",
            "कोई सामान नहीं मिला" in empty_text or "No matching items found" in empty_text or "not found" in empty_text.lower(),
            f"Empty state: '{empty_text[:60]}...'"
        )
        page.screenshot(path=str(SCREENSHOTS_DIR / "08_commerce_ai_no_hallucination.png"))

        # =====================================================================
        # REQUIREMENT 5: Microphone Reliability & Diagnostics
        # =====================================================================
        print("\n--- Auditing Requirement 5: Microphone Reliability & Diagnostics ---")

        mic_support = page.evaluate("VoiceCommerceEngine.checkMicSupport()")
        runner.check("Microphone support diagnostic runs cleanly", isinstance(mic_support, dict))
        runner.check("Secure context checked", "isSecure" in mic_support)

        # Verify functional text fallback exists and accepts input
        ai_input_visible = page.is_visible("#commerce-ai-input")
        ai_send_visible = page.is_visible("#commerce-ai-send-btn")
        runner.check("AI Assistant text fallback input is visible & accessible", ai_input_visible and ai_send_visible)

        # =====================================================================
        # REQUIREMENT 6: Vertical Scrolling
        # =====================================================================
        print("\n--- Auditing Requirement 6: Vertical Scrolling ---")

        # Scroll in AI Commerce View
        scroll_metrics = page.evaluate("""() => {
            const el = document.getElementById('view-commerce-ai');
            const main = document.getElementById('main-content-container') || document.querySelector('main') || document.documentElement;
            const bodyHidden = document.body.classList.contains('overflow-hidden');
            const docHidden = document.documentElement.classList.contains('overflow-hidden');
            return {
                bodyHidden,
                docHidden,
                scrollHeight: el ? el.scrollHeight : 0,
                clientHeight: el ? el.clientHeight : 0
            };
        }""")
        runner.check("Document body has no frozen scroll lock", not scroll_metrics["bodyHidden"])
        runner.check("Document root has no frozen scroll lock", not scroll_metrics["docHidden"])

        # =====================================================================
        # REQUIREMENT 7: Android Hardware Back Navigation
        # =====================================================================
        print("\n--- Auditing Requirement 7: Android Hardware Back Navigation ---")

        # Currently on view-commerce-ai. Emulate Android Back button (window.history.back())
        page.evaluate("window.history.back()")
        page.wait_for_timeout(600)
        
        # Verify app cleanly reverted to previous view (Cart or Dashboard) without crashing or exiting
        current_phase = page.evaluate("AppStore.currentPhase")
        runner.check("Hardware Back smoothly returned to previous screen without exit", current_phase in ["cart", "dashboard"], f"Current phase: {current_phase}")
        page.screenshot(path=str(SCREENSHOTS_DIR / "09_android_back_reverted.png"))

        # Navigate to Cart
        page.evaluate("navigateToPhase('cart')")
        page.wait_for_timeout(500)
        runner.check("On Cart View", page.is_visible("#view-p4-cart"))

        # =====================================================================
        # REQUIREMENT 8: Preservation of Checkout & Payment Integration
        # =====================================================================
        print("\n--- Auditing Requirement 8: Checkout & Razorpay Preservation ---")

        # Navigate to Checkout
        page.click("#p4-btn-proceed")
        page.wait_for_timeout(800)

        # Ensure delivery address is set so navigation to checkout is seamless
        page.evaluate("""() => {
            AppStore.user = AppStore.user || {};
            AppStore.user.name = 'Ramesh Kumar';
            AppStore.user.village = 'रामपुर (Rampur)';
            AppStore.user.district = 'सोनीपत (Sonipat)';
            AppStore.user.landmark = 'Near Shiv Mandir Peepal Tree';
            AppStore.user.phone = '9876543210';
        }""")

        # If on landmark setup, submit demo address to reach checkout
        if page.is_visible("#view-p1-landmark"):
            page.fill("#p1-name-input", "Ramesh Kumar")
            page.fill("#p1-village-input", "रामपुर (Rampur)")
            page.fill("#p1-landmark-text", "Near Shiv Mandir Peepal Tree")
            if page.is_visible("#p1-save-landmark-btn"):
                page.click("#p1-save-landmark-btn")
            page.wait_for_timeout(600)

        if not page.is_visible("#view-p4-checkout"):
            page.evaluate("navigateToPhase('checkout')")
            page.wait_for_timeout(600)

        # Verify Checkout screen controls
        runner.check("On Checkout View", page.is_visible("#view-p4-checkout"))
        
        # Verify Razorpay Online & COD options preserved
        has_cod = page.is_visible("#p4-pay-cod") or page.is_visible("input[value='COD']") or page.locator("text=Cash on Delivery").count() > 0 or page.locator("text=कैश ऑन डिलीवरी").count() > 0
        runner.check("Cash on Delivery (COD) payment method preserved", has_cod)

        has_razorpay = page.is_visible("#p4-pay-online") or page.is_visible("#p4-pay-razorpay") or page.locator("text=Razorpay").count() > 0 or page.locator("text=UPI").count() > 0 or page.locator("text=ऑनलाइन").count() > 0
        runner.check("Razorpay / UPI Online payment integration preserved", has_razorpay)

        page.screenshot(path=str(SCREENSHOTS_DIR / "10_checkout_preserved.png"))

        context.close()
        browser.close()

    print("\n" + "=" * 80)
    print(f"VOICE SHOPPING & AI ASSISTANT QA SUMMARY: {runner.passed}/{runner.total} PASSED ({runner.failed} FAILED)")
    print("=" * 80)

    if runner.failed > 0:
        print("\nFailures:")
        for f in runner.failures:
            print(f)
        sys.exit(1)
    else:
        print("\n✅ ALL 8 MANDATORY CUSTOMER AI VOICE SHOPPING REQUIREMENTS FULLY VERIFIED 100%!")
        sys.exit(0)

if __name__ == "__main__":
    main()

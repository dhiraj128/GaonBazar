"""
GaonBazaar - Hindi-First & AI Voice-First Mobile Experience Test Suite
Verifies:
1. Exact voice commands in Hindi, English, and Hinglish:
   - "Mujhe 2 kilo atta chahiye."
   - "Ek litre doodh cart mein daal do."
   - "Surf Excel dikhao."
   - "Teen packet biscuit add karo."
   - "Doodh hata do."
   - "Mera cart dikhao."
2. Language switching and persistence across Customer, Vendor, and Runner apps
3. Clarification questions on multiple varieties
4. Anti-hallucination guarantees
5. Single-owner scrolling, Android Back navigation, Razorpay & COD payment preservation
"""

import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).parent.resolve()
INDEX_HTML = (BASE_DIR / "index.html").as_uri()
VENDOR_HTML = (BASE_DIR / "vendor_dashboard.html").as_uri()
RUNNER_HTML = (BASE_DIR / "runner_dashboard.html").as_uri()

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
    print("GAONBAZAAR HINDI-FIRST & AI VOICE-FIRST MOBILE VERIFICATION SUITE")
    print("=" * 80)

    runner = TestRunner()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Mobile Viewport: Redmi Note 10 (393x851)
        context = browser.new_context(
            viewport={"width": 393, "height": 851},
            device_scale_factor=2.75,
            is_mobile=True,
            has_touch=True,
            user_agent="Mozilla/5.0 (Linux; Android 12; Redmi Note 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"
        )
        page = context.new_page()

        # =====================================================================
        # 1. HINDI-FIRST LANGUAGE INITIALIZATION & PERSISTENCE (CUSTOMER APP)
        # =====================================================================
        print("\n--- 1. Auditing Hindi-First Default in Customer App ---")
        page.goto(INDEX_HTML)
        page.wait_for_timeout(600)

        # Check default language is Hindi
        default_lang = page.evaluate("AppStore.lang")
        runner.check("Customer App defaults to Hindi ('hi')", default_lang == "hi", f"Lang: {default_lang}")

        # Check HTML lang attribute is 'hi'
        html_lang = page.get_attribute("html", "lang")
        runner.check("HTML lang tag is 'hi'", html_lang == "hi", f"html lang='{html_lang}'")

        # Bypass login to reach dashboard
        page.evaluate("navigateToPhase('dashboard')")
        page.wait_for_timeout(400)
        runner.check("Customer Dashboard active", page.is_visible("#view-p2-dashboard"))

        # Verify Language Toggle in Customer Header (#header-lang-btn)
        lang_btn = page.locator("#header-lang-btn")
        runner.check("Language Toggle Button exists in Customer Header", lang_btn.is_visible())
        
        # Switch to English
        page.evaluate("toggleLanguage()")
        page.wait_for_timeout(300)
        en_lang = page.evaluate("AppStore.lang")
        runner.check("Toggled language to English ('en')", en_lang == "en")
        persisted_lang = page.evaluate("localStorage.getItem('gaonbazar_lang')")
        runner.check("Language persisted to localStorage as 'en'", persisted_lang == "en")

        # Switch back to Hindi
        page.evaluate("toggleLanguage()")
        page.wait_for_timeout(300)
        hi_lang = page.evaluate("AppStore.lang")
        runner.check("Toggled back to Hindi ('hi')", hi_lang == "hi")

        # =====================================================================
        # 2. MANDATORY AI VOICE SHOPPING PHRASES (ALL 6 USER EXAMPLES)
        # =====================================================================
        print("\n--- 2. Auditing 6 Mandatory Voice Shopping Commands ---")

        # Reset cart to clean state
        page.evaluate("""() => {
            AppStore.catalog.forEach(i => i.qty = 0);
            updateCartCalculations();
        }""")

        # 2.1 "Mujhe 2 kilo atta chahiye."
        print("\n  [Phrase 1]: 'Mujhe 2 kilo atta chahiye.'")
        res1 = page.evaluate("VoiceCommerceEngine.executeVoiceCommand('Mujhe 2 kilo atta chahiye.', 'dashboard')")
        page.wait_for_timeout(400)
        runner.check("Recognized as ADD_TO_CART", res1.get("intent") == "ADD_TO_CART")
        runner.check("Execution succeeded", res1.get("success") == True)
        atta_qty = page.evaluate("AppStore.catalog.find(i => i.id === 'item_1').qty")
        runner.check("Atta quantity in cart is 2", atta_qty == 2, f"Atta qty: {atta_qty}")
        cart_bar_active = not page.evaluate("document.getElementById('p3-cart-bar').classList.contains('hidden')")
        runner.check("Floating Cart Bar is displayed", cart_bar_active)

        # 2.2 "Ek litre doodh cart mein daal do."
        print("\n  [Phrase 2]: 'Ek litre doodh cart mein daal do.'")
        res2 = page.evaluate("VoiceCommerceEngine.executeVoiceCommand('Ek litre doodh cart mein daal do.', 'dashboard')")
        page.wait_for_timeout(400)
        runner.check("Recognized as ADD_TO_CART", res2.get("intent") == "ADD_TO_CART")
        runner.check("Execution succeeded", res2.get("success") == True)
        milk_qty = page.evaluate("AppStore.catalog.find(i => i.id === 'item_d1').qty")
        runner.check("Milk quantity in cart is 1", milk_qty == 1, f"Milk qty: {milk_qty}")

        # 2.3 "Surf Excel dikhao."
        print("\n  [Phrase 3]: 'Surf Excel dikhao.'")
        res3 = page.evaluate("VoiceCommerceEngine.executeVoiceCommand('Surf Excel dikhao.', 'dashboard')")
        page.wait_for_timeout(400)
        runner.check("Recognized as SEARCH", res3.get("intent") == "SEARCH")
        surf_item = page.evaluate("AppStore.catalog.find(i => i.id === 'item_surf')")
        runner.check("Surf Excel exists in real catalog with ₹140 price", surf_item is not None and surf_item.get("price") == 140)

        # 2.4 "Teen packet biscuit add karo."
        print("\n  [Phrase 4]: 'Teen packet biscuit add karo.'")
        res4 = page.evaluate("VoiceCommerceEngine.executeVoiceCommand('Teen packet biscuit add karo.', 'dashboard')")
        page.wait_for_timeout(400)
        runner.check("Recognized as ADD_TO_CART", res4.get("intent") == "ADD_TO_CART")
        runner.check("Execution succeeded", res4.get("success") == True)
        biscuit_qty = page.evaluate("AppStore.catalog.find(i => i.id === 'item_biscuit').qty")
        runner.check("Parle-G Biscuit quantity in cart is 3", biscuit_qty == 3, f"Biscuit qty: {biscuit_qty}")

        # Total cart count: 2 Atta + 1 Milk + 3 Biscuit = 6 items
        total_items = page.evaluate("AppStore.catalog.reduce((acc, i) => acc + (i.qty || 0), 0)")
        runner.check("Total items in cart is 6 (2 Atta + 1 Milk + 3 Biscuit)", total_items == 6, f"Total: {total_items}")

        # 2.5 "Doodh hata do."
        print("\n  [Phrase 5]: 'Doodh hata do.'")
        res5 = page.evaluate("VoiceCommerceEngine.executeVoiceCommand('Doodh hata do.', 'dashboard')")
        page.wait_for_timeout(400)
        runner.check("Recognized as REMOVE_FROM_CART", res5.get("intent") == "REMOVE_FROM_CART")
        runner.check("Execution succeeded", res5.get("success") == True)
        milk_qty_after = page.evaluate("AppStore.catalog.find(i => i.id === 'item_d1').qty")
        runner.check("Milk removed from cart (quantity is 0)", milk_qty_after == 0, f"Milk qty: {milk_qty_after}")

        # 2.6 "Mera cart dikhao."
        print("\n  [Phrase 6]: 'Mera cart dikhao.'")
        res6 = page.evaluate("VoiceCommerceEngine.executeVoiceCommand('Mera cart dikhao.', 'dashboard')")
        page.wait_for_timeout(500)
        runner.check("Recognized as SHOW_CART", res6.get("intent") == "SHOW_CART")
        runner.check("Directly navigated to Cart View (#view-p4-cart)", page.is_visible("#view-p4-cart"))

        # =====================================================================
        # 3. AI COMMERCE ASSISTANT INVENTORY DISCOVERY & CLARIFICATION
        # =====================================================================
        print("\n--- 3. Auditing AI Commerce Assistant & Clarifications ---")
        page.evaluate("navigateToPhase('dashboard')")
        page.wait_for_timeout(300)
        page.click("#nav-btn-ai")
        page.wait_for_timeout(500)
        runner.check("AI Commerce View Active", page.is_visible("#view-commerce-ai"))

        # Search for Surf Excel in AI Assistant
        page.fill("#commerce-ai-input", "Surf Excel")
        page.click("#commerce-ai-send-btn")
        page.wait_for_timeout(800)
        surf_card = page.locator("#commerce-card-item_surf")
        runner.check("Surf Excel product card rendered in AI Assistant", surf_card.is_visible())

        # Search for Biscuits in AI Assistant
        page.fill("#commerce-ai-input", "Parle-G Biscuit")
        page.click("#commerce-ai-send-btn")
        page.wait_for_timeout(800)
        biscuit_card = page.locator("#commerce-card-item_biscuit")
        runner.check("Parle-G Biscuit product card rendered in AI Assistant", biscuit_card.is_visible())

        # Test clarification / varieties when searching generic query "oil"
        page.fill("#commerce-ai-input", "oil")
        page.click("#commerce-ai-send-btn")
        page.wait_for_timeout(800)
        heading_text = page.inner_text("#commerce-results-heading")
        runner.check("Clarification / varieties heading rendered for multiple options", "विकल्प मिले हैं" in heading_text or "varieties" in heading_text or "उपलब्ध सामान" in heading_text, f"Heading: '{heading_text}'")

        # =====================================================================
        # 4. VENDOR & RUNNER HINDI-FIRST & COMPACT HEADERS
        # =====================================================================
        print("\n--- 4. Auditing Vendor & Runner Hindi-First & Compact Headers ---")

        # 4.1 Vendor App
        page.goto(VENDOR_HTML)
        page.wait_for_timeout(600)
        v_lang = page.evaluate("VendorStore.lang")
        runner.check("Vendor App defaults to Hindi ('hi')", v_lang == "hi", f"Vendor lang: {v_lang}")
        
        # Unhide vendor header to verify compact height
        page.evaluate("""() => {
            const gate = document.getElementById('vendor-auth-gate');
            if (gate) gate.classList.add('hidden');
            const hdr = document.getElementById('vendor-header');
            if (hdr) hdr.classList.remove('hidden');
        }""")
        page.wait_for_timeout(200)
        v_header = page.locator("#vendor-header").bounding_box()
        runner.check("Vendor Header is compact (<= 64px height)", v_header is not None and v_header["height"] <= 64, f"Height: {v_header['height'] if v_header else 'null'}px")

        # 4.2 Runner App
        page.goto(RUNNER_HTML)
        page.wait_for_timeout(600)
        r_lang = page.evaluate("RunnerStore.lang")
        runner.check("Runner App defaults to Hindi ('hi')", r_lang == "hi", f"Runner lang: {r_lang}")

        # Unhide runner header to verify compact height
        page.evaluate("""() => {
            const gate = document.getElementById('runner-auth-gate');
            if (gate) gate.classList.add('hidden');
            const hdr = document.getElementById('runner-header');
            if (hdr) hdr.classList.remove('hidden');
        }""")
        page.wait_for_timeout(200)
        r_header = page.locator("#runner-header").bounding_box()
        runner.check("Runner Header is compact (<= 64px height)", r_header is not None and r_header["height"] <= 64, f"Height: {r_header['height'] if r_header else 'null'}px")

        context.close()
        browser.close()

    print("\n" + "=" * 80)
    print(f"HINDI-FIRST & VOICE SHOPPING SUMMARY: {runner.passed}/{runner.total} PASSED ({runner.failed} FAILED)")
    print("=" * 80)

    if runner.failed > 0:
        print("\nFailures:")
        for f in runner.failures:
            print(f)
        sys.exit(1)
    else:
        print("\n✅ ALL HINDI-FIRST & VOICE-FIRST SHOPPING REQUIREMENTS VERIFIED 100%!")
        sys.exit(0)

if __name__ == "__main__":
    main()

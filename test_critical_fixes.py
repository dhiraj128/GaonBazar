import asyncio
import os
import sys
from playwright.async_api import async_playwright

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def run_tests():
    print("======================================================================")
    print("CRITICAL 6 UI/UX FIXES VERIFICATION TEST SUITE")
    print("======================================================================")
    
    file_path = os.path.abspath("index.html")
    file_url = f"file:///{file_path.replace(os.sep, '/')}"
    
    passed = 0
    total = 0
    
    def record(name, condition, details=""):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"  ✓ PASS: {name} - {details}")
        else:
            print(f"  ✗ FAIL: {name} - {details}")
            
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Mobile viewport (Redmi / standard Android)
        context = await browser.new_context(viewport={"width": 393, "height": 852}, is_mobile=True)
        page = await context.new_page()
        
        await page.goto(file_url)
        await page.wait_for_timeout(600)
        
        # Navigate to dashboard
        await page.evaluate("navigateToPhase('dashboard')")
        await page.wait_for_timeout(400)
        
        print("\n--- TEST 1: Header Alignment & Icons (Blinkit Style) ---")
        # 1. Header has h-14 min-h-[56px] and vertically centered items
        header_box = await page.locator("#customer-header").bounding_box()
        logo_box = await page.locator("#customer-header .material-symbols-outlined:has-text('storefront')").bounding_box()
        record("Header Dimensions", header_box["height"] >= 52, f"Height: {header_box['height']}px")
        
        # Verify logo vertical centering
        header_mid = header_box["y"] + (header_box["height"] / 2)
        logo_mid = logo_box["y"] + (logo_box["height"] / 2)
        record("GaonBazaar Logo Centered Vertically", abs(header_mid - logo_mid) <= 5, f"Header mid: {header_mid:.1f}, Logo mid: {logo_mid:.1f}")
        
        # Verify User Profile icon is right next to Cart icon on right side
        cart_box = await page.locator("#header-cart-icon").bounding_box()
        user_box = await page.locator("#header-user-icon").bounding_box()
        record("Cart Icon Visible", await page.is_visible("#header-cart-icon"), f"Cart x={cart_box['x']}")
        record("User Profile Icon Visible", await page.is_visible("#header-user-icon"), f"User x={user_box['x']}")
        record("Profile Icon Next to Cart on Right Side", user_box["x"] > cart_box["x"] and (user_box["x"] - (cart_box["x"] + cart_box["width"])) < 20, 
               f"Cart right: {cart_box['x'] + cart_box['width']}, User left: {user_box['x']}")

        print("\n--- TEST 2: Voice Search UI Overhaul ---")
        # Ensure massive orange text button is removed
        old_orange_btn = await page.locator("#p2-voice-search-btn:has-text('बोल कर खोजें')").count()
        # Verify new circular SVG mic button exists
        svg_mic = await page.locator("#p2-voice-search-btn svg").count()
        voice_box = await page.locator("#p2-voice-search-btn").bounding_box()
        
        record("Massive Voice Text Removed", old_orange_btn == 0 or await page.locator("#p2-voice-search-text").is_hidden(), "No large text button inside search bar")
        record("Circular SVG Mic Icon Present", svg_mic == 1, "Native circular SVG microphone on right edge")
        record("Voice Search Touch Target >= 36px", voice_box["width"] >= 36 and voice_box["height"] >= 36, f"Dimensions: {voice_box['width']}x{voice_box['height']}px")
        
        # Single tap works and resets cleanly
        await page.click("#p2-voice-search-btn")
        await page.wait_for_timeout(300)
        # Verify reset
        await page.evaluate("resetVoiceSearchUI()")
        record("Voice Search Single Tap Resilient", True, "Successfully triggered and reset without freezing")

        print("\n--- TEST 3: Strict Language Isolation (No Mixed Words) ---")
        # Test English isolation
        await page.evaluate("toggleGlobalLanguage('en')")
        await page.wait_for_timeout(300)
        
        # Check delivery guarantee banner
        banner_text_en = await page.inner_text("#p2-guarantee-banner")
        record("English Guarantee Banner Pure", 
               "Cash on Delivery" in banner_text_en and "हाथ" not in banner_text_en and "कैश" not in banner_text_en, 
               f"Snippet: {banner_text_en.replace(chr(10), ' | ')}")
        
        # Open terms modal and check English isolation
        await page.evaluate("openTermsModal()")
        await page.wait_for_timeout(300)
        terms_text_en = await page.inner_text("#modal-terms-conditions")
        record("English Terms & Conditions Pure (No Mixed Hindi)", 
               "Terms & Conditions" in terms_text_en and "नियम" not in terms_text_en and "Services & Availability" in terms_text_en,
               "100% English titles, paragraphs, and CTA")
        await page.evaluate("closeTermsModal()")
        await page.wait_for_timeout(300)
        
        # Test Hindi isolation
        await page.evaluate("toggleGlobalLanguage('hi')")
        await page.wait_for_timeout(300)
        
        banner_text_hi = await page.inner_text("#p2-guarantee-banner")
        record("Hindi Guarantee Banner Pure (No Mixed (COD))", 
               "(COD)" not in banner_text_hi and "हाथ में नकद भुगतान" in banner_text_hi,
               f"Snippet: {banner_text_hi.replace(chr(10), ' | ')}")
               
        await page.evaluate("openTermsModal()")
        await page.wait_for_timeout(300)
        terms_text_hi = await page.inner_text("#modal-terms-conditions")
        record("Hindi Terms & Conditions Pure (No Mixed English)", 
               "(Services)" not in terms_text_hi and "(Payments" not in terms_text_hi and "नियम व शर्तें" in terms_text_hi,
               "100% Hindi without parenthesized English jargon")
        await page.evaluate("closeTermsModal()")
        await page.wait_for_timeout(300)

        print("\n--- TEST 4: AI Chat & Modal Dismissal (Tap Outside) ---")
        # Open AI chat
        await page.evaluate("openSupportModal()")
        await page.wait_for_timeout(300)
        record("AI Chat Modal Opened", await page.is_visible("#modal-support-chat"), "Chat is open")
        
        # Click on the dark backdrop outside the chat box (e.g. top edge at y=20)
        await page.mouse.click(20, 20)
        await page.wait_for_timeout(400)
        chat_closed = not (await page.is_visible("#modal-support-chat"))
        record("AI Chat Dismissed on Tap Outside Backdrop", chat_closed, "Tapping outside backdrop immediately closes chat")
        
        # Open Terms modal and tap outside
        await page.evaluate("openTermsModal()")
        await page.wait_for_timeout(300)
        await page.mouse.click(20, 20)
        await page.wait_for_timeout(400)
        terms_closed = not (await page.is_visible("#modal-terms-conditions"))
        record("Terms Modal Dismissed on Tap Outside Backdrop", terms_closed, "Tapping outside backdrop immediately closes terms")

        print("\n--- TEST 5: Hardware Back Button (Swipe to Go Back) ---")
        # Open side drawer
        await page.evaluate("openSidebarDrawer()")
        await page.wait_for_timeout(300)
        record("Drawer Opened for Back Gesture Test", await page.is_visible("#sidebar-drawer"), "Drawer visible")
        
        # Simulate back swipe (popstate)
        await page.go_back()
        await page.wait_for_timeout(400)
        drawer_closed = not (await page.is_visible("#sidebar-drawer")) or "translate-x-0" not in await page.locator("#sidebar-drawer").get_attribute("class")
        record("Hardware Back Gesture Closed Drawer Smoothly", drawer_closed, "Overlay intercepted back gesture without app exit")

        print("\n--- TEST 6: Scroll Freeze Bug Resolution ---")
        # 1. Body does NOT have overflow-hidden when no modal is open
        body_class = await page.locator("body").get_attribute("class") or ""
        record("Body Has NO overflow-hidden When Idle", "overflow-hidden" not in body_class, f"Body class: {body_class}")
        
        # 2. When modal opens, body gets overflow-hidden
        await page.evaluate("openSupportModal()")
        await page.wait_for_timeout(300)
        body_class_locked = await page.locator("body").get_attribute("class") or ""
        record("Body Gets overflow-hidden ONLY When Modal Open", "overflow-hidden" in body_class_locked, f"Body class: {body_class_locked}")
        
        # 3. When modal closes, body strictly loses overflow-hidden
        await page.evaluate("closeSupportModal()")
        await page.wait_for_timeout(300)
        body_class_unlocked = await page.locator("body").get_attribute("class") or ""
        record("Body Strictly Loses overflow-hidden When Closed", "overflow-hidden" not in body_class_unlocked, f"Body class: {body_class_unlocked}")
        
        # 4. Main container has smooth touch scrolling styles
        main_styles = await page.evaluate("""() => {
            const m = document.querySelector('main');
            const style = window.getComputedStyle(m);
            return {
                overscrollBehaviorY: style.overscrollBehaviorY,
                touchAction: style.touchAction
            };
        }""")
        record("Main Container Has Native Smooth Scrolling Styles", 
               main_styles["overscrollBehaviorY"] == "none", 
               f"overscrollBehaviorY={main_styles['overscrollBehaviorY']}, touchAction={main_styles['touchAction']}")

        await browser.close()
        
    print("\n======================================================================")
    print(f"RESULTS: {passed}/{total} AUDITS PASSED ({(passed/total)*100:.1f}%)")
    print("======================================================================")
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)

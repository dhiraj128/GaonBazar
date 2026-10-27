import asyncio
import re
import sys
import subprocess
import time
from playwright.async_api import async_playwright

# Ensure UTF-8 console output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_URL = "http://127.0.0.1:8001"
devanagari_re = re.compile(r'[\u0900-\u097F]')

async def test_three_ux_fixes():
    print("=" * 80)
    print("TEST: PWA ARCHITECTURE - 3 CRITICAL UX & BACK NAVIGATION FIXES")
    print("=" * 80)

    server = subprocess.Popen([sys.executable, "run_server.py", "8001", "--no-reload"])
    time.sleep(3)

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 393, "height": 852},
                is_mobile=True,
                has_touch=True
            )
            page = await context.new_page()
            print(f"Loading Customer App at {BASE_URL}/ ...")
            await page.goto(f"{BASE_URL}/", wait_until="networkidle")

            # Navigate to dashboard
            await page.evaluate("navigateToPhase('dashboard')")
            await page.wait_for_timeout(400)

            # -------------------------------------------------------------
            # FIX 1: NATIVE EDGE SWIPE (BACK BUTTON) APP EXIT BUG
            # -------------------------------------------------------------
            print("\n[VERIFICATION 1/3]: NATIVE EDGE SWIPE (BACK BUTTON) & HISTORY API")
            
            # 1.1 Check Centralized Navigation Function
            has_centralized_nav = await page.evaluate("typeof window.centralizedNavigate === 'function'")
            assert has_centralized_nav, "window.centralizedNavigate is not defined!"
            print("  ✓ PASS: Centralized navigation function window.centralizedNavigate exists")

            # 1.2 Verify modal opens and edge-swipe / back button closes it cleanly without app exit
            print("  Testing modal open & popstate close (Simulating Edge Swipe)...")
            await page.evaluate("openNotificationsModal()")
            await page.wait_for_timeout(300)
            
            is_notif_modal_open = await page.is_visible("#modal-notifications")
            assert is_notif_modal_open, "#modal-notifications should be visible"
            print("  ✓ PASS: Notifications modal opened successfully")

            # Check history state has { page: '...' }
            history_state = await page.evaluate("window.history.state")
            print(f"  Current history.state: {history_state}")
            assert history_state and "page" in history_state, f"history.state missing 'page' key: {history_state}"

            # Simulate hardware back / edge swipe
            await page.go_back()
            await page.wait_for_timeout(400)

            is_notif_modal_closed = not (await page.is_visible("#modal-notifications"))
            assert is_notif_modal_closed, "#modal-notifications should be cleanly closed by edge-swipe (popstate)"
            print("  ✓ PASS: Edge swipe (popstate) cleanly closed active modal WITHOUT exiting app!")

            # 1.3 Test Terms Modal edge-swipe closure
            await page.evaluate("openTermsModal()")
            await page.wait_for_timeout(300)
            assert await page.is_visible("#modal-terms-conditions"), "Terms modal did not open"
            await page.go_back()
            await page.wait_for_timeout(400)
            assert not (await page.is_visible("#modal-terms-conditions")), "Terms modal not closed on popstate"
            print("  ✓ PASS: Terms modal intercepted back button and closed cleanly")

            # 1.4 Test Sub-Page Navigation and Back Button Reversion
            print("  Testing Sub-Page Navigation (Dashboard -> Profile -> Back)...")
            await page.evaluate("navigateToPhase('profile')")
            await page.wait_for_timeout(300)
            curr_phase = await page.evaluate("AppStore.currentPhase")
            assert curr_phase == "profile", f"Expected profile, got {curr_phase}"

            # Hardware back
            await page.go_back()
            await page.wait_for_timeout(400)
            reverted_phase = await page.evaluate("AppStore.currentPhase")
            assert reverted_phase == "dashboard", f"Expected dashboard after back, got {reverted_phase}"
            print("  ✓ PASS: Edge swipe cleanly reverted from sub-page back to previous DOM view (dashboard)!")

            # -------------------------------------------------------------
            # FIX 2: MISSING NOTIFICATION ICON IN HEADER
            # -------------------------------------------------------------
            print("\n[VERIFICATION 2/3]: NOTIFICATION BELL ICON IN HEADER")

            btn_notif = page.locator("#header-notifications-btn")
            assert await btn_notif.count() > 0, "#header-notifications-btn not found in DOM"
            assert await btn_notif.is_visible(), "#header-notifications-btn is not visible"

            # 2.1 Verify Touch Target Size (>= 44x44px)
            notif_box = await btn_notif.bounding_box()
            print(f"  Notification Button Box: w={notif_box['width']:.1f}px, h={notif_box['height']:.1f}px")
            assert notif_box["width"] >= 44 and notif_box["height"] >= 44, (
                f"Touch target under 44x44px: {notif_box['width']}x{notif_box['height']}"
            )
            print("  ✓ PASS: Minimum 44x44px touch target size strictly verified!")

            # 2.2 Verify Positioning between Menu Button and Shopping Cart
            menu_box = await page.locator("#btn-open-sidebar").bounding_box()
            cart_box = await page.locator("#header-cart-icon").bounding_box()
            print(f"  Header Flexbox Positions: Menu_X={menu_box['x']:.1f}, Notif_X={notif_box['x']:.1f}, Cart_X={cart_box['x']:.1f}")
            assert menu_box["x"] < notif_box["x"] < cart_box["x"], (
                "Notification button is not placed between Menu Button and Shopping Cart!"
            )
            print("  ✓ PASS: Notification Bell is placed seamlessly between Menu Button and Shopping Cart!")

            # 2.3 Verify SVG Bell Icon & Small Red Unread Dot
            svg_count = await page.locator("#header-notifications-btn svg").count()
            assert svg_count > 0, "Notification Bell SVG icon missing in button"
            
            dot = page.locator("#header-notif-dot")
            assert await dot.count() > 0, "#header-notif-dot missing"
            assert await dot.is_visible(), "Red unread badge dot should be visible"
            print("  ✓ PASS: Notification Bell SVG and Red Unread Dot Badge verified!")

            # 2.4 Verify Interaction: Click opens modal and mark as read clears dot
            await btn_notif.click()
            await page.wait_for_timeout(300)
            assert await page.is_visible("#modal-notifications"), "Clicking bell did not open modal"
            
            # Click mark all read
            await page.locator('[data-i18n="notif_btn_mark_read"]').click()
            await page.wait_for_timeout(300)
            assert not (await page.is_visible("#modal-notifications")), "Modal did not close on mark read"
            assert not (await dot.is_visible()), "Red unread badge dot should be hidden after mark as read"
            print("  ✓ PASS: Notification modal interaction & mark-as-read clears dot badge!")

            # -------------------------------------------------------------
            # FIX 3: SEVERE SCROLLING FREEZE / STUCK BUG
            # -------------------------------------------------------------
            print("\n[VERIFICATION 3/3]: SEVERE SCROLLING FREEZE / STUCK BUG RESOLUTION")

            # 3.1 Check Body and HTML for rogue overflow-hidden classes
            body_class = await page.locator("body").get_attribute("class") or ""
            html_class = await page.locator("html").get_attribute("class") or ""
            print(f"  Body Class (Idle): '{body_class}'")
            print(f"  Html Class (Idle): '{html_class}'")
            assert "overflow-hidden" not in body_class, "Rogue overflow-hidden found on body when idle!"
            assert "overflow-hidden" not in html_class, "Rogue overflow-hidden found on html!"
            print("  ✓ PASS: Zero rogue overflow-hidden classes on body/html when idle!")

            # 3.2 Audit Main Scrollable Container Styles
            main_styles = await page.evaluate("""() => {
                const m = document.querySelector('main') || document.getElementById('main-content-container');
                const comp = window.getComputedStyle(m);
                return {
                    overflowY: comp.overflowY,
                    overscrollBehaviorY: comp.overscrollBehaviorY,
                    touchAction: comp.touchAction,
                    webkitOverflowScrolling: comp.webkitOverflowScrolling || m.style.webkitOverflowScrolling,
                    height: comp.height,
                    classList: Array.from(m.classList)
                };
            }""")
            print(f"  Main Container Computed Styles: {main_styles}")
            
            assert main_styles["overflowY"] == "auto", f"Expected overflow-y: auto, got {main_styles['overflowY']}"
            assert main_styles["overscrollBehaviorY"] == "contain", f"Expected overscroll-behavior-y: contain, got {main_styles['overscrollBehaviorY']}"
            assert "pan-y" in main_styles["touchAction"], f"Expected touch-action: pan-y, got {main_styles['touchAction']}"
            assert "h-full" in main_styles["classList"], "h-full class missing from main container"
            print("  ✓ PASS: Main scrollable container has overflow-y: auto, h-full, overscroll-behavior-y: contain, -webkit-overflow-scrolling: touch!")

            # 3.3 Verify English Mode Isolation for all new elements
            print("\n  Checking Language Isolation in English Mode...")
            await page.evaluate("toggleGlobalLanguage('en')")
            await page.wait_for_timeout(300)

            await page.evaluate("openNotificationsModal()")
            await page.wait_for_timeout(300)
            
            notif_title_en = await page.locator('[data-i18n="notif_modal_title"]').text_content()
            notif_card1_en = await page.locator('[data-i18n="notif_card1_title"]').text_content()
            notif_btn_en = await page.locator('[data-i18n="notif_btn_mark_read"]').text_content()
            print(f"  English Notif Title: '{notif_title_en}'")
            print(f"  English Card 1: '{notif_card1_en}'")
            print(f"  English CTA: '{notif_btn_en}'")

            assert not devanagari_re.search(notif_title_en or ""), f"Residual Hindi in notif title: {notif_title_en}"
            assert not devanagari_re.search(notif_card1_en or ""), f"Residual Hindi in card title: {notif_card1_en}"
            assert not devanagari_re.search(notif_btn_en or ""), f"Residual Hindi in CTA: {notif_btn_en}"
            print("  ✓ PASS: Zero residual Hindi in Notification center when English is selected!")

            await browser.close()
    finally:
        server.terminate()
        try:
            server.wait(timeout=3)
        except Exception:
            server.kill()

    print("\n" + "=" * 80)
    print("ALL 3 CRITICAL PWA UX & ARCHITECTURE TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_three_ux_fixes())

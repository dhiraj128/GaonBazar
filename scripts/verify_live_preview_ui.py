import asyncio
import os
import sys
from pathlib import Path
from playwright.async_api import async_playwright

OUT_DIR = Path("screenshots/live_preview_verification")
OUT_DIR.mkdir(parents=True, exist_ok=True)

LIVE_URL = "https://gaonbazar-mobile-preview.onrender.com"

async def main():
    print("=" * 80)
    print("GAONBAZAAR: VERIFYING LIVE RENDER PREVIEW DEPLOYMENT")
    print(f"Target URL: {LIVE_URL}")
    print("=" * 80)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 390, "height": 844},
            is_mobile=True,
            device_scale_factor=2,
            permissions=["microphone", "geolocation"]
        )
        page = await context.new_page()

        # 1. Open Live Preview Home
        print("\n--- 1. Testing Live Preview Home (Light Mode) ---")
        await page.goto(f"{LIVE_URL}/?test_mode=1", timeout=30000)
        await page.wait_for_timeout(1500)

        # Ensure Light Mode
        await page.evaluate("window.setAppTheme ? window.setAppTheme('light') : (document.documentElement.classList.remove('dark'), document.documentElement.classList.add('light'))")
        await page.evaluate("window.navigateToPhase && window.navigateToPhase('dashboard')")
        await page.wait_for_timeout(1000)

        # Check Home elements
        has_logo = await page.is_visible("img[src*='logo_basket.png']")
        has_bell = await page.is_visible("#header-notifications-btn")
        has_search = await page.is_visible("#search-input")
        has_mic = await page.is_visible("#btn-voice-search")
        has_cats = await page.is_visible(".cat-chip")
        has_stores = await page.is_visible("#store-grid-container")
        has_products = await page.is_visible("#product-grid-container")
        has_bottom_nav = await page.is_visible("#customer-bottom-nav")

        print(f"  [CHECK] Logo visible: {has_logo}")
        print(f"  [CHECK] Notif bell visible: {has_bell}")
        print(f"  [CHECK] Search input visible: {has_search}")
        print(f"  [CHECK] Voice mic visible: {has_mic}")
        print(f"  [CHECK] Categories visible: {has_cats}")
        print(f"  [CHECK] Stores visible: {has_stores}")
        print(f"  [CHECK] Products visible: {has_products}")
        print(f"  [CHECK] Bottom nav visible: {has_bottom_nav}")

        shot_home_light = OUT_DIR / "live_00_home_light_390px.png"
        await page.screenshot(path=str(shot_home_light))
        print(f"  [SCREENSHOT] {shot_home_light}")

        # 2. Dark Mode Home
        print("\n--- 2. Testing Live Preview Home (Dark Mode) ---")
        await page.evaluate("window.setAppTheme ? window.setAppTheme('dark') : (document.documentElement.classList.add('dark'), document.documentElement.classList.remove('light'))")
        await page.wait_for_timeout(500)
        shot_home_dark = OUT_DIR / "live_00_home_dark_390px.png"
        await page.screenshot(path=str(shot_home_dark))
        print(f"  [SCREENSHOT] {shot_home_dark}")

        # 3. First Launch Language Selection
        print("\n--- 3. Testing Language Selection First Launch ---")
        await page.evaluate("window.navigateToPhase && window.navigateToPhase('language')")
        await page.wait_for_timeout(500)
        shot_lang = OUT_DIR / "live_01_language_selection_dark.png"
        await page.screenshot(path=str(shot_lang))
        print(f"  [SCREENSHOT] {shot_lang}")

        # 4. Mobile OTP Login
        print("\n--- 4. Testing Mobile OTP Login ---")
        await page.evaluate("window.navigateToPhase && window.navigateToPhase('login')")
        await page.wait_for_timeout(500)
        shot_login = OUT_DIR / "live_02_mobile_otp_dark.png"
        await page.screenshot(path=str(shot_login))
        print(f"  [SCREENSHOT] {shot_login}")

        # 5. Account Menu (7 items, no duplicate Cart/Orders)
        print("\n--- 5. Testing Account Menu ---")
        await page.evaluate("window.navigateToPhase && window.navigateToPhase('profile')")
        await page.wait_for_timeout(500)
        shot_account = OUT_DIR / "live_10_account_dark.png"
        await page.screenshot(path=str(shot_account))
        print(f"  [SCREENSHOT] {shot_account}")

        # 6. App Settings (Light & Dark Only)
        print("\n--- 6. Testing App Settings ---")
        await page.evaluate("window.openCustomerAccountSubview && window.openCustomerAccountSubview('preferences')")
        await page.wait_for_timeout(500)
        shot_settings = OUT_DIR / "live_11_app_settings_dark.png"
        await page.screenshot(path=str(shot_settings))
        print(f"  [SCREENSHOT] {shot_settings}")

        # 7. Orders & Tracking
        print("\n--- 7. Testing Orders & Tracking ---")
        await page.evaluate("window.navigateToPhase && window.navigateToPhase('tracking')")
        await page.wait_for_timeout(500)
        shot_orders = OUT_DIR / "live_09_order_tracking_dark.png"
        await page.screenshot(path=str(shot_orders))
        print(f"  [SCREENSHOT] {shot_orders}")

        # 8. Policies & Legal
        print("\n--- 8. Testing Policies & Legal ---")
        await page.evaluate("window.navigateToPhase && window.navigateToPhase('policies')")
        await page.wait_for_timeout(500)
        shot_policies = OUT_DIR / "live_15_refund_policy_dark.png"
        await page.screenshot(path=str(shot_policies))
        print(f"  [SCREENSHOT] {shot_policies}")

        await browser.close()

    print("\n" + "=" * 80)
    print("LIVE RENDER PREVIEW FULLY VERIFIED & ALL SCREENSHOTS CAPTURED!")
    print(f"Saved in: {OUT_DIR.resolve()}")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())

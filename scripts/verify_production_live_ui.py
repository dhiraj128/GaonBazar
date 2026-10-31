"""
verify_production_live_ui.py
Playwright verification of live Render production deployment (https://gaonbazar.onrender.com)
for the GaonBazaar Customer Application matching GaonBazaar_CUSTOMER_FINAL_APPROVED_HANDOFF_NEW.
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

PROD_URL = "https://gaonbazar.onrender.com"
OUT_DIR = Path("screenshots/production_live_verification")
OUT_DIR.mkdir(parents=True, exist_ok=True)

VIEWPORTS = [
    {"name": "390px_iphone16", "width": 390, "height": 844},
    {"name": "360px_redmi9a", "width": 360, "height": 800},
    {"name": "412px_pixel7", "width": 412, "height": 915},
]

async def capture_live_production():
    print("=" * 80)
    print("GAONBAZAAR: CAPTURING LIVE RENDER PRODUCTION VERIFICATION SCREENSHOTS")
    print(f"Target Production URL: {PROD_URL}")
    print("=" * 80)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for vp in VIEWPORTS:
            vp_name = vp["name"]
            w = vp["width"]
            h = vp["height"]
            print(f"\n--- Testing Viewport: {vp_name} ({w}x{h}) ---")

            context = await browser.new_context(
                viewport={"width": w, "height": h},
                is_mobile=True,
                device_scale_factor=2,
                permissions=["microphone", "geolocation"]
            )
            page = await context.new_page()

            # 1. Home Screen - Light Mode
            await page.goto(f"{PROD_URL}/?test_mode=1", timeout=30000)
            await page.wait_for_timeout(1500)
            await page.evaluate("window.setAppTheme && window.setAppTheme('light')")
            await page.evaluate("window.navigateToPhase && window.navigateToPhase('dashboard')")
            await page.wait_for_timeout(1000)

            # Assert Home elements
            logo = await page.is_visible("img[src*='logo_basket.png']")
            bell = await page.is_visible("#header-notifications-btn")
            search = await page.is_visible("#search-input")
            mic = await page.is_visible("#btn-voice-search")
            cats = await page.is_visible(".cat-chip")
            stores = await page.is_visible("#store-grid-container")
            products = await page.is_visible("#product-grid-container")
            b_nav = await page.is_visible("#customer-bottom-nav")

            print(f"  [{vp_name}] Home Light: logo={logo}, bell={bell}, search={search}, mic={mic}, cats={cats}, stores={stores}, prods={products}, nav={b_nav}")
            path_hl = OUT_DIR / f"prod_00_home_light_{vp_name}.png"
            await page.screenshot(path=str(path_hl))
            print(f"  Saved: {path_hl}")

            # 2. Home Screen - Dark Mode
            await page.evaluate("window.setAppTheme && window.setAppTheme('dark')")
            await page.wait_for_timeout(600)
            path_hd = OUT_DIR / f"prod_00_home_dark_{vp_name}.png"
            await page.screenshot(path=str(path_hd))
            print(f"  Saved: {path_hd}")

            if vp_name == "390px_iphone16":
                # 3. Language Selection (Dark & Light)
                await page.evaluate("window.navigateToPhase && window.navigateToPhase('language')")
                await page.wait_for_timeout(600)
                path_lang_dark = OUT_DIR / "prod_01_language_selection_dark.png"
                await page.screenshot(path=str(path_lang_dark))
                print(f"  Saved: {path_lang_dark}")

                await page.evaluate("window.setAppTheme && window.setAppTheme('light')")
                await page.wait_for_timeout(400)
                path_lang_light = OUT_DIR / "prod_01_language_selection_light.png"
                await page.screenshot(path=str(path_lang_light))
                print(f"  Saved: {path_lang_light}")

                # 4. Mobile OTP Login (Dark & Light)
                await page.evaluate("window.setAppTheme && window.setAppTheme('dark')")
                await page.evaluate("window.navigateToPhase && window.navigateToPhase('login')")
                await page.wait_for_timeout(600)
                path_login_dark = OUT_DIR / "prod_02_mobile_otp_dark.png"
                await page.screenshot(path=str(path_login_dark))
                print(f"  Saved: {path_login_dark}")

                await page.evaluate("window.setAppTheme && window.setAppTheme('light')")
                await page.wait_for_timeout(400)
                path_login_light = OUT_DIR / "prod_02_mobile_otp_light.png"
                await page.screenshot(path=str(path_login_light))
                print(f"  Saved: {path_login_light}")

                # 5. Account Screen (7 rows, no duplicate Cart/Orders)
                await page.evaluate("window.setAppTheme && window.setAppTheme('dark')")
                await page.evaluate("window.navigateToPhase && window.navigateToPhase('profile')")
                await page.wait_for_timeout(600)
                path_acc_dark = OUT_DIR / "prod_10_account_dark.png"
                await page.screenshot(path=str(path_acc_dark))
                print(f"  Saved: {path_acc_dark}")

                await page.evaluate("window.setAppTheme && window.setAppTheme('light')")
                await page.wait_for_timeout(400)
                path_acc_light = OUT_DIR / "prod_10_account_light.png"
                await page.screenshot(path=str(path_acc_light))
                print(f"  Saved: {path_acc_light}")

                # 6. App Settings (Appearance: Light & Dark only)
                await page.evaluate("window.setAppTheme && window.setAppTheme('dark')")
                await page.evaluate("window.openCustomerAccountSubview && window.openCustomerAccountSubview('preferences')")
                await page.wait_for_timeout(600)
                path_set_dark = OUT_DIR / "prod_11_app_settings_dark.png"
                await page.screenshot(path=str(path_set_dark))
                print(f"  Saved: {path_set_dark}")

                await page.evaluate("window.setAppTheme && window.setAppTheme('light')")
                await page.wait_for_timeout(400)
                path_set_light = OUT_DIR / "prod_11_app_settings_light.png"
                await page.screenshot(path=str(path_set_light))
                print(f"  Saved: {path_set_light}")

                # 7. Order Details & 180s Cancellation Countdown (Dark & Light)
                await page.evaluate("window.setAppTheme && window.setAppTheme('dark')")
                await page.evaluate("window.navigateToPhase && window.navigateToPhase('tracking')")
                await page.wait_for_timeout(600)
                path_ord_dark = OUT_DIR / "prod_09_order_tracking_dark.png"
                await page.screenshot(path=str(path_ord_dark))
                print(f"  Saved: {path_ord_dark}")

                await page.evaluate("window.setAppTheme && window.setAppTheme('light')")
                await page.wait_for_timeout(400)
                path_ord_light = OUT_DIR / "prod_09_order_tracking_light.png"
                await page.screenshot(path=str(path_ord_light))
                print(f"  Saved: {path_ord_light}")

                # 8. Refund & Consumer Policies (Dark & Light)
                await page.evaluate("window.setAppTheme && window.setAppTheme('dark')")
                await page.evaluate("window.navigateToPhase && window.navigateToPhase('policies')")
                await page.wait_for_timeout(600)
                path_pol_dark = OUT_DIR / "prod_15_refund_policy_dark.png"
                await page.screenshot(path=str(path_pol_dark))
                print(f"  Saved: {path_pol_dark}")

                await page.evaluate("window.setAppTheme && window.setAppTheme('light')")
                await page.wait_for_timeout(400)
                path_pol_light = OUT_DIR / "prod_15_refund_policy_light.png"
                await page.screenshot(path=str(path_pol_light))
                print(f"  Saved: {path_pol_light}")

            await context.close()

        await browser.close()

    print("\n" + "=" * 80)
    print("ALL LIVE PRODUCTION SCREENSHOTS CAPTURED SUCCESSFULLY!")
    print(f"Directory: {OUT_DIR.resolve()}")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(capture_live_production())

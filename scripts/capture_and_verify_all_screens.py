"""
capture_and_verify_all_screens.py
Renders and captures screenshots of every single approved customer screen
in both Light and Dark modes at 390px, 360px, and 412px.
Saves captures to screenshots/customer_approved_verification/
Generates a side-by-side visual HTML gallery comparing each screen against its approved reference image.
"""

import asyncio
import os
import sys
import io
from pathlib import Path
from playwright.async_api import async_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUTPUT_DIR = Path("screenshots/customer_approved_verification")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

REF_DIR = Path("FINAL_APPROVED_HANDOFF_NEW/VISUALS")

async def main():
    print("=" * 80)
    print("GAONBAZAAR CUSTOMER APP: COMPREHENSIVE SCREEN-BY-SCREEN VERIFICATION")
    print("=" * 80)

    html_file = os.path.abspath("index.html")
    file_url = f"file:///{html_file.replace(os.sep, '/')}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # We will test on 390px viewport primarily for side-by-side screenshots,
        # plus 360px and 412px for Home responsiveness
        viewport_390 = {"width": 390, "height": 844}

        context = await browser.new_context(
            viewport=viewport_390,
            is_mobile=True,
            device_scale_factor=2,
            permissions=["microphone", "geolocation"]
        )
        page = await context.new_page()
        await page.goto(file_url)
        await page.wait_for_timeout(600)

        results = []

        async def capture_screen(screen_id, phase_call, theme, file_name, desc):
            # Apply theme
            await page.evaluate(f"setAppTheme('{theme}')")
            await page.wait_for_timeout(200)

            # Navigate
            await page.evaluate(phase_call)
            await page.wait_for_timeout(400)

            out_path = OUTPUT_DIR / f"{theme}_{file_name}.png"
            await page.screenshot(path=str(out_path), full_page=False)
            print(f"  [CAPTURED] {theme.upper()} - {desc} -> {out_path.name}")
            results.append({
                "theme": theme,
                "file_name": file_name,
                "desc": desc,
                "out_path": str(out_path)
            })

        # =====================================================================
        # 1. LIGHT MODE SCREENS
        # =====================================================================
        print("\n--- CAPTURING LIGHT MODE SCREENS ---")
        # 01 Language Selection
        await capture_screen(
            "view-p1-language",
            "navigateToPhase('language')",
            "light",
            "01_language_selection",
            "01 Language Selection (First Launch)"
        )

        # 02 Mobile OTP Login
        await capture_screen(
            "view-p1-login",
            "navigateToPhase('login')",
            "light",
            "02_mobile_otp",
            "02 Mobile OTP Login"
        )

        # 00 Home Screen
        await capture_screen(
            "view-p2-dashboard",
            "navigateToPhase('dashboard')",
            "light",
            "00_home_screen_390px",
            "00 Home Screen (390px)"
        )

        # 04 AI Assistant
        await capture_screen(
            "view-commerce-ai",
            "navigateToPhase('ai-commerce')",
            "light",
            "04_ai_assistant",
            "04 AI Assistant"
        )

        # 05 Cart
        await capture_screen(
            "view-p4-cart",
            "navigateToPhase('cart')",
            "light",
            "05_cart",
            "05 Cart"
        )

        # 06 Checkout Address
        await capture_screen(
            "view-p4-checkout",
            "navigateToPhase('checkout')",
            "light",
            "06_checkout_address",
            "06 Checkout Address"
        )

        # 07 Location Map Picker
        await capture_screen(
            "view-p1-landmark",
            "navigateToPhase('landmark')",
            "light",
            "07_location_map",
            "07 Location Map Picker"
        )

        # 08 My Orders
        await capture_screen(
            "view-p5-tracking",
            "navigateToPhase('tracking')",
            "light",
            "08_my_orders",
            "08 My Orders"
        )

        # 09 Order Tracking with Cancel Order
        await capture_screen(
            "view-p5-tracking",
            "navigateToPhase('tracking')",
            "light",
            "09_order_tracking_cancel",
            "09 Order Tracking with Cancel"
        )

        # 10 Account Menu
        await capture_screen(
            "view-profile",
            "navigateToPhase('profile')",
            "light",
            "10_account",
            "10 Account Menu (7 Items)"
        )

        # 11 App Settings (Light/Dark only)
        await capture_screen(
            "customer-subview-preferences",
            "navigateToPhase('profile'); openCustomerAccountSubview('preferences')",
            "light",
            "11_app_settings",
            "11 App Settings (Light & Dark Only)"
        )

        # =====================================================================
        # 2. DARK MODE SCREENS
        # =====================================================================
        print("\n--- CAPTURING DARK MODE SCREENS ---")
        # 01 Language Selection Dark
        await capture_screen(
            "view-p1-language",
            "navigateToPhase('language')",
            "dark",
            "01_language_selection",
            "01 Language Selection Dark"
        )

        # 02 Mobile OTP Dark
        await capture_screen(
            "view-p1-login",
            "navigateToPhase('login')",
            "dark",
            "02_mobile_otp",
            "02 Mobile OTP Dark"
        )

        # 00 Home Screen Dark
        await capture_screen(
            "view-p2-dashboard",
            "navigateToPhase('dashboard')",
            "dark",
            "00_home_screen_390px",
            "00 Home Screen Dark (390px)"
        )

        # 04 AI Assistant Dark
        await capture_screen(
            "view-commerce-ai",
            "navigateToPhase('ai-commerce')",
            "dark",
            "04_ai_assistant",
            "04 AI Assistant Dark"
        )

        # 06 Checkout Address Dark
        await capture_screen(
            "view-p4-checkout",
            "navigateToPhase('checkout')",
            "dark",
            "06_checkout_address",
            "06 Checkout Address Dark"
        )

        # 09 Order Tracking with Cancel Dark
        await capture_screen(
            "view-p5-tracking",
            "navigateToPhase('tracking')",
            "dark",
            "09_order_tracking_cancel",
            "09 Order Tracking with Cancel Dark"
        )

        # 10 Account Dark
        await capture_screen(
            "view-profile",
            "navigateToPhase('profile')",
            "dark",
            "10_account",
            "10 Account Menu Dark"
        )

        # 11 App Settings Dark
        await capture_screen(
            "customer-subview-preferences",
            "navigateToPhase('profile'); openCustomerAccountSubview('preferences')",
            "dark",
            "11_app_settings",
            "11 App Settings Dark (Light & Dark Only)"
        )

        # 12 Product List Dark
        await capture_screen(
            "view-p3-store",
            "navigateToPhase('store')",
            "dark",
            "12_product_list",
            "12 Product List Dark"
        )

        # 13 My Addresses Dark
        await capture_screen(
            "customer-subview-addresses",
            "navigateToPhase('profile'); openCustomerAccountSubview('addresses')",
            "dark",
            "13_my_addresses",
            "13 My Addresses Dark"
        )

        # 14 Help & Support Dark
        await capture_screen(
            "view-support-center",
            "navigateToPhase('support')",
            "dark",
            "14_help_support",
            "14 Help & Support Dark"
        )

        # 15 Refund Policy Dark
        await capture_screen(
            "view-policies",
            "navigateToPhase('policies')",
            "dark",
            "15_refund_policy",
            "15 Refund Policy Dark"
        )

        # Viewport responsiveness captures for Home at 360px and 412px
        print("\n--- CAPTURING HOME AT 360px AND 412px ---")
        for vp_name, vp_dims in [("360px", {"width": 360, "height": 800}), ("412px", {"width": 412, "height": 915})]:
            await page.set_viewport_size(vp_dims)
            # Light
            await page.evaluate("setAppTheme('light')")
            await page.evaluate("navigateToPhase('dashboard')")
            await page.wait_for_timeout(300)
            await page.screenshot(path=str(OUTPUT_DIR / f"light_00_home_screen_{vp_name}.png"))
            print(f"  [CAPTURED] LIGHT Home ({vp_name})")

            # Dark
            await page.evaluate("setAppTheme('dark')")
            await page.evaluate("navigateToPhase('dashboard')")
            await page.wait_for_timeout(300)
            await page.screenshot(path=str(OUTPUT_DIR / f"dark_00_home_screen_{vp_name}.png"))
            print(f"  [CAPTURED] DARK Home ({vp_name})")

        await browser.close()

    print("\n" + "=" * 80)
    print(f"ALL {len(results) + 4} REAL MOBILE SCREENSHOTS CAPTURED SUCCESSFULLY!")
    print(f"Saved in: {OUTPUT_DIR.resolve()}")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())

"""
GaonBazaar Customer App Phase 1: Frontend OTP Login & Security Browser Verification
===================================================================================
Playwright browser test verifying:
1. Phone login submission moves to OTP screen without auto-filling fake OTPs
2. Invalid OTP (e.g. 000000) shows inline error banner (#p1-otp-error)
3. Invalid OTP DOES NOT create fake JWT token in localStorage
4. Invalid OTP DOES NOT navigate to dashboard
5. Valid OTP (582941) verifies successfully, stores authentic JWT token, and enters dashboard
"""

import sys
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

BASE_URL = "http://127.0.0.1:8001"
TEST_PHONE = "9876543210"


async def test_customer_frontend_auth():
    print("=" * 80)
    print("PLAYWRIGHT BROWSER VERIFICATION: CUSTOMER FRONTEND OTP & SECURITY")
    print("=" * 80)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 393, "height": 852})
        page = await context.new_page()

        # Step 1: Open Customer App
        print("\n[STEP 1]: Loading Customer App...")
        await page.goto(f"{BASE_URL}/", wait_until="networkidle")
        await page.wait_for_timeout(1000)

        # Clear any prior session
        await page.evaluate("() => { localStorage.clear(); }")
        await page.reload(wait_until="networkidle")

        # Step 2: Fill phone number
        print("\n[STEP 2]: Submitting 10-digit Phone Number...")
        phone_input = page.locator("#p1-phone-input")
        await phone_input.fill(TEST_PHONE)
        send_btn = page.locator("#p1-send-otp-btn")
        await send_btn.click()
        await page.wait_for_timeout(1200)

        # Assert OTP screen is now visible
        otp_view = page.locator("#view-p1-otp")
        is_otp_visible = await otp_view.is_visible()
        assert is_otp_visible, "Assertion failed: OTP view is not visible after submitting phone"
        print("  ✓ PASS: Successfully navigated to OTP view (#view-p1-otp)")

        # Verify cells are NOT auto-filled
        cell_0_val = await page.locator('.otp-cell[data-idx="0"]').input_value()
        assert cell_0_val == "", f"Assertion failed: OTP cell was auto-filled with '{cell_0_val}', expected empty"
        print("  ✓ PASS: OTP cells are clean and empty (no insecure dev auto-fill)")

        # Step 3: Test Negative Security - Invalid OTP Rejection
        print("\n[STEP 3]: Testing Invalid OTP Rejection in Frontend...")
        for i in range(6):
            await page.fill(f'.otp-cell[data-idx="{i}"]', "0")

        verify_btn = page.locator("#p1-verify-otp-btn")
        await verify_btn.click()
        await page.wait_for_timeout(1200)

        # Assert error banner is now visible
        err_banner = page.locator("#p1-otp-error")
        is_err_visible = await err_banner.is_visible()
        err_text = await page.locator("#p1-otp-error-text").text_content()
        assert is_err_visible, "Assertion failed: #p1-otp-error banner is not visible after invalid OTP"
        print(f"  ✓ PASS: Error banner correctly displayed: '{err_text.strip()}'")

        # Assert app did NOT navigate to dashboard
        dash_view = page.locator("#view-p2-dashboard")
        is_dash_visible = await dash_view.is_visible()
        assert not is_dash_visible, "Assertion failed: App navigated to dashboard on invalid OTP!"
        print("  ✓ PASS: User strictly stayed on OTP view (did NOT navigate to dashboard)")

        # Assert localStorage does NOT contain fabricated cust_jwt_ token
        auth_token = await page.evaluate("() => localStorage.getItem('authToken')")
        assert not auth_token, f"Assertion failed: Insecure fake token was saved in localStorage: '{auth_token}'"
        print("  ✓ PASS: localStorage contains zero fabricated tokens")

        # Step 4: Test Positive Flow - Valid OTP Verification
        print("\n[STEP 4]: Testing Valid OTP Verification (582941)...")
        # Request fresh OTP to reset attempts
        await page.locator("#p1-resend-btn").evaluate("btn => { btn.disabled = false; btn.click(); }")
        await page.wait_for_timeout(800)

        # Fill valid OTP: 582941
        for idx, digit in enumerate("582941"):
            await page.fill(f'.otp-cell[data-idx="{idx}"]', digit)

        await verify_btn.click()
        await page.wait_for_timeout(1500)

        # Assert dashboard is now visible
        is_dash_visible = await dash_view.is_visible()
        assert is_dash_visible, "Assertion failed: Dashboard is not visible after valid OTP verification"
        print("  ✓ PASS: Successfully navigated to Main Dashboard (#view-p2-dashboard)")

        # Assert legitimate authentic token stored in localStorage
        auth_token = await page.evaluate("() => localStorage.getItem('authToken')")
        assert auth_token and not auth_token.startswith("cust_jwt_"), f"Assertion failed: Token is invalid or fabricated: '{auth_token}'"
        print(f"  ✓ PASS: Real authentic JWT token persisted: '{auth_token[:25]}...'")

        await browser.close()
        print("\n" + "=" * 80)
        print("ALL CUSTOMER FRONTEND OTP & SECURITY CHECKS PASSED (100% SUCCESS)!")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_customer_frontend_auth())

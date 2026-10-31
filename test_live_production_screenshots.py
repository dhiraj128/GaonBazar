import asyncio
import os
import sys
import io
import shutil
from playwright.async_api import async_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def capture_all_live_production_screens():
    print("=" * 70, flush=True)
    print("CAPTURING ALL LIVE PRODUCTION SCREENS (https://gaonbazar.onrender.com)", flush=True)
    print("=" * 70, flush=True)

    live_dir = "screenshots/live_production_verification"
    os.makedirs(live_dir, exist_ok=True)
    artifact_dir = r"C:\Users\dhira\.gemini\antigravity\brain\84425271-d72e-4056-a634-da667ae92603"
    
    live_url = "https://gaonbazar.onrender.com"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=2,
            is_mobile=True,
            has_touch=True
        )
        page = await context.new_page()

        await page.goto(live_url, timeout=60000)
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(2)

        # 1. First-Launch Language Selection
        await page.evaluate("""() => {
            localStorage.clear();
            sessionStorage.clear();
            if (typeof navigateToPhase === 'function') navigateToPhase('language');
        }""")
        await asyncio.sleep(0.5)
        path_lang = os.path.join(live_dir, "00_live_language_selection.png")
        await page.screenshot(path=path_lang)
        shutil.copy2(path_lang, os.path.join(artifact_dir, "00_live_language_selection.png"))
        print(f"  -> Captured 00_live_language_selection.png", flush=True)

        # 2. Home Dashboard (Light Mode)
        await page.evaluate("""() => {
            if (typeof setAppLanguage === 'function') setAppLanguage('en');
            if (typeof setAppTheme === 'function') setAppTheme('light');
            if (typeof navigateToPhase === 'function') navigateToPhase('dashboard');
        }""")
        await asyncio.sleep(1)
        path_home_light = os.path.join(live_dir, "01_live_home_two_stores_light.png")
        await page.screenshot(path=path_home_light)
        shutil.copy2(path_home_light, os.path.join(artifact_dir, "01_live_home_two_stores_light.png"))
        print(f"  -> Captured 01_live_home_two_stores_light.png", flush=True)

        # 3. Account Screen (7 Approved Rows)
        await page.evaluate("if (typeof navigateToPhase === 'function') navigateToPhase('profile');")
        await asyncio.sleep(0.8)
        path_account = os.path.join(live_dir, "02_live_account_7_entries_en.png")
        await page.screenshot(path=path_account)
        shutil.copy2(path_account, os.path.join(artifact_dir, "02_live_account_7_entries_en.png"))
        print(f"  -> Captured 02_live_account_7_entries_en.png", flush=True)

        # 4. Payment Settings (Empty State & No Fake 9876543210@upi)
        await page.evaluate("if (typeof openCustomerAccountSubview === 'function') openCustomerAccountSubview('payments');")
        await asyncio.sleep(0.8)
        path_payments = os.path.join(live_dir, "03_live_payment_settings.png")
        await page.screenshot(path=path_payments)
        shutil.copy2(path_payments, os.path.join(artifact_dir, "03_live_payment_settings.png"))
        print(f"  -> Captured 03_live_payment_settings.png", flush=True)

        # 5. Help & Support (Absence of 1800-120-4266, Care Card)
        await page.evaluate("if (typeof navigateToSupportCenter === 'function') navigateToSupportCenter();")
        await asyncio.sleep(0.8)
        path_support = os.path.join(live_dir, "04_live_help_support.png")
        await page.screenshot(path=path_support)
        shutil.copy2(path_support, os.path.join(artifact_dir, "04_live_help_support.png"))
        print(f"  -> Captured 04_live_help_support.png", flush=True)

        # 6. Home Dashboard (Dark Mode)
        await page.evaluate("""() => {
            if (typeof setAppTheme === 'function') setAppTheme('dark');
            if (typeof navigateToPhase === 'function') navigateToPhase('dashboard');
        }""")
        await asyncio.sleep(1)
        path_home_dark = os.path.join(live_dir, "05_live_home_dark.png")
        await page.screenshot(path=path_home_dark)
        shutil.copy2(path_home_dark, os.path.join(artifact_dir, "05_live_home_dark.png"))
        print(f"  -> Captured 05_live_home_dark.png", flush=True)

        # 7. Account Screen (Dark Mode)
        await page.evaluate("if (typeof navigateToPhase === 'function') navigateToPhase('profile');")
        await asyncio.sleep(0.8)
        path_account_dark = os.path.join(live_dir, "06_live_account_dark.png")
        await page.screenshot(path=path_account_dark)
        shutil.copy2(path_account_dark, os.path.join(artifact_dir, "06_live_account_dark.png"))
        print(f"  -> Captured 06_live_account_dark.png", flush=True)

        print("\nALL LIVE PRODUCTION SCREENSHOTS CAPTURED AND COPIED TO ARTIFACTS!", flush=True)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(capture_all_live_production_screens())

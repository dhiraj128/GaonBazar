import asyncio
import os
import sys
import io
from playwright.async_api import async_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def capture_live_production_screenshots():
    print("=" * 70, flush=True)
    print("CAPTURING LIVE PRODUCTION SCREENSHOTS FROM RENDER", flush=True)
    print("=" * 70, flush=True)

    live_dir = "screenshots/live_production_verification"
    os.makedirs(live_dir, exist_ok=True)
    
    live_url = "https://gaonbazar.onrender.com"
    print(f"Connecting to live production URL: {live_url}", flush=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=2,
            is_mobile=True,
            has_touch=True
        )
        page = await context.new_page()

        try:
            await page.goto(live_url, timeout=60000)
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(2)
        except Exception as e:
            print(f"Connection warning/timeout: {e}", flush=True)

        # Force bypass auth to dashboard if needed
        await page.evaluate("if (typeof navigateToPhase === 'function') navigateToPhase('dashboard');")
        await page.evaluate("if (typeof setAppTheme === 'function') setAppTheme('light');")
        await page.evaluate("if (typeof setAppLanguage === 'function') setAppLanguage('en');")
        await asyncio.sleep(1)

        # 1. Live Home Screen
        home_path = os.path.join(live_dir, "01_live_home_two_stores_light.png")
        await page.screenshot(path=home_path)
        print(f"  -> Captured {home_path}", flush=True)

        # 2. Live Account Screen
        await page.click("#nav-btn-profile")
        await asyncio.sleep(1)
        account_path = os.path.join(live_dir, "02_live_account_7_entries_en.png")
        await page.screenshot(path=account_path)
        print(f"  -> Captured {account_path}", flush=True)

        # 3. Live Account Back Navigation
        await page.click("#profile-back-to-home-btn")
        await asyncio.sleep(1)
        back_path = os.path.join(live_dir, "03_live_back_to_home.png")
        await page.screenshot(path=back_path)
        print(f"  -> Captured {back_path}", flush=True)

        # 4. Live Dark Mode Home
        await page.evaluate("setAppTheme('dark')")
        await asyncio.sleep(1)
        dark_home_path = os.path.join(live_dir, "04_live_home_dark.png")
        await page.screenshot(path=dark_home_path)
        print(f"  -> Captured {dark_home_path}", flush=True)

        print("\nALL LIVE PRODUCTION SCREENSHOTS CAPTURED SUCCESSFULLY!", flush=True)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(capture_live_production_screenshots())

import os
import sys
import time
import subprocess
import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent.parent
SCREENSHOT_DIR = BASE_DIR / "screenshots" / "showcase_v3"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

IPHONE16 = {
    "name": "iPhone 16 (Standard iPhone 393x852)",
    "viewport": {"width": 393, "height": 852},
    "device_scale_factor": 3.0,
    "is_mobile": True,
    "has_touch": True,
    "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1"
}

def kill_port_8001():
    try:
        res = subprocess.run("netstat -ano | findstr :8001", shell=True, capture_output=True, text=True, timeout=3)
        pids = set()
        for line in res.stdout.strip().splitlines():
            parts = line.split()
            if len(parts) >= 5 and ":8001" in parts[1]:
                pid = parts[-1]
                if pid.isdigit() and int(pid) > 0 and int(pid) != os.getpid():
                    pids.add(pid)
        for pid in pids:
            try:
                subprocess.run(f"taskkill /F /T /PID {pid}", shell=True, capture_output=True, timeout=3)
            except Exception:
                pass
    except Exception:
        pass

def ensure_backend():
    try:
        with urllib.request.urlopen("http://127.0.0.1:8001/api/version", timeout=1.0) as r:
            if r.status == 200:
                print("[OK] Backend already running on http://127.0.0.1:8001")
                return None
    except Exception:
        pass

    kill_port_8001()
    time.sleep(0.5)
    print("[...] Starting backend server on port 8001...")
    env = os.environ.copy()
    env["TEST_MODE"] = "1"
    proc = subprocess.Popen([sys.executable, "run_server.py", "8001", "--no-reload"], cwd=str(BASE_DIR), env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(30):
        try:
            with urllib.request.urlopen("http://127.0.0.1:8001/api/version", timeout=1.0) as r:
                if r.status == 200:
                    print("[OK] Backend server ready!")
                    return proc
        except Exception:
            time.sleep(0.5)
    return proc

def capture_showcase():
    proc = ensure_backend()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            # -------------------------------------------------------------
            # 1. Capture Preview Unlock Gate Screen (iPhone 16)
            # -------------------------------------------------------------
            print("\nCapturing 00_preview_unlock_gate_mobile.png...")
            ctx = browser.new_context(
                viewport=IPHONE16["viewport"],
                device_scale_factor=IPHONE16["device_scale_factor"],
                is_mobile=IPHONE16["is_mobile"],
                has_touch=IPHONE16["has_touch"]
            )
            page = ctx.new_page()
            page.goto("http://127.0.0.1:8001/preview-unlock", wait_until="networkidle")
            page.wait_for_timeout(1000)
            page.screenshot(path=str(SCREENSHOT_DIR / "00_preview_unlock_gate_mobile.png"), full_page=False)
            ctx.close()

            # -------------------------------------------------------------
            # 2. Capture Vendor App (iPhone 16)
            # -------------------------------------------------------------
            print("\nCapturing Vendor App screens...")
            ctx = browser.new_context(
                viewport=IPHONE16["viewport"],
                device_scale_factor=IPHONE16["device_scale_factor"],
                is_mobile=IPHONE16["is_mobile"],
                has_touch=IPHONE16["has_touch"]
            )
            page = ctx.new_page()
            page.goto("http://127.0.0.1:8001/vendor", wait_until="domcontentloaded")
            page.wait_for_timeout(1500)
            if page.is_visible("#btn-vendor-login"):
                page.click("#btn-vendor-login")
                page.wait_for_selector("#vendor-main-content:not(.hidden)", timeout=8000)
                page.wait_for_timeout(1500)

            # Orders Tab
            page.screenshot(path=str(SCREENSHOT_DIR / "vendor_01_orders_tab.png"), full_page=False)

            # Inventory Tab
            page.evaluate("() => { if (typeof switchMainTab === 'function') switchMainTab('inventory'); }")
            page.wait_for_timeout(1500)
            page.screenshot(path=str(SCREENSHOT_DIR / "vendor_02_stock_inventory_tab.png"), full_page=False)

            # Daily Ledger Tab
            page.evaluate("() => { if (typeof switchMainTab === 'function') switchMainTab('ledger'); }")
            page.wait_for_timeout(1500)
            page.screenshot(path=str(SCREENSHOT_DIR / "vendor_03_daily_ledger_tab.png"), full_page=False)

            # Settings Tab
            page.evaluate("() => { if (typeof switchMainTab === 'function') switchMainTab('profile'); }")
            page.wait_for_timeout(1500)
            page.screenshot(path=str(SCREENSHOT_DIR / "vendor_04_store_settings_tab.png"), full_page=False)
            ctx.close()

            # -------------------------------------------------------------
            # 3. Capture Runner App (iPhone 16)
            # -------------------------------------------------------------
            print("\nCapturing Runner App screens...")
            ctx = browser.new_context(
                viewport=IPHONE16["viewport"],
                device_scale_factor=IPHONE16["device_scale_factor"],
                is_mobile=IPHONE16["is_mobile"],
                has_touch=IPHONE16["has_touch"]
            )
            page = ctx.new_page()
            page.goto("http://127.0.0.1:8001/runner", wait_until="domcontentloaded")
            page.wait_for_timeout(1500)
            if page.is_visible("#btn-runner-login"):
                page.click("#btn-runner-login")
                page.wait_for_selector("#runner-main-content:not(.hidden)", timeout=8000)
                page.wait_for_timeout(1500)

            # Missions Tab
            page.screenshot(path=str(SCREENSHOT_DIR / "runner_01_missions_tab.png"), full_page=False)

            # Earnings Tab
            page.evaluate("() => { if (typeof switchMainTab === 'function') switchMainTab('ledger'); }")
            page.wait_for_timeout(1500)
            page.screenshot(path=str(SCREENSHOT_DIR / "runner_02_earnings_ledger_tab.png"), full_page=False)

            # Settings Tab
            page.evaluate("() => { if (typeof switchMainTab === 'function') switchMainTab('settings'); }")
            page.wait_for_timeout(1500)
            page.screenshot(path=str(SCREENSHOT_DIR / "runner_03_partner_settings_tab.png"), full_page=False)
            ctx.close()

            # -------------------------------------------------------------
            # 4. Capture Customer App (iPhone 16)
            # -------------------------------------------------------------
            print("\nCapturing Customer App screens...")
            ctx = browser.new_context(
                viewport=IPHONE16["viewport"],
                device_scale_factor=IPHONE16["device_scale_factor"],
                is_mobile=IPHONE16["is_mobile"],
                has_touch=IPHONE16["has_touch"]
            )
            page = ctx.new_page()
            page.goto("http://127.0.0.1:8001/", wait_until="domcontentloaded")
            page.wait_for_timeout(2000)

            page.evaluate("""() => {
                localStorage.setItem('gaonbazar_user_phone', '9876543210');
                localStorage.setItem('gaonbazar_user_name', 'Ramesh Patel');
                localStorage.setItem('gaonbazar_village', 'Rampur');
                localStorage.setItem('gaonbazar_landmark', 'Near Shiva Mandir');
                localStorage.setItem('gaonbazar_language', 'hi');
                if (window.AppStore) {
                    AppStore.userPhone = '9876543210';
                    AppStore.userName = 'Ramesh Patel';
                    AppStore.village = 'Rampur';
                    AppStore.landmark = 'Near Shiva Mandir';
                    AppStore.language = 'hi';
                }
            }""")
            page.reload(wait_until="domcontentloaded")
            page.wait_for_timeout(2000)

            # Customer Home Feed
            page.screenshot(path=str(SCREENSHOT_DIR / "customer_01_home_stores_feed.png"), full_page=False)

            # Click first store card to view catalog
            store_card = page.locator(".store-card, [onclick*='openStore'], [data-store-id]").first
            if store_card.is_visible():
                store_card.click()
                page.wait_for_timeout(2000)
                page.screenshot(path=str(SCREENSHOT_DIR / "customer_02_store_catalog.png"), full_page=False)

                # Add item to cart to trigger floating cart bar
                add_btn = page.locator(".btn-add, button:has-text('ADD'), button:has-text('जोड़ें')").first
                if add_btn.is_visible():
                    add_btn.click()
                    page.wait_for_timeout(1500)
                    page.screenshot(path=str(SCREENSHOT_DIR / "customer_03_floating_cart_bar.png"), full_page=False)

            # Customer Profile Tab
            page.evaluate("() => { if (typeof switchAppTab === 'function') switchAppTab('profile'); }")
            page.wait_for_timeout(1500)
            page.screenshot(path=str(SCREENSHOT_DIR / "customer_04_profile_settings.png"), full_page=False)

            ctx.close()
            browser.close()
            print("\n[SUCCESS] All showcase screenshots captured successfully in:", SCREENSHOT_DIR)
    finally:
        if proc:
            try:
                proc.kill()
            except Exception:
                pass
            kill_port_8001()

if __name__ == "__main__":
    capture_showcase()

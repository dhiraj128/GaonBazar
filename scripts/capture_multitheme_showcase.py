import os
import sys
import time
import shutil
import subprocess
import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = Path(__file__).resolve().parent.parent
LOCAL_SHOWCASE_DIR = BASE_DIR / "screenshots" / "showcase_v4"
LOCAL_SHOWCASE_DIR.mkdir(parents=True, exist_ok=True)

ARTIFACT_SHOWCASE_DIR = Path(r"C:\Users\dhira\.gemini\antigravity\brain\29d41e64-3ddf-4124-92c9-f8acce5c35e0\showcase_v4")
ARTIFACT_SHOWCASE_DIR.mkdir(parents=True, exist_ok=True)

VIEWPORTS = {
    "iphone16": {"width": 393, "height": 852, "dpr": 3.0, "name": "iPhone 16 (393x852)"},
    "redmi9a": {"width": 360, "height": 800, "dpr": 2.0, "name": "Redmi 9A (360x800)"},
    "compact320": {"width": 320, "height": 640, "dpr": 2.0, "name": "Compact Feature (320x640)"},
    "large414": {"width": 414, "height": 896, "dpr": 3.0, "name": "iPhone Plus (414x896)"}
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
                print("[OK] Backend already active on port 8001")
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

def save_and_copy(page, filename):
    local_path = LOCAL_SHOWCASE_DIR / filename
    art_path = ARTIFACT_SHOWCASE_DIR / filename
    page.screenshot(path=str(local_path), full_page=False)
    shutil.copy2(str(local_path), str(art_path))
    print(f"  ✓ Saved: {filename} ({local_path.stat().st_size} bytes)")

def apply_theme(page, theme):
    if theme == 'dark':
        page.evaluate("""() => {
            document.documentElement.classList.remove('light');
            document.documentElement.classList.add('dark');
            localStorage.setItem('gaonbazar_theme', 'dark');
            localStorage.setItem('theme', 'dark');
            if (window.AppStore) AppStore.theme = 'dark';
            if (window.VendorStore) VendorStore.theme = 'dark';
            if (window.RunnerStore) RunnerStore.theme = 'dark';
        }""")
    else:
        page.evaluate("""() => {
            document.documentElement.classList.remove('dark');
            document.documentElement.classList.add('light');
            localStorage.setItem('gaonbazar_theme', 'light');
            localStorage.setItem('theme', 'light');
            if (window.AppStore) AppStore.theme = 'light';
            if (window.VendorStore) VendorStore.theme = 'light';
            if (window.RunnerStore) RunnerStore.theme = 'light';
        }""")
    page.wait_for_timeout(400)

def capture_all():
    proc = ensure_backend()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            vp = VIEWPORTS["iphone16"]

            # =========================================================
            # 1. CUSTOMER APP SHOWCASE (Light & Dark)
            # =========================================================
            print("\n📸 [1/3] Capturing Customer App Showcase...")
            ctx = browser.new_context(
                viewport={"width": vp["width"], "height": vp["height"]},
                device_scale_factor=vp["dpr"],
                is_mobile=True,
                has_touch=True
            )
            page = ctx.new_page()
            page.goto("http://127.0.0.1:8001/", wait_until="domcontentloaded")
            page.wait_for_timeout(1000)

            # Set user session so app is directly on Dashboard
            page.evaluate("""() => {
                localStorage.setItem('gaonbazar_session', JSON.stringify({
                    phone: '9876543210',
                    name: 'रामेश पटेल',
                    village: 'रामपुर',
                    landmark: 'शिव मंदिर के पास'
                }));
                localStorage.setItem('gaonbazar_lang', 'hi');
                localStorage.setItem('gaonbazar_theme', 'light');
                if (typeof navigateToPhase === 'function') navigateToPhase('dashboard');
            }""")
            page.reload(wait_until="domcontentloaded")
            page.wait_for_timeout(1500)
            apply_theme(page, 'light')

            # 1.1 Home Stores Feed with Horizontal Category Filter Chips (Light Mode)
            save_and_copy(page, "cust_01_home_light.png")

            # 1.2 Home Stores Feed (Dark Mode)
            apply_theme(page, 'dark')
            save_and_copy(page, "cust_01_home_dark.png")
            apply_theme(page, 'light')

            # 1.3 Store Catalog Screen
            page.evaluate("() => { if (typeof openStoreView === 'function') openStoreView('sharma_brothers'); }")
            page.wait_for_timeout(1500)
            save_and_copy(page, "cust_02_store_catalog_light.png")
            apply_theme(page, 'dark')
            save_and_copy(page, "cust_02_store_catalog_dark.png")
            apply_theme(page, 'light')

            # 1.4 Add to cart & Floating Cart Bar
            page.evaluate("() => { if (typeof addToCart === 'function') addToCart('item_1', 'sharma_brothers'); }")
            page.wait_for_timeout(800)
            save_and_copy(page, "cust_03_floating_cart_bar.png")

            # 1.5 Cart View
            page.evaluate("() => { if (typeof navigateToPhase === 'function') navigateToPhase('cart'); }")
            page.wait_for_timeout(1000)
            save_and_copy(page, "cust_04_cart_review.png")

            # 1.6 Profile / Settings View
            page.evaluate("() => { if (typeof navigateToPhase === 'function') navigateToPhase('profile'); }")
            page.wait_for_timeout(1000)
            save_and_copy(page, "cust_05_profile_settings.png")

            # 1.7 Live Order Tracking
            page.evaluate("""() => {
                AppStore.orderId = '#RUR-8821';
                AppStore.activeOrder = {
                    id: '#RUR-8821',
                    stage: 4,
                    store_name: 'शर्मा ब्रदर्स किराना',
                    user_name: 'रामेश पटेल',
                    delivery_otp: '4289',
                    total_amount: 355,
                    payment_mode: 'COD',
                    runner_name: 'कमल सिंह',
                    runner_phone: '9876543299',
                    items: [{ name: 'आशीर्वाद आटा 5kg', qty: 1, price: 210 }]
                };
                if (typeof navigateToPhase === 'function') navigateToPhase('tracking');
                if (typeof renderOrderTrackingView === 'function') renderOrderTrackingView();
            }""")
            page.wait_for_timeout(1200)
            save_and_copy(page, "cust_06_live_order_tracking.png")
            ctx.close()

            # =========================================================
            # 2. VENDOR APP SHOWCASE (Light & Dark)
            # =========================================================
            print("\n📸 [2/3] Capturing Vendor App Showcase...")
            ctx = browser.new_context(
                viewport={"width": vp["width"], "height": vp["height"]},
                device_scale_factor=vp["dpr"],
                is_mobile=True,
                has_touch=True
            )
            page = ctx.new_page()
            page.goto("http://127.0.0.1:8001/vendor", wait_until="domcontentloaded")
            page.wait_for_timeout(1000)
            if page.is_visible("#btn-vendor-login"):
                page.click("#btn-vendor-login")
                page.wait_for_selector("#vendor-main-content:not(.hidden)", timeout=10000)
                page.wait_for_timeout(1200)

            apply_theme(page, 'light')
            # 2.1 Vendor Orders Queue (Light Mode - Orders First)
            save_and_copy(page, "vend_01_orders_light.png")

            # 2.2 Vendor Orders Queue (Dark Mode)
            apply_theme(page, 'dark')
            save_and_copy(page, "vend_01_orders_dark.png")
            apply_theme(page, 'light')

            # 2.3 Stock Inventory Toggles
            page.evaluate("() => { if (typeof switchMainTab === 'function') switchMainTab('inventory'); }")
            page.wait_for_timeout(1000)
            save_and_copy(page, "vend_02_stock_inventory.png")

            # 2.4 Daily Ledger
            page.evaluate("() => { if (typeof switchMainTab === 'function') switchMainTab('ledger'); }")
            page.wait_for_timeout(1000)
            save_and_copy(page, "vend_03_daily_ledger.png")

            # 2.5 Store Profile & Settings
            page.evaluate("() => { if (typeof switchMainTab === 'function') switchMainTab('profile'); }")
            page.wait_for_timeout(1000)
            save_and_copy(page, "vend_04_store_settings.png")
            ctx.close()

            # =========================================================
            # 3. RUNNER APP SHOWCASE (Light & Dark)
            # =========================================================
            print("\n📸 [3/3] Capturing Runner App Showcase...")
            ctx = browser.new_context(
                viewport={"width": vp["width"], "height": vp["height"]},
                device_scale_factor=vp["dpr"],
                is_mobile=True,
                has_touch=True
            )
            page = ctx.new_page()
            page.goto("http://127.0.0.1:8001/runner", wait_until="domcontentloaded")
            page.wait_for_timeout(1000)
            if page.is_visible("#btn-runner-login"):
                page.click("#btn-runner-login")
                page.wait_for_selector("#runner-main-content:not(.hidden)", timeout=10000)
                page.wait_for_timeout(1200)

            # 3.1 Runner Missions Queue (Light Mode)
            apply_theme(page, 'light')
            save_and_copy(page, "runn_01_missions_light.png")

            # 3.2 Runner Missions Queue (Balanced Charcoal Dark Mode)
            apply_theme(page, 'dark')
            save_and_copy(page, "runn_01_missions_dark.png")
            apply_theme(page, 'light')

            # 3.3 Runner Shift Earnings Ledger
            page.evaluate("() => { if (typeof switchTab === 'function') switchTab('ledger'); }")
            page.wait_for_timeout(1000)
            save_and_copy(page, "runn_02_earnings_ledger.png")

            # 3.4 Runner Partner Settings & Duty Toggle
            page.evaluate("() => { if (typeof switchTab === 'function') switchTab('settings'); }")
            page.wait_for_timeout(1000)
            save_and_copy(page, "runn_03_partner_settings.png")
            ctx.close()

            # =========================================================
            # 4. MULTI-VIEWPORT VERIFICATION (320px, 360px, 414px)
            # =========================================================
            print("\n📸 [4/4] Capturing Multi-Viewport Verifications...")
            for dev_key in ["compact320", "redmi9a", "large414"]:
                dev = VIEWPORTS[dev_key]
                vctx = browser.new_context(
                    viewport={"width": dev["width"], "height": dev["height"]},
                    device_scale_factor=dev["dpr"],
                    is_mobile=True,
                    has_touch=True
                )
                vpage = vctx.new_page()
                vpage.goto("http://127.0.0.1:8001/", wait_until="domcontentloaded")
                vpage.wait_for_timeout(1000)
                vpage.evaluate("""() => {
                    localStorage.setItem('gaonbazar_session', JSON.stringify({
                        phone: '9876543210', name: 'रामेश', village: 'रामपुर'
                    }));
                    if (typeof navigateToPhase === 'function') navigateToPhase('dashboard');
                }""")
                vpage.reload(wait_until="domcontentloaded")
                vpage.wait_for_timeout(1200)
                save_and_copy(vpage, f"viewport_{dev['width']}px_customer_home.png")
                vctx.close()

            browser.close()
            print("\n🎉 ALL SHOWCASE SCREENSHOTS CAPTURED AND COPIED TO ARTIFACT DIR!")
    finally:
        if proc:
            try:
                proc.kill()
            except Exception:
                pass
            kill_port_8001()

if __name__ == "__main__":
    capture_all()

# scripts/capture_approved_design_showcase.py
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
LOCAL_SHOWCASE_DIR = BASE_DIR / "screenshots" / "showcase_v5_approved"
LOCAL_SHOWCASE_DIR.mkdir(parents=True, exist_ok=True)

ARTIFACT_SHOWCASE_DIR = Path(r"C:\Users\dhira\.gemini\antigravity\brain\29d41e64-3ddf-4124-92c9-f8acce5c35e0\showcase_v5_approved")
ARTIFACT_SHOWCASE_DIR.mkdir(parents=True, exist_ok=True)

VIEWPORT = {"width": 393, "height": 852, "dpr": 2.0} # iPhone 16 Reference

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
                print("[OK] Backend already running on port 8001.")
                return None
    except Exception:
        pass

    kill_port_8001()
    time.sleep(1)
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8001"],
        cwd=str(BASE_DIR),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    for _ in range(30):
        time.sleep(0.5)
        try:
            with urllib.request.urlopen("http://127.0.0.1:8001/api/version", timeout=1.0) as r:
                if r.status == 200:
                    print("[OK] Backend spawned and verified on port 8001.")
                    return proc
        except Exception:
            pass
    return proc

def save_screenshot(page, filename, desc):
    loc_path = LOCAL_SHOWCASE_DIR / filename
    art_path = ARTIFACT_SHOWCASE_DIR / filename
    page.screenshot(path=str(loc_path), full_page=False)
    shutil.copy2(loc_path, art_path)
    print(f"  [SAVED] {filename} -> {desc}")

def run_showcase():
    backend_proc = ensure_backend()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            # ==================================================================
            # 1. CUSTOMER APP SHOWCASE (LIGHT & DARK)
            # ==================================================================
            print("\n--- Capturing Customer App Showcases ---")
            context = browser.new_context(
                viewport={"width": VIEWPORT["width"], "height": VIEWPORT["height"]},
                device_scale_factor=VIEWPORT["dpr"],
                is_mobile=True,
                has_touch=True
            )
            page = context.new_page()

            for theme in ["light", "dark"]:
                page.goto("http://127.0.0.1:8001/?force_auth=customer_verified")
                page.wait_for_load_state("networkidle")
                time.sleep(1)

                # Set theme
                page.evaluate(f"""() => {{
                    if ('{theme}' === 'dark') {{
                        document.documentElement.classList.add('dark');
                        document.documentElement.classList.remove('light');
                        localStorage.setItem('gaonbazar_theme', 'dark');
                    }} else {{
                        document.documentElement.classList.remove('dark');
                        document.documentElement.classList.add('light');
                        localStorage.setItem('gaonbazar_theme', 'light');
                    }}
                }}""")
                time.sleep(0.5)

                # 1. Home / Store Feed
                page.evaluate("navigateToPhase('dashboard')")
                time.sleep(0.5)
                save_screenshot(page, f"cust_01_home_{theme}.png", f"Customer Home Screen ({theme})")

                # 2. AI Voice Assistant
                page.evaluate("navigateToPhase('commerce-ai')")
                time.sleep(0.5)
                save_screenshot(page, f"cust_02_voice_ai_{theme}.png", f"Customer AI Shopping Assistant ({theme})")

                # 3. Cart & Checkout (Add items first)
                page.evaluate("""() => {
                    quickAddFeaturedItem('tomato', 'Fresh Tomato', 30, 'kg');
                    quickAddFeaturedItem('milk', 'Amul Taaza Milk', 60, '1L');
                    quickAddFeaturedItem('onion', 'Onion', 25, 'kg');
                    navigateToPhase('cart');
                }""")
                time.sleep(0.5)
                save_screenshot(page, f"cust_03_cart_{theme}.png", f"Customer Cart Screen ({theme})")

                # 4. Live Tracking
                page.evaluate("navigateToPhase('tracking')")
                time.sleep(0.5)
                save_screenshot(page, f"cust_04_tracking_{theme}.png", f"Customer Live Tracking Screen ({theme})")

                # 5. Side Drawer Menu
                page.evaluate("""() => {
                    navigateToPhase('dashboard');
                    openSidebarDrawer();
                }""")
                time.sleep(0.5)
                save_screenshot(page, f"cust_05_drawer_{theme}.png", f"Customer Sidebar Drawer Menu ({theme})")
                page.evaluate("closeSidebarDrawer()")
                time.sleep(0.3)

            context.close()

            # ==================================================================
            # 2. VENDOR APP SHOWCASE (LIGHT & DARK)
            # ==================================================================
            print("\n--- Capturing Vendor App Showcases ---")
            context = browser.new_context(
                viewport={"width": VIEWPORT["width"], "height": VIEWPORT["height"]},
                device_scale_factor=VIEWPORT["dpr"],
                is_mobile=True,
                has_touch=True
            )
            page = context.new_page()

            for theme in ["light", "dark"]:
                page.goto("http://127.0.0.1:8001/vendor_dashboard.html")
                page.wait_for_load_state("networkidle")
                time.sleep(1)

                if page.is_visible("#vendor-login-gate"):
                    page.click("#btn-vendor-login")
                    page.wait_for_selector("#vendor-main-content:not(.hidden)", timeout=10000)
                    time.sleep(1)

                page.evaluate(f"""() => {{
                    if ('{theme}' === 'dark') {{
                        document.documentElement.classList.add('dark');
                        document.documentElement.classList.remove('light');
                        localStorage.setItem('gaonbazar_vendor_theme', 'dark');
                    }} else {{
                        document.documentElement.classList.remove('dark');
                        document.documentElement.classList.add('light');
                        localStorage.setItem('gaonbazar_vendor_theme', 'light');
                    }}
                }}""")
                time.sleep(0.5)

                # 1. Orders Queue
                page.evaluate("switchMainTab('orders')")
                time.sleep(0.5)
                save_screenshot(page, f"vend_01_orders_{theme}.png", f"Vendor Orders Queue ({theme})")

                # 2. Products & Inventory
                page.evaluate("switchMainTab('inventory')")
                time.sleep(0.5)
                save_screenshot(page, f"vend_02_inventory_{theme}.png", f"Vendor Stock & Inventory ({theme})")

                # 3. Daily Ledger
                page.evaluate("switchMainTab('ledger')")
                time.sleep(0.5)
                save_screenshot(page, f"vend_03_ledger_{theme}.png", f"Vendor Daily Ledger ({theme})")

                # 4. Settings / Menu
                page.evaluate("switchMainTab('settings')")
                time.sleep(0.5)
                save_screenshot(page, f"vend_04_menu_{theme}.png", f"Vendor Menu & Settings ({theme})")

            context.close()

            # ==================================================================
            # 3. RUNNER APP SHOWCASE (LIGHT & DARK)
            # ==================================================================
            print("\n--- Capturing Runner App Showcases ---")
            context = browser.new_context(
                viewport={"width": VIEWPORT["width"], "height": VIEWPORT["height"]},
                device_scale_factor=VIEWPORT["dpr"],
                is_mobile=True,
                has_touch=True
            )
            page = context.new_page()

            for theme in ["light", "dark"]:
                page.goto("http://127.0.0.1:8001/runner_dashboard.html")
                page.wait_for_load_state("networkidle")
                time.sleep(1)

                if page.is_visible("#runner-login-gate"):
                    page.click("#btn-runner-login")
                    page.wait_for_selector("#runner-main-content:not(.hidden)", timeout=10000)
                    time.sleep(1)

                page.evaluate(f"""() => {{
                    if ('{theme}' === 'dark') {{
                        document.documentElement.classList.add('dark');
                        document.documentElement.classList.remove('light');
                        localStorage.setItem('gaonbazar_runner_theme', 'dark');
                    }} else {{
                        document.documentElement.classList.remove('dark');
                        document.documentElement.classList.add('light');
                        localStorage.setItem('gaonbazar_runner_theme', 'light');
                    }}
                }}""")
                time.sleep(0.5)

                # 1. Missions Dashboard
                page.evaluate("switchTab('missions')")
                time.sleep(0.5)
                save_screenshot(page, f"runn_01_missions_{theme}.png", f"Runner Missions Dashboard ({theme})")

                # 2. Delivery & Navigation
                page.evaluate("switchTab('detail')")
                time.sleep(0.5)
                save_screenshot(page, f"runn_02_delivery_{theme}.png", f"Runner Navigation & OTP View ({theme})")

                # 3. Earnings Ledger
                page.evaluate("switchTab('ledger')")
                time.sleep(0.5)
                save_screenshot(page, f"runn_03_ledger_{theme}.png", f"Runner Earnings Ledger ({theme})")

                # 4. Profile & Menu Settings
                page.evaluate("switchTab('settings')")
                time.sleep(0.5)
                save_screenshot(page, f"runn_04_menu_{theme}.png", f"Runner Profile & Menu Settings ({theme})")

            context.close()

            # ==================================================================
            # 4. SUPER ADMIN WEB DASHBOARD
            # ==================================================================
            print("\n--- Capturing Super Admin Web Dashboard Showcases ---")
            context = browser.new_context(
                viewport={"width": 1280, "height": 800},
                device_scale_factor=1.0
            )
            page = context.new_page()
            page.goto("http://127.0.0.1:8001/admin_dashboard.html")
            page.wait_for_load_state("networkidle")
            time.sleep(1)

            # Overview & Vendors
            save_screenshot(page, "admin_01_overview.png", "Super Admin Dashboard Overview")

            # God-View Orders
            page.evaluate("switchTab('orders')")
            time.sleep(0.5)
            save_screenshot(page, "admin_02_godview_orders.png", "Super Admin Live Orders God-View")

            # Complaints & Help Desk Tickets
            page.evaluate("switchTab('tickets')")
            time.sleep(0.5)
            save_screenshot(page, "admin_03_tickets_helpdesk.png", "Super Admin Help Desk & Grievance Tickets")

            context.close()
            browser.close()

        print("\n[COMPLETE] All showcase screenshots captured and stored in:")
        print(f"  - {LOCAL_SHOWCASE_DIR}")
        print(f"  - {ARTIFACT_SHOWCASE_DIR}")

    finally:
        if backend_proc:
            backend_proc.terminate()
            kill_port_8001()

if __name__ == "__main__":
    run_showcase()

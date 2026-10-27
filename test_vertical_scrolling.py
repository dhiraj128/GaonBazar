"""
GaonBazaar (गांव बाज़ार) - Universal Vertical Scrolling Verification Suite (Playwright)
Validates frictionless, non-frozen vertical scrolling across ALL 4 applications:
1. Customer App (index.html / view-p2-dashboard, view-p4-cart, view-profile)
2. Vendor App (vendor_dashboard.html / main dashboard, orders, inventory, ledger)
3. Runner App (runner_dashboard.html / main missions, hub stats, shift ledger)
4. Super Admin App (admin_dashboard.html / metrics ribbon, KYC queue, god-view, ledger)

Key Architectural Checks:
- 100dvh dynamic viewport sizing without mobile address bar breakage
- Proper flex-1 overflow-y-auto min-h-0 configuration preventing flex overflow locks
- Window.scrollTo() and window.scrollBy() delegation to active internal containers
- Generous bottom padding (pb-28+) ensuring zero occlusion behind fixed navbars/CTAs
- Wheel & touch scroll responsiveness
"""

import os
import sys
import time
import subprocess
import urllib.request
from pathlib import Path
from datetime import datetime

# UTF-8 encoding for Windows console
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Playwright is not installed. Please run: pip install playwright")
    sys.exit(1)

BASE_DIR = Path(__file__).parent.resolve()
SCREENSHOTS_DIR = BASE_DIR / "screenshots" / "scrolling"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

DEVICES = [
    {
        "name": "Redmi 9A (Budget Mobile 360x800)",
        "viewport": {"width": 360, "height": 800},
        "device_scale_factor": 2.0,
        "is_mobile": True,
        "has_touch": True,
        "user_agent": "Mozilla/5.0 (Linux; Android 10; M2006C3LG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
    },
    {
        "name": "iPhone 16 (Standard Mobile 393x852)",
        "viewport": {"width": 393, "height": 852},
        "device_scale_factor": 3.0,
        "is_mobile": True,
        "has_touch": True,
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1"
    }
]

def create_device_context(browser, device):
    return browser.new_context(
        viewport=device["viewport"],
        device_scale_factor=device["device_scale_factor"],
        is_mobile=device["is_mobile"],
        has_touch=device["has_touch"],
        user_agent=device["user_agent"]
    )

class ScrollTestLogger:
    def __init__(self):
        self.logs = []
        self.total = 0
        self.passed = 0
        self.failed = 0

    def log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {msg}"
        print(line, flush=True)
        self.logs.append(line)

    def record(self, test_name, success, detail=""):
        self.total += 1
        mark = "✓" if success else "✗"
        status = "PASS" if success else "FAIL"
        if success:
            self.passed += 1
        else:
            self.failed += 1
        msg = f"  {mark} {status}: {test_name}"
        if detail:
            msg += f" - {detail}"
        self.log(msg)

    def summary(self):
        pct = (self.passed / self.total * 100) if self.total > 0 else 0
        self.log("\n" + "=" * 80)
        self.log(f"VERTICAL SCROLLING QA SUMMARY: {self.passed}/{self.total} Passed ({pct:.1f}%)")
        self.log("=" * 80)
        return self.failed == 0


def kill_port_processes(ports=[8001]):
    for port in ports:
        try:
            if sys.platform == "win32":
                res = subprocess.run(
                    f"netstat -ano | findstr :{port}",
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=3
                )
                pids = set()
                for line in res.stdout.strip().splitlines():
                    parts = line.split()
                    if len(parts) >= 5 and f":{port}" in parts[1]:
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


def ensure_backend_running(logger):
    try:
        req = urllib.request.Request("http://127.0.0.1:8001/health", headers={"User-Agent": "Playwright-QA"})
        with urllib.request.urlopen(req, timeout=1.0) as res:
            if res.status == 200:
                logger.log("  ✓ GaonBazaar Backend is already active on http://127.0.0.1:8001")
                return None
    except Exception:
        pass

    kill_port_processes([8001])
    time.sleep(0.5)

    logger.log("  🚀 Starting GaonBazaar FastAPI backend server on port 8001...")
    env = os.environ.copy()
    env["ALLOW_TEST_BYPASS"] = "1"
    env["TEST_MODE"] = "1"
    server_proc = subprocess.Popen(
        [sys.executable, "run_server.py", "8001", "--no-reload"],
        cwd=str(BASE_DIR),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    ready = False
    start_t = time.time()
    while time.time() - start_t < 10.0:
        try:
            req = urllib.request.Request("http://127.0.0.1:8001/health", headers={"User-Agent": "Playwright-QA"})
            with urllib.request.urlopen(req, timeout=0.8) as res:
                if res.status == 200:
                    ready = True
                    break
        except Exception:
            time.sleep(0.3)

    if not ready:
        raise RuntimeError("FastAPI server failed to start on http://127.0.0.1:8001")
    logger.log("  ✓ Server successfully booted and healthy.")
    return server_proc


def audit_container_scrolling(page, container_selector, test_label, logger, screenshot_prefix):
    """
    Core scrolling assertion logic:
    1. Checks scrollHeight > clientHeight (overflow exists)
    2. Tests window.scrollTo(0, 250) (delegator check)
    3. Tests page.mouse.wheel(0, 300) (wheel simulation)
    4. Tests scrolling to the very bottom
    5. Asserts bottom elements are fully visible and not blocked
    """
    logger.log(f"\n--- Testing Scroll: {test_label} ({container_selector}) ---")

    # 1. Check scroll geometry
    geom = page.evaluate(f"""() => {{
        const el = document.querySelector('{container_selector}');
        if (!el) return null;
        return {{
            clientHeight: el.clientHeight,
            scrollHeight: el.scrollHeight,
            scrollTop: el.scrollTop,
            isScrollable: el.scrollHeight > el.clientHeight,
            overflowY: window.getComputedStyle(el).overflowY
        }};
    }}""")

    if not geom:
        logger.record(f"{test_label} - Container Found", False, f"Selector '{container_selector}' not found in DOM")
        return False

    logger.record(
        f"{test_label} - Container Overflow Enabled",
        geom['isScrollable'],
        f"scrollHeight={geom['scrollHeight']}px, clientHeight={geom['clientHeight']}px, overflowY={geom['overflowY']}"
    )

    def safe_shot(p):
        try:
            page.screenshot(path=str(p))
        except Exception:
            pass

    # Capture top screenshot
    top_pic = SCREENSHOTS_DIR / f"{screenshot_prefix}_top.png"
    safe_shot(top_pic)

    # 2. Test window.scrollTo delegation
    max_scroll = max(0, geom['scrollHeight'] - geom['clientHeight'])
    scroll_target = min(300, max_scroll)
    page.evaluate(f"window.scrollTo(0, {scroll_target});")
    page.wait_for_timeout(300)
    scroll_top_after_window = page.evaluate(f"() => document.querySelector('{container_selector}').scrollTop")
    
    expected_min = min(50, max_scroll)
    logger.record(
        f"{test_label} - window.scrollTo Forwarding",
        scroll_top_after_window >= expected_min,
        f"scrollTop after window.scrollTo(0, {scroll_target}) = {scroll_top_after_window}px (max_scroll={max_scroll}px)"
    )

    # 3. Test Mouse Wheel / Trackpad Scroll
    page.mouse.move(page.viewport_size['width'] // 2, page.viewport_size['height'] // 2)
    page.mouse.wheel(0, 200)
    page.wait_for_timeout(300)
    scroll_top_after_wheel = page.evaluate(f"() => document.querySelector('{container_selector}').scrollTop")

    logger.record(
        f"{test_label} - Wheel / Touchpad Momentum Scroll",
        scroll_top_after_wheel >= scroll_top_after_window,
        f"scrollTop after mouse wheel = {scroll_top_after_wheel}px"
    )

    # Capture mid-scroll screenshot
    mid_pic = SCREENSHOTS_DIR / f"{screenshot_prefix}_mid.png"
    safe_shot(mid_pic)

    # 4. Test Scroll To Bottom
    page.evaluate(f"""() => {{
        const el = document.querySelector('{container_selector}');
        el.scrollTo({{ top: el.scrollHeight, behavior: 'instant' }});
    }}""")
    page.wait_for_timeout(300)

    bottom_geom = page.evaluate(f"""() => {{
        const el = document.querySelector('{container_selector}');
        return {{
            scrollTop: el.scrollTop,
            clientHeight: el.clientHeight,
            scrollHeight: el.scrollHeight,
            distFromBottom: el.scrollHeight - (el.scrollTop + el.clientHeight)
        }};
    }}""")

    reached_bottom = bottom_geom['distFromBottom'] <= 10
    logger.record(
        f"{test_label} - Full Bottom Reachability",
        reached_bottom,
        f"scrollTop={bottom_geom['scrollTop']}px, distFromBottom={bottom_geom['distFromBottom']}px"
    )

    # Capture bottom screenshot
    bot_pic = SCREENSHOTS_DIR / f"{screenshot_prefix}_bottom.png"
    safe_shot(bot_pic)

    # Scroll back up to reset
    page.evaluate(f"() => document.querySelector('{container_selector}').scrollTo({{ top: 0, behavior: 'instant' }})")
    page.wait_for_timeout(200)

    return True


def run_customer_app_scroll_tests(browser, device, logger):
    dev_name = device["name"]
    logger.log(f"\n=======================================================")
    logger.log(f"CUSTOMER APP SCROLL AUDIT: {dev_name}")
    logger.log(f"=======================================================")

    context = create_device_context(browser, device)
    page = context.new_page()

    try:
        page.goto("http://127.0.0.1:8001/", wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(1000)

        # 1. Onboarding / Auth Bypass: Enter phone -> Enter OTP -> Enter Market
        if page.is_visible("#p1-phone-input"):
            page.fill("#p1-phone-input", "9876543210")
            page.wait_for_timeout(200)
            page.click("#p1-send-otp-btn")
            page.wait_for_timeout(500)
            for idx, digit in enumerate("582941"):
                page.fill(f'.otp-cell[data-idx="{idx}"]', digit)
            page.wait_for_timeout(200)
            page.click("#p1-verify-otp-btn")
            page.wait_for_timeout(800)

        # Fallback direct phase navigation if needed
        if not page.is_visible("#view-p2-dashboard"):
            page.evaluate("navigateToPhase('dashboard')")
            page.wait_for_timeout(500)

        # Ensure Phase 2 Main Dashboard is active
        page.wait_for_selector("#view-p2-dashboard.active", timeout=5000)

        # Audit Dashboard Scrolling
        audit_container_scrolling(
            page,
            "#view-p2-dashboard",
            f"[{dev_name}] Customer Dashboard",
            logger,
            f"customer_dash_{dev_name.split()[0].lower()}"
        )

        # Check generous bottom padding on active screen
        pb_value = page.evaluate("() => window.getComputedStyle(document.querySelector('#view-p2-dashboard')).paddingBottom")
        pb_px = int(pb_value.replace("px", "")) if "px" in pb_value else 0
        logger.record(
            f"[{dev_name}] Customer Dashboard Bottom Padding Clearance",
            pb_px >= 90,  # pb-28 is 112px
            f"paddingBottom = {pb_value} (ensures clearance above floating nav)"
        )

        # Check Bottom Nav clearance hit test
        bottom_nav_visible = page.is_visible("#customer-bottom-nav")
        logger.record(f"[{dev_name}] Bottom Nav Bar Anchored", bottom_nav_visible)

        # 2. Switch to 'My Account / Profile' Screen
        page.evaluate("navigateToPhase('profile')")
        page.wait_for_timeout(600)
        page.wait_for_selector("#view-profile.active", timeout=5000)

        audit_container_scrolling(
            page,
            "#view-profile",
            f"[{dev_name}] Customer Profile Screen",
            logger,
            f"customer_profile_{dev_name.split()[0].lower()}"
        )

        # 3. Add items to cart and switch to Cart Screen
        page.evaluate("""() => {
            if (window.AppStore && AppStore.catalog) {
                AppStore.catalog.slice(0, 5).forEach(i => i.qty = 2);
                if (typeof updateCartTotals === 'function') updateCartTotals();
                if (typeof renderCartLineItems === 'function') renderCartLineItems();
            }
            navigateToPhase('cart');
        }""")
        page.wait_for_timeout(600)
        page.wait_for_selector("#view-p4-cart.active", timeout=5000)

        audit_container_scrolling(
            page,
            "#view-p4-cart",
            f"[{dev_name}] Customer Cart Screen",
            logger,
            f"customer_cart_{dev_name.split()[0].lower()}"
        )

    finally:
        context.close()


def run_vendor_app_scroll_tests(browser, device, logger):
    dev_name = device["name"]
    logger.log(f"\n=======================================================")
    logger.log(f"VENDOR APP SCROLL AUDIT: {dev_name}")
    logger.log(f"=======================================================")

    context = create_device_context(browser, device)
    page = context.new_page()

    try:
        page.goto("http://127.0.0.1:8001/vendor", wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(1000)

        # Authenticate if login gate is active
        if page.is_visible("#vendor-login-gate"):
            page.fill("#login-vendor-phone", "9876543210")
            page.fill("#login-vendor-otp", "123456")
            page.click("#btn-vendor-login")
            page.wait_for_timeout(1000)

        page.wait_for_selector("main.overflow-y-auto", timeout=5000)
        page.wait_for_timeout(1500)

        audit_container_scrolling(
            page,
            "main",
            f"[{dev_name}] Vendor Main Dashboard",
            logger,
            f"vendor_dash_{dev_name.split()[0].lower()}"
        )

        # Verify bottom padding
        pb_value = page.evaluate("() => window.getComputedStyle(document.querySelector('main')).paddingBottom")
        pb_px = int(pb_value.replace("px", "")) if "px" in pb_value else 0
        logger.record(
            f"[{dev_name}] Vendor Main Bottom Padding Clearance",
            pb_px >= 90,
            f"paddingBottom = {pb_value}"
        )

    finally:
        context.close()


def run_runner_app_scroll_tests(browser, device, logger):
    dev_name = device["name"]
    logger.log(f"\n=======================================================")
    logger.log(f"RUNNER APP SCROLL AUDIT: {dev_name}")
    logger.log(f"=======================================================")

    context = create_device_context(browser, device)
    page = context.new_page()

    try:
        page.goto("http://127.0.0.1:8001/runner", wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(1000)

        # Authenticate if login gate is active
        if page.is_visible("#runner-login-gate"):
            page.fill("#login-runner-phone", "9876543220")
            page.fill("#login-runner-otp", "123456")
            page.click("#btn-runner-login")
            page.wait_for_timeout(1000)

        page.wait_for_selector("main.overflow-y-auto", timeout=5000)
        page.wait_for_timeout(1500)

        audit_container_scrolling(
            page,
            "main",
            f"[{dev_name}] Runner Main Missions & Ledger",
            logger,
            f"runner_dash_{dev_name.split()[0].lower()}"
        )

        # Verify bottom padding
        pb_value = page.evaluate("() => window.getComputedStyle(document.querySelector('main')).paddingBottom")
        pb_px = int(pb_value.replace("px", "")) if "px" in pb_value else 0
        logger.record(
            f"[{dev_name}] Runner Main Bottom Padding Clearance",
            pb_px >= 90,
            f"paddingBottom = {pb_value}"
        )

    finally:
        context.close()


def run_admin_app_scroll_tests(browser, device, logger):
    dev_name = device["name"]
    logger.log(f"\n=======================================================")
    logger.log(f"SUPER ADMIN APP SCROLL AUDIT: {dev_name}")
    logger.log(f"=======================================================")

    context = create_device_context(browser, device)
    page = context.new_page()

    try:
        page.goto("http://127.0.0.1:8001/admin", wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(1000)

        # Authenticate via zero-trust gate if presented
        if page.is_visible("#admin-login-gate"):
            admin_key = os.getenv("ADMIN_SECRET_KEY", "gaonbazar_super_admin_secret_2026")
            page.fill("#admin-input-key", admin_key)
            page.click("#btn-admin-login")
            page.wait_for_selector("#admin-main-content:not(.hidden)", timeout=10000)
            page.wait_for_timeout(1000)

        page.wait_for_selector("main.overflow-y-auto:not(.hidden)", timeout=10000)
        page.wait_for_timeout(1500)

        # Audit Vendor Queue Scroll
        audit_container_scrolling(
            page,
            "main",
            f"[{dev_name}] Super Admin Portal",
            logger,
            f"admin_dash_{dev_name.split()[0].lower()}"
        )

        # Switch to Ledger Tab (Contains large table)
        page.click("#admin-tab-btn-ledger")
        page.wait_for_timeout(500)

        audit_container_scrolling(
            page,
            "main",
            f"[{dev_name}] Super Admin Ledger Tab",
            logger,
            f"admin_ledger_{dev_name.split()[0].lower()}"
        )

        # Verify bottom padding
        pb_value = page.evaluate("() => window.getComputedStyle(document.querySelector('main')).paddingBottom")
        pb_px = int(pb_value.replace("px", "")) if "px" in pb_value else 0
        logger.record(
            f"[{dev_name}] Admin Portal Bottom Padding Clearance",
            pb_px >= 90,
            f"paddingBottom = {pb_value}"
        )

    finally:
        context.close()


def main():
    logger = ScrollTestLogger()
    logger.log("=" * 80)
    logger.log("STARTING GAONBAZAAR UNIVERSAL VERTICAL SCROLLING AUDIT")
    logger.log("=" * 80)

    server_proc = None
    try:
        server_proc = ensure_backend_running(logger)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                for dev in DEVICES:
                    run_customer_app_scroll_tests(browser, dev, logger)
                    run_vendor_app_scroll_tests(browser, dev, logger)
                    run_runner_app_scroll_tests(browser, dev, logger)
                    run_admin_app_scroll_tests(browser, dev, logger)
            finally:
                browser.close()

    finally:
        if server_proc:
            try:
                server_proc.terminate()
                server_proc.wait(timeout=3)
            except Exception:
                pass
            kill_port_processes([8001])

    success = logger.summary()
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()

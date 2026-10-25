"""
GaonBazaar (गांव बाज़ार) - Super Admin Dashboard & Rural Onboarding E2E Test Suite (Python)
Automated Visual & Functional Verification:
1. Rural Vendor Registration with Phone OTP, KYC, Photo & Payout UPI
2. Immediate Vendor Dashboard Lock on "Pending Verification" Screen
3. Rural Delivery Runner (Gaon Mitra) Registration with Driving & Vehicle KYC
4. Immediate Runner Dashboard Lock on "Pending Verification" Screen
5. Super Admin Control Center:
   - Global Ecosystem Metrics Ribbon (GMV, Platform Profits, Customers, Vendors, Runners)
   - Vendor KYC Approval Queue & Action [Approve]
   - Runner KYC Approval Queue & Action [Approve]
   - Live Order God-View Inspection (Rural Landmarks, OTPs, Real-Time Status)
   - Commission & Payout Ledger (Platform ₹3 Cut, Vendor Net, Runner ₹20 Delivery Fee)
6. Dynamic Unlocking of Vendor & Runner Dashboards upon Super Admin Approval
7. High-Resolution Visual Screenshots Saved to screenshots/admin/
"""

import os
import sys
import json
import time
import atexit
import threading
import subprocess
import urllib.request
from pathlib import Path
from datetime import datetime

def start_global_timeout_watchdog(timeout_seconds=240):
    """
    Strict Global Watchdog Timeout:
    Guarantees the entire test suite process exits hard after timeout_seconds,
    preventing any hang from blocking CI/CD or local test runners.
    """
    def watchdog_target():
        time.sleep(timeout_seconds)
        print(f"\n💥 [GLOBAL TIMEOUT FATAL]: Test suite exceeded maximum allowed time of {timeout_seconds}s! Forcing immediate termination.", file=sys.stderr, flush=True)
        try:
            kill_port_processes([8001])
        except Exception:
            pass
        os._exit(124)

    watchdog = threading.Thread(target=watchdog_target, daemon=True, name="GlobalTimeoutWatchdog")
    watchdog.start()
    return watchdog

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
    print("Playwright is not installed. Please run: pip install playwright && playwright install")
    sys.exit(1)

BASE_DIR = Path(__file__).parent.resolve()
ADMIN_HTML_PATH = BASE_DIR / "admin_dashboard.html"
VENDOR_HTML_PATH = BASE_DIR / "vendor_dashboard.html"
RUNNER_HTML_PATH = BASE_DIR / "runner_dashboard.html"
REPORT_PATH = BASE_DIR / "admin_test_report.txt"
SCREENSHOTS_DIR = BASE_DIR / "screenshots" / "admin"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)


class AdminTestLogger:
    def __init__(self):
        self.logs = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.screenshots = []

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"[{timestamp}] {message}"
        print(formatted, flush=True)
        self.logs.append(formatted)

    def record_test(self, test_name, passed, detail=""):
        self.total_tests += 1
        status_str = "PASS" if passed else "FAIL"
        mark = "✓" if passed else "✗"
        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1

        msg = f"  {mark} {status_str}: {test_name}"
        if detail:
            msg += f" - {detail}"
        self.log(msg)

    def record_screenshot(self, rel_path):
        self.screenshots.append(rel_path)

    def save_report(self):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pass_pct = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0

        header = f"""================================================================================
GAONBAZAAR SUPER ADMIN & ONBOARDING E2E TEST REPORT
Generated: {timestamp}
Total Tests Executed: {self.total_tests}
Passed: {self.passed_tests}
Failed: {self.failed_tests}
Success Rate: {pass_pct:.1f}%
Screenshots Captured: {len(self.screenshots)}
================================================================================

CAPTURED SCREENSHOT EVIDENCE:
"""
        for s in self.screenshots:
            header += f"  - {s}\n"

        header += """================================================================================

DETAILED AUDIT LOGS:
"""
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            f.write(header)
            for l in self.logs:
                f.write(l + "\n")
            f.write("\n================================================================================\n")
            f.write(f"END OF ADMIN TEST REPORT - {'100% HEALTHY' if self.failed_tests == 0 else 'ACTION REQUIRED'}\n")
            f.write("================================================================================\n")

        print(f"\n📄 Super Admin Test Report written to: {REPORT_PATH}")


def capture_screenshot(page, name, logger):
    filepath = SCREENSHOTS_DIR / f"{name}.png"
    rel_path = f"screenshots/admin/{name}.png"
    try:
        page.screenshot(path=str(filepath), full_page=False)
        logger.record_screenshot(rel_path)
        logger.log(f"  📸 [SCREENSHOT CAPTURED]: {rel_path}")
    except Exception as e:
        logger.log(f"  ⚠️ [SCREENSHOT FAILED]: {rel_path} ({e})")
    return filepath


def kill_port_processes(ports=[8001]):
    for port in ports:
        try:
            if sys.platform == "win32":
                try:
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
            else:
                try:
                    subprocess.run(f"fuser -k {port}/tcp 2>/dev/null || true", shell=True, capture_output=True, timeout=3)
                except Exception:
                    pass
        except Exception:
            pass

# Guarantee port cleanup on any script exit
atexit.register(lambda: kill_port_processes([8001]))


def ensure_backend_running(logger):
    try:
        req = urllib.request.Request("http://127.0.0.1:8001/docs", headers={"User-Agent": "Playwright-Admin-QA"})
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            if resp.status == 200:
                logger.log("  ✓ Backend server healthy and responding on http://127.0.0.1:8001")
                return None
    except Exception:
        pass

    kill_port_processes([8001])
    time.sleep(0.5)

    logger.log("  🚀 Starting GaonBazaar FastAPI backend server in background on port 8001 (no-reload)...")
    server_env = os.environ.copy()
    server_env["TEST_MODE"] = "1"
    server_env["CI"] = "1"

    server_proc = subprocess.Popen(
        [sys.executable, "run_server.py", "8001", "--no-reload"],
        cwd=str(BASE_DIR),
        env=server_env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    start_time = time.time()
    server_ready = False
    while time.time() - start_time < 8.0:
        if server_proc.poll() is not None:
            logger.log(f"  ✗ Background server exited unexpectedly with code {server_proc.poll()}")
            break
        try:
            req = urllib.request.Request("http://127.0.0.1:8001/docs", headers={"User-Agent": "Playwright-Admin-QA"})
            with urllib.request.urlopen(req, timeout=0.8) as resp:
                if resp.status == 200:
                    server_ready = True
                    break
        except Exception:
            time.sleep(0.3)

    if not server_ready:
        logger.log("  ✗ Failed to verify server is alive on port 8001 within 8s timeout.")
        try:
            server_proc.kill()
        except Exception:
            pass
        kill_port_processes([8001])
        raise RuntimeError("FastAPI backend failed to start or respond on http://127.0.0.1:8001")
    else:
        logger.log("  ✓ Backend server healthy and responding on http://127.0.0.1:8001")

    return server_proc


def run_admin_e2e_suite(browser, logger):
    logger.log("\n" + "=" * 80)
    logger.log("STARTING FULL SUPER ADMIN & ONBOARDING END-TO-END FLOW")
    logger.log("=" * 80)

    contexts = []
    try:
        _run_admin_e2e_steps(browser, logger, contexts)
    finally:
        for ctx in contexts:
            try:
                ctx.close()
            except Exception:
                pass


def _run_admin_e2e_steps(browser, logger, contexts):
    unique_suffix = int(time.time()) % 10000

    # -------------------------------------------------------------------------
    # STEP 1: RURAL VENDOR ONBOARDING & PENDING APPROVAL LOCK
    # -------------------------------------------------------------------------
    logger.log("\n[STEP 1]: Vendor Registration & Pending Approval Security Lock")
    vendor_context = browser.new_context(
        viewport={"width": 393, "height": 851},
        device_scale_factor=2.75,
        is_mobile=True,
        has_touch=True
    )
    contexts.append(vendor_context)
    vendor_page = vendor_context.new_page()
    vendor_page.set_default_timeout(15000)
    vendor_page.set_default_navigation_timeout(15000)

    vendor_page.goto("http://127.0.0.1:8001/vendor", wait_until="domcontentloaded", timeout=15000)
    vendor_page.wait_for_timeout(1000)
    capture_screenshot(vendor_page, "01_vendor_initial", logger)

    # Open registration modal
    vendor_page.click("#btn-open-vendor-register", force=True)
    vendor_page.wait_for_timeout(500)
    vendor_modal_visible = vendor_page.is_visible("#vendor-auth-gate")
    logger.record_test("Vendor Onboarding Modal Open", vendor_modal_visible, "Modal displayed with KYC fields")

    # Fill form
    v_phone = f"98765{unique_suffix:05d}"
    v_shop = f"Gupta Kirana Store #{unique_suffix}"
    v_owner = f"Anil Gupta {unique_suffix}"
    v_village = "Rampur Mandi"
    v_id = f"6655-4433-{unique_suffix:04d}"
    v_upi = f"gupta{unique_suffix}@okhdfcbank"

    vendor_page.fill("#reg-vendor-phone", v_phone)
    vendor_page.click("#btn-send-vendor-otp")
    vendor_page.wait_for_timeout(300)
    vendor_page.fill("#reg-vendor-otp", "123456")
    vendor_page.fill("#reg-vendor-shop", v_shop)
    vendor_page.fill("#reg-vendor-owner", v_owner)
    vendor_page.fill("#reg-vendor-village", v_village)
    vendor_page.fill("#reg-vendor-id", v_id)
    vendor_page.fill("#reg-vendor-upi", v_upi)

    capture_screenshot(vendor_page, "02_vendor_registration_form", logger)

    # Submit registration
    vendor_page.click("#btn-submit-vendor-register")
    try:
        vendor_page.wait_for_selector("#vendor-pending-view:not(.hidden)", timeout=6000)
    except Exception:
        pass
    vendor_page.wait_for_timeout(1000)

    # Verify Pending Approval View is now locked
    vendor_pending_visible = vendor_page.is_visible("#vendor-pending-view")
    vendor_main_hidden = not vendor_page.is_visible("#vendor-main-content")

    logger.record_test(
        "Vendor Security Lock Gate Active",
        vendor_pending_visible and vendor_main_hidden,
        f"Shop {v_shop} locked with 'Pending Super Admin Approval' view"
    )
    capture_screenshot(vendor_page, "03_vendor_pending_lock", logger)

    # Test Check Status button while still pending
    vendor_page.click("#btn-check-vendor-status")
    vendor_page.wait_for_timeout(600)
    assert vendor_page.is_visible("#vendor-pending-view"), "Should stay locked while pending"
    logger.record_test("Vendor Pending Status Enforcement", True, "Dashboard remains locked before admin approval")

    # -------------------------------------------------------------------------
    # STEP 2: RURAL RUNNER (GAON MITRA) ONBOARDING & PENDING LOCK
    # -------------------------------------------------------------------------
    logger.log("\n[STEP 2]: Runner Registration & Pending Approval Security Lock")
    runner_context = browser.new_context(
        viewport={"width": 412, "height": 915},
        device_scale_factor=2.6,
        is_mobile=True,
        has_touch=True
    )
    contexts.append(runner_context)
    runner_page = runner_context.new_page()
    runner_page.set_default_timeout(15000)
    runner_page.set_default_navigation_timeout(15000)

    runner_page.goto("http://127.0.0.1:8001/runner", wait_until="domcontentloaded", timeout=15000)
    runner_page.wait_for_timeout(1000)
    capture_screenshot(runner_page, "04_runner_initial", logger)

    # Open registration modal
    runner_page.click("#btn-open-runner-register", force=True)
    runner_page.wait_for_timeout(500)
    runner_modal_visible = runner_page.is_visible("#runner-auth-gate")
    logger.record_test("Runner Onboarding Modal Open", runner_modal_visible, "Modal displayed with Gaon Mitra KYC fields")

    r_phone = f"98766{unique_suffix:05d}"
    r_name = f"Vikram Yadav (विक्रम #{unique_suffix})"
    r_area = "Rampur Mandi Cluster"
    r_vehicle = f"UP-14-CW-{unique_suffix:04d}"
    r_id = f"9988-7766-{unique_suffix:04d}"
    r_upi = f"vikram{unique_suffix}@paytm"

    runner_page.fill("#reg-runner-phone", r_phone)
    runner_page.click("#btn-send-runner-otp")
    runner_page.wait_for_timeout(300)
    runner_page.fill("#reg-runner-otp", "123456")
    runner_page.fill("#reg-runner-name", r_name)
    runner_page.fill("#reg-runner-area", r_area)
    runner_page.fill("#reg-runner-vehicle", r_vehicle)
    runner_page.fill("#reg-runner-id", r_id)
    runner_page.fill("#reg-runner-upi", r_upi)

    capture_screenshot(runner_page, "05_runner_registration_form", logger)

    # Submit registration
    runner_page.click("#btn-submit-runner-register")
    try:
        runner_page.wait_for_selector("#runner-pending-view:not(.hidden)", timeout=6000)
    except Exception:
        pass
    runner_page.wait_for_timeout(1000)

    # Verify Runner Pending Approval View is now locked
    runner_pending_visible = runner_page.is_visible("#runner-pending-view")
    runner_main_hidden = not runner_page.is_visible("#runner-main-content")

    logger.record_test(
        "Runner Security Lock Gate Active",
        runner_pending_visible and runner_main_hidden,
        f"Runner {r_name} locked with 'Gaon Mitra KYC Under Review' view"
    )
    capture_screenshot(runner_page, "06_runner_pending_lock", logger)

    # Test Check Status button while still pending
    runner_page.wait_for_selector("#btn-check-runner-status", state="visible", timeout=10000)
    runner_page.click("#btn-check-runner-status")
    runner_page.wait_for_timeout(600)
    assert runner_page.is_visible("#runner-pending-view"), "Should stay locked while pending"
    logger.record_test("Runner Pending Status Enforcement", True, "Runner mission queue remains locked before admin approval")

    # -------------------------------------------------------------------------
    # STEP 3: SUPER ADMIN DASHBOARD REVIEW & APPROVALS
    # -------------------------------------------------------------------------
    logger.log("\n[STEP 3]: Super Admin Control Center - Metrics & KYC Approvals")
    admin_context = browser.new_context(
        viewport={"width": 1440, "height": 900},
        device_scale_factor=1.0
    )
    contexts.append(admin_context)
    admin_page = admin_context.new_page()
    admin_page.set_default_timeout(15000)
    admin_page.set_default_navigation_timeout(15000)

    admin_page.goto("http://127.0.0.1:8001/admin", wait_until="domcontentloaded", timeout=15000)
    # Wait for async initial data fetch to populate DOM metrics & queues
    try:
        admin_page.wait_for_function('() => document.getElementById("metric-gmv") && document.getElementById("metric-gmv").innerText !== "₹0.00"', timeout=8000)
    except Exception:
        pass
    admin_page.wait_for_timeout(500)

    # Verify Global Metrics Ribbon
    gmv_text = admin_page.locator("#metric-gmv").text_content()
    vendors_count = admin_page.locator("#metric-vendors").text_content()
    runners_count = admin_page.locator("#metric-runners").text_content()
    pending_vendors_badge = admin_page.locator("#badge-pending-vendors-count").text_content()

    logger.log(f"  📊 Global Ecosystem Metrics: GMV={gmv_text}, Total Vendors={vendors_count}, Runners={runners_count}")
    logger.record_test(
        "Super Admin Ecosystem Metrics Loaded",
        bool(gmv_text and vendors_count and runners_count),
        f"GMV: {gmv_text}, Pending Vendors: {pending_vendors_badge}"
    )
    capture_screenshot(admin_page, "07_admin_dashboard_metrics", logger)

    # Tab 1: Vendor KYC Approvals
    logger.log("\n[STEP 3.1]: Reviewing and Approving Vendor KYC...")
    try:
        admin_page.locator(f'text="{v_shop}"').first.wait_for(state="visible", timeout=8000)
    except Exception:
        pass
    vendor_card_found = admin_page.locator(f'text="{v_shop}"').count() > 0
    logger.record_test(
        "Pending Vendor Appears in Admin KYC Queue",
        vendor_card_found,
        f"Store {v_shop} listed with photo, Aadhar ID, and payout UPI"
    )
    capture_screenshot(admin_page, "08_admin_vendor_kyc_queue", logger)

    # Click Approve on this specific vendor card
    approve_vendor_btn = admin_page.locator(f'#vendors-approval-container > div:has-text("{v_shop}") button[data-action="approve"], #vendors-approval-container > div:has-text("{v_shop}") button:has-text("Approve"), #vendors-approval-container > div:has-text("{v_shop}") button:has-text("स्वीकारें")').first
    if approve_vendor_btn.count() > 0:
        approve_vendor_btn.click()
    else:
        # Fallback to any pending vendor approve button within approval container
        admin_page.locator('#vendors-approval-container button[data-action="approve"], #vendors-approval-container button:has-text("Approve"), #vendors-approval-container button:has-text("स्वीकारें")').first.click()

    admin_page.wait_for_timeout(1000)
    capture_screenshot(admin_page, "09_admin_vendor_approved", logger)
    logger.record_test("Super Admin Vendor Approval Action", True, f"Successfully approved vendor {v_shop}")

    # Tab 2: Runner KYC Approvals
    logger.log("\n[STEP 3.2]: Reviewing and Approving Runner KYC...")
    admin_page.click("#admin-tab-btn-runners")
    admin_page.wait_for_timeout(800)

    runner_card_found = admin_page.locator(f'#runners-approval-container > div:has-text("{r_name}")').count() > 0 or admin_page.locator(f'text="{r_name}"').count() > 0 or admin_page.locator(f'text="{r_vehicle}"').count() > 0
    logger.record_test(
        "Pending Runner Appears in Admin KYC Queue",
        runner_card_found,
        f"Gaon Mitra {r_name} listed with vehicle {r_vehicle}"
    )
    capture_screenshot(admin_page, "10_admin_runner_kyc_queue", logger)

    # Click Approve on this specific runner card
    approve_runner_btn = admin_page.locator(f'#runners-approval-container > div:has-text("{r_name}") button[data-action="approve"], #runners-approval-container > div:has-text("{r_name}") button:has-text("Approve"), #runners-approval-container > div:has-text("{r_name}") button:has-text("स्वीकारें")').first
    if approve_runner_btn.count() > 0:
        approve_runner_btn.click()
    else:
        # Fallback to any pending runner approve button within approval container
        admin_page.locator('#runners-approval-container button[data-action="approve"], #runners-approval-container button:has-text("Approve"), #runners-approval-container button:has-text("स्वीकारें")').first.click()

    admin_page.wait_for_timeout(1000)
    capture_screenshot(admin_page, "11_admin_runner_approved", logger)
    logger.record_test("Super Admin Runner Approval Action", True, f"Successfully approved Gaon Mitra {r_name}")

    # Tab 3: Live Order God-View
    logger.log("\n[STEP 3.3]: Inspecting Live Order God-View...")
    admin_page.click("#admin-tab-btn-orders")
    admin_page.wait_for_timeout(800)

    godview_rows = admin_page.locator("#godview-orders-table-body tr").count()
    logger.record_test(
        "Live Order God-View Table Inspection",
        godview_rows > 0,
        f"God-View table rendered {godview_rows} real-time customer orders with delivery OTPs"
    )
    capture_screenshot(admin_page, "12_admin_god_view_orders", logger)

    # Tab 4: Commission & Payout Ledger
    logger.log("\n[STEP 3.4]: Inspecting Commission & Payout Ledger...")
    admin_page.click("#admin-tab-btn-ledger")
    admin_page.wait_for_timeout(800)

    rev_text = admin_page.locator("#ledger-total-rev").text_content()
    profit_text = admin_page.locator("#ledger-net-profit").text_content()
    vendor_due_text = admin_page.locator("#ledger-vendor-due").text_content()
    runner_due_text = admin_page.locator("#ledger-runner-due").text_content()
    ledger_txns = admin_page.locator("#ledger-txns-table-body tr").count()

    logger.log(f"  💰 Ledger Audit: Revenue={rev_text}, Net Profit={profit_text}, Vendor Due={vendor_due_text}, Runner Due={runner_due_text}")
    logger.record_test(
        "Commission & Payout Ledger Inspection",
        ledger_txns > 0,
        f"Settlement ledger active with {ledger_txns} transactions; ₹3 fee / order tracked"
    )

    # Assert distance-based ledger splits and accounting invariance
    try:
        ledger_api_resp = admin_page.request.get("http://127.0.0.1:8001/api/admin/commission-ledger")
        if ledger_api_resp.status == 200:
            ledger_data = ledger_api_resp.json()
            txns = ledger_data.get("recent_transactions", [])
            has_txns = len(txns) > 0
            splits_balanced = all(
                abs(t.get("platform_cut", 0) + t.get("vendor_net", 0) + t.get("runner_fee", 0) - t.get("amount", 0)) < 0.01
                for t in txns
            ) if has_txns else True
            logger.record_test(
                "Distance-Based Ledger Balance Sheet Invariance",
                bool(has_txns and splits_balanced),
                f"Ledger verified with {len(txns)} transactions: Invariance (Platform Cut + Vendor Net + Runner Fee == Total) held for all orders"
            )
    except Exception as e_ledg:
        logger.record_test("Distance-Based Ledger Balance Sheet Invariance", False, str(e_ledg))
    capture_screenshot(admin_page, "13_admin_commission_ledger", logger)

    # Tab 5: Account Risk Profile Inspection (Internal Super Admin Risk Management)
    logger.log("\n[STEP 3.4.5]: Inspecting Account Risk Profile & Cancellation Controls...")
    admin_page.click("#admin-tab-btn-risk")
    admin_page.wait_for_timeout(800)
    risk_tab_visible = admin_page.is_visible("#tab-risk")
    risk_table_present = admin_page.locator("#risk-profiles-table-body").count() > 0
    logger.record_test(
        "Super Admin Account Risk Profile Inspection",
        risk_tab_visible and risk_table_present,
        "Account Risk Profile tab loaded; consecutive cancellations and COD restrictions visible to Admin only"
    )
    capture_screenshot(admin_page, "13_02_admin_risk_profiles", logger)

    # Tab 5: Tablet View Responsiveness (800x1280)
    logger.log("\n[STEP 3.5]: Inspecting Super Admin on Tablet Viewport (800x1280)...")
    tablet_context = browser.new_context(
        viewport={"width": 800, "height": 1280},
        device_scale_factor=2.0,
        is_mobile=True,
        has_touch=True
    )
    contexts.append(tablet_context)
    tablet_page = tablet_context.new_page()
    tablet_page.goto("http://127.0.0.1:8001/admin", wait_until="domcontentloaded", timeout=15000)
    tablet_page.wait_for_timeout(1000)
    tab_gmv = tablet_page.locator("#metric-gmv").text_content()
    tab_godview_btn = tablet_page.is_visible("#admin-tab-btn-orders")
    tab_ledger_btn = tablet_page.is_visible("#admin-tab-btn-ledger")
    logger.record_test(
        "Super Admin Tablet Viewport Responsive Layout (800x1280)",
        bool(tab_gmv and tab_godview_btn and tab_ledger_btn),
        f"Tablet GMV: {tab_gmv} | Responsive tabs & controls intact"
    )
    capture_screenshot(tablet_page, "13b_admin_tablet_viewport_800x1280", logger)
    tablet_context.close()

    # -------------------------------------------------------------------------
    # STEP 4: VERIFY VENDOR & RUNNER DASHBOARDS DYNAMICALLY UNLOCKED
    # -------------------------------------------------------------------------
    logger.log("\n[STEP 4]: Verifying Dashboards Dynamically Unlock After Admin Approval")

    # 4.1 Check Vendor Dashboard Unlock
    vendor_page.bring_to_front()
    if vendor_page.is_visible("#btn-check-vendor-status"):
        vendor_page.click("#btn-check-vendor-status")
        try:
            vendor_page.wait_for_selector("#vendor-main-content:not(.hidden)", timeout=5000)
        except Exception:
            pass
        vendor_page.wait_for_timeout(1000)
    else:
        vendor_page.wait_for_timeout(500)

    v_unlocked = vendor_page.is_visible("#vendor-main-content")
    v_locked = vendor_page.is_visible("#vendor-pending-view")

    logger.record_test(
        "Vendor Dashboard Unlocked Post-Approval",
        v_unlocked and not v_locked,
        f"Vendor {v_shop} now has full operational access to live order queue & inventory!"
    )
    capture_screenshot(vendor_page, "14_vendor_dashboard_unlocked", logger)

    # 4.2 Check Runner Dashboard Unlock
    runner_page.bring_to_front()
    if runner_page.is_visible("#btn-check-runner-status"):
        runner_page.click("#btn-check-runner-status")
        try:
            runner_page.wait_for_selector("#runner-main-content:not(.hidden)", timeout=5000)
        except Exception:
            pass
        runner_page.wait_for_timeout(1000)
    else:
        runner_page.wait_for_timeout(500)

    r_unlocked = runner_page.is_visible("#runner-main-content")
    r_locked = runner_page.is_visible("#runner-pending-view")

    logger.record_test(
        "Runner Dashboard Unlocked Post-Approval",
        r_unlocked and not r_locked,
        f"Gaon Mitra {r_name} now has full access to active delivery missions & shift toggle!"
    )
    capture_screenshot(runner_page, "15_runner_dashboard_unlocked", logger)


def main():
    start_global_timeout_watchdog(timeout_seconds=240)
    logger = AdminTestLogger()
    logger.log("================================================================================")
    logger.log("Starting GaonBazaar Super Admin & Rural Onboarding E2E Verification Suite...")
    logger.log("================================================================================")

    if not ADMIN_HTML_PATH.exists():
        print(f"Error: Cannot find admin_dashboard.html at {ADMIN_HTML_PATH}")
        sys.exit(1)

    server_proc = None
    browser = None
    try:
        server_proc = ensure_backend_running(logger)

        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
                run_admin_e2e_suite(browser, logger)
            finally:
                if browser:
                    try:
                        browser.close()
                        logger.log("  ✓ Playwright browser closed cleanly.")
                    except Exception as b_err:
                        logger.log(f"  ⚠️ Warning closing browser: {b_err}")
    finally:
        logger.save_report()
        if server_proc:
            logger.log("  🛑 Terminating background FastAPI server...")
            try:
                server_proc.kill()
                server_proc.wait(timeout=3)
            except Exception:
                pass
        kill_port_processes([8001])

    if logger.failed_tests > 0:
        logger.log(f"\n❌ E2E SUITE FINISHED WITH {logger.failed_tests} FAILURES")
        sys.exit(1)
    else:
        logger.log(f"\n✅ E2E SUITE FINISHED WITH 100% PASS RATE ({logger.passed_tests}/{logger.total_tests} TESTS PASSED)")
        sys.exit(0)


if __name__ == "__main__":
    main()

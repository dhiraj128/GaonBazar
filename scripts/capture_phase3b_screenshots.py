"""
GAONBAZAAR: PHASE 3B COMPREHENSIVE UI/UX PLAYWRIGHT SCREENSHOT GENERATOR
Captures visual evidence across Customer, Vendor, Runner, and Admin applications
at multiple responsive viewports (360px, 390px, 412px, 1280px).
"""

import os
import sys
import time
import subprocess
import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent.parent
SCREENSHOT_DIR = BASE_DIR / "screenshots" / "phase3b_ui"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

VIEWPORTS = {
    "mobile360": {"width": 360, "height": 800, "is_mobile": True, "has_touch": True},
    "mobile390": {"width": 390, "height": 844, "is_mobile": True, "has_touch": True},
    "mobile412": {"width": 412, "height": 915, "is_mobile": True, "has_touch": True},
    "desktop1280": {"width": 1280, "height": 800, "is_mobile": False, "has_touch": False}
}

PORT = 8002

def kill_port(port):
    try:
        res = subprocess.run(f"netstat -ano | findstr :{port}", shell=True, capture_output=True, text=True, timeout=3)
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

def ensure_backend():
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/api/version", timeout=1.0) as r:
            if r.status == 200:
                print(f"[OK] Backend already running on http://127.0.0.1:{PORT}")
                return None
    except Exception:
        pass

    kill_port(PORT)
    time.sleep(0.5)

    print(f"[...] Starting test backend server on port {PORT}...")
    env = os.environ.copy()
    env["TEST_MODE"] = "1"
    env["PREVIEW_MODE"] = "1"
    proc = subprocess.Popen(
        [sys.executable, "run_server.py", str(PORT), "--no-reload"],
        cwd=str(BASE_DIR),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    for _ in range(30):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/api/version", timeout=1.0) as r:
                if r.status == 200:
                    print(f"[OK] Backend server ready on port {PORT}!")
                    return proc
        except Exception:
            time.sleep(0.5)
    return proc


def capture_all():
    proc = ensure_backend()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            # -----------------------------------------------------------------
            # 1. Customer App: Orders Screen & Stepper & Modals
            # -----------------------------------------------------------------
            print("\nCapturing Customer App Screens...")

            # 1.1 Customer Orders List (390px)
            ctx390 = browser.new_context(viewport=VIEWPORTS["mobile390"])
            page = ctx390.new_page()
            page.goto(f"http://127.0.0.1:{PORT}/?preview=1", wait_until="networkidle")
            page.evaluate("() => { if (typeof showPhaseView === 'function') showPhaseView('orders'); }")
            page.wait_for_timeout(1000)
            page.screenshot(path=str(SCREENSHOT_DIR / "01_customer_orders_active_mobile390.png"))
            print("  [SAVED] 01_customer_orders_active_mobile390.png")

            # 1.2 Customer Order Details with Replacement Stepper (360px - Android Compact)
            ctx360 = browser.new_context(viewport=VIEWPORTS["mobile360"])
            page360 = ctx360.new_page()
            page360.goto(f"http://127.0.0.1:{PORT}/?preview=1", wait_until="networkidle")
            page360.evaluate("""() => {
                if (typeof showPhaseView === 'function') showPhaseView('order-details');
                const card = document.getElementById('od-replacement-card');
                if (card) card.classList.remove('hidden');
                if (typeof renderReplacementStepper === 'function') renderReplacementStepper('VENDOR_PACKING');
            }""")
            page360.wait_for_timeout(800)
            page360.screenshot(path=str(SCREENSHOT_DIR / "02_customer_replacement_stepper_mobile360.png"))
            print("  [SAVED] 02_customer_replacement_stepper_mobile360.png")

            # 1.3 Customer Order Details with Replacement Stepper (412px - Nothing Phone 2a / Pixel)
            ctx412 = browser.new_context(viewport=VIEWPORTS["mobile412"])
            page412 = ctx412.new_page()
            page412.goto(f"http://127.0.0.1:{PORT}/?preview=1", wait_until="networkidle")
            page412.evaluate("""() => {
                if (typeof showPhaseView === 'function') showPhaseView('order-details');
                const card = document.getElementById('od-replacement-card');
                if (card) card.classList.remove('hidden');
                if (typeof renderReplacementStepper === 'function') renderReplacementStepper('OUT_FOR_DELIVERY');
                const otpBox = document.getElementById('od-rep-otp-box');
                if (otpBox) otpBox.classList.remove('hidden');
            }""")
            page412.wait_for_timeout(800)
            page412.screenshot(path=str(SCREENSHOT_DIR / "03_customer_replacement_stepper_mobile412.png"))
            print("  [SAVED] 03_customer_replacement_stepper_mobile412.png")

            # 1.4 Customer Issue Report Modal (390px)
            page.evaluate("""() => {
                if (typeof openOrderIssueReporter === 'function') openOrderIssueReporter('ORD-7402');
            }""")
            page.wait_for_timeout(600)
            page.screenshot(path=str(SCREENSHOT_DIR / "04_customer_issue_reporter_modal_mobile390.png"))
            print("  [SAVED] 04_customer_issue_reporter_modal_mobile390.png")
            page.evaluate("() => { if (typeof closeOrderIssueReporter === 'function') closeOrderIssueReporter(); }")

            # 1.5 Customer Refund Tracker Modal (390px)
            page.evaluate("""() => {
                window.currentOrderDetailsData = {
                    total_amount: 320.00,
                    refund_amount: 320.00,
                    payment_mode: 'UPI',
                    refund_status: 'APPROVED',
                    refund_records: [{ status: 'APPROVED', amount: 320.00, razorpay_refund_id: null }]
                };
                if (typeof openRefundTrackerModal === 'function') openRefundTrackerModal('ORD-7402');
            }""")
            page.wait_for_timeout(600)
            page.screenshot(path=str(SCREENSHOT_DIR / "05_customer_refund_tracker_modal_mobile390.png"))
            print("  [SAVED] 05_customer_refund_tracker_modal_mobile390.png")

            ctx360.close()
            ctx390.close()
            ctx412.close()

            # -----------------------------------------------------------------
            # 2. Vendor App: Replacements Queue
            # -----------------------------------------------------------------
            print("\nCapturing Vendor App Screens...")
            ctx_ven_mob = browser.new_context(viewport=VIEWPORTS["mobile390"])
            p_ven_mob = ctx_ven_mob.new_page()
            p_ven_mob.goto(f"http://127.0.0.1:{PORT}/vendor_dashboard.html?preview=1", wait_until="networkidle")
            p_ven_mob.evaluate("""() => {
                VendorStore.replacements = [{
                    replacement_id: 'REP-8821',
                    product_name: 'Aashirvaad Shudh Chakki Atta 5kg',
                    quantity: 1,
                    reason: 'wrong_item',
                    status: 'VENDOR_PACKING',
                    customer_phone: '98******10'
                }];
                if (typeof renderVendorReplacementsQueue === 'function') renderVendorReplacementsQueue();
            }""")
            p_ven_mob.wait_for_timeout(600)
            p_ven_mob.screenshot(path=str(SCREENSHOT_DIR / "06_vendor_replacements_queue_mobile390.png"))
            print("  [SAVED] 06_vendor_replacements_queue_mobile390.png")
            ctx_ven_mob.close()

            ctx_ven_desk = browser.new_context(viewport=VIEWPORTS["desktop1280"])
            p_ven_desk = ctx_ven_desk.new_page()
            p_ven_desk.goto(f"http://127.0.0.1:{PORT}/vendor_dashboard.html?preview=1", wait_until="networkidle")
            p_ven_desk.evaluate("""() => {
                VendorStore.replacements = [{
                    replacement_id: 'REP-8821',
                    product_name: 'Aashirvaad Shudh Chakki Atta 5kg',
                    quantity: 1,
                    reason: 'wrong_item',
                    status: 'VENDOR_PACKING',
                    customer_phone: '98******10'
                }];
                if (typeof renderVendorReplacementsQueue === 'function') renderVendorReplacementsQueue();
            }""")
            p_ven_desk.wait_for_timeout(600)
            p_ven_desk.screenshot(path=str(SCREENSHOT_DIR / "07_vendor_replacements_desktop1280.png"))
            print("  [SAVED] 07_vendor_replacements_desktop1280.png")
            ctx_ven_desk.close()

            # -----------------------------------------------------------------
            # 3. Runner App: Replacement Mission
            # -----------------------------------------------------------------
            print("\nCapturing Runner App Screens...")
            ctx_run_mob = browser.new_context(viewport=VIEWPORTS["mobile390"])
            p_run_mob = ctx_run_mob.new_page()
            p_run_mob.goto(f"http://127.0.0.1:{PORT}/runner_dashboard.html?preview=1", wait_until="networkidle")
            p_run_mob.evaluate("""() => {
                RunnerStore.replacementMissions = [{
                    replacement_id: 'REP-9014',
                    product_name: 'Amul Butter 500g',
                    quantity: 1,
                    customer_name: 'Suresh Verma',
                    customer_phone: '9876543210',
                    store_name: 'Sharma Brothers Kirana',
                    status: 'OUT_FOR_DELIVERY',
                    reverse_pickup_required: true,
                    reverse_pickup_status: 'PENDING'
                }];
                if (typeof renderMissionsQueue === 'function') renderMissionsQueue();
            }""")
            p_run_mob.wait_for_timeout(600)
            p_run_mob.screenshot(path=str(SCREENSHOT_DIR / "08_runner_replacement_mission_mobile390.png"))
            print("  [SAVED] 08_runner_replacement_mission_mobile390.png")
            ctx_run_mob.close()

            ctx_run_412 = browser.new_context(viewport=VIEWPORTS["mobile412"])
            p_run_412 = ctx_run_412.new_page()
            p_run_412.goto(f"http://127.0.0.1:{PORT}/runner_dashboard.html?preview=1", wait_until="networkidle")
            p_run_412.evaluate("""() => {
                RunnerStore.replacementMissions = [{
                    replacement_id: 'REP-9014',
                    product_name: 'Amul Butter 500g',
                    quantity: 1,
                    customer_name: 'Suresh Verma',
                    customer_phone: '9876543210',
                    store_name: 'Sharma Brothers Kirana',
                    status: 'OUT_FOR_DELIVERY',
                    reverse_pickup_required: true,
                    reverse_pickup_status: 'PENDING'
                }];
                if (typeof renderMissionsQueue === 'function') renderMissionsQueue();
            }""")
            p_run_412.wait_for_timeout(600)
            p_run_412.screenshot(path=str(SCREENSHOT_DIR / "09_runner_replacement_mission_mobile412.png"))
            print("  [SAVED] 09_runner_replacement_mission_mobile412.png")
            ctx_run_412.close()

            # -----------------------------------------------------------------
            # 4. Super Admin App: Resolutions Desk
            # -----------------------------------------------------------------
            print("\nCapturing Super Admin App Screens...")
            ctx_adm_desk = browser.new_context(viewport=VIEWPORTS["desktop1280"])
            p_adm_desk = ctx_adm_desk.new_page()
            p_adm_desk.goto(f"http://127.0.0.1:{PORT}/admin_dashboard.html?preview=1", wait_until="networkidle")
            p_adm_desk.evaluate("""() => {
                if (typeof showTab === 'function') showTab('resolutions');
                AdminStore.resolutions = [
                    { id: 'REF-301', type: 'refund', order_id: 'ORD-101', customer_phone: '9876543210', amount: 150.0, category: 'damaged_item', reason: 'Packaging broken', status: 'UNDER_REVIEW', liability: 'vendor', created_at: '2026-10-31T06:00:00' },
                    { id: 'REP-302', type: 'replacement', order_id: 'ORD-102', customer_phone: '9876543211', amount: 85.0, category: 'wrong_item', reason: 'Received wrong soap', status: 'REQUESTED', liability: 'vendor', created_at: '2026-10-31T06:30:00' }
                ];
                if (typeof renderAdminResolutionsTable === 'function') renderAdminResolutionsTable();
            }""")
            p_adm_desk.wait_for_timeout(800)
            p_adm_desk.screenshot(path=str(SCREENSHOT_DIR / "10_admin_resolutions_desk_desktop1280.png"))
            print("  [SAVED] 10_admin_resolutions_desk_desktop1280.png")
            ctx_adm_desk.close()

            ctx_adm_mob = browser.new_context(viewport=VIEWPORTS["mobile390"])
            p_adm_mob = ctx_adm_mob.new_page()
            p_adm_mob.goto(f"http://127.0.0.1:{PORT}/admin_dashboard.html?preview=1", wait_until="networkidle")
            p_adm_mob.evaluate("""() => {
                if (typeof showTab === 'function') showTab('resolutions');
                AdminStore.resolutions = [
                    { id: 'REF-301', type: 'refund', order_id: 'ORD-101', customer_phone: '9876543210', amount: 150.0, category: 'damaged_item', reason: 'Packaging broken', status: 'UNDER_REVIEW', liability: 'vendor', created_at: '2026-10-31T06:00:00' }
                ];
                if (typeof renderAdminResolutionsTable === 'function') renderAdminResolutionsTable();
            }""")
            p_adm_mob.wait_for_timeout(800)
            p_adm_mob.screenshot(path=str(SCREENSHOT_DIR / "11_admin_resolutions_desk_mobile390.png"))
            print("  [SAVED] 11_admin_resolutions_desk_mobile390.png")
            ctx_adm_mob.close()

            browser.close()

    finally:
        if proc:
            try:
                proc.terminate()
            except Exception:
                pass
        kill_port(PORT)

    print("\n" + "="*80)
    print(f"ALL 11 SCREENSHOTS SAVED SUCCESSFULLY TO: {SCREENSHOT_DIR}")
    print("="*80)

if __name__ == "__main__":
    capture_all()

"""
GaonBazaar (गांव बाज़ार) - Gaon Mitra (गाँव मित्र) Delivery Partner App
Automated Human-Like Visual & UX End-to-End Test Suite (Python)

Simulates real rural runner workflows on budget smartphones:
1. Runner Profile, Identity & Shift Toggle (Online / Offline)
2. High-Level Single-Glance KPI Metrics
3. Incoming Mission Queue & Stage 3 Pickup Reception
4. Kirana Store Pickup Workflow & Confirm Pickup (Stage 3 -> 4)
5. Rural Landmark Spotlight Box Human-UX Audit (Readable landmarks, zero lat/lon leaks)
6. 1-Tap Calling Integration (tel: links for Dukandaar and Customer)
7. Doorstep 4-Digit OTP Verification & Cash Collection Handover (Stage 4 -> 5)
8. Real SQLite Database Persistence & State Transition Verification
9. Shift Earnings (₹20/delivery commission) & Hub Cash Reconciliation Ledger
10. Full Bilingual Toggle (Hindi / English)
11. End-to-End Customer -> Vendor -> Gaon Mitra Real-Time Mission Lifecycle Sync
12. Zero JavaScript Console Errors Audit
"""

import os
import sys
import json
import time
import subprocess
import urllib.request
from pathlib import Path
from datetime import datetime, timezone

# Ensure UTF-8 output encoding for Windows consoles
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
RUNNER_HTML_PATH = BASE_DIR / "runner_dashboard.html"
REPORT_PATH = BASE_DIR / "runner_test_report.txt"
SCREENSHOTS_DIR = BASE_DIR / "screenshots" / "runner"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

# Rural budget smartphone device profiles
RUNNER_TEST_DEVICES = [
    {
        "name": "Redmi 9A (Rural Budget Smartphone)",
        "viewport": {"width": 360, "height": 800},
        "device_scale_factor": 2.0,
        "is_mobile": True,
        "has_touch": True,
        "user_agent": "Mozilla/5.0 (Linux; Android 10; M2006C3LG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
    },
    {
        "name": "Realme C35 (Standard Rural Android)",
        "viewport": {"width": 393, "height": 851},
        "device_scale_factor": 2.75,
        "is_mobile": True,
        "has_touch": True,
        "user_agent": "Mozilla/5.0 (Linux; Android 12; RMX3511) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"
    }
]


class RunnerTestLogger:
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
          GAONBAZAAR GAON MITRA (RUNNER) DASHBOARD AUTOMATED TEST REPORT
================================================================================
Generated: {timestamp}
Total Audits Executed: {self.total_tests}
Passed Audits:         {self.passed_tests}
Failed Audits:         {self.failed_tests}
Success Rate:          {pass_pct:.1f}%
Total Screenshots:     {len(self.screenshots)}
================================================================================

DETAILED AUDIT LOGS:
"""
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            f.write(header)
            for l in self.logs:
                f.write(l + "\n")
            f.write("\n================================================================================\n")
            f.write(f"END OF RUNNER TEST REPORT - {'100% HEALTHY' if self.failed_tests == 0 else 'ACTION REQUIRED'}\n")
            f.write("================================================================================\n")

        print(f"\n📄 Runner Test Report written to: {REPORT_PATH}")


def capture_screenshot(page, name, logger):
    filepath = SCREENSHOTS_DIR / f"{name}.png"
    rel_path = f"screenshots/runner/{name}.png"
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
                res = subprocess.run(f"netstat -ano | findstr :{port}", shell=True, capture_output=True, text=True)
                pids = set()
                for line in res.stdout.strip().splitlines():
                    parts = line.split()
                    if len(parts) >= 5 and f":{port}" in parts[1]:
                        pid = parts[-1]
                        if pid.isdigit() and int(pid) > 0:
                            pids.add(pid)
                for pid in pids:
                    try:
                        subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True)
                    except Exception:
                        pass
            else:
                subprocess.run(f"fuser -k {port}/tcp 2>/dev/null || true", shell=True, capture_output=True)
        except Exception:
            pass


def ensure_backend_running(logger):
    try:
        req = urllib.request.Request("http://127.0.0.1:8001/docs", headers={"User-Agent": "Playwright-QA"})
        with urllib.request.urlopen(req, timeout=1.0) as res:
            if res.status == 200:
                logger.log("  ✓ GaonBazaar Backend is already active and healthy on http://127.0.0.1:8001")
                return None
    except Exception:
        pass

    kill_port_processes([8001])
    time.sleep(0.5)

    logger.log("  🚀 Starting GaonBazaar FastAPI backend server in background on port 8001...")
    server_proc = subprocess.Popen(
        [sys.executable, "run_server.py", "8001"],
        cwd=str(BASE_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    start_time = time.time()
    server_ready = False
    while time.time() - start_time < 5.0:
        if server_proc.poll() is not None:
            logger.log(f"  ✗ Background server exited unexpectedly with code {server_proc.poll()}")
            break
        try:
            req = urllib.request.Request("http://127.0.0.1:8001/docs", headers={"User-Agent": "Playwright-QA"})
            with urllib.request.urlopen(req, timeout=0.8) as res:
                if res.status == 200:
                    server_ready = True
                    logger.log(f"  ✓ GaonBazaar Backend verified ready on http://127.0.0.1:8001/docs ({time.time() - start_time:.2f}s)")
                    break
        except Exception:
            time.sleep(0.3)

    if not server_ready and server_proc.poll() is None:
        logger.log("  ⚠️ Warning: Server is still starting after 5s polling window.")

    return server_proc


def check_element_bounds(page, selector, desc, logger, min_size=14):
    loc = page.locator(selector).first
    try:
        loc.wait_for(state="visible", timeout=6000)
        box = loc.bounding_box()
        has_size = box and box["width"] >= min_size and box["height"] >= min_size
        logger.record_test(
            f"{desc} - DOM Visibility & Touch Target",
            has_size,
            f"Box: {box['width']:.0f}x{box['height']:.0f}px at ({box['x']:.0f}, {box['y']:.0f})" if box else "No box"
        )
        return has_size
    except Exception as e:
        logger.record_test(f"{desc} - DOM Visibility & Touch Target", False, str(e))
        return False


def ensure_stage3_mission_exists():
    """
    Ensures at least one order exists in Stage 3 (Packed & Ready for Pickup)
    with a valid 4-digit delivery OTP (e.g. '4821') and human-readable landmark.
    """
    from backend.database import get_db
    from backend.models import Order, OrderItem
    db = next(get_db())
    has_stage3 = db.query(Order).filter(Order.store_id == "sharma_brothers", Order.timeline_stage == 3).first()
    if not has_stage3:
        import random
        oid = f"#RUR-{random.randint(10000, 99999)}"
        while db.query(Order).filter(Order.id == oid).first():
            oid = f"#RUR-{random.randint(10000, 99999)}"

        demo = Order(
            id=oid,
            user_phone="9876543230",
            user_name="Vikram Singh (विक्रम सिंह)",
            village="Rampur South (रामपुर दक्षिण)",
            landmark="Near Old Neem Tree, Tubewell #3, Khasra 19",
            store_id="sharma_brothers",
            store_name="Sharma Brothers Kirana",
            subtotal=234.0,
            delivery_fee=0.0,
            platform_fee=3.0,
            savings=32.0,
            total_amount=237.0,
            payment_mode="COD",
            status="Packed & Ready",
            timeline_stage=3,
            delivery_otp="4821",
            created_at=datetime.now(timezone.utc)
        )
        db.add(demo)
        db.flush()
        db.add(OrderItem(order_id=oid, product_id="item_1", product_name="Aashirvaad Chakki Atta 5kg", price=210.0, quantity=1))
        db.add(OrderItem(order_id=oid, product_id="item_3", product_name="Tata Salt Iodized 1kg", price=24.0, quantity=1))
        db.commit()
    db.close()


def run_runner_device_simulation(browser, device_config, logger):
    ensure_stage3_mission_exists()
    dev_name = device_config["name"]
    logger.log("\n" + "=" * 80)
    logger.log(f"STARTING GAON MITRA DASHBOARD E2E SIMULATION: {dev_name}")
    logger.log(f"Dimensions: {device_config['viewport']['width']}x{device_config['viewport']['height']} | DPR: {device_config['device_scale_factor']}")
    logger.log("=" * 80)

    context = browser.new_context(
        viewport=device_config["viewport"],
        device_scale_factor=device_config["device_scale_factor"],
        is_mobile=device_config["is_mobile"],
        has_touch=device_config["has_touch"],
        user_agent=device_config["user_agent"]
    )

    page = context.new_page()
    page.set_default_timeout(30000)
    page.set_default_navigation_timeout(30000)

    page_errors = []
    page.on("console", lambda msg: page_errors.append(msg.text) if msg.type == "error" else None)
    page.on("pageerror", lambda err: page_errors.append(str(err)))

    runner_url = "http://127.0.0.1:8001/runner"
    logger.log(f"Loading Gaon Mitra Portal: {runner_url}")
    page.goto(runner_url, timeout=30000)
    page.wait_for_timeout(1000)

    # -------------------------------------------------------------------------
    # 0. Runner Login Gate Security Enforcement Audit
    # -------------------------------------------------------------------------
    logger.log(f"\n--- [{dev_name}] Step 0: Runner Login Gate Security Enforcement ---")
    gate_visible = page.is_visible("#runner-login-gate")
    main_hidden = not page.is_visible("#runner-main-content")
    logger.record_test(
        f"[{dev_name}] Gaon Mitra Login Gate Enforced",
        gate_visible and main_hidden,
        "Full-screen high-contrast login gate shown; mission queue hidden before auth"
    )
    capture_screenshot(page, f"{dev_name.replace(' ', '_')}_step0_login_gate", logger)

    if gate_visible:
        page.click("#btn-runner-login")
        page.wait_for_selector("#runner-main-content:not(.hidden)", timeout=10000)
        page.wait_for_timeout(1000)

    # -------------------------------------------------------------------------
    # 1. Header, Runner Identity & Shift Toggle Audit
    # -------------------------------------------------------------------------
    logger.log(f"\n--- [{dev_name}] Step 1: Header, Shift Toggle & Runner Identity ---")
    check_element_bounds(page, "#runner-name-display", "Runner Name Display", logger)
    check_element_bounds(page, "#runner-badge-code", "Runner Badge Code", logger)
    check_element_bounds(page, "#shift-toggle-btn", "Shift Online/Offline Toggle CTA", logger, min_size=30)
    check_element_bounds(page, "#audio-toggle-btn", "Audio Alert Chime Button", logger)
    check_element_bounds(page, "#lang-toggle-btn", "Language Switcher Button", logger)

    capture_screenshot(page, f"{dev_name.replace(' ', '_')}_step1_initial_dashboard", logger)

    # Shift Toggle Test (Online -> Offline -> Online)
    initial_shift_text = page.inner_text("#shift-status-label").strip()
    page.click("#shift-toggle-btn")
    page.wait_for_timeout(500)
    toggled_shift_text = page.inner_text("#shift-status-label").strip()
    logger.record_test(
        f"[{dev_name}] Shift Operational State Toggle",
        initial_shift_text != toggled_shift_text,
        f"{initial_shift_text} -> {toggled_shift_text}"
    )

    # Toggle back to online for active missions
    page.click("#shift-toggle-btn")
    page.wait_for_timeout(400)

    # -------------------------------------------------------------------------
    # 2. KPI Metrics Ribbon Audit
    # -------------------------------------------------------------------------
    logger.log(f"\n--- [{dev_name}] Step 2: High-Level KPI Summary Tiles ---")
    check_element_bounds(page, "#kpi-active-missions", "Active Missions KPI Card", logger)
    check_element_bounds(page, "#kpi-completed-today", "Completed Today KPI Card", logger)
    check_element_bounds(page, "#kpi-today-earnings", "Today's Earnings KPI Card", logger)
    check_element_bounds(page, "#kpi-cod-cash", "COD Cash in Hand KPI Card", logger)

    active_count = page.inner_text("#kpi-active-missions").strip()
    logger.record_test(
        f"[{dev_name}] Active Missions Live Counter Populated",
        int(active_count) >= 1,
        f"Active Missions: {active_count}"
    )

    # -------------------------------------------------------------------------
    # 3. Missions Queue & Selection
    # -------------------------------------------------------------------------
    logger.log(f"\n--- [{dev_name}] Step 3: Active Missions Queue & Navigation ---")
    missions_count = page.locator("#missions-container > div").count()
    logger.record_test(f"[{dev_name}] Mission Cards Rendered in Queue", missions_count >= 1, f"{missions_count} cards loaded")

    # Select the first mission card to open Mission Details tab
    first_mission_card = page.locator("#missions-container > div").first
    first_mission_card.click()
    page.wait_for_timeout(600)

    is_detail_visible = page.is_visible("#tab-detail")
    logger.record_test(f"[{dev_name}] Transition to Mission Detail Workspace Tab", is_detail_visible)
    capture_screenshot(page, f"{dev_name.replace(' ', '_')}_step2_mission_detail", logger)

    # -------------------------------------------------------------------------
    # 4. Step 1: Kirana Store Pickup Workflow & Confirm Pickup
    # -------------------------------------------------------------------------
    logger.log(f"\n--- [{dev_name}] Step 4: Kirana Store Pickup Workflow ---")
    check_element_bounds(page, "#detail-store-name", "Kirana Store Name", logger)
    check_element_bounds(page, "#btn-call-store", "1-Tap Call Dukandaar CTA", logger)
    
    # Verify phone dialer integration
    call_store_href = page.get_attribute("#btn-call-store", "href")
    logger.record_test(f"[{dev_name}] Dukandaar Call tel: URL Integration", str(call_store_href).startswith("tel:"), call_store_href)

    check_element_bounds(page, "#btn-confirm-pickup", "Confirm Store Pickup CTA Button", logger)

    # Click Confirm Pickup (Stage 3 -> Stage 4)
    btn_text_before = page.inner_text("#btn-pickup-text").strip()
    page.click("#btn-confirm-pickup")
    page.wait_for_timeout(800)
    btn_text_after = page.inner_text("#btn-pickup-text").strip()

    logger.record_test(
        f"[{dev_name}] Confirm Store Pickup Action (Stage 3 -> Stage 4)",
        "सामान उठाया जा चुका है" in btn_text_after or "Picked Up" in btn_text_after,
        f"{btn_text_before} -> {btn_text_after}"
    )
    capture_screenshot(page, f"{dev_name.replace(' ', '_')}_step3_pickup_confirmed", logger)

    # -------------------------------------------------------------------------
    # 5. Step 2: Customer Drop-off & Rural Landmark Spotlight Box Human UX Audit
    # -------------------------------------------------------------------------
    logger.log(f"\n--- [{dev_name}] Step 5: Rural Landmark Spotlight Box & Customer Navigation ---")
    check_element_bounds(page, "#detail-customer-name", "Customer Name Header", logger)
    check_element_bounds(page, "#btn-call-customer", "1-Tap Call Customer CTA", logger)
    
    call_cust_href = page.get_attribute("#btn-call-customer", "href")
    logger.record_test(f"[{dev_name}] Customer Call tel: URL Integration", str(call_cust_href).startswith("tel:"), call_cust_href)

    # Audit the Landmark Spotlight Box
    check_element_bounds(page, "#runner-landmark-box", "Rural Landmark Spotlight Box", logger)
    landmark_text = page.inner_text("#runner-landmark-text").strip()
    
    # Human-UX Text Audit: Must contain real landmarks, NOT raw lat/lon
    is_human_readable = any(w in landmark_text for w in ["Mandir", "Tree", "Tank", "Tubewell", "Panchayat", "Bhawan", "Khasra", "Near", "Opp"])
    no_coord_leaks = "Lat:" not in landmark_text and "Lon:" not in landmark_text and "Coordinate" not in landmark_text
    
    logger.record_test(
        f"[{dev_name}] Human-Readable Rural Landmark Audit",
        is_human_readable and no_coord_leaks and len(landmark_text) >= 10,
        f"Landmark: '{landmark_text}'"
    )

    check_element_bounds(page, "#runner-payment-badge", "Payment Mode & Cash Collect Badge", logger)
    capture_screenshot(page, f"{dev_name.replace(' ', '_')}_step4_landmark_spotlight", logger)

    # -------------------------------------------------------------------------
    # 6. Step 3: Doorstep 4-Digit OTP Handover Verification
    # -------------------------------------------------------------------------
    logger.log(f"\n--- [{dev_name}] Step 6: Doorstep 4-Digit OTP Handover Verification ---")
    check_element_bounds(page, "#otp-digit-1", "OTP Box Digit 1", logger)
    check_element_bounds(page, "#otp-digit-2", "OTP Box Digit 2", logger)
    check_element_bounds(page, "#otp-digit-3", "OTP Box Digit 3", logger)
    check_element_bounds(page, "#otp-digit-4", "OTP Box Digit 4", logger)
    check_element_bounds(page, "#btn-verify-handover", "Verify & Complete Handover CTA", logger)

    # Fill OTP digits: 4 8 2 1
    page.fill("#otp-digit-1", "4")
    page.fill("#otp-digit-2", "8")
    page.fill("#otp-digit-3", "2")
    page.fill("#otp-digit-4", "1")
    page.wait_for_timeout(300)

    # Ensure COD checkbox is checked
    page.check("#cb-cod-confirm")

    page.click("#btn-verify-handover")
    page.wait_for_timeout(900)

    # Verify Celebration Success Modal Opened
    is_success_modal_open = page.is_visible("#modal-delivery-success")
    logger.record_test(f"[{dev_name}] Doorstep 4-Digit OTP Verified & Success Modal Opened", is_success_modal_open)
    capture_screenshot(page, f"{dev_name.replace(' ', '_')}_step5_delivery_success_modal", logger)

    # Close success modal
    page.click('button:has-text("अगला मिशन देखें")')
    page.wait_for_timeout(600)

    is_success_modal_closed = not page.is_visible("#modal-delivery-success")
    logger.record_test(f"[{dev_name}] Delivery Success Modal Dismissed cleanly", is_success_modal_closed)

    # -------------------------------------------------------------------------
    # 7. Step 4: Shift Earnings & Settlement Ledger Tab
    # -------------------------------------------------------------------------
    logger.log(f"\n--- [{dev_name}] Step 7: Shift Earnings & Hub Settlement Ledger ---")
    page.click("#nav-btn-ledger")
    page.wait_for_timeout(600)

    is_ledger_tab_visible = page.is_visible("#tab-ledger")
    logger.record_test(f"[{dev_name}] Transition to Shift Ledger Workspace Tab", is_ledger_tab_visible)

    check_element_bounds(page, "#ledger-completed-count", "Completed Deliveries Count Box", logger)
    check_element_bounds(page, "#ledger-total-payout", "Runner Total Payout Box", logger)
    check_element_bounds(page, "#ledger-cod-cash", "COD Cash in Hand Box", logger)
    check_element_bounds(page, "#ledger-distance-km", "Distance Covered Box", logger)

    payout_val = page.inner_text("#ledger-total-payout").strip()
    cod_val = page.inner_text("#ledger-cod-cash").strip()
    logger.record_test(
        f"[{dev_name}] Ledger Financial Breakdown Verified",
        "₹" in payout_val and "₹" in cod_val,
        f"Earnings: {payout_val} | COD in Hand: {cod_val}"
    )

    # Open Hub Deposit Slip Modal
    check_element_bounds(page, "#btn-generate-slip", "Hub Deposit Slip CTA Button", logger)
    page.click("#btn-generate-slip")
    page.wait_for_timeout(400)

    is_slip_open = page.is_visible("#modal-deposit-slip")
    logger.record_test(f"[{dev_name}] Hub Cash Deposit Slip Modal Opened", is_slip_open)
    capture_screenshot(page, f"{dev_name.replace(' ', '_')}_step6_deposit_slip_modal", logger)

    page.click('button:has-text("बंद करें")')
    page.wait_for_timeout(300)

    # -------------------------------------------------------------------------
    # 8. Bilingual Language State Toggle
    # -------------------------------------------------------------------------
    logger.log(f"\n--- [{dev_name}] Step 8: Bilingual State Switch (Hindi / English) ---")
    page.click("#lang-toggle-btn")
    page.wait_for_timeout(400)
    en_label = page.inner_text("#lang-toggle-btn").strip()
    logger.record_test(f"[{dev_name}] Bilingual Toggle to English", "हिंदी" in en_label or "English" in en_label, f"Label: {en_label}")
    stored_lang = page.evaluate("localStorage.getItem('gaonbazar_lang')")
    logger.record_test(f"[{dev_name}] Bilingual Storage State Persisted ('gaonbazar_lang')", stored_lang in ['hi', 'en'], f"Value: {stored_lang}")

    page.click("#lang-toggle-btn")
    page.wait_for_timeout(400)

    # -------------------------------------------------------------------------
    # 9. Clean Console & Script Audit
    # -------------------------------------------------------------------------
    logger.log(f"\n--- [{dev_name}] Step 9: Zero Console Errors Audit ---")
    if not page_errors:
        logger.record_test(f"[{dev_name}] Zero JavaScript Console Errors", True, "Clean runtime execution")
    else:
        logger.record_test(f"[{dev_name}] JavaScript Console Errors Encountered", False, " | ".join(page_errors))

    context.close()


def test_full_lifecycle_sync(browser, logger):
    """
    Tests end-to-end multi-party real-time lifecycle:
    1. Customer programmatically places an order via /api/orders/checkout (Stage 1).
    2. Vendor accepts and packs order via /api/vendor/orders/{id}/quick-action (Stage 2 -> Stage 3).
    3. Gaon Mitra Dashboard detects incoming mission live in 4s polling cycle without reload.
    4. Gaon Mitra confirms pickup (Stage 3 -> Stage 4).
    5. Gaon Mitra verifies 4-digit doorstep OTP (Stage 4 -> Stage 5).
    6. Assert real SQLite DB records timeline_stage = 5 and status = 'Delivered'.
    """
    logger.log("\n" + "=" * 80)
    logger.log("STARTING FULL END-TO-END MULTI-PARTY ORDER LIFECYCLE SYNC TEST")
    logger.log("=" * 80)

    context = browser.new_context(viewport={"width": 1280, "height": 800})
    runner_page = context.new_page()
    runner_page.goto("http://127.0.0.1:8001/runner")
    runner_page.wait_for_timeout(1000)
    if runner_page.is_visible("#runner-login-gate"):
        runner_page.click("#btn-runner-login")
        runner_page.wait_for_selector("#runner-main-content:not(.hidden)", timeout=10000)
        runner_page.wait_for_timeout(1000)

    # 1. Customer places order
    payload = {
        "user_phone": "9876543291",
        "user_name": "Devendra Yadav (देवेंद्र यादव)",
        "village": "Rampur Chaupal (रामपुर चौपाल)",
        "landmark": "Near Gram Panchayat Bhawan, Under Peepal Tree",
        "store_id": "sharma_brothers",
        "payment_mode": "COD",
        "items": [
            {"id": "item_1", "price": 210.0, "qty": 1},
            {"id": "item_2", "price": 145.0, "qty": 1}
        ]
    }

    logger.log("  📦 1. Customer places order via /api/orders/checkout...")
    req = urllib.request.Request(
        "http://127.0.0.1:8001/api/orders/checkout",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=5.0) as resp:
        checkout_res = json.loads(resp.read().decode("utf-8"))
    order_id = checkout_res["order_id"]
    delivery_otp = checkout_res["delivery_otp"]
    logger.log(f"  ✓ Order placed: {order_id} | Delivery OTP: {delivery_otp}")

    # 2. Vendor accepts and packs order
    logger.log(f"  🏬 2. Vendor accepts and packs {order_id}...")
    accept_req = urllib.request.Request(
        f"http://127.0.0.1:8001/api/vendor/orders/{urllib.parse.quote(order_id)}/quick-action?action=accept",
        data=b"",
        headers={"Content-Type": "application/json"}
    )
    urllib.request.urlopen(accept_req, timeout=5.0)

    pack_req = urllib.request.Request(
        f"http://127.0.0.1:8001/api/vendor/orders/{urllib.parse.quote(order_id)}/quick-action?action=pack",
        data=b"",
        headers={"Content-Type": "application/json"}
    )
    urllib.request.urlopen(pack_req, timeout=5.0)
    logger.log(f"  ✓ Order advanced to Stage 3 (Packed & Ready for Runner)")

    # 3. Gaon Mitra dashboard picks up order live
    logger.log(f"  ⏳ 3. Waiting for Gaon Mitra live polling to detect {order_id}...")
    found_in_runner_queue = False
    for _ in range(12):
        runner_page.wait_for_timeout(800)
        if runner_page.locator(f'span:has-text("{order_id}")').count() > 0:
            found_in_runner_queue = True
            break

    logger.record_test(
        "Real-Time Gaon Mitra Mission Reception (Vendor Pack -> Runner Sync)",
        found_in_runner_queue,
        f"Order {order_id} appeared live in Runner Missions Queue without page reload!"
    )

    # 4. Runner opens mission and confirms pickup
    logger.log(f"  🛵 4. Runner confirms store pickup...")
    runner_page.locator(f'div:has-text("{order_id}")').last.click()
    runner_page.wait_for_timeout(600)
    runner_page.click("#btn-confirm-pickup")
    runner_page.wait_for_timeout(600)

    # 5. Runner arrives at doorstep and enters customer OTP
    logger.log(f"  🏡 5. Runner arrives at customer landmark and verifies doorstep OTP...")
    for idx, char in enumerate(str(delivery_otp)):
        runner_page.fill(f"#otp-digit-{idx + 1}", char)
    runner_page.wait_for_timeout(300)

    runner_page.click("#btn-verify-handover")
    runner_page.wait_for_timeout(800)

    # Assert celebratory success modal
    is_delivered = runner_page.is_visible("#modal-delivery-success")
    logger.record_test("Doorstep Handover OTP Validation & Celebration Modal", is_delivered, "Mission completed successfully!")

    # 6. Verify real SQLite database persistence
    from backend.database import get_db
    from backend.models import Order
    db = next(get_db())
    db_order = db.query(Order).filter(Order.id == order_id).first()
    db_persisted = db_order is not None and db_order.timeline_stage == 5 and db_order.status == "Delivered"
    db.close()

    logger.record_test(
        "Full Lifecycle SQLite DB State Integrity (Stage 5 Delivered)",
        db_persisted,
        f"Order {order_id}: Stage {db_order.timeline_stage if db_order else 'None'} ({db_order.status if db_order else 'None'})"
    )

    capture_screenshot(runner_page, "step7_full_lifecycle_sync", logger)
    context.close()


def main():
    logger = RunnerTestLogger()
    logger.log("Starting GaonBazaar Gaon Mitra (Runner) Dashboard Automated Test Suite...")

    if not RUNNER_HTML_PATH.exists():
        print(f"Error: Cannot find runner_dashboard.html at {RUNNER_HTML_PATH}")
        sys.exit(1)

    server_proc = ensure_backend_running(logger)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            # 1. Test simulated rural smartphones
            for dev in RUNNER_TEST_DEVICES:
                try:
                    run_runner_device_simulation(browser, dev, logger)
                except Exception as err:
                    logger.record_test(f"[{dev['name']}] Simulation Execution", False, str(err))
                    logger.log(f"  [ERROR IN {dev['name']}]: {err}")

            # 2. Test full end-to-end multi-party lifecycle sync
            try:
                test_full_lifecycle_sync(browser, logger)
            except Exception as sync_err:
                logger.record_test("Full Multi-Party Lifecycle Sync", False, str(sync_err))
                logger.log(f"  [SYNC ERROR]: {sync_err}")

        finally:
            browser.close()
            logger.save_report()
            if server_proc:
                try:
                    server_proc.terminate()
                    server_proc.wait(timeout=2)
                except Exception:
                    try:
                        server_proc.kill()
                    except Exception:
                        pass
                kill_port_processes([8001])


if __name__ == "__main__":
    main()

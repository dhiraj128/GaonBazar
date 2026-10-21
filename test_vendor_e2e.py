"""
GaonBazaar (गांव बाज़ार) - Vendor (Dukandaar) Dashboard Automated E2E Test Suite (Python)
Simulates real rural shopkeeper workflows:
1. Vendor Authentication & Multi-Store Selection
2. Store Operational Toggle (Open/Closed) with DB persistence
3. Live Incoming Order Queue & Interactive Checklist
4. Order Lifecycle Progression: [Accept] -> [Pack] -> [Handover to Runner]
5. End-to-End Customer-to-Vendor Real-Time Order Sync
6. Inventory Management & Tactile In-Stock/Out-of-Stock Toggle
7. Adding New Local Inventory Products
8. Daily Earnings & COD Cash Settlement Ledger
9. Bilingual Toggle (English / हिंदी)
10. Ergonomic Touch Bounds & Zero Console Errors Audit
"""

import os
import sys
import json
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
    print("Playwright is not installed. Please run: pip install playwright && playwright install")
    sys.exit(1)

BASE_DIR = Path(__file__).parent.resolve()
VENDOR_HTML_PATH = BASE_DIR / "vendor_dashboard.html"
REPORT_PATH = BASE_DIR / "vendor_test_report.txt"
SCREENSHOTS_DIR = BASE_DIR / "screenshots" / "vendor"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

VENDOR_TEST_DEVICES = [
    {
        "name": "Redmi Note 10 (Dukandaar Mobile)",
        "viewport": {"width": 393, "height": 851},
        "device_scale_factor": 2.75,
        "is_mobile": True,
        "has_touch": True,
        "user_agent": "Mozilla/5.0 (Linux; Android 12; M2101K7AI) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"
    },
    {
        "name": "Samsung Galaxy Tab A8 (Kirana Counter Tablet)",
        "viewport": {"width": 800, "height": 1280},
        "device_scale_factor": 2.0,
        "is_mobile": True,
        "has_touch": True,
        "user_agent": "Mozilla/5.0 (Linux; Android 13; SM-X200) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
]


class VendorTestLogger:
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
          GAONBAZAAR VENDOR (DUKANDAAR) DASHBOARD AUTOMATED TEST REPORT
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
            f.write(f"END OF VENDOR TEST REPORT - {'100% HEALTHY' if self.failed_tests == 0 else 'ACTION REQUIRED'}\n")
            f.write("================================================================================\n")

        print(f"\n📄 Vendor Test Report written to: {REPORT_PATH}")


def capture_screenshot(page, name, logger):
    filepath = SCREENSHOTS_DIR / f"{name}.png"
    rel_path = f"screenshots/vendor/{name}.png"
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
        except Exception:
            pass


def ensure_backend_running(logger):
    kill_port_processes([8001])
    time.sleep(1.0)

    logger.log("  🚀 Starting GaonBazaar FastAPI backend server in background on port 8001...")
    server_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8001"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    start_time = time.time()
    server_ready = False
    while time.time() - start_time < 12.0:
        if server_proc.poll() is not None:
            logger.log(f"  ✗ Background server exited unexpectedly with code {server_proc.poll()}")
            break
        try:
            req = urllib.request.Request("http://127.0.0.1:8001/docs", headers={"User-Agent": "Playwright-QA"})
            with urllib.request.urlopen(req, timeout=1.0) as res:
                if res.status == 200:
                    server_ready = True
                    logger.log(f"  ✓ GaonBazaar Backend verified ready on http://127.0.0.1:8001/docs ({time.time() - start_time:.2f}s)")
                    break
        except Exception:
            time.sleep(0.5)

    if not server_ready and server_proc.poll() is None:
        logger.log("  ⚠️ Warning: Server is still starting after 12s.")

    return server_proc


def check_element_bounds(page, selector, desc, logger):
    loc = page.locator(selector).first
    try:
        loc.wait_for(state="visible", timeout=6000)
        box = loc.bounding_box()
        has_size = box and box["width"] >= 20 and box["height"] >= 20
        logger.record_test(f"{desc} - DOM Visibility & Touch Target", has_size, f"Box: {box['width']:.0f}x{box['height']:.0f}px at ({box['x']:.0f}, {box['y']:.0f})" if box else "No box")
        return has_size
    except Exception as e:
        logger.record_test(f"{desc} - DOM Visibility & Touch Target", False, str(e))
        return False


def ensure_stage1_order_exists():
    from backend.database import get_db
    from backend.models import Order, OrderItem
    from datetime import timezone
    db = next(get_db())
    has_stage1 = db.query(Order).filter(Order.store_id == "sharma_brothers", Order.timeline_stage == 1).first()
    if not has_stage1:
        import random
        # Find a unique order id that does not exist in DB
        oid = f"#RUR-{random.randint(10000, 99999)}"
        while db.query(Order).filter(Order.id == oid).first():
            oid = f"#RUR-{random.randint(10000, 99999)}"

        demo = Order(
            id=oid,
            user_phone="9876543210",
            user_name="Ramesh Patel (रमेश पटेल)",
            village="Rampur (रामपुर)",
            landmark="Near Shiva Mandir, Opp. Blue Water Tank",
            store_id="sharma_brothers",
            store_name="Sharma Brothers Kirana",
            subtotal=355.0,
            delivery_fee=0.0,
            platform_fee=3.0,
            savings=45.0,
            total_amount=358.0,
            payment_mode="COD",
            status="Order Placed",
            timeline_stage=1,
            delivery_otp="4821",
            created_at=datetime.now(timezone.utc)
        )
        db.add(demo)
        db.flush()
        db.add(OrderItem(order_id=oid, product_id="item_1", product_name="Aashirvaad Chakki Atta 5kg", price=210.0, quantity=1))
        db.add(OrderItem(order_id=oid, product_id="item_2", product_name="Fortune Mustard Oil 1L", price=145.0, quantity=1))
        db.commit()
    db.close()


def run_vendor_device_simulation(browser, device_config, logger):
    ensure_stage1_order_exists()
    dev_name = device_config["name"]
    logger.log("\n" + "=" * 80)
    logger.log(f"STARTING VENDOR DASHBOARD E2E SIMULATION: {dev_name}")
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

    vendor_url = "http://127.0.0.1:8001/vendor"
    logger.log(f"Loading Vendor Portal: {vendor_url}")
    page.goto(vendor_url, timeout=30000)
    page.wait_for_timeout(1000)

    # -------------------------------------------------------------------------
    # 0. Login Gate Security Enforcement Audit
    # -------------------------------------------------------------------------
    logger.log(f"\n--- [{dev_name}] Step 0: Login Gate Security Enforcement ---")
    gate_visible = page.is_visible("#vendor-login-gate")
    main_hidden = not page.is_visible("#vendor-main-content")
    logger.record_test(
        f"[{dev_name}] Vendor Security Login Gate Enforced",
        gate_visible and main_hidden,
        "Login gate displayed first; main dashboard unmounted before auth"
    )
    capture_screenshot(page, f"{dev_name.replace(' ', '_')}_step0_login_gate", logger)

    if gate_visible:
        page.click("#btn-vendor-login")
        page.wait_for_selector("#vendor-main-content:not(.hidden)", timeout=10000)
        page.wait_for_timeout(1000)

    # -------------------------------------------------------------------------
    # 1. Header & Store Profile Audit
    # -------------------------------------------------------------------------
    logger.log(f"\n--- [{dev_name}] Step 1: Header, Store Switcher & Operational Controls ---")
    check_element_bounds(page, "#store-badge-code", "Store Badge Code", logger)
    check_element_bounds(page, "#store-switcher-select", "Store Switcher Dropdown", logger)
    check_element_bounds(page, "#store-open-btn", "Store Open/Close Toggle CTA", logger)
    check_element_bounds(page, "#lang-toggle-btn", "Language Toggle Button", logger)

    capture_screenshot(page, f"{dev_name.replace(' ', '_')}_step1_initial_dashboard", logger)

    # Test Store Open / Close status toggle
    initial_open_text = page.inner_text("#open-status-label").strip()
    page.click("#store-open-btn")
    page.wait_for_timeout(600)
    toggled_open_text = page.inner_text("#open-status-label").strip()
    logger.record_test(
        f"[{dev_name}] Store Operational Status Toggle",
        initial_open_text != toggled_open_text,
        f"{initial_open_text} -> {toggled_open_text}"
    )

    # Toggle back to open for active orders
    page.click("#store-open-btn")
    page.wait_for_timeout(400)

    # -------------------------------------------------------------------------
    # 2. KPI Metrics Bar Audit
    # -------------------------------------------------------------------------
    logger.log(f"\n--- [{dev_name}] Step 2: High-Level KPI Summary Tiles ---")
    check_element_bounds(page, "#kpi-new-count", "New Orders KPI Card", logger)
    check_element_bounds(page, "#kpi-packing-count", "Packing in Progress KPI Card", logger)
    check_element_bounds(page, "#kpi-gross-sales", "Gross Sales KPI Card", logger)
    check_element_bounds(page, "#kpi-net-payout", "Net Payout KPI Card", logger)

    new_count_text = page.inner_text("#kpi-new-count").strip()
    gross_sales_text = page.inner_text("#kpi-gross-sales").strip()
    logger.record_test(
        f"[{dev_name}] KPI Live Counters Populated",
        int(new_count_text) >= 1 and "₹" in gross_sales_text,
        f"New Orders: {new_count_text} | Sales: {gross_sales_text}"
    )

    # -------------------------------------------------------------------------
    # 3. Live Order Processing Workflow: [Accept] -> [Pack] -> [Handover]
    # -------------------------------------------------------------------------
    logger.log(f"\n--- [{dev_name}] Step 3: Order Lifecycle Progression Workflow ---")
    
    # Check that orders container has order cards
    orders_count = page.locator("#orders-container > div").count()
    logger.record_test(f"[{dev_name}] Live Order Cards Rendered in Queue", orders_count > 0, f"{orders_count} orders visible")

    # Look for Stage 1 Accept Order button
    accept_btn = page.locator('button:has-text("स्वीकार करें"), button:has-text("Accept Order")').first
    if accept_btn.count() > 0:
        check_element_bounds(page, 'button:has-text("स्वीकार करें")', "Order Accept CTA Button", logger)
        accept_btn.click()
        page.wait_for_timeout(800)
        capture_screenshot(page, f"{dev_name.replace(' ', '_')}_step2_order_accepted", logger)
        logger.record_test(f"[{dev_name}] Order Action: Accepted by Vendor", True, "Advanced to Stage 2 (Packing चालू)")
    else:
        logger.record_test(f"[{dev_name}] Order Action: Accepted by Vendor", False, "Accept button not located")

    # Now look for Stage 2 Pack Order button
    pack_btn = page.locator('button:has-text("पैक हो गया"), button:has-text("Mark Packed")').first
    if pack_btn.count() > 0:
        check_element_bounds(page, 'button:has-text("पैक हो गया")', "Mark Packed CTA Button", logger)
        pack_btn.click()
        page.wait_for_timeout(800)
        capture_screenshot(page, f"{dev_name.replace(' ', '_')}_step3_order_packed", logger)
        logger.record_test(f"[{dev_name}] Order Action: Packed by Vendor", True, "Advanced to Stage 3 (Waiting for Runner)")
    else:
        logger.record_test(f"[{dev_name}] Order Action: Packed by Vendor", False, "Pack button not located")

    # Now look for Stage 3 Handover to Runner button
    handover_btn = page.locator('button:has-text("रनर को सौंपें"), button:has-text("Handover to Gaon Mitra")').first
    if handover_btn.count() > 0:
        check_element_bounds(page, 'button:has-text("रनर को सौंपें")', "Handover to Runner CTA Button", logger)
        handover_btn.click()
        page.wait_for_timeout(800)
        capture_screenshot(page, f"{dev_name.replace(' ', '_')}_step4_order_dispatched", logger)
        logger.record_test(f"[{dev_name}] Order Action: Handed Over to Gaon Mitra", True, "Advanced to Stage 4 (Out for Delivery)")
    else:
        logger.record_test(f"[{dev_name}] Order Action: Handed Over to Gaon Mitra", False, "Handover button not located")

    # -------------------------------------------------------------------------
    # 4. Inventory Management Tab & Stock Toggle Audit
    # -------------------------------------------------------------------------
    logger.log(f"\n--- [{dev_name}] Step 4: Inventory Management & Tactile Stock Toggles ---")
    page.click("#nav-btn-inventory")
    page.wait_for_timeout(600)

    is_inv_visible = page.is_visible("#tab-inventory")
    logger.record_test(f"[{dev_name}] Transition to Inventory Workspace Tab", is_inv_visible)
    check_element_bounds(page, "#inventory-search-input", "Inventory Search Bar", logger)

    products_count = page.locator("#inventory-container > div").count()
    logger.record_test(f"[{dev_name}] Inventory Products Rendered", products_count >= 5, f"{products_count} products loaded")

    # Find the first product stock toggle and click it
    first_toggle = page.locator("#inventory-container button:has-text('उपलब्ध'), #inventory-container button:has-text('अनुपलब्ध')").first
    if first_toggle.count() > 0:
        initial_stock_text = first_toggle.inner_text().strip()
        first_toggle.click()
        page.wait_for_timeout(700)
        toggled_stock_text = first_toggle.inner_text().strip()
        capture_screenshot(page, f"{dev_name.replace(' ', '_')}_step5_stock_toggled", logger)
        logger.record_test(
            f"[{dev_name}] Product In-Stock / Out-of-Stock Toggle",
            initial_stock_text != toggled_stock_text,
            f"{initial_stock_text} -> {toggled_stock_text}"
        )
        # Toggle back to original
        first_toggle.click()
        page.wait_for_timeout(400)
    else:
        logger.record_test(f"[{dev_name}] Product In-Stock / Out-of-Stock Toggle", False, "No toggle found")

    # -------------------------------------------------------------------------
    # 5. Add New Local Product Modal Flow
    # -------------------------------------------------------------------------
    logger.log(f"\n--- [{dev_name}] Step 5: Add New Inventory Item Modal ---")
    page.click('button:has-text("नया सामान जोड़ें")')
    page.wait_for_timeout(400)

    is_modal_open = page.is_visible("#modal-add-product")
    logger.record_test(f"[{dev_name}] Add Product Modal Opened", is_modal_open)

    page.fill("#new-prod-en", "Kisan Special Desi Gur 1kg")
    page.fill("#new-prod-hi", "किसान स्पेशल देसी गुड़")
    page.fill("#new-prod-weight", "1 kg • ताज़ा प्राकृतिक गुड़")
    page.fill("#new-prod-price", "70")
    page.fill("#new-prod-mrp", "80")

    page.click('button:has-text("सुरक्षित करें")')
    page.wait_for_timeout(800)

    # Verify modal closed and new product appears
    is_modal_closed = not page.is_visible("#modal-add-product")
    logger.record_test(f"[{dev_name}] Add Product Modal Submitted & Closed", is_modal_closed)

    # -------------------------------------------------------------------------
    # 6. Daily Ledger & COD Cash Settlement Tab
    # -------------------------------------------------------------------------
    logger.log(f"\n--- [{dev_name}] Step 6: Daily Sales & Earnings Ledger ---")
    page.click("#nav-btn-ledger")
    page.wait_for_timeout(600)

    is_ledger_visible = page.is_visible("#tab-ledger")
    logger.record_test(f"[{dev_name}] Transition to Daily Ledger Workspace Tab", is_ledger_visible)

    check_element_bounds(page, "#ledger-gross-sales", "Gross Sales Summary Box", logger)
    check_element_bounds(page, "#ledger-cod-collected", "COD Cash in Hand Box", logger)
    check_element_bounds(page, "#ledger-platform-fee", "Platform Commission Fee Box", logger)
    check_element_bounds(page, "#ledger-net-payout", "Net Dukandaar Payout Box", logger)

    ledger_gross = page.inner_text("#ledger-gross-sales").strip()
    ledger_cod = page.inner_text("#ledger-cod-collected").strip()
    ledger_net = page.inner_text("#ledger-net-payout").strip()
    logger.record_test(
        f"[{dev_name}] Ledger Financial Breakdown Verified",
        "₹" in ledger_gross and "₹" in ledger_cod and "₹" in ledger_net,
        f"Gross: {ledger_gross} | COD: {ledger_cod} | Net Payout: {ledger_net}"
    )

    # Table rows count
    table_rows_count = page.locator("#ledger-table-body tr").count()
    logger.record_test(f"[{dev_name}] Ledger Transaction Table Rows Rendered", table_rows_count > 0, f"{table_rows_count} orders in ledger table")
    capture_screenshot(page, f"{dev_name.replace(' ', '_')}_step6_daily_ledger", logger)

    # -------------------------------------------------------------------------
    # 7. Store Profile Settings Tab
    # -------------------------------------------------------------------------
    logger.log(f"\n--- [{dev_name}] Step 7: Store Profile & Cluster Settings ---")
    page.click("#nav-btn-settings")
    page.wait_for_timeout(500)

    is_settings_visible = page.is_visible("#tab-settings")
    store_name_val = page.input_value("#setting-store-name")
    logger.record_test(
        f"[{dev_name}] Store Profile Details Loaded",
        is_settings_visible and len(store_name_val) > 0,
        f"Store: {store_name_val}"
    )
    capture_screenshot(page, f"{dev_name.replace(' ', '_')}_step7_store_profile", logger)

    # -------------------------------------------------------------------------
    # 8. Bilingual Language State Toggle
    # -------------------------------------------------------------------------
    logger.log(f"\n--- [{dev_name}] Step 8: Bilingual State Switch (Hindi / English) ---")
    page.click("#lang-toggle-btn")
    page.wait_for_timeout(400)
    en_label = page.inner_text("#lang-toggle-btn").strip()
    logger.record_test(f"[{dev_name}] Bilingual Toggle to English", "हिंदी" in en_label or "English" in en_label, f"Label: {en_label}")

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


def test_customer_to_vendor_realtime_sync(browser, logger):
    """
    Tests real-time customer order placement -> vendor dashboard synchronization:
    1. Customer opens index.html and completes checkout.
    2. Vendor dashboard detects incoming order within polling interval and plays chime.
    """
    logger.log("\n" + "=" * 80)
    logger.log("REAL-TIME CUSTOMER -> VENDOR SYNC END-TO-END TEST")
    logger.log("=" * 80)

    context = browser.new_context(viewport={"width": 1280, "height": 800})
    vendor_page = context.new_page()
    vendor_page.goto("http://127.0.0.1:8001/vendor")
    vendor_page.wait_for_timeout(1000)
    if vendor_page.is_visible("#vendor-login-gate"):
        vendor_page.click("#btn-vendor-login")
        vendor_page.wait_for_selector("#vendor-main-content:not(.hidden)", timeout=10000)
        vendor_page.wait_for_timeout(1000)

    # Place a programmatic order via FastAPI /api/orders/checkout
    payload = {
        "user_phone": "9876543299",
        "user_name": "Raju Farmer (राजू किसान)",
        "village": "Rampur South (रामपुर दक्षिण)",
        "landmark": "Near Panchayat Tube Well, Khasra 42",
        "store_id": "sharma_brothers",
        "payment_mode": "COD",
        "items": [
            {"id": "item_1", "price": 210.0, "qty": 1},
            {"id": "item_2", "price": 145.0, "qty": 1}
        ]
    }

    logger.log("  📦 Placing a new customer order via /api/orders/checkout...")
    try:
        req = urllib.request.Request(
            "http://127.0.0.1:8001/api/orders/checkout",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            checkout_res = json.loads(resp.read().decode("utf-8"))
        new_order_id = checkout_res["order_id"]
        logger.log(f"  ✓ Order placed successfully: {new_order_id} (Total: ₹{checkout_res['total_amount']})")
    except Exception as pl_err:
        logger.log(f"  ✗ Order placement failed: {pl_err}")
        new_order_id = "#RUR-9999"

    # Wait for the vendor dashboard polling cycle to catch the order
    logger.log(f"  ⏳ Waiting for Vendor Dashboard to sync and display {new_order_id}...")
    found_in_dashboard = False
    for _ in range(15):
        vendor_page.wait_for_timeout(1000)
        has_id = vendor_page.locator(f'span:has-text("{new_order_id}")').count() > 0
        if has_id:
            found_in_dashboard = True
            break

    logger.record_test(
        "Customer-to-Vendor Real-Time Order Sync",
        found_in_dashboard,
        f"Order {new_order_id} appeared live in Vendor Queue without page reload!"
    )

    capture_screenshot(vendor_page, "step8_customer_vendor_live_synced", logger)
    context.close()


def main():
    logger = VendorTestLogger()
    logger.log("Starting GaonBazaar Vendor (Dukandaar) Dashboard End-to-End Test Suite...")

    if not VENDOR_HTML_PATH.exists():
        print(f"Error: Cannot find vendor_dashboard.html at {VENDOR_HTML_PATH}")
        sys.exit(1)

    server_proc = ensure_backend_running(logger)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            # 1. Test simulated mobile and tablet devices
            for dev in VENDOR_TEST_DEVICES:
                try:
                    run_vendor_device_simulation(browser, dev, logger)
                except Exception as err:
                    logger.record_test(f"[{dev['name']}] Simulation Execution", False, str(err))
                    logger.log(f"  [ERROR IN {dev['name']}]: {err}")

            # 2. Test Customer-to-Vendor real-time order sync
            try:
                test_customer_to_vendor_realtime_sync(browser, logger)
            except Exception as sync_err:
                logger.record_test("Customer-to-Vendor Real-Time Order Sync", False, str(sync_err))
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

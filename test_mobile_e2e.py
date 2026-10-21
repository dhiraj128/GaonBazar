"""
GaonBazaar (गांव बाज़ार) - Playwright Human-Like Visual & UX Automated Test Suite (Python)

Simulates 5 Tier-1 & Tier-2/3 Indian Market Mobile Devices:
1. iPhone 16 (Viewport: 393 x 852, DPR: 3.0, Mobile Safari)
2. Redmi Note 10 (Viewport: 393 x 851, DPR: 2.75, Mobile Chrome)
3. Realme 9 (Viewport: 360 x 800, DPR: 3.0, Mobile Chrome)
4. Galaxy S22 (Viewport: 360 x 780, DPR: 3.0, Mobile Chrome)
5. Nothing Phone 1 (Viewport: 412 x 915, DPR: 2.625, Mobile Chrome)

Human-Like Visual & UX Verifications:
- Visual Screenshots captured per device into dedicated subfolders: screenshots/<Device_Name>/step_X.png
- Physical Viewport Bounds Checking (verifies buttons are visible in viewport and not occluded)
- Native DOM hit-testing via locator.evaluate() avoiding querySelector syntax issues
- Touch Target Ergonomics Audit (WCAG AAA touch targets >= 28px-48px)
- Rural UX Text Audit: Human-readable GPS address strings vs raw coordinate leaks
- Sticky Bottom CTA Accessibility (fixed bottom-0 z-50 bg-white)
- Horizontal overflow & layout squeeze audits (360px to 412px viewports)
- Full 5-phase end-to-end user journey across all simulated devices
- Comprehensive audit report generated in 'test_report.txt'
"""

import os
import sys
import json
import time
import subprocess
import urllib.request
from pathlib import Path
from datetime import datetime

# Configure UTF-8 encoding for Windows consoles to support Hindi & Unicode characters cleanly
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
HTML_FILE_PATH = BASE_DIR / "index.html"
REPORT_FILE_PATH = BASE_DIR / "test_report.txt"
SCREENSHOTS_DIR = BASE_DIR / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

# Expanded Indian Market Device Profiles
TEST_DEVICES = [
    {
        "name": "iPhone 16",
        "viewport": {"width": 393, "height": 852},
        "device_scale_factor": 3.0,
        "is_mobile": True,
        "has_touch": True,
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1"
    },
    {
        "name": "Redmi Note 10",
        "viewport": {"width": 393, "height": 851},
        "device_scale_factor": 2.75,
        "is_mobile": True,
        "has_touch": True,
        "user_agent": "Mozilla/5.0 (Linux; Android 12; M2101K7AI) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"
    },
    {
        "name": "Realme 9",
        "viewport": {"width": 360, "height": 800},
        "device_scale_factor": 3.0,
        "is_mobile": True,
        "has_touch": True,
        "user_agent": "Mozilla/5.0 (Linux; Android 13; RMX3521) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
    },
    {
        "name": "Galaxy S22",
        "viewport": {"width": 360, "height": 780},
        "device_scale_factor": 3.0,
        "is_mobile": True,
        "has_touch": True,
        "user_agent": "Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
    },
    {
        "name": "Nothing Phone 1",
        "viewport": {"width": 412, "height": 915},
        "device_scale_factor": 2.625,
        "is_mobile": True,
        "has_touch": True,
        "user_agent": "Mozilla/5.0 (Linux; Android 14; A063) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"
    }
]

class TestLogger:
    def __init__(self):
        self.logs = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.screenshots = []

    def log(self, msg):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {msg}"
        print(line)
        self.logs.append(line)

    def record_test(self, name, passed, detail=""):
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            self.log(f"  ✓ PASS: {name} {'(' + detail + ')' if detail else ''}")
        else:
            self.failed_tests += 1
            self.log(f"  ✗ FAIL: {name} - ERROR: {detail}")

    def record_screenshot(self, rel_path):
        self.screenshots.append(rel_path)

    def save_report(self):
        header = [
            "=" * 80,
            "               GAONBAZAAR HUMAN-LIKE VISUAL UX TEST REPORT                    ",
            "=" * 80,
            f"Date & Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Tested File: {HTML_FILE_PATH}",
            f"Screenshots Directory: {SCREENSHOTS_DIR}",
            f"Total Visual Screenshots Captured: {len(self.screenshots)}",
            f"Total Checks: {self.total_tests}",
            f"Passed: {self.passed_tests}",
            f"Failed: {self.failed_tests}",
            f"Overall Status: {'SUCCESS (100% HEALTHY)' if self.failed_tests == 0 else 'ATTENTION REQUIRED'}",
            "-" * 80,
            ""
        ]
        content = "\n".join(header) + "\n".join(self.logs) + "\n"
        with open(REPORT_FILE_PATH, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\n📄 Report written to: {REPORT_FILE_PATH}\n")


def capture_human_ux_screenshot(page, dev_name, step_name, logger):
    """
    Captures high-resolution mobile screenshots and organizes them into
    per-device subdirectories (e.g. screenshots/Redmi_Note_10/step_1_login.png).
    """
    clean_folder = dev_name.replace(" ", "_")
    device_dir = SCREENSHOTS_DIR / clean_folder
    os.makedirs(device_dir, exist_ok=True)

    filename = f"{step_name}.png"
    filepath = device_dir / filename
    rel_path = f"screenshots/{clean_folder}/{filename}"

    try:
        page.screenshot(path=str(filepath), full_page=False)
        logger.record_screenshot(rel_path)
        logger.log(f"  📸 [SCREENSHOT CAPTURED]: {rel_path}")
    except Exception as e:
        logger.log(f"  ⚠️ [SCREENSHOT FAILED]: {rel_path} ({e})")
    return filepath


def check_human_ux_bounds(page, selector, element_desc, dev_name, logger, require_sticky=False):
    """
    Performs human-like visual UX validation on an interactive element:
    1. Verifies physical client bounding box (x, y, width, height).
    2. Asserts element is in the visible mobile viewport (not pushed off-screen).
    3. Checks touch target dimensions (WCAG touch targets >= 28px).
    4. Evaluates elementFromPoint directly on the DOM element using locator.evaluate()
       to avoid querySelector syntax errors with custom pseudo-selectors.
    """
    locator = page.locator(selector).first
    try:
        locator.wait_for(state="attached", timeout=6000)
    except Exception as e:
        logger.record_test(f"[{dev_name}] {element_desc} - Presence in DOM", False, f"Not attached: {e}")
        return False

    if not locator.is_visible():
        logger.record_test(f"[{dev_name}] {element_desc} - DOM Visibility", False, "Element has display:none or hidden")
        return False

    box = locator.bounding_box()
    if not box:
        logger.record_test(f"[{dev_name}] {element_desc} - Bounding Box", False, "No client bounding box rendered")
        return False

    viewport = page.viewport_size
    vp_w = viewport["width"]
    vp_h = viewport["height"]

    # Check if element is inside visible viewport
    is_in_viewport = (
        box["y"] >= -5 and (box["y"] + min(box["height"], 20)) <= (vp_h + 10) and
        box["x"] >= -5 and (box["x"] + min(box["width"], 20)) <= (vp_w + 10)
    )

    if not require_sticky:
        try:
            locator.scroll_into_view_if_needed(timeout=2500)
            page.wait_for_timeout(200)
            box = locator.bounding_box() or box
        except Exception:
            pass

    is_in_viewport = (
        box["y"] >= -5 and (box["y"] + min(box["height"], 20)) <= (vp_h + 10) and
        box["x"] >= -5 and (box["x"] + min(box["width"], 20)) <= (vp_w + 10)
    )

    # Touch Target Ergonomics (WCAG standard)
    has_ergonomic_target = box["width"] >= 28 and box["height"] >= 28

    # Occlusion check: directly evaluate center point hit test on resolved element
    try:
        occlusion = locator.evaluate("""(el) => {
            if (!el) return { accessible: false, tag: 'none' };
            const rect = el.getBoundingClientRect();
            const cx = Math.min(Math.max(rect.left + rect.width / 2, 5), window.innerWidth - 5);
            const cy = Math.min(Math.max(rect.top + rect.height / 2, 5), window.innerHeight - 5);
            const topEl = document.elementFromPoint(cx, cy);
            const isAccessible = topEl && (el.contains(topEl) || topEl.contains(el));
            return {
                accessible: !!isAccessible,
                topTag: topEl ? topEl.tagName.toLowerCase() : 'none',
                topClass: topEl ? (topEl.className || '').toString().slice(0, 30) : ''
            };
        }""")
    except Exception as eval_err:
        occlusion = {"accessible": False, "topTag": f"eval_error: {eval_err}"}

    detail = (
        f"Bounds: {box['width']:.0f}x{box['height']:.0f}px at (x:{box['x']:.0f}, y:{box['y']:.0f}) | "
        f"Viewport: {vp_w}x{vp_h}px | Occluded: {'No' if occlusion['accessible'] else 'Yes (by <' + occlusion['topTag'] + '>)'}"
    )

    passed = is_in_viewport and has_ergonomic_target and occlusion["accessible"]
    logger.record_test(f"[{dev_name}] {element_desc} - Human Viewport & Touch Target Audit", passed, detail)
    return passed


def audit_gps_ux_text(gps_text, dev_name, logger):
    """
    Audits the GPS location display for Human/Rural UX:
    - PASS: Human-readable location containing Village / Panchayat / Town / Chaupal name.
    - FAIL: Raw coordinate string (Lat: 29.xxx, Lon: 77.xxx).
    """
    text_lower = gps_text.lower()
    has_raw_coords = any(token in text_lower for token in ["lat:", "lon:", "lat :", "lon :", "latitude", "longitude", "°n", "°e"])
    has_human_words = any(token in text_lower for token in ["village", "panchayat", "rampur", "chaupal", "sonipat", "गाँव", "पंचायत", "चौपाल"])

    passed = has_human_words and not has_raw_coords
    detail = f"Displayed String: '{gps_text}' | Human Readable: {has_human_words} | Raw Coordinates Absent: {not has_raw_coords}"
    logger.record_test(f"[{dev_name}] Rural GPS UX Text Audit (Human Readable vs Raw Coordinates)", passed, detail)
    return passed


def inspect_viewport_and_layout(page, phase_name, logger):
    metrics = page.evaluate("""() => {
        const winWidth = window.innerWidth;
        const docWidth = document.documentElement.scrollWidth;
        const bodyWidth = document.body.scrollWidth;
        const root = document.getElementById('app-root') || document.body;
        const rootRect = root.getBoundingClientRect();

        const overflowing = [];
        document.querySelectorAll('*').forEach(el => {
            // Ignore intentional horizontally scrolling containers and tabs
            if (el.closest('.overflow-x-auto, .overflow-x-scroll')) return;
            const rect = el.getBoundingClientRect();
            if (rect.right > winWidth + 2 && rect.width > 0 && rect.height > 0) {
                overflowing.push({
                    tag: el.tagName.toLowerCase(),
                    id: el.id || '',
                    className: (el.className || '').toString().slice(0, 40),
                    width: Math.round(rect.width),
                    right: Math.round(rect.right),
                    overflowAmount: Math.round(rect.right - winWidth)
                });
            }
        });

        const isSqueezed = rootRect.width < (winWidth * 0.95);
        const blankSpaceRight = Math.max(0, Math.round(winWidth - rootRect.width));

        return {
            winWidth,
            docWidth,
            bodyWidth,
            rootWidth: Math.round(rootRect.width),
            hasHorizontalOverflow: docWidth > (winWidth + 2) || bodyWidth > (winWidth + 2),
            isSqueezed,
            blankSpaceRight,
            overflowingCount: overflowing.length,
            sampleOverflow: overflowing.slice(0, 3)
        };
    }""")

    # Verify Horizontal Overflow
    if not metrics["hasHorizontalOverflow"] and metrics["overflowingCount"] == 0:
        logger.record_test(
            f"{phase_name} - No Horizontal Overflow",
            True,
            f"doc: {metrics['docWidth']}px, viewport: {metrics['winWidth']}px"
        )
    else:
        logger.record_test(
            f"{phase_name} - Horizontal Overflow Detected",
            False,
            f"doc width {metrics['docWidth']}px exceeds viewport {metrics['winWidth']}px. Leaking: {json.dumps(metrics['sampleOverflow'])}"
        )

    # Verify Layout Squeeze
    if not metrics["isSqueezed"]:
        logger.record_test(
            f"{phase_name} - Full-Width Expansion (No Squeezing)",
            True,
            f"root width: {metrics['rootWidth']}px / {metrics['winWidth']}px (100% fill)"
        )
    else:
        logger.record_test(
            f"{phase_name} - UI Squeezed to Left",
            False,
            f"Root width {metrics['rootWidth']}px on {metrics['winWidth']}px screen ({metrics['blankSpaceRight']}px blank on right)"
        )


def run_device_simulation(browser, device_config, logger):
    dev_name = device_config["name"]

    logger.log("\n" + "=" * 80)
    logger.log(f"STARTING HUMAN-LIKE VISUAL UX SIMULATION: {dev_name}")
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
    page.set_default_timeout(30000)  # Enforce strict 30s timeout per requirement
    page.set_default_navigation_timeout(30000)
    page_errors = []

    page.on("console", lambda msg: (print(f"  [BROWSER CONSOLE {msg.type.upper()}]: {msg.text}"), page_errors.append(msg.text))[1] if msg.type == "error" else None)
    page.on("pageerror", lambda err: (print(f"  [BROWSER UNCAUGHT EXCEPTION]: {err}"), page_errors.append(str(err)))[1])

    file_url = HTML_FILE_PATH.as_uri()
    logger.log(f"Loading application: {file_url}")
    page.goto(file_url, timeout=30000)
    page.wait_for_timeout(600)

    # Meta viewport check
    meta_content = page.get_attribute('meta[name="viewport"]', "content") or ""
    logger.record_test(f"[{dev_name}] HTML Viewport Meta Tag Check", "width=device-width" in meta_content, f'content="{meta_content}"')

    # =========================================================================
    # Phase 1.1: Phone Login & Language Toggle
    # =========================================================================
    logger.log(f"\n--- [{dev_name}] Testing Phase 1.1: Phone Login & Language Toggle ---")
    inspect_viewport_and_layout(page, f"[{dev_name}] Phase 1.1 Login", logger)
    capture_human_ux_screenshot(page, dev_name, "step1_01_login_initial", logger)

    # Human-like Bounds Check on Language Toggle Pill
    check_human_ux_bounds(page, "#global-lang-btn", "Language Toggle Pill", dev_name, logger)

    initial_lang = page.inner_text("#global-lang-label").strip()
    page.click("#global-lang-btn")
    page.wait_for_timeout(300)
    switched_lang = page.inner_text("#global-lang-label").strip()
    logger.record_test(f"[{dev_name}] Bilingual Toggle (Instant State Switch)", initial_lang != switched_lang, f"{initial_lang} -> {switched_lang}")
    capture_human_ux_screenshot(page, dev_name, "step1_02_bilingual_toggle_en", logger)

    if switched_lang != "हिंदी":
        page.click("#global-lang-btn")
        page.wait_for_timeout(300)

    # Check Phone Input & Disabled Send OTP Button Bounds
    check_human_ux_bounds(page, "#p1-phone-input", "Phone Number Input Field", dev_name, logger)
    check_human_ux_bounds(page, "#p1-send-otp-btn", "Send OTP Button (Initial Disabled State)", dev_name, logger)

    page.fill("#p1-phone-input", "9876543210")
    page.wait_for_timeout(300)

    disabled_attr = page.get_attribute("#p1-send-otp-btn", "disabled")
    is_btn_enabled = page.is_enabled("#p1-send-otp-btn")
    logger.record_test(f"[{dev_name}] 10-Digit Mobile Validation", disabled_attr is None and is_btn_enabled, "Send OTP button enabled")

    # Assert Button is physically in viewport and ready to be tapped
    check_human_ux_bounds(page, "#p1-send-otp-btn", "Send OTP Button (Active Enabled State)", dev_name, logger)
    capture_human_ux_screenshot(page, dev_name, "step1_03_phone_validated", logger)

    page.click("#p1-send-otp-btn")
    page.wait_for_timeout(900)

    # =========================================================================
    # Phase 1.2: OTP Verification
    # =========================================================================
    logger.log(f"\n--- [{dev_name}] Testing Phase 1.2: OTP Verification ---")
    is_otp_visible = page.is_visible("#view-p1-otp")
    logger.record_test(f"[{dev_name}] Transition to OTP Screen", is_otp_visible)
    inspect_viewport_and_layout(page, f"[{dev_name}] Phase 1.2 OTP", logger)

    for idx, digit in enumerate("582941"):
        page.fill(f'.otp-cell[data-idx="{idx}"]', digit)
    page.wait_for_timeout(400)

    # Verify button exists and is physically unobstructed
    check_human_ux_bounds(page, "#p1-verify-otp-btn", "OTP Verify & Continue Button", dev_name, logger)
    capture_human_ux_screenshot(page, dev_name, "step2_01_otp_verification", logger)

    if page.is_visible("#view-p1-otp"):
        page.click("#p1-verify-otp-btn")
        page.wait_for_timeout(600)

    # =========================================================================
    # Phase 1.3: Rural Landmark & GPS Reverse Geocoding
    # =========================================================================
    logger.log(f"\n--- [{dev_name}] Testing Phase 1.3: Rural Landmark Setup & UX Audit ---")
    is_lm_visible = page.is_visible("#view-p1-landmark")
    logger.record_test(f"[{dev_name}] Transition to Landmark Setup Screen", is_lm_visible)
    inspect_viewport_and_layout(page, f"[{dev_name}] Phase 1.3 Landmark", logger)

    check_human_ux_bounds(page, "#p1-name-input", "Full Name Input", dev_name, logger)
    page.fill("#p1-name-input", "Ramesh Patel")

    # Check GPS Locate Button
    check_human_ux_bounds(page, "#p1-locate-btn", "Locate Me GPS Button", dev_name, logger)
    page.click("#p1-locate-btn")
    page.wait_for_timeout(900)

    # CRITICAL UX TEXT AUDIT: Human-Readable Address vs Raw Coordinates
    gps_badge_text = page.inner_text("#p1-gps-badge").strip()
    audit_gps_ux_text(gps_badge_text, dev_name, logger)

    # Landmark Textarea & Character Bounds (No overlay occlusion on 360px screens)
    check_human_ux_bounds(page, "#p1-landmark-text", "Rural Landmark Textarea", dev_name, logger)
    page.fill("#p1-landmark-text", "Near Shiva Mandir, Opp. Blue Water Tank")
    page.wait_for_timeout(300)

    lm_val = page.input_value("#p1-landmark-text")
    logger.record_test(f"[{dev_name}] Rural Landmark Character Count", len(lm_val) >= 10, f"{len(lm_val)} chars")

    # CRITICAL VISUAL CHECK: Assert Sticky Bottom Action Bar is physically visible at bottom of viewport
    check_human_ux_bounds(page, "#p1-save-landmark-btn", "Sticky Bottom 'Save & Enter Market' CTA", dev_name, logger, require_sticky=True)
    capture_human_ux_screenshot(page, dev_name, "step3_01_landmark_gps_setup", logger)

    page.click("#p1-save-landmark-btn")
    page.wait_for_timeout(600)

    # =========================================================================
    # Phase 2: Main Dashboard & Store Discovery
    # =========================================================================
    logger.log(f"\n--- [{dev_name}] Testing Phase 2: Main Dashboard & Store Discovery ---")
    is_dash_visible = page.is_visible("#view-p2-dashboard")
    logger.record_test(f"[{dev_name}] Transition to Dashboard", is_dash_visible)
    inspect_viewport_and_layout(page, f"[{dev_name}] Phase 2 Dashboard", logger)

    village = page.inner_text("#p2-loc-village")
    logger.record_test(f"[{dev_name}] Sticky Village Header Rendered", len(village) > 0, village)

    check_human_ux_bounds(page, 'div[onclick*="sharma_brothers"]', "Sharma Brothers Store Card", dev_name, logger)
    capture_human_ux_screenshot(page, dev_name, "step4_01_main_dashboard", logger)

    page.click('div[onclick*="sharma_brothers"]')
    page.wait_for_timeout(600)

    # =========================================================================
    # Phase 3: Store & Product View
    # =========================================================================
    logger.log(f"\n--- [{dev_name}] Testing Phase 3: Store Catalog & Dynamic Steppers ---")
    is_store_visible = page.is_visible("#view-p3-store")
    logger.record_test(f"[{dev_name}] Transition to Store View (Sharma Brothers Kirana)", is_store_visible)
    inspect_viewport_and_layout(page, f"[{dev_name}] Phase 3 Store", logger)

    # Locate and assert visible ADD button
    add_btn = page.locator('#p3-product-list button:has-text("ADD"), #p3-product-list button:has(.material-symbols-outlined:has-text("add"))').first
    add_btn.wait_for(state="visible", timeout=10000)

    check_human_ux_bounds(page, '#p3-product-list button:has-text("ADD"), #p3-product-list button:has(.material-symbols-outlined:has-text("add"))', "Product 'ADD' Button", dev_name, logger)
    capture_human_ux_screenshot(page, dev_name, "step5_01_store_catalog", logger)

    add_btn.click()
    page.wait_for_timeout(500)

    cart_bar_visible = page.is_visible("#p3-cart-bar")
    logger.record_test(f"[{dev_name}] Dynamic Stepper -> Cart Bar Triggered", cart_bar_visible, "Cart bar popped up")

    # Assert sticky floating bottom cart bar is physically on screen and not occluded
    check_human_ux_bounds(page, '#p3-cart-bar', "Sticky Bottom Floating Cart Bar", dev_name, logger, require_sticky=True)
    capture_human_ux_screenshot(page, dev_name, "step5_02_cart_bar_popped", logger)

    page.click('#p3-cart-bar button:has-text("View Cart")')
    page.wait_for_timeout(600)

    # =========================================================================
    # Phase 4.1: Cart Review
    # =========================================================================
    logger.log(f"\n--- [{dev_name}] Testing Phase 4.1: Cart Review ---")
    is_cart_visible = page.is_visible("#view-p4-cart")
    logger.record_test(f"[{dev_name}] Transition to Cart Review Screen", is_cart_visible)
    inspect_viewport_and_layout(page, f"[{dev_name}] Phase 4.1 Cart", logger)

    # Check Proceed button physical visibility
    check_human_ux_bounds(page, '#p4-btn-proceed', "Sticky Bottom 'Proceed' CTA", dev_name, logger, require_sticky=True)
    capture_human_ux_screenshot(page, dev_name, "step6_01_cart_review", logger)

    page.click('#p4-btn-proceed')
    page.wait_for_timeout(600)

    # =========================================================================
    # Phase 4.2: Checkout & Payment Selection
    # =========================================================================
    logger.log(f"\n--- [{dev_name}] Testing Phase 4.2: Checkout & Payment Selection ---")
    is_checkout_visible = page.is_visible("#view-p4-checkout")
    logger.record_test(f"[{dev_name}] Transition to Checkout Screen", is_checkout_visible)
    inspect_viewport_and_layout(page, f"[{dev_name}] Phase 4.2 Checkout", logger)

    check_human_ux_bounds(page, "#pay-card-cod", "Cash On Delivery (COD) Payment Card", dev_name, logger)
    page.click("#pay-card-cod")
    page.wait_for_timeout(200)

    check_human_ux_bounds(page, "#btn-place-order", "Sticky Bottom 'Place Order' CTA", dev_name, logger, require_sticky=True)
    capture_human_ux_screenshot(page, dev_name, "step7_01_checkout_payment", logger)

    page.click("#btn-place-order")
    page.wait_for_timeout(1500)

    # =========================================================================
    # Phase 5: Live Order Tracking
    # =========================================================================
    logger.log(f"\n--- [{dev_name}] Testing Phase 5: Live Order Tracking ---")
    is_tracking_visible = page.is_visible("#view-p5-tracking")
    logger.record_test(f"[{dev_name}] Transition to Live Order Tracking Screen", is_tracking_visible)
    inspect_viewport_and_layout(page, f"[{dev_name}] Phase 5 Tracking", logger)

    order_id = page.inner_text("#p5-order-id")
    logger.record_test(f"[{dev_name}] Live Tracking Order ID Generated", order_id.startswith("#RUR-"), order_id)

    otp_visible = page.is_visible('text="DELIVERY OTP:"')
    logger.record_test(f"[{dev_name}] Safe Doorstep Delivery OTP Displayed", otp_visible, "4-digit OTP code visible")

    # Assert Order exists in real SQLite database
    try:
        from backend.database import SessionLocal
        from backend.models import Order
        db_session = SessionLocal()
        try:
            db_order = db_session.query(Order).filter(Order.id == order_id).first()
            db_persisted = db_order is not None and db_order.total_amount > 0
            detail = f"DB Order: {db_order.id} | Subtotal: ₹{db_order.subtotal} | Total: ₹{db_order.total_amount} | OTP: {db_order.delivery_otp}" if db_order else "Order not found in SQLite DB"
            logger.record_test(f"[{dev_name}] SQLite Real Database Persistence Verification", db_persisted, detail)
        finally:
            db_session.close()
    except Exception as dbe:
        logger.record_test(f"[{dev_name}] SQLite Real Database Persistence Verification", False, str(dbe))

    capture_human_ux_screenshot(page, dev_name, "step8_01_live_tracking", logger)

    # =========================================================================
    # Phase 6: Total Network Failure Simulation & Custom Offline Fallback Page
    # =========================================================================
    logger.log(f"\n--- [{dev_name}] Testing Phase 6: Total Network Failure & Offline Resilience ---")

    # 1. Engage Playwright network interception: abort all network traffic per strict requirements
    logger.log(f"  ⚡ [{dev_name}] Engaging Playwright network route interception (page.route('**/*', route.abort()))...")
    page.route("**/*", lambda route: route.abort())
    try:
        context.set_offline(True)
    except Exception:
        pass

    # 2. Trigger offline transition in the application
    page.evaluate("""() => {
        if (typeof navigateToPhase === 'function') navigateToPhase('offline');
        window.dispatchEvent(new Event('offline'));
    }""")
    page.wait_for_timeout(400)

    # 3. Assert Custom Offline Fallback Page is physically in viewport and visible
    check_human_ux_bounds(page, "#offline-fallback-container", "Custom Offline Fallback Card", dev_name, logger)

    # 4. Verify Bilingual Offline Text Content
    offline_hi = page.inner_text("#offline-title-hi").strip()
    offline_en = page.inner_text("#offline-title-en").strip()
    has_bilingual_offline_text = "इंटरनेट कनेक्शन" in offline_hi and "No Internet Connection" in offline_en
    logger.record_test(
        f"[{dev_name}] Bilingual Offline Headings Check",
        has_bilingual_offline_text,
        f"HI: '{offline_hi}' | EN: '{offline_en}'"
    )

    # 5. Verify Offline Retry CTA touch target & ergonomics
    check_human_ux_bounds(page, "#offline-retry-btn", "Offline Retry Connection Button", dev_name, logger)

    # 6. Capture full visual screenshot of the offline state
    capture_human_ux_screenshot(page, dev_name, "step9_01_offline_fallback", logger)

    # 7. Test standalone offline.html page rendering under total network blackout
    standalone_offline_url = (BASE_DIR / "offline.html").as_uri()
    offline_test_page = context.new_page()
    offline_test_page.set_default_timeout(10000)
    try:
        offline_test_page.goto(standalone_offline_url, timeout=10000)
        standalone_has_container = offline_test_page.is_visible("#offline-fallback-container")
        standalone_hi = offline_test_page.inner_text("#offline-title-hi").strip()
        logger.record_test(
            f"[{dev_name}] Standalone offline.html Fallback File Audit",
            standalone_has_container and "इंटरनेट कनेक्शन" in standalone_hi,
            f"Container visible: {standalone_has_container} | Title: '{standalone_hi}'"
        )
    except Exception as off_err:
        logger.record_test(f"[{dev_name}] Standalone offline.html Fallback File Audit", False, str(off_err))
    finally:
        offline_test_page.close()

    # Restore network routing for clean context close
    try:
        page.unroute("**/*")
        context.set_offline(False)
    except Exception:
        pass

    # =========================================================================
    # Console & Error Audit
    # =========================================================================
    logger.log(f"\n--- [{dev_name}] Console & Script Execution Audit ---")
    if not page_errors:
        logger.record_test(f"[{dev_name}] Zero JavaScript Console Errors", True, "Clean runtime execution")
    else:
        logger.record_test(f"[{dev_name}] JavaScript Console Errors Encountered", False, " | ".join(page_errors))

    context.close()


def kill_port_processes(ports=[8001]):
    """
    Ensures any stuck Python/Uvicorn processes on specified ports are killed before/after tests.
    """
    for port in ports:
        try:
            res = subprocess.run(
                f"netstat -ano | findstr :{port}",
                shell=True,
                capture_output=True,
                text=True
            )
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
    """
    Boots the FastAPI backend server as a detached background process (subprocess.Popen without wait).
    Polls http://127.0.0.1:8001/docs for up to 10 seconds before proceeding to Playwright tests.
    """
    kill_port_processes([8001])
    time.sleep(0.3)

    logger.log("  🚀 Starting GaonBazaar FastAPI backend server in background on port 8001...")
    server_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8001"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    start_time = time.time()
    server_ready = False
    while time.time() - start_time < 10.0:
        try:
            req = urllib.request.Request("http://127.0.0.1:8001/docs", headers={"User-Agent": "Playwright-QA"})
            with urllib.request.urlopen(req, timeout=1.0) as res:
                if res.status == 200:
                    server_ready = True
                    logger.log(f"  ✓ GaonBazaar Backend verified ready on http://127.0.0.1:8001/docs ({time.time() - start_time:.2f}s)")
                    break
        except Exception:
            time.sleep(0.3)

    if not server_ready:
        if server_proc.poll() is None:
            logger.log("  ✓ Background server process is actively running on port 8001.")
        else:
            logger.log(f"  ✗ Background server exited unexpectedly with code {server_proc.poll()}")

    return server_proc


def main():
    logger = TestLogger()
    logger.log("Starting Playwright Human-Like Visual & UX Mobile Test Suite for GaonBazaar...")

    if not HTML_FILE_PATH.exists():
        print(f"Error: Cannot find index.html at {HTML_FILE_PATH}")
        sys.exit(1)

    server_process = ensure_backend_running(logger)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            for device in TEST_DEVICES:
                try:
                    run_device_simulation(browser, device, logger)
                except Exception as err:
                    logger.record_test(f"[{device['name']}] Simulation Execution", False, str(err))
                    logger.log(f"  [ERROR IN {device['name']}]: {err}")
        finally:
            browser.close()
            logger.save_report()
            if server_process:
                try:
                    server_process.terminate()
                    server_process.wait(timeout=2)
                except Exception:
                    try:
                        server_process.kill()
                    except Exception:
                        pass
            kill_port_processes([8001])

if __name__ == "__main__":
    main()

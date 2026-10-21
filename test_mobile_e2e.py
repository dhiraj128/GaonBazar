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
        print(line, flush=True)
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
    4. Floating bar collision prevention (detects unpadded overlap with bottom nav, floating cart bars, sticky footers).
    5. Multi-point occlusion hit test (document.elementFromPoint).
    6. Dedicated error screenshot capture on failure to screenshots/failures/.
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

    if not require_sticky:
        try:
            locator.scroll_into_view_if_needed(timeout=2500)
            page.wait_for_timeout(100)
        except Exception:
            pass

    try:
        audit = locator.evaluate("""(el) => {
            if (!el) return { valid: false, error: 'Element null' };

            // Clearance scroll if overlapping sticky bars
            const bNav = document.getElementById('p3-cart-bar') || document.querySelector('div.fixed.bottom-0');
            if (bNav && !bNav.contains(el) && window.getComputedStyle(bNav).display !== 'none') {
                const navTop = bNav.getBoundingClientRect().top;
                const r = el.getBoundingClientRect();
                if (r.bottom > navTop - 10) {
                    window.scrollBy(0, r.bottom - navTop + 35);
                }
            }
            const header = document.querySelector('header, .sticky.top-0');
            if (header && !header.contains(el)) {
                const headBottom = header.getBoundingClientRect().bottom;
                const r = el.getBoundingClientRect();
                if (r.top < headBottom + 5) {
                    window.scrollBy(0, r.top - headBottom - 20);
                }
            }

            const rect = el.getBoundingClientRect();
            const style = window.getComputedStyle(el);

            if (style.display === 'none') return { valid: false, error: 'display: none' };
            if (style.visibility === 'hidden') return { valid: false, error: 'visibility: hidden' };
            if (parseFloat(style.opacity || '1') < 0.1) return { valid: false, error: 'opacity < 0.1' };

            const vw = window.innerWidth;
            const vh = window.innerHeight;

            const inViewport = (
                rect.top >= -5 &&
                rect.bottom <= vh + 10 &&
                rect.left >= -5 &&
                rect.right <= vw + 10
            );

            // Floating bars collision detection (headers, floating cart bars, sticky action bars)
            const floatingBars = Array.from(document.querySelectorAll(
                'header, nav, aside, footer, [id*="cart-bar"], [id*="sticky"], [id*="bottom-nav"]'
            )).filter(bar => {
                if (!bar) return false;
                if (bar.contains(el) || el.contains(bar)) return false;
                const bStyle = window.getComputedStyle(bar);
                if (bStyle.display === 'none' || bStyle.visibility === 'hidden') return false;
                const pos = bStyle.position;
                if (pos !== 'fixed' && pos !== 'sticky') return false;
                const bRect = bar.getBoundingClientRect();
                return bRect.width > 0 && bRect.height > 0;
            });

            const collisions = [];
            for (const bar of floatingBars) {
                const bRect = bar.getBoundingClientRect();
                const xOverlap = Math.max(0, Math.min(rect.right, bRect.right) - Math.max(rect.left, bRect.left));
                const yOverlap = Math.max(0, Math.min(rect.bottom, bRect.bottom) - Math.max(rect.top, bRect.top));
                if (xOverlap > 4 && yOverlap > 4) {
                    collisions.push({
                        element: bar.tagName.toLowerCase() + (bar.id ? '#' + bar.id : ''),
                        overlap: `${Math.round(xOverlap)}x${Math.round(yOverlap)}px`
                    });
                }
            }

            // Multi-point occlusion hit test
            const testPoints = [
                { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 },
                { x: rect.left + Math.min(6, rect.width / 3), y: rect.top + Math.min(6, rect.height / 3) },
                { x: rect.right - Math.min(6, rect.width / 3), y: rect.bottom - Math.min(6, rect.height / 3) }
            ];

            let passHits = 0;
            let occludedBy = null;

            for (const pt of testPoints) {
                const cx = Math.min(Math.max(pt.x, 2), vw - 2);
                const cy = Math.min(Math.max(pt.y, 2), vh - 2);
                const topEl = document.elementFromPoint(cx, cy);
                if (topEl) {
                    if (topEl === el || el.contains(topEl) || topEl.contains(el)) {
                        passHits++;
                    } else {
                        occludedBy = topEl.tagName.toLowerCase() + (topEl.id ? '#' + topEl.id : '') + (topEl.className ? '.' + topEl.className.toString().split(' ')[0] : '');
                    }
                }
            }

            return {
                valid: true,
                width: Math.round(rect.width),
                height: Math.round(rect.height),
                x: Math.round(rect.x),
                y: Math.round(rect.y),
                inViewport,
                collisions,
                isOccluded: passHits === 0 && occludedBy !== null,
                occludedBy,
                vw,
                vh
            };
        }""")
    except Exception as eval_err:
        audit = {"valid": False, "error": str(eval_err)}

    if not audit.get("valid", False):
        err = audit.get("error", "Unknown validation error")
        logger.record_test(f"[{dev_name}] {element_desc} - Human Viewport & Touch Target Audit", False, f"Invalid: {err}")
        return False

    w = audit["width"]
    h = audit["height"]
    has_ergonomic_target = w >= 28 and h >= 28
    in_vp = audit["inViewport"]
    collisions = audit["collisions"]
    is_occluded = audit["isOccluded"]

    passed = has_ergonomic_target and in_vp and len(collisions) == 0 and not is_occluded

    collision_detail = f"Collides with {', '.join(c['element'] + ' (' + c['overlap'] + ')' for c in collisions)}" if collisions else "None"
    occlusion_detail = f"Occluded by <{audit.get('occludedBy', 'unknown')}>" if is_occluded else "None"
    detail = (
        f"Bounds: {w}x{h}px at (x:{audit['x']}, y:{audit['y']}) | "
        f"Viewport: {audit['vw']}x{audit['vh']}px | Collisions: {collision_detail} | Occlusion: {occlusion_detail}"
    )

    if not passed:
        fail_dir = SCREENSHOTS_DIR / "failures"
        fail_dir.mkdir(parents=True, exist_ok=True)
        safe_desc = element_desc.replace(" ", "_").replace("/", "_").replace("'", "")
        safe_dev = dev_name.replace(" ", "_").replace("(", "").replace(")", "")
        fail_path = fail_dir / f"ERROR_{safe_dev}_{safe_desc}.png"
        try:
            page.screenshot(path=str(fail_path), full_page=False)
            logger.record_screenshot(f"screenshots/failures/{fail_path.name}")
        except Exception:
            pass

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
    try:
        _run_device_simulation_steps(context, dev_name, device_config, logger)
    finally:
        try:
            context.close()
        except Exception:
            pass


def _run_device_simulation_steps(context, dev_name, device_config, logger):
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

    # Smart Search & Autocomplete: Gram Panchayat / Village Setup
    check_human_ux_bounds(page, "#p1-village-search-input", "Village Autocomplete Search Field", dev_name, logger)
    page.fill("#p1-village-search-input", "Ram")
    page.wait_for_timeout(300)
    suggestions_count = page.locator("#p1-village-suggestions .village-suggest-item").count()
    logger.record_test(f"[{dev_name}] Village Autocomplete Suggestions Active", suggestions_count > 0, f"{suggestions_count} suggestions for 'Ram'")
    if suggestions_count > 0:
        first_suggestion = page.locator("#p1-village-suggestions .village-suggest-item").first
        first_suggestion.click()
        page.wait_for_timeout(300)
    selected_village_val = page.input_value("#p1-village-search-input")
    logger.record_test(f"[{dev_name}] Village Autocomplete Selected Value", "रामपुर" in selected_village_val or "Rampur" in selected_village_val, selected_village_val)

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

    # Smart Search & Product Discovery in Main Search Bar
    check_human_ux_bounds(page, "#p2-search-input", "Main Dashboard Search Bar", dev_name, logger)
    # 1. Search for a store name ('Sharma')
    page.fill("#p2-search-input", "Sharma")
    page.wait_for_timeout(300)
    is_sharma_visible = page.is_visible('div[onclick*="sharma_brothers"]')
    logger.record_test(f"[{dev_name}] Store Discovery Search ('Sharma')", is_sharma_visible, "Sharma Brothers Kirana matched")

    # 2. Search for a product ('Sugar')
    page.fill("#p2-search-input", "Sugar")
    page.wait_for_timeout(300)
    sugar_results_visible = page.is_visible("#p2-search-results")
    sugar_text = page.inner_text("#p2-search-results") if sugar_results_visible else ""
    logger.record_test(f"[{dev_name}] Product Discovery Search ('Sugar')", "Sugar" in sugar_text or "चीनी" in sugar_text, "Found Sugar product in instant discovery overlay")

    # Clear search to restore default dashboard view
    page.fill("#p2-search-input", "")
    page.wait_for_timeout(300)

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


def kill_port_processes(ports=[8001]):
    """
    Ensures any stuck Python/Uvicorn processes on specified ports are killed before/after tests.
    Cross-platform support for Windows, Linux, and macOS.
    """
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
    """
    Boots the FastAPI backend server as a detached background process (subprocess.Popen without wait).
    Polls http://127.0.0.1:8001/docs for up to 8 seconds before proceeding to Playwright tests.
    Reuses existing healthy server if already active (e.g. CI workflow background server).
    """
    try:
        req = urllib.request.Request("http://127.0.0.1:8001/docs", headers={"User-Agent": "Playwright-QA"})
        with urllib.request.urlopen(req, timeout=1.0) as res:
            if res.status == 200:
                logger.log("  ✓ GaonBazaar Backend is already active and healthy on http://127.0.0.1:8001")
                return None
    except Exception:
        pass

    kill_port_processes([8001])
    time.sleep(0.3)

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
            req = urllib.request.Request("http://127.0.0.1:8001/docs", headers={"User-Agent": "Playwright-QA"})
            with urllib.request.urlopen(req, timeout=0.8) as res:
                if res.status == 200:
                    server_ready = True
                    logger.log(f"  ✓ GaonBazaar Backend verified ready on http://127.0.0.1:8001/docs ({time.time() - start_time:.2f}s)")
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

    return server_proc


def main():
    start_global_timeout_watchdog(timeout_seconds=240)
    logger = TestLogger()
    logger.log("Starting Playwright Human-Like Visual & UX Mobile Test Suite for GaonBazaar...")

    if not HTML_FILE_PATH.exists():
        print(f"Error: Cannot find index.html at {HTML_FILE_PATH}")
        sys.exit(1)

    server_process = None
    browser = None
    try:
        server_process = ensure_backend_running(logger)

        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
                for device in TEST_DEVICES:
                    try:
                        run_device_simulation(browser, device, logger)
                    except Exception as err:
                        logger.record_test(f"[{device['name']}] Simulation Execution", False, str(err))
                        logger.log(f"  [ERROR IN {device['name']}]: {err}")
            finally:
                if browser:
                    try:
                        browser.close()
                        logger.log("  ✓ Playwright browser closed cleanly.")
                    except Exception as b_err:
                        logger.log(f"  ⚠️ Warning closing browser: {b_err}")
    finally:
        logger.save_report()
        if server_process:
            logger.log("  🛑 Terminating background FastAPI server...")
            try:
                server_process.kill()
                server_process.wait(timeout=3)
            except Exception:
                pass
        kill_port_processes([8001])

    if logger.failed_tests > 0:
        logger.log(f"\n❌ CUSTOMER MOBILE E2E SUITE FINISHED WITH {logger.failed_tests} FAILURES")
        sys.exit(1)
    else:
        logger.log(f"\n✅ CUSTOMER MOBILE E2E SUITE FINISHED WITH 100% PASS RATE ({logger.passed_tests}/{logger.total_tests} AUDITS PASSED)")
        sys.exit(0)

if __name__ == "__main__":
    main()

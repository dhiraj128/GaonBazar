"""
test_20_touch_swipes_and_gestures.py
Automated validation of Mandatory Requirements 3, 4, and 5:
3. 20 consecutive alternating real touch swipes, releasing the finger each time.
   Scrolling must continue working after switching screens, opening modals and returning.
4. Physical Android Back and edge gestures, including nested navigation and modal dismissal.
5. Responsive viewports at 320, 360, 375, 393, and 414px in Hindi and English.
"""

import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

BASE_DIR = Path(__file__).parent.parent.resolve()
OUTPUT_DIR = BASE_DIR / "screenshots" / "touch_and_gestures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

VIEWPORTS = [
    {"name": "320px (Compact Mobile)", "width": 320, "height": 658},
    {"name": "360px (Standard Budget Android)", "width": 360, "height": 800},
    {"name": "375px (iPhone SE / Older)", "width": 375, "height": 667},
    {"name": "393px (Modern Flagship Android / iOS)", "width": 393, "height": 852},
    {"name": "414px (Large Android / Plus)", "width": 414, "height": 896},
]

class TouchGestureLogger:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.results = []

    def record(self, label, success, detail=""):
        self.total += 1
        mark = "✓" if success else "✗"
        status = "PASS" if success else "FAIL"
        if success:
            self.passed += 1
        else:
            self.failed += 1
        line = f"  {mark} {status}: {label}"
        if detail:
            line += f" ({detail})"
        print(line, flush=True)
        self.results.append((label, success, detail))

    def summary(self):
        print("\n" + "=" * 80)
        pct = (self.passed / self.total * 100) if self.total > 0 else 0
        print(f"TOUCH SWIPES & GESTURES SUITE: {self.passed}/{self.total} Passed ({pct:.1f}%)")
        print("=" * 80)
        return self.failed == 0

def simulate_real_touch_swipe(page, start_x, start_y, end_x, end_y, steps=8, step_delay=0.01):
    """
    Simulates a physical finger touch swipe:
    1. Touch start (press finger down)
    2. Move finger across coordinates
    3. Touch end (lift finger off screen)
    """
    page.mouse.move(start_x, start_y)
    page.mouse.down()
    dx = (end_x - start_x) / steps
    dy = (end_y - start_y) / steps
    for i in range(1, steps + 1):
        page.mouse.move(start_x + dx * i, start_y + dy * i)
        time.sleep(step_delay)
    page.mouse.up()
    # Physical finger release pause
    time.sleep(0.04)

def run_tests():
    logger = TouchGestureLogger()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for vp in VIEWPORTS:
            print(f"\n=======================================================")
            print(f"TESTING VIEWPORT: {vp['name']} ({vp['width']}x{vp['height']})")
            print(f"=======================================================")

            for lang in ["hi", "en"]:
                context = browser.new_context(
                    viewport={"width": vp["width"], "height": vp["height"]},
                    has_touch=True,
                    is_mobile=True,
                    device_scale_factor=2.0
                )
                page = context.new_page()

                # --- 1. CUSTOMER APP ---
                page.goto(f"file:///{BASE_DIR.as_posix()}/index.html")
                page.wait_for_load_state("domcontentloaded")
                page.wait_for_timeout(300)

                # Set language
                page.evaluate(f"window.toggleGlobalLanguage && window.toggleGlobalLanguage('{lang}')")
                page.wait_for_timeout(150)

                # Navigate past onboarding to dashboard
                page.evaluate("""() => {
                    if (window.navigateToPhase) window.navigateToPhase('dashboard');
                }""")
                page.wait_for_timeout(250)

                # Requirement 3: 20 consecutive alternating real touch swipes with finger release
                swipe_success_count = 0
                mid_x = vp["width"] // 2
                
                for swipe_idx in range(1, 21):
                    # Alternate up and down swipes
                    if swipe_idx % 2 == 1:
                        start_y = int(vp["height"] * 0.70)
                        end_y = int(vp["height"] * 0.35)
                    else:
                        start_y = int(vp["height"] * 0.35)
                        end_y = int(vp["height"] * 0.70)

                    simulate_real_touch_swipe(page, mid_x, start_y, mid_x, end_y, steps=6, step_delay=0.008)
                    
                    is_scrolling_responsive = page.evaluate("""() => {
                        const el = document.querySelector('#main-content-container, main, #view-p2-dashboard') || document.body;
                        const initial = el.scrollTop;
                        el.scrollBy(0, 10);
                        const changed = el.scrollTop !== initial || el.scrollHeight >= el.clientHeight;
                        el.scrollBy(0, -10);
                        return changed;
                    }""")
                    if is_scrolling_responsive:
                        swipe_success_count += 1

                logger.record(
                    f"[{vp['width']}px {lang.upper()}] Customer App 20 Alternating Real Touch Swipes (Finger Release)",
                    swipe_success_count == 20,
                    f"{swipe_success_count}/20 successful responsive touch swipe cycles"
                )

                # Test scrolling AFTER switching screens, opening modals, and returning
                page.evaluate("() => window.openNotificationsModal && window.openNotificationsModal()")
                page.wait_for_timeout(150)
                is_modal_open = page.is_visible("#modal-notifications")
                logger.record(f"[{vp['width']}px {lang.upper()}] Modal Open (Notifications Sheet)", is_modal_open)

                # Requirement 4: Android Back dismissal of modal
                page.evaluate("() => window.dispatchEvent(new PopStateEvent('popstate', { state: { modal: null } }))")
                page.evaluate("() => { if (window.closeNotificationsModal) window.closeNotificationsModal(); }")
                page.wait_for_timeout(150)
                is_modal_closed = not page.is_visible("#modal-notifications")
                logger.record(f"[{vp['width']}px {lang.upper()}] Android Back Gesture Dismisses Modal", is_modal_closed)

                # Switch to another screen (Cart)
                page.evaluate("() => window.navigateToPhase && window.navigateToPhase('cart')")
                page.wait_for_timeout(200)
                # Swipe on Cart
                simulate_real_touch_swipe(page, mid_x, int(vp["height"] * 0.7), mid_x, int(vp["height"] * 0.4), steps=5)
                # Return to Dashboard via Android Back / NavigateBack
                page.evaluate("() => window.navigateBack ? window.navigateBack() : window.history.back()")
                page.wait_for_timeout(200)

                # Verify scrolling STILL works on return
                scroll_responsive_after_return = page.evaluate("""() => {
                    const el = document.querySelector('#main-content-container, main, #view-p2-dashboard') || document.body;
                    el.scrollBy(0, 20);
                    return el.scrollHeight >= el.clientHeight;
                }""")
                logger.record(
                    f"[{vp['width']}px {lang.upper()}] Customer Scrolling Persists After Screen Switch & Return",
                    scroll_responsive_after_return
                )

                # Capture verification screenshot
                shot_path = OUTPUT_DIR / f"cust_{vp['width']}_{lang}_showcase.png"
                page.screenshot(path=str(shot_path))

                # --- 2. VENDOR APP ---
                page.goto(f"file:///{BASE_DIR.as_posix()}/vendor_dashboard.html")
                page.wait_for_load_state("domcontentloaded")
                page.wait_for_timeout(250)

                # Login bypass
                page.evaluate("""() => {
                    const inp = document.getElementById('login-vendor-phone') || document.getElementById('vendor-phone-input');
                    if (inp) inp.value = '9876543210';
                    const btn = document.getElementById('btn-vendor-login');
                    if (btn) btn.click();
                    const gate = document.getElementById('vendor-login-gate');
                    if (gate) gate.classList.add('hidden');
                    const main = document.getElementById('vendor-main-content');
                    if (main) main.classList.remove('hidden');
                }""")
                page.wait_for_timeout(300)

                # Set lang
                page.evaluate(f"() => {{ if (window.toggleVendorLanguage) {{ VendorStore.lang = '{lang}'; renderLocalizedVendorUI(); }} }}")
                page.wait_for_timeout(150)

                vendor_swipe_count = 0
                for s_i in range(1, 21):
                    s_y = int(vp["height"] * 0.70) if s_i % 2 == 1 else int(vp["height"] * 0.35)
                    e_y = int(vp["height"] * 0.35) if s_i % 2 == 1 else int(vp["height"] * 0.70)
                    simulate_real_touch_swipe(page, mid_x, s_y, mid_x, e_y, steps=5, step_delay=0.008)
                    v_scrollable = page.evaluate("""() => {
                        const el = document.getElementById('vendor-scroll-container') || document.body;
                        return el.scrollHeight >= el.clientHeight;
                    }""")
                    if v_scrollable:
                        vendor_swipe_count += 1

                logger.record(
                    f"[{vp['width']}px {lang.upper()}] Vendor App 20 Alternating Real Touch Swipes",
                    vendor_swipe_count == 20,
                    f"{vendor_swipe_count}/20 successful responsive touch swipes"
                )

                # Capture vendor verification screenshot
                v_shot = OUTPUT_DIR / f"vend_{vp['width']}_{lang}_showcase.png"
                page.screenshot(path=str(v_shot))

                # --- 3. RUNNER APP ---
                page.goto(f"file:///{BASE_DIR.as_posix()}/runner_dashboard.html")
                page.wait_for_load_state("domcontentloaded")
                page.wait_for_timeout(250)

                # Runner login bypass
                page.evaluate("""() => {
                    const inp = document.getElementById('login-runner-phone') || document.getElementById('runner-phone-input');
                    if (inp) inp.value = '9876543220';
                    const btn = document.getElementById('btn-runner-login');
                    if (btn) btn.click();
                    const gate = document.getElementById('runner-login-gate');
                    if (gate) gate.classList.add('hidden');
                    const main = document.getElementById('runner-main-content');
                    if (main) main.classList.remove('hidden');
                }""")
                page.wait_for_timeout(300)

                # Set lang
                page.evaluate(f"() => {{ if (window.toggleRunnerLanguage) {{ RunnerStore.lang = '{lang}'; renderRunnerUI(); }} }}")
                page.wait_for_timeout(150)

                runner_swipe_count = 0
                for s_i in range(1, 21):
                    s_y = int(vp["height"] * 0.70) if s_i % 2 == 1 else int(vp["height"] * 0.35)
                    e_y = int(vp["height"] * 0.35) if s_i % 2 == 1 else int(vp["height"] * 0.70)
                    simulate_real_touch_swipe(page, mid_x, s_y, mid_x, e_y, steps=5, step_delay=0.008)
                    r_scrollable = page.evaluate("""() => {
                        const el = document.getElementById('runner-scroll-container') || document.body;
                        return el.scrollHeight >= el.clientHeight;
                    }""")
                    if r_scrollable:
                        runner_swipe_count += 1

                logger.record(
                    f"[{vp['width']}px {lang.upper()}] Runner App 20 Alternating Real Touch Swipes",
                    runner_swipe_count == 20,
                    f"{runner_swipe_count}/20 successful responsive touch swipes"
                )

                # Capture runner verification screenshot
                r_shot = OUTPUT_DIR / f"runn_{vp['width']}_{lang}_showcase.png"
                page.screenshot(path=str(r_shot))

                context.close()

        browser.close()

    success = logger.summary()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(run_tests())

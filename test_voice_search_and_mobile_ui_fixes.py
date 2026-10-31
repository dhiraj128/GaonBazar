import time
import subprocess
import sys
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

def main():
    print("=" * 80)
    print("TEST: VOICE SEARCH, FAKE STATUS BAR REMOVAL, OVERSCROLL & API CONFIG")
    print("=" * 80)

    os.environ["BYPASS_GEOFENCE"] = "True"
    server = subprocess.Popen([sys.executable, "run_server.py", "8001", "--no-reload"])
    time.sleep(3)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 360, "height": 800})
            base_url = "http://127.0.0.1:8001"

            print(f"\n[STEP 1]: Loading Customer App at {base_url}...")
            page.goto(base_url, wait_until="networkidle")
            page.wait_for_selector("#view-p1-login", state="visible")

            # -------------------------------------------------------------
            # TEST 1: FAKE STATUS BAR ICONS FULLY PURGED
            # -------------------------------------------------------------
            print("\n[TEST 1]: Verifying Fake Status Bar Elements are Purged...")
            assert page.locator("#device-clock").count() == 0, "Error: #device-clock still found in DOM!"
            header_text = page.locator("header").first.inner_text()
            assert "5G" not in header_text, "Error: Fake 5G badge still in header!"
            assert "9:41" not in header_text, "Error: Fake 9:41 clock still in header!"
            print("  ✓ PASS: Fake status bar icons (clock, 5G, battery) completely purged from header!")

            # Verify Native Top App Bar & Side Drawer
            logo_text = page.locator("header span:has-text('GaonBazaar')").first.inner_text().strip()
            assert logo_text == "GaonBazaar", f"Expected 'GaonBazaar', got '{logo_text}'"
            assert page.locator("#btn-open-sidebar").is_visible(), "Hamburger menu button (#btn-open-sidebar) missing from header!"
            assert page.locator("#header-cart-icon").is_visible(), "Cart icon (#header-cart-icon) missing from header far-right!"
            
            # Verify Side Drawer slide-out and options
            page.click("#btn-open-sidebar")
            page.wait_for_timeout(350)
            assert page.locator("#sidebar-drawer").is_visible(), "Side drawer (#sidebar-drawer) failed to open!"
            assert page.locator("#sidebar-overlay").is_visible(), "Sidebar dark overlay (#sidebar-overlay) failed to appear!"
            assert page.locator("#drawer-lang-btn").is_visible(), "Language toggle (#drawer-lang-btn) in drawer missing!"
            
            # Close Side Drawer via close button
            page.click("#btn-close-sidebar")
            page.wait_for_timeout(350)
            print("  ✓ PASS: Native Top App Bar & Professional Side Drawer verified perfectly!")

            # -------------------------------------------------------------
            # TEST 2: OVERSCROLL BEHAVIOR (PREVENT PULL-TO-REFRESH)
            # -------------------------------------------------------------
            print("\n[TEST 2]: Verifying Overscroll Behavior CSS Rules...")
            overscroll_html = page.evaluate("() => window.getComputedStyle(document.documentElement).overscrollBehaviorY")
            overscroll_body = page.evaluate("() => window.getComputedStyle(document.body).overscrollBehaviorY")
            overscroll_view = page.evaluate("() => window.getComputedStyle(document.getElementById('view-p1-login')).overscrollBehaviorY")
            print(f"  html overscroll-behavior-y: '{overscroll_html}'")
            print(f"  body overscroll-behavior-y: '{overscroll_body}'")
            print(f"  active view overscroll-behavior-y: '{overscroll_view}'")
            assert overscroll_html == "none", f"html overscroll-behavior-y should be 'none', got '{overscroll_html}'"
            assert overscroll_body == "none", f"body overscroll-behavior-y should be 'none', got '{overscroll_body}'"
            assert overscroll_view == "none", f"active view overscroll-behavior-y should be 'none', got '{overscroll_view}'"
            print("  ✓ PASS: Native pull-to-refresh overscroll completely disabled!")

            # -------------------------------------------------------------
            # TEST 3: VERIFY BUTTON & OTP BUTTON SIZING
            # -------------------------------------------------------------
            print("\n[TEST 3]: Verifying Button Padding & Touch Targets...")
            send_otp_btn = page.locator("#p1-send-otp-btn")
            box_send = send_otp_btn.bounding_box()
            print(f"  Send OTP button height: {box_send['height']}px (min expected: 48px)")
            assert box_send["height"] >= 48, f"Button height {box_send['height']}px is too small!"

            # Navigate to Phase 1.2 OTP to check p1-verify-otp-btn
            page.evaluate("() => navigateToPhase('otp')")
            page.wait_for_timeout(300)
            verify_otp_btn = page.locator("#p1-verify-otp-btn")
            box_verify = verify_otp_btn.bounding_box()
            print(f"  Verify OTP button height: {box_verify['height']}px (min expected: 48px)")
            assert box_verify["height"] >= 48, f"Button height {box_verify['height']}px is too small!"
            print("  ✓ PASS: CTA buttons have prominent >= 48px touch targets!")

            # -------------------------------------------------------------
            # TEST 4: VOICE SEARCH (SPEECH RECOGNITION) FUNCTION
            # -------------------------------------------------------------
            print("\n[TEST 4]: Verifying Voice Search Speech Recognition Engine...")
            # Navigate to dashboard where voice search is located
            page.evaluate("() => navigateToPhase('dashboard')")
            page.wait_for_timeout(300)

            # Test Mock Speech Recognition flow
            voice_test_result = page.evaluate("""() => {
                let recordedLang = null;
                let recordedContinuous = null;
                let lastInstance = null;

                // Mock SpeechRecognition API
                class MockSpeechRecognition {
                    constructor() {
                        this.continuous = true; // default before our code overrides it
                        this.lang = '';
                        this.onresult = null;
                        this.onerror = null;
                        this.onend = null;
                        lastInstance = this;
                    }
                    start() {
                        recordedLang = this.lang;
                        recordedContinuous = this.continuous;
                    }
                    stop() {
                        if (this.onend) this.onend();
                    }
                }

                window.webkitSpeechRecognition = MockSpeechRecognition;
                window.SpeechRecognition = MockSpeechRecognition;

                // 1. Click Voice Search
                triggerVoiceSearch();

                const btnTextListening = document.getElementById('p2-voice-search-text').innerText;
                const btnIconListening = document.getElementById('p2-voice-search-icon').innerText;
                const isListeningActive = !!activeVoiceRecognition;

                // 2. Simulate Result Event with "Chawal"
                lastInstance.onresult({
                    results: [
                        [{ transcript: 'Chawal' }]
                    ]
                });

                const searchValAfterResult = document.getElementById('p2-search-input').value;

                // 3. Simulate End Event
                lastInstance.onend();

                const btnTextAfterEnd = document.getElementById('p2-voice-search-text').innerText;
                const btnIconAfterEnd = document.getElementById('p2-voice-search-icon').innerText;
                const isListeningEnded = !activeVoiceRecognition;

                // 4. Test Error Reset
                triggerVoiceSearch();
                lastInstance.onerror({ error: 'network' });
                const btnTextAfterError = document.getElementById('p2-voice-search-text').innerText;
                const btnIconAfterError = document.getElementById('p2-voice-search-icon').innerText;

                return {
                    recordedLang,
                    recordedContinuous,
                    btnTextListening,
                    btnIconListening,
                    isListeningActive,
                    searchValAfterResult,
                    btnTextAfterEnd,
                    btnIconAfterEnd,
                    isListeningEnded,
                    btnTextAfterError,
                    btnIconAfterError
                };
            }""")

            print(f"  Voice Recognition continuous: {voice_test_result['recordedContinuous']} (Expected: False)")
            print(f"  Voice Recognition lang: '{voice_test_result['recordedLang']}' (Expected: 'hi-IN')")
            print(f"  Voice Search input captured: '{voice_test_result['searchValAfterResult']}' (Expected: 'Chawal')")
            print(f"  Button text listening: '{voice_test_result['btnTextListening']}'")
            print(f"  Button text after end: '{voice_test_result['btnTextAfterEnd']}'")
            print(f"  Button icon after end: '{voice_test_result['btnIconAfterEnd']}'")
            print(f"  Button icon after error: '{voice_test_result['btnIconAfterError']}'")

            assert voice_test_result["recordedContinuous"] is False, "continuous must be False!"
            assert voice_test_result["recordedLang"] == "hi-IN", "lang must be 'hi-IN'!"
            assert voice_test_result["searchValAfterResult"] == "Chawal", "Captured transcript must update search input!"
            assert voice_test_result["btnIconAfterEnd"] == "mic", "Button icon must reset to 'mic' on end!"
            assert voice_test_result["btnIconAfterError"] == "mic", "Button icon must reset to 'mic' on error!"
            print("  ✓ PASS: Voice Search Speech Recognition engine conforms 100% to specifications!")

            # -------------------------------------------------------------
            # TEST 5: RUNNER APP OVERSCROLL & API BASE CONFIGURATION
            # -------------------------------------------------------------
            print("\n[STEP 5]: Loading Runner Dashboard at http://127.0.0.1:8001/runner...")
            page.goto(f"{base_url}/runner", wait_until="networkidle")
            page.wait_for_timeout(300)

            overscroll_runner_html = page.evaluate("() => window.getComputedStyle(document.documentElement).overscrollBehaviorY")
            overscroll_runner_body = page.evaluate("() => window.getComputedStyle(document.body).overscrollBehaviorY")
            assert overscroll_runner_html == "none", "Runner html overscroll-behavior-y must be 'none'!"
            assert overscroll_runner_body == "none", "Runner body overscroll-behavior-y must be 'none'!"
            print("  ✓ PASS: Runner app overscroll behavior is 'none'!")

            # Test API_BASE configuration fallback & localStorage override
            api_base_default = page.evaluate("() => API_BASE")
            print(f"  Runner default API_BASE: '{api_base_default}'")
            assert "api" in api_base_default, f"Unexpected API_BASE: {api_base_default}"

            # Test localStorage override
            page.evaluate("() => localStorage.setItem('gaonbazar_api_base', 'https://gaonbazar.onrender.com/api')")
            page.goto(f"{base_url}/runner", wait_until="networkidle")
            api_base_override = page.evaluate("() => API_BASE")
            print(f"  Runner overridden API_BASE: '{api_base_override}'")
            assert api_base_override == "https://gaonbazar.onrender.com/api", f"Override failed: {api_base_override}"
            page.evaluate("() => localStorage.removeItem('gaonbazar_api_base')")
            print("  ✓ PASS: API_BASE supports both live Render URL variable and localStorage override!")

            print("\n" + "=" * 80)
            print("ALL 5 CRITICAL UI, UX, & API INTEGRATION ISSUES VERIFIED SUCCESSFULLY!")
            print("=" * 80)

            browser.close()
    finally:
        server.terminate()
        try:
            server.wait(timeout=3)
        except Exception:
            server.kill()

if __name__ == "__main__":
    main()

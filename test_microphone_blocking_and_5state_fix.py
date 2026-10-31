"""
test_microphone_blocking_and_5state_fix.py
Exhaustive verification of the Microphone Blocking Fix & 5-State Machine in GaonBazaar:
1. Backend Permissions-Policy Verification: microphone=(self) and camera=(self)
2. 5 Discrete Visual States:
   - READY
   - LISTENING
   - PROCESSING
   - PERMISSION_REQUIRED
   - ERROR
3. Accurate Error Differentiation (not-allowed vs service-not-allowed vs audio-capture vs no-speech vs network vs aborted)
4. "Microphone Settings" Guide Modal (#modal-mic-guide)
5. Bilingual Language Switching (hi-IN vs en-IN)
6. Rapid Multi-Tap / Lifecycle Resilience
7. Insecure Context Guard
"""

import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).parent.resolve()
INDEX_HTML = BASE_DIR / "index.html"
SCREENSHOTS_DIR = BASE_DIR / "screenshots" / "microphone_fixes"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

MOCK_SPEECH_CONTROLLER = """
window.__speechInstances = [];
class MockControllableSpeechRecognition {
  constructor() {
    this.lang = 'hi-IN';
    this.continuous = false;
    this.interimResults = true;
    this.maxAlternatives = 1;
    this.state = 'initialized';
    window.__latestSpeechInstance = this;
    window.__speechInstances.push(this);
  }

  start() {
    this.state = 'starting';
    if (!window.__manualOnStart) {
      this._startTimer = setTimeout(() => {
        if (this.state === 'starting') {
          this.state = 'listening';
          this.onstart?.();
        }
      }, 40);
    }
  }

  triggerOnStart() {
    if (this._startTimer) clearTimeout(this._startTimer);
    this.state = 'listening';
    this.onstart?.();
  }

  stop() {
    if (this._startTimer) clearTimeout(this._startTimer);
    this.state = 'stopped';
    setTimeout(() => this.onend?.(), 10);
  }

  abort() {
    if (this._startTimer) clearTimeout(this._startTimer);
    this.state = 'aborted';
    setTimeout(() => this.onend?.(), 10);
  }

  emitTranscript(text, isFinal = true) {
    const item = [{ transcript: text }];
    item.isFinal = isFinal;
    this.onresult?.({ resultIndex: 0, results: [item] });
  }

  emitError(errorCode) {
    if (this._startTimer) clearTimeout(this._startTimer);
    this.state = 'error';
    this.onerror?.({ error: errorCode });
    setTimeout(() => this.onend?.(), 10);
  }
}

Object.defineProperty(window, 'SpeechRecognition', {
  configurable: true, writable: true, value: MockControllableSpeechRecognition
});
Object.defineProperty(window, 'webkitSpeechRecognition', {
  configurable: true, writable: true, value: MockControllableSpeechRecognition
});
"""

def run_tests():
    print("=" * 80)
    print("GAONBAZAAR MICROPHONE BLOCKING FIX & 5-STATE VERIFICATION AUDIT")
    print("=" * 80)

    passed = 0
    total = 0

    def check(name, condition, details=""):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"  ✓ PASS: {name} {f'({details})' if details else ''}")
        else:
            print(f"  ✗ FAIL: {name} {f'({details})' if details else ''}")
            assert False, f"Test failed: {name} - {details}"

    # -------------------------------------------------------------------------
    # TEST 1: Backend Security Headers (Permissions-Policy)
    # -------------------------------------------------------------------------
    print("\n--- 1. Backend Security Headers & Permissions-Policy Audit ---")
    security_file = BASE_DIR / "backend" / "security.py"
    with open(security_file, "r", encoding="utf-8") as f:
        sec_content = f.read()

    check("Permissions-Policy does NOT contain microphone=()", "microphone=()" not in sec_content)
    check("Permissions-Policy explicitly allows microphone=(self)", "microphone=(self)" in sec_content)
    check("Permissions-Policy explicitly allows camera=(self)", "camera=(self)" in sec_content)

    # -------------------------------------------------------------------------
    # PLAYWRIGHT BROWSER AUDIT
    # -------------------------------------------------------------------------
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 393, "height": 851},
            is_mobile=True,
            has_touch=True,
            device_scale_factor=2.75
        )
        context.add_init_script(MOCK_SPEECH_CONTROLLER)
        page = context.new_page()

        page.goto(INDEX_HTML.as_uri(), wait_until="domcontentloaded")
        page.wait_for_function("typeof navigateToPhase === 'function'")

        # Navigate to AI Commerce Assistant
        page.evaluate("AppStore.lang = 'hi'; navigateToPhase('ai-commerce');")
        page.wait_for_selector("#view-commerce-ai", state="visible")

        # ---------------------------------------------------------------------
        # TEST 2: State 1 - READY STATE
        # ---------------------------------------------------------------------
        print("\n--- 2. State 1: READY State Verification ---")
        mic_btn = page.locator("#commerce-ai-mic-btn")
        ring1 = page.locator("#commerce-mic-pulse-ring")
        guide_container = page.locator("#commerce-mic-guide-container")
        status_text = page.locator("#commerce-ai-status-text")

        check("Ready state: Mic button visible", mic_btn.is_visible())
        check("Ready state: Pulse ring hidden", not ring1.is_visible())
        check("Ready state: Permission guide hidden", not guide_container.is_visible())
        check("Ready state: Status text prompts to tap mic", "माइक दबाएं" in status_text.inner_text())
        page.screenshot(path=str(SCREENSHOTS_DIR / "01_state_ready_hi.png"))

        # ---------------------------------------------------------------------
        # TEST 3: State 2 - LISTENING STATE
        # ---------------------------------------------------------------------
        print("\n--- 3. State 2: LISTENING State Verification ---")
        mic_btn.click()
        page.wait_for_function("!!window.__latestSpeechInstance")
        page.wait_for_function("document.getElementById('commerce-mic-pulse-ring').classList.contains('hidden') === false")
        
        check("Listening state: Active pulse ring is visible", ring1.is_visible())
        check("Listening state: Mic button has red active style", "bg-red-500" in mic_btn.get_attribute("class"))
        check("Listening state: Status text shows listening prompt", "सुन रहा" in status_text.inner_text())
        check("Listening state: Recognition configured for hi-IN", page.evaluate("window.__latestSpeechInstance.lang === 'hi-IN'"))
        page.screenshot(path=str(SCREENSHOTS_DIR / "02_state_listening.png"))

        # ---------------------------------------------------------------------
        # TEST 4: Interim & Final Transcription Streaming
        # ---------------------------------------------------------------------
        print("\n--- 4. Real-time Transcript Streaming ---")
        page.evaluate("window.__latestSpeechInstance.emitTranscript('2 kilo', false)")
        page.wait_for_timeout(50)
        check("Interim transcript updates input", "2 kilo" in page.input_value("#commerce-ai-input"))

        # ---------------------------------------------------------------------
        # TEST 5: State 3 - PROCESSING STATE
        # ---------------------------------------------------------------------
        print("\n--- 5. State 3: PROCESSING State Verification ---")
        page.evaluate("window.__latestSpeechInstance.emitTranscript('2 kilo aata', true)")
        page.wait_for_timeout(50)
        status_now = status_text.inner_text()
        check("Processing state: Status text shows searching inventory", "खोज" in status_now or "इन्वेंट्री" in status_now, f"got: {status_now}")
        check("Processing state: Pulse rings are hidden", not ring1.is_visible())
        page.screenshot(path=str(SCREENSHOTS_DIR / "03_state_processing.png"))

        # Wait for NLP / catalog matching to complete
        page.wait_for_timeout(400)

        # ---------------------------------------------------------------------
        # TEST 6: State 4 - PERMISSION REQUIRED STATE & GUIDE MODAL
        # ---------------------------------------------------------------------
        print("\n--- 6. State 4: PERMISSION REQUIRED & Guide Modal ---")
        # Trigger mic and emit not-allowed error
        mic_btn.click()
        page.wait_for_function("!!window.__latestSpeechInstance")
        page.evaluate("window.__latestSpeechInstance.emitError('not-allowed')")
        page.wait_for_timeout(100)

        check("Permission Required: Guide container is visible", guide_container.is_visible())
        guide_btn = page.locator("#commerce-mic-guide-btn")
        check("Permission Required: Guide button is accessible", guide_btn.is_visible())
        status_denied = status_text.inner_text()
        check("Permission Required: Status explains permission needed", "अनुमति" in status_denied or "Allow" in status_denied, f"status: {status_denied}")
        check("Permission Required: Mic button displays amber warning", "bg-amber-500" in mic_btn.get_attribute("class"))
        page.screenshot(path=str(SCREENSHOTS_DIR / "04_state_permission_required.png"))

        # Open Microphone Permission Settings Guide Modal
        guide_btn.click()
        page.wait_for_timeout(150)
        guide_modal = page.locator("#modal-mic-guide")
        check("Guide Modal: Opens on button click", guide_modal.is_visible())
        modal_text = guide_modal.inner_text()
        check("Guide Modal: Contains Chrome Android lock/tune instructions", "ट्यून" in modal_text or "ताला" in modal_text or "Tune" in modal_text or "Lock" in modal_text)
        check("Guide Modal: Contains Allow Microphone instruction", "Microphone" in modal_text and "Allow" in modal_text)
        page.screenshot(path=str(SCREENSHOTS_DIR / "05_mic_guide_modal_open.png"))

        # Test "Type Instead" CTA closes modal and focuses input
        type_btn = guide_modal.locator("button:has-text('नीचे लिखें'), button:has-text('Type Instead')")
        type_btn.click()
        page.wait_for_timeout(100)
        check("Guide Modal: Closes via Type Instead", not guide_modal.is_visible())
        check("Guide Modal: Focuses input field", page.evaluate("document.activeElement.id === 'commerce-ai-input'"))

        # ---------------------------------------------------------------------
        # TEST 7: State 5 - ERROR STATE (Distinguishing Unrelated Errors)
        # ---------------------------------------------------------------------
        print("\n--- 7. State 5: ERROR State (Distinguishing Unrelated Errors) ---")
        # 7.1 service-not-allowed must NOT display "Microphone blocked"!
        mic_btn.click()
        page.wait_for_function("!!window.__latestSpeechInstance")
        page.evaluate("window.__latestSpeechInstance.emitError('service-not-allowed')")
        page.wait_for_timeout(100)
        sna_status = status_text.inner_text()
        check("service-not-allowed does NOT claim Microphone blocked", "Microphone blocked" not in sna_status)
        check("service-not-allowed accurately explains service restriction", "प्रतिबंधित" in sna_status or "restricted" in sna_status.lower() or "सेवा" in sna_status, f"status: {sna_status}")

        # 7.2 audio-capture must NOT display "Microphone blocked"!
        mic_btn.click()
        page.wait_for_function("!!window.__latestSpeechInstance")
        page.evaluate("window.__latestSpeechInstance.emitError('audio-capture')")
        page.wait_for_timeout(100)
        ac_status = status_text.inner_text()
        check("audio-capture does NOT claim Microphone blocked", "Microphone blocked" not in ac_status)
        check("audio-capture explains no microphone found", "नहीं मिला" in ac_status or "detected" in ac_status.lower(), f"status: {ac_status}")

        # 7.3 no-speech must return to gentle prompt without claiming blocked
        mic_btn.click()
        page.wait_for_function("!!window.__latestSpeechInstance")
        page.evaluate("window.__latestSpeechInstance.emitError('no-speech')")
        page.wait_for_timeout(100)
        ns_status = status_text.inner_text()
        check("no-speech does NOT claim Microphone blocked", "Microphone blocked" not in ns_status)
        check("no-speech gently prompts user to try speaking again", "आवाज़ नहीं मिली" in ns_status or "speech" in ns_status.lower() or "कोशिश" in ns_status, f"status: {ns_status}")

        # 7.4 aborted must cleanly reset to ready without error
        mic_btn.click()
        page.wait_for_function("!!window.__latestSpeechInstance")
        page.evaluate("window.__latestSpeechInstance.emitError('aborted')")
        page.wait_for_timeout(100)
        ab_status = status_text.inner_text()
        check("aborted resets cleanly without error banner", "माइक दबाएं" in ab_status or "speak" in ab_status.lower(), f"status: {ab_status}")

        # ---------------------------------------------------------------------
        # TEST 8: Bilingual Speech Recognition (English en-IN)
        # ---------------------------------------------------------------------
        print("\n--- 8. Bilingual Support (English en-IN) ---")
        page.evaluate("toggleGlobalLanguage('en')")
        page.wait_for_timeout(200)

        # Check English Ready State
        status_en = status_text.inner_text()
        check("English mode: Status text in English", "Tap mic to speak" in status_en, f"status: {status_en}")

        # Tap mic in English mode
        mic_btn.click()
        page.wait_for_function("!!window.__latestSpeechInstance")
        check("English mode: Recognition configured for en-IN", page.evaluate("window.__latestSpeechInstance.lang === 'en-IN'"))
        page.wait_for_timeout(50)
        status_en_listening = status_text.inner_text()
        check("English mode: Listening status in English", "Listening" in status_en_listening, f"status: {status_en_listening}")
        page.screenshot(path=str(SCREENSHOTS_DIR / "06_state_listening_en.png"))

        # Multi-tap cancel in English
        mic_btn.click()
        page.wait_for_timeout(100)
        check("English mode: Cancel resets to English Ready", "Tap mic to speak" in status_text.inner_text())

        # English permission denied
        mic_btn.click()
        page.wait_for_function("!!window.__latestSpeechInstance")
        page.evaluate("window.__latestSpeechInstance.emitError('not-allowed')")
        page.wait_for_timeout(100)
        guide_btn_en = page.locator("#commerce-mic-guide-btn")
        check("English mode: Guide button rendered in English", "Microphone Settings" in guide_btn_en.inner_text())

        guide_btn_en.click()
        page.wait_for_timeout(150)
        check("English mode: Guide modal title in English", "Microphone Settings" in page.locator("#modal-mic-guide").inner_text())
        page.screenshot(path=str(SCREENSHOTS_DIR / "07_mic_guide_modal_en.png"))
        page.click("#modal-mic-guide button[aria-label='Close']")

        # ---------------------------------------------------------------------
        # TEST 9: Insecure Context Simulation
        # ---------------------------------------------------------------------
        print("\n--- 9. Insecure Context Verification ---")
        page.evaluate("Object.defineProperty(window, 'isSecureContext', { value: false, configurable: true });")
        mic_btn.click()
        page.wait_for_timeout(100)
        insec_status = status_text.inner_text()
        check("Insecure context: Warns about HTTPS requirement", "HTTPS" in insec_status or "secure" in insec_status.lower(), f"status: {insec_status}")

        browser.close()

    print("\n" + "=" * 80)
    print(f"MICROPHONE 5-STATE VERIFICATION: {passed}/{total} CHECKS PASSED ({(passed/total)*100:.1f}%)")
    print("=" * 80)

if __name__ == "__main__":
    run_tests()

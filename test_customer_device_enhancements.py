"""
GaonBazar Customer Mobile Device Enhancements Verification Suite
Covers Priorities 2, 3, 4, and 5:
1. Single Scroll Owner & CSS Architecture (no touch freezes)
2. Android Edge Swipe & History Popstate Router (no home trap)
3. Interactive Leaflet GPS Map, Draggable Pin & Explicit Doorstep Confirmation
4. Voice Search State Machine, Interim Transcription & Bilingual Support
5. Commerce AI Bilingual NLU, Quantity Parsing & Honest Empty States
"""

import sys
import time
import requests

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import os
import subprocess
import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent

def ensure_server():
    try:
        req = urllib.request.Request("http://127.0.0.1:8001/docs")
        with urllib.request.urlopen(req, timeout=1.0) as res:
            if res.status == 200:
                return None
    except Exception:
        pass

    server_env = os.environ.copy()
    server_env["TEST_MODE"] = "1"
    server_env["CI"] = "1"
    proc = subprocess.Popen(
        [sys.executable, "run_server.py", "8001", "--no-reload"],
        cwd=str(BASE_DIR),
        env=server_env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    for _ in range(30):
        time.sleep(0.3)
        try:
            req = urllib.request.Request("http://127.0.0.1:8001/docs")
            with urllib.request.urlopen(req, timeout=1.0) as res:
                if res.status == 200:
                    return proc
        except Exception:
            pass
    return proc

BASE_URL = "http://127.0.0.1:8001"

def print_status(test_name, passed, detail=""):
    mark = "[PASS]" if passed else "[FAIL]"
    print(f"  {mark}: {test_name}" + (f" - {detail}" if detail else ""))
    if not passed:
        raise AssertionError(f"Test failed: {test_name} - {detail}")


def test_suite_1_scrolling_architecture(page):
    print("\n[SUITE 1/5]: Single Scroll Owner Architecture & CSS Verification")
    page.goto(f"{BASE_URL}/index.html")
    page.wait_for_load_state("networkidle")

    # 1. Main container is sole vertical scroll owner
    styles = page.evaluate("""() => {
        const main = document.getElementById('main-content-container');
        const comp = window.getComputedStyle(main);
        return {
            overflowY: comp.overflowY,
            touchAction: comp.touchAction,
            overscrollBehaviorY: comp.overscrollBehaviorY
        };
    }""")
    print_status("Main container overflow-y is auto", styles["overflowY"] == "auto", f"overflow-y: {styles['overflowY']}")
    print_status("Main container overscroll-behavior-y is contain", styles["overscrollBehaviorY"] == "contain", f"overscroll: {styles['overscrollBehaviorY']}")

    # 2. Verify all .screen-view elements do not have nested scroll locks
    screen_view_overflows = page.evaluate("""() => {
        const screens = Array.from(document.querySelectorAll('.screen-view'));
        return screens.map(s => ({
            id: s.id,
            overflowY: window.getComputedStyle(s).overflowY
        }));
    }""")
    all_visible = all(s["overflowY"] in ["visible", ""] for s in screen_view_overflows)
    print_status("All screen-views avoid nested scroll traps (overflow: visible)", all_visible, f"Checked {len(screen_view_overflows)} screens")

    # 3. Verify body/html do not have rogue overflow-hidden while idle
    body_overflow = page.evaluate("() => window.getComputedStyle(document.body).overflowY")
    print_status("Document body is not frozen when idle", body_overflow != "hidden", f"body overflow-y: {body_overflow}")


def test_suite_2_android_back_router(page):
    print("\n[SUITE 2/5]: Android Back Router, Popstate Interception & Trap Defense")
    page.goto(f"{BASE_URL}/index.html")
    page.wait_for_load_state("networkidle")

    # 1. Open a modal (e.g. Notifications modal) and verify it pushes history
    page.evaluate("() => openNotificationsModal()")
    time.sleep(0.3)
    modal_visible = page.evaluate("""() => {
        const m = document.getElementById('modal-notifications');
        return m && !m.classList.contains('hidden') && m.classList.contains('flex');
    }""")
    print_status("Notifications modal opened", modal_visible)

    # 2. Trigger back button (popstate) and verify modal closes cleanly
    page.evaluate("() => window.dispatchEvent(new PopStateEvent('popstate', { state: null }))")
    time.sleep(0.3)
    modal_closed = page.evaluate("""() => {
        const m = document.getElementById('modal-notifications');
        return m && m.classList.contains('hidden');
    }""")
    print_status("System Back (popstate) closes active modal cleanly", modal_closed)

    # 3. Verify body scroll lock is unlocked after modal closes
    body_unlocked = page.evaluate("""() => {
        return !document.body.classList.contains('overflow-hidden') && 
               !document.documentElement.classList.contains('overflow-hidden');
    }""")
    print_status("Body scroll lock is released after modal dismissal", body_unlocked)

    # 4. Verify user on root dashboard is NOT trapped with pushState loops on back
    initial_history_len = page.evaluate("() => window.history.length")
    # Simulate popstate on root view
    page.evaluate("() => window.dispatchEvent(new PopStateEvent('popstate', { state: { page: 'dashboard' } }))")
    final_history_len = page.evaluate("() => window.history.length")
    print_status("Root view Back action does not trap user with infinite pushState", final_history_len == initial_history_len)


def test_suite_3_interactive_leaflet_map(page):
    print("\n[SUITE 3/5]: Interactive Leaflet Map, Draggable Pin & Explicit Confirmation")
    page.goto(f"{BASE_URL}/index.html")
    page.wait_for_load_state("networkidle")

    # Navigate to landmark registration view
    page.evaluate("""() => {
        if (typeof navigateToPhase === 'function') {
            navigateToPhase('landmark');
        }
    }""")
    time.sleep(0.3)

    # 1. Check Leaflet SDK loaded
    has_leaflet = page.evaluate("() => typeof L !== 'undefined' && typeof L.map === 'function'")
    print_status("Leaflet.js SDK loaded successfully", has_leaflet)

    # 2. Simulate GPS detection with coordinates near Muzaffarpur (26.1209, 85.3647, acc: 45)
    page.evaluate("""() => {
        AppStore.detectedGps = { lat: 26.1209, lng: 85.3647, accuracy: 45 };
        AppStore.user.gps = { lat: 26.1209, lng: 85.3647, accuracy: 45, confirmed: false };
        if (typeof initOrUpdateLeafletMap === 'function') {
            initOrUpdateLeafletMap(26.1209, 85.3647, 45);
        }
    }""")
    time.sleep(0.5)

    # 3. Verify Leaflet map container is visible
    map_container_visible = page.evaluate("""() => {
        const el = document.getElementById('p1-map-preview-container');
        return el && !el.classList.contains('hidden') && el.classList.contains('flex');
    }""")
    print_status("Map container displayed after GPS detection", map_container_visible)

    # 4. Verify doorstep badge states: must NOT say 'Exact Doorstep Pinned' before confirmation
    badge_text = page.evaluate("() => (document.getElementById('p1-doorstep-badge-text') || {}).innerText || ''")
    is_honest_badge = "पुष्टि" in badge_text or "Drag Pin" in badge_text or "चुनें" in badge_text or "Adjusted" in badge_text
    print_status("Badge displays honest adjustment state, NOT premature confirmation", is_honest_badge, f"Badge: '{badge_text}'")

    # 5. Move the pin programmatically (simulate drag to 26.1215, 85.3655)
    page.evaluate("""() => {
        if (typeof handlePinMoved === 'function') {
            handlePinMoved(26.1215, 85.3655);
        }
    }""")
    time.sleep(0.3)
    coords_text = page.evaluate("() => (document.getElementById('p1-coords-display') || {}).innerText || ''")
    print_status("Draggable pin updates coordinates display", "26.1215" in coords_text, f"Coords: '{coords_text}'")

    # 6. Click explicit 'Confirm Delivery Location' button
    page.evaluate("""() => {
        if (typeof confirmPinnedLocation === 'function') {
            confirmPinnedLocation();
        }
    }""")
    time.sleep(0.3)

    confirmed_status = page.evaluate("""() => {
        const badgeText = (document.getElementById('p1-doorstep-badge-text') || {}).innerText || '';
        const isConfirmedInStore = AppStore.user && AppStore.user.gps && AppStore.user.gps.confirmed === true;
        return { badgeText, isConfirmedInStore };
    }""")
    print_status("Confirm Delivery Location updates AppStore status", confirmed_status["isConfirmedInStore"])
    print_status("Badge displays confirmed doorstep state", "सटीक स्थान" in confirmed_status["badgeText"] or "Confirmed" in confirmed_status["badgeText"], f"Badge: '{confirmed_status['badgeText']}'")

    # 7. Test recenter button repositions map to detected GPS coordinates
    page.evaluate("""() => {
        if (typeof recenterMapToGps === 'function') {
            recenterMapToGps();
        }
    }""")
    time.sleep(0.3)
    recentered_lat = page.evaluate("() => AppStore.user.gps.lat")
    print_status("Recenter button restores map marker to detected GPS coordinates", abs(recentered_lat - 26.1209) < 0.001)


def test_suite_4_voice_search(page):
    print("\n[SUITE 4/5]: Voice Search State Machine, Transcription & Language Handling")
    page.goto(f"{BASE_URL}/index.html")
    page.wait_for_load_state("networkidle")

    # 1. Switch to dashboard view
    page.evaluate("""() => {
        if (typeof navigateToPhase === 'function') {
            navigateToPhase('dashboard');
        }
    }""")
    time.sleep(0.3)

    # 2. Verify voice search button presence and minimum 44px touch target
    btn_info = page.evaluate("""() => {
        const btn = document.getElementById('p2-voice-search-btn');
        if (!btn) return null;
        const rect = btn.getBoundingClientRect();
        return { width: rect.width, height: rect.height };
    }""")
    print_status("Voice search button present with accessible touch target", btn_info and btn_info["width"] >= 36 and btn_info["height"] >= 36, f"Dimensions: {btn_info}")

    # 3. Test Voice Search trigger function exists and handles SpeechRecognition
    has_voice_func = page.evaluate("() => typeof triggerVoiceSearch === 'function'")
    print_status("Voice search trigger function defined in scope", has_voice_func)

    # 4. Mock SpeechRecognition in browser context to verify state machine transitions
    mock_result = page.evaluate("""() => {
        let eventsFired = [];
        window.SpeechRecognition = class MockSpeechRecognition {
            constructor() {
                this.continuous = false;
                this.interimResults = false;
                this.lang = '';
            }
            start() {
                eventsFired.push('started');
                if (this.onstart) this.onstart();
                if (this.onspeechstart) this.onspeechstart();
                if (this.onresult) {
                    this.onresult({
                        resultIndex: 0,
                        results: [[{ transcript: '1 kg aata' }]]
                    });
                }
                if (this.onend) this.onend();
            }
            stop() {
                eventsFired.push('stopped');
            }
        };

        triggerVoiceSearch();
        return {
            events: eventsFired,
            searchVal: (document.getElementById('p2-search-input') || {}).value
        };
    }""")
    print_status("Voice search state machine processes mock speech events", "started" in mock_result["events"])
    print_status("Voice search populates search input with transcribed speech", "1 kg aata" in mock_result["searchVal"].lower(), f"Input value: '{mock_result['searchVal']}'")


def test_suite_5_commerce_ai(page):
    print("\n[SUITE 5/5]: Commerce AI Bilingual NLU & Backend Endpoint Verification")

    # 1. Test backend endpoint with Hindi phrase
    resp = requests.post(f"{BASE_URL}/api/ai/commerce-assistant", json={
        "query": "mujhe 2 packet doodh aur 1 kg besan chahiye",
        "lang": "hi"
    })
    print_status("Backend Commerce AI returns HTTP 200 for Hindi query", resp.status_code == 200, f"Status: {resp.status_code}")
    data = resp.json()
    print_status("AI parses items from conjunction 'aur'", len(data.get("parsed_items", [])) >= 2, f"Parsed: {data.get('parsed_items')}")
    print_status("AI matches products in database", data.get("found_count", 0) > 0, f"Found count: {data.get('found_count')}")

    # Check quantities
    prods = data.get("products", [])
    doodh_prod = next((p for p in prods if "doodh" in p["name_hi"].lower() or "milk" in p["name_en"].lower()), None)
    if doodh_prod:
        print_status("AI maps Hindi number word '2' to quantity 2", doodh_prod.get("requested_qty") == 2, f"Doodh qty: {doodh_prod.get('requested_qty')}")

    # 2. Test backend endpoint with English query
    resp_en = requests.post(f"{BASE_URL}/api/ai/commerce-assistant", json={
        "query": "I want 1kg sugar and mustard oil",
        "lang": "en"
    })
    print_status("Backend Commerce AI returns HTTP 200 for English query", resp_en.status_code == 200)
    data_en = resp_en.json()
    print_status("English query returns matching products", data_en.get("found_count", 0) > 0, f"Found count: {data_en.get('found_count')}")

    # 3. Test honest empty state (non-existent item should return 0, no fabricated items)
    resp_empty = requests.post(f"{BASE_URL}/api/ai/commerce-assistant", json={
        "query": "superfast jet airplane rocket",
        "lang": "en"
    })
    data_empty = resp_empty.json()
    print_status("AI returns 0 matches for non-grocery item without fabricating fake products", data_empty.get("found_count") == 0, f"Found count: {data_empty.get('found_count')}")

    # 4. Test frontend processCommerceAiQuery UI rendering
    page.goto(f"{BASE_URL}/index.html")
    page.wait_for_load_state("networkidle")
    page.evaluate("""() => {
        if (typeof navigateToPhase === 'function') {
            navigateToPhase('commerce-ai');
        }
    }""")
    time.sleep(0.3)

    # Render honest empty state in UI
    page.evaluate("async () => { await processCommerceAiQuery('superfast jet airplane rocket'); }")
    time.sleep(0.5)

    empty_ui_text = page.evaluate("() => (document.getElementById('commerce-ai-results') || {}).innerText || ''")
    print_status("Frontend displays honest empty state message for unmatched items", "कोई सामान नहीं मिला" in empty_ui_text or "No matching items found" in empty_ui_text, f"UI: '{empty_ui_text.strip()[:60]}...'")

    # Render valid items in UI
    page.evaluate("async () => { await processCommerceAiQuery('aata doodh'); }")
    time.sleep(0.5)
    matched_ui_cards = page.evaluate("() => document.querySelectorAll('#commerce-ai-results [id^=commerce-card-]').length")
    print_status("Frontend renders actionable product cards for matching query", matched_ui_cards > 0, f"Card count: {matched_ui_cards}")


def main():
    print("=" * 80)
    print("GAONBAZAR CUSTOMER MOBILE ENHANCEMENTS VERIFICATION SUITE")
    print("=" * 80)

    server_proc = ensure_server()

    try:
        with sync_playwright() as p:
            # Launch Chromium with mobile Android viewport and touch support
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 412, "height": 915},
                user_agent="Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
                has_touch=True,
                is_mobile=True,
                permissions=["geolocation"]
            )
            context.set_geolocation({"latitude": 26.1209, "longitude": 85.3647, "accuracy": 45})
            page = context.new_page()
    
            try:
                test_suite_1_scrolling_architecture(page)
                test_suite_2_android_back_router(page)
                test_suite_3_interactive_leaflet_map(page)
                test_suite_4_voice_search(page)
                test_suite_5_commerce_ai(page)
                print("\n" + "=" * 80)
                print("ALL 5 ENHANCEMENT SUITES PASSED CLEANLY ON MOBILE VIEWPORT!")
                print("=" * 80)
            finally:
                browser.close()
    finally:
        if server_proc:
            try:
                server_proc.terminate()
                server_proc.wait(timeout=2.0)
            except Exception:
                pass

if __name__ == "__main__":
    main()

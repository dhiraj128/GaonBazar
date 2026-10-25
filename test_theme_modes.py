"""
GaonBazar Theme Modes Verification Suite (Light / Dark / System)
Covers all 3 PWAs:
1. Customer App (index.html)
2. Vendor Dashboard (vendor_dashboard.html)
3. Runner / Gaon Mitra Dashboard (runner_dashboard.html)
"""

import sys
import time
import os
import subprocess
import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
SERVER_PORT = "8001"
BASE_URL = f"http://127.0.0.1:{SERVER_PORT}"

def ensure_server():
    try:
        req = urllib.request.Request(f"{BASE_URL}/docs")
        with urllib.request.urlopen(req, timeout=1.0) as res:
            if res.status == 200:
                return None
    except Exception:
        pass

    server_env = os.environ.copy()
    server_env["TEST_MODE"] = "1"
    server_env["CI"] = "1"
    proc = subprocess.Popen(
        [sys.executable, "run_server.py", SERVER_PORT, "--no-reload"],
        cwd=str(BASE_DIR),
        env=server_env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    for _ in range(30):
        time.sleep(0.3)
        try:
            req = urllib.request.Request(f"{BASE_URL}/docs")
            with urllib.request.urlopen(req, timeout=1.0) as res:
                if res.status == 200:
                    return proc
        except Exception:
            pass
    return proc


def test_customer_theme(page):
    print("\n--- TEST: Customer App Theme Engine ---")
    page.goto(f"{BASE_URL}/?theme_test=1")
    page.wait_for_selector("#app-root", timeout=10000)

    # Navigate to Profile / Settings
    page.evaluate("() => { if (window.navigateToPhase) window.navigateToPhase('profile'); }")
    page.wait_for_selector("#view-profile", timeout=5000)

    # 1. Verify Theme UI controls exist
    assert page.is_visible("#profile-row-theme"), "Theme row should be visible in settings"
    assert page.is_visible("#btn-theme-light"), "Light mode button should exist"
    assert page.is_visible("#btn-theme-dark"), "Dark mode button should exist"
    assert page.is_visible("#btn-theme-system"), "System mode button should exist"
    assert page.is_visible("#profile-current-theme-badge"), "Theme status badge should exist"
    print("  [PASS] Customer theme controls located in Settings")

    # 2. Test Dark Mode
    page.click("#btn-theme-dark")
    time.sleep(0.2)
    is_dark = page.evaluate("() => document.documentElement.classList.contains('dark')")
    is_light = page.evaluate("() => document.documentElement.classList.contains('light')")
    stored_theme = page.evaluate("() => localStorage.getItem('gaonbazar_theme')")
    assert is_dark is True, "Dark class should be on html"
    assert is_light is False, "Light class should not be on html"
    assert stored_theme == "dark", f"Expected dark in localStorage, got {stored_theme}"
    print("  [PASS] Dark mode activates immediately with .dark class and localStorage")

    # 3. Test Light Mode
    page.click("#btn-theme-light")
    time.sleep(0.2)
    is_dark = page.evaluate("() => document.documentElement.classList.contains('dark')")
    is_light = page.evaluate("() => document.documentElement.classList.contains('light')")
    stored_theme = page.evaluate("() => localStorage.getItem('gaonbazar_theme')")
    assert is_dark is False, "Dark class should not be on html"
    assert is_light is True, "Light class should be on html"
    assert stored_theme == "light", f"Expected light in localStorage, got {stored_theme}"
    print("  [PASS] Light mode activates immediately with .light class and localStorage")

    # 4. Test System Mode & Media Query Reactivity
    page.click("#btn-theme-system")
    time.sleep(0.2)
    assert page.evaluate("() => localStorage.getItem('gaonbazar_theme')") == "system"
    
    # Emulate Dark scheme
    page.emulate_media(color_scheme="dark")
    time.sleep(0.3)
    sys_dark = page.evaluate("() => document.documentElement.classList.contains('dark')")
    assert sys_dark is True, "System mode should follow dark color scheme"
    print("  [PASS] System mode dynamically follows dark color scheme")

    # Emulate Light scheme
    page.emulate_media(color_scheme="light")
    time.sleep(0.3)
    sys_light = page.evaluate("() => document.documentElement.classList.contains('light')")
    assert sys_light is True, "System mode should follow light color scheme"
    print("  [PASS] System mode dynamically follows light color scheme")

    # 5. Test Persistence on Reload
    page.click("#btn-theme-dark")
    page.reload()
    page.wait_for_selector("#app-root", timeout=10000)
    reloaded_dark = page.evaluate("() => document.documentElement.classList.contains('dark')")
    assert reloaded_dark is True, "Dark theme should persist on page reload without FOUC"
    print("  [PASS] Customer theme persists across page reload")

    # 6. Test Bilingual labels
    page.evaluate("() => { if (window.toggleGlobalLanguage) window.toggleGlobalLanguage('en'); }")
    time.sleep(0.2)
    light_text_en = page.inner_text("#btn-theme-light")
    assert "Light" in light_text_en, f"Expected Light in button, got {light_text_en}"
    page.evaluate("() => { if (window.toggleGlobalLanguage) window.toggleGlobalLanguage('hi'); }")
    time.sleep(0.2)
    light_text_hi = page.inner_text("#btn-theme-light")
    assert "हल्का" in light_text_hi, f"Expected हल्का in button, got {light_text_hi}"
    print("  [PASS] Customer theme labels support English and Hindi")


def test_vendor_theme(page):
    print("\n--- TEST: Vendor Dashboard Theme Engine ---")
    page.goto(f"{BASE_URL}/vendor")
    page.wait_for_selector("body", timeout=10000)

    # Bypass gate if visible
    page.evaluate("""() => {
        localStorage.setItem('gaonbazar_vendor_token', 'mock_vendor_token_123');
        localStorage.setItem('gaonbazar_vendor_store_id', 'sharma_brothers');
        const gate = document.getElementById('vendor-login-gate');
        if (gate) gate.classList.add('hidden');
        if (window.switchMainTab) window.switchMainTab('settings');
    }""")
    time.sleep(0.5)

    # 1. Verify Theme UI controls exist
    assert page.is_visible("#vendor-theme-settings-card"), "Vendor theme card should exist in settings"
    assert page.is_visible("#btn-vendor-theme-light"), "Light button should exist"
    assert page.is_visible("#btn-vendor-theme-dark"), "Dark button should exist"
    assert page.is_visible("#btn-vendor-theme-system"), "System button should exist"
    print("  [PASS] Vendor theme controls located in Settings tab")

    # 2. Test Dark Mode
    page.click("#btn-vendor-theme-dark")
    time.sleep(0.2)
    is_dark = page.evaluate("() => document.documentElement.classList.contains('dark')")
    stored = page.evaluate("() => localStorage.getItem('gaonbazar_vendor_theme')")
    assert is_dark is True, "Vendor dark mode should apply .dark class"
    assert stored == "dark", f"Expected dark stored, got {stored}"
    print("  [PASS] Vendor dark mode activates immediately with .dark class")

    # 3. Test Light Mode
    page.click("#btn-vendor-theme-light")
    time.sleep(0.2)
    is_light = page.evaluate("() => document.documentElement.classList.contains('light')")
    is_dark = page.evaluate("() => document.documentElement.classList.contains('dark')")
    stored = page.evaluate("() => localStorage.getItem('gaonbazar_vendor_theme')")
    assert is_light is True and is_dark is False, "Vendor light mode should remove .dark"
    assert stored == "light", f"Expected light stored, got {stored}"
    print("  [PASS] Vendor light mode activates immediately")

    # 4. Test System Mode & Media Query Reactivity
    page.click("#btn-vendor-theme-system")
    time.sleep(0.2)
    page.emulate_media(color_scheme="dark")
    time.sleep(0.3)
    assert page.evaluate("() => document.documentElement.classList.contains('dark')") is True
    page.emulate_media(color_scheme="light")
    time.sleep(0.3)
    assert page.evaluate("() => document.documentElement.classList.contains('light')") is True
    print("  [PASS] Vendor system mode follows device color scheme")

    # 5. Test Persistence on Reload
    page.click("#btn-vendor-theme-dark")
    page.reload()
    time.sleep(0.5)
    assert page.evaluate("() => document.documentElement.classList.contains('dark')") is True
    print("  [PASS] Vendor theme persists across page reload")


def test_runner_theme(page):
    print("\n--- TEST: Runner / Gaon Mitra Dashboard Genuine Light & Dark Modes ---")
    page.goto(f"{BASE_URL}/runner")
    page.wait_for_selector("body", timeout=10000)

    # Authenticate Runner cleanly via Login Gate button
    if page.is_visible("#runner-login-gate"):
        page.click("#btn-runner-login")
        page.wait_for_selector("#runner-main-content:not(.hidden)", timeout=10000)
        time.sleep(0.5)

    # Click Settings tab in bottom nav
    page.click("#nav-btn-settings")
    page.wait_for_selector("#runner-theme-settings-card", timeout=5000)

    # 1. Verify Theme UI controls exist
    assert page.is_visible("#runner-theme-settings-card"), "Runner theme card should exist in settings"
    assert page.is_visible("#btn-runner-theme-light"), "Light button should exist"
    assert page.is_visible("#btn-runner-theme-dark"), "Dark button should exist"
    assert page.is_visible("#btn-runner-theme-system"), "System button should exist"
    print("  [PASS] Runner theme controls located in Settings tab")

    # 2. Test Genuine Light Mode (Crucial requirement: Runner must support a genuine Light Mode, not just dark)
    page.click("#btn-runner-theme-light")
    time.sleep(0.3)
    is_light = page.evaluate("() => document.documentElement.classList.contains('light')")
    is_dark = page.evaluate("() => document.documentElement.classList.contains('dark')")
    stored = page.evaluate("() => localStorage.getItem('gaonbazar_runner_theme')")
    assert is_light is True, "Runner must have .light class in Light Mode"
    assert is_dark is False, "Runner must not have .dark class in Light Mode"
    assert stored == "light", f"Expected light stored, got {stored}"

    # Verify Computed Styles in Genuine Light Mode
    body_bg = page.evaluate("() => window.getComputedStyle(document.body).backgroundColor")
    body_color = page.evaluate("() => window.getComputedStyle(document.body).color")
    card_bg = page.evaluate("() => { const c = document.getElementById('runner-theme-settings-card'); return c ? window.getComputedStyle(c).backgroundColor : ''; }")
    print(f"  [EVIDENCE] Runner Light Mode Computed Styles: body bg={body_bg}, body text={body_color}, card bg={card_bg}")
    
    # Check that background is indeed a light color (rgb 248, 250, 252) and text is dark
    assert "248, 250, 252" in body_bg or "255, 255, 255" in body_bg or "241, 245, 249" in body_bg, f"Expected light body background, got {body_bg}"
    assert "15, 23, 42" in body_color or "0, 0, 0" in body_color or "30, 41, 59" in body_color, f"Expected dark text color, got {body_color}"
    assert "255, 255, 255" in card_bg, f"Expected white card background in light mode, got {card_bg}"
    print("  [PASS] Genuine Runner Light Mode verified with clean white cards and dark text!")

    # 3. Test Dark Mode
    page.click("#btn-runner-theme-dark")
    time.sleep(0.3)
    is_dark = page.evaluate("() => document.documentElement.classList.contains('dark')")
    stored = page.evaluate("() => localStorage.getItem('gaonbazar_runner_theme')")
    assert is_dark is True, "Runner must have .dark class in Dark Mode"
    assert stored == "dark"
    dark_body_bg = page.evaluate("() => window.getComputedStyle(document.body).backgroundColor")
    print(f"  [EVIDENCE] Runner Dark Mode Computed Styles: body bg={dark_body_bg}")
    assert "15, 23, 42" in dark_body_bg or "2, 6, 23" in dark_body_bg or "11, 17, 32" in dark_body_bg, f"Expected dark background, got {dark_body_bg}"
    print("  [PASS] Runner Dark Mode verified with slate-900 background")

    # 4. Test System Mode & Media Query Reactivity
    page.click("#btn-runner-theme-system")
    time.sleep(0.2)
    page.emulate_media(color_scheme="dark")
    time.sleep(0.3)
    assert page.evaluate("() => document.documentElement.classList.contains('dark')") is True
    page.emulate_media(color_scheme="light")
    time.sleep(0.3)
    assert page.evaluate("() => document.documentElement.classList.contains('light')") is True
    print("  [PASS] Runner system mode dynamically follows phone theme")

    # 5. Test Persistence on Reload
    page.click("#btn-runner-theme-light")
    page.reload()
    time.sleep(0.5)
    assert page.evaluate("() => document.documentElement.classList.contains('light')") is True
    print("  [PASS] Runner Light Mode persists across page reload without FOUC")


def run_all_tests():
    server_proc = ensure_server()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 390, "height": 844})
            page = context.new_page()

            test_customer_theme(page)
            test_vendor_theme(page)
            test_runner_theme(page)

            browser.close()
            print("\n==================================================")
            print(" ALL THEME MODES VERIFICATION CHECKS PASSED (100%)")
            print("==================================================")
    finally:
        if server_proc:
            try:
                server_proc.terminate()
            except Exception:
                pass

if __name__ == "__main__":
    run_all_tests()

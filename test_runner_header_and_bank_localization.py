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
    print("TEST: RUNNER DASHBOARD HEADER & SAVED BANK CARD LOCALIZATION")
    print("=" * 80)

    # Start server with BYPASS_GEOFENCE=True
    os.environ["BYPASS_GEOFENCE"] = "True"
    server = subprocess.Popen([sys.executable, "run_server.py", "8001", "--no-reload"])
    time.sleep(3)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 360, "height": 800})
            base_url = "http://127.0.0.1:8001/runner"
            print(f"Loading Runner Dashboard at {base_url}...")
            page.goto(base_url, wait_until="networkidle")
            page.wait_for_timeout(600)

            # Ensure runner is logged in and UI is displayed
            page.evaluate("""() => {
                sessionStorage.setItem('runner_token', 'mock_token');
                sessionStorage.setItem('runner_id', 'gm_1');
                RunnerStore.token = 'mock_token';
                RunnerStore.runnerId = 'gm_1';
                document.getElementById('runner-auth-gate')?.classList.add('hidden');
                document.getElementById('runner-header')?.classList.remove('hidden');
                document.getElementById('runner-bottom-nav')?.classList.remove('hidden');
                document.getElementById('runner-main-content')?.classList.remove('hidden');
                document.getElementById('runner-pending-view')?.classList.add('hidden');
            }""")

            # -------------------------------------------------------------
            # TEST 1: HINDI MODE (Default or explicit toggle)
            # -------------------------------------------------------------
            print("\n[TEST 1]: Verifying Elements in HINDI Mode...")
            page.evaluate("RunnerStore.lang = 'hi'; applyRunnerLanguageUI();")
            page.wait_for_timeout(300)

            runner_name_hi = page.inner_text("#runner-name-display").strip()
            hub_text_hi = page.inner_text("#runner-hub-name-text").strip()
            hub_display_hi = page.inner_text("#runner-hub-display").strip()

            print(f"  Runner Name (HI): '{runner_name_hi}'")
            print(f"  Hub Text (HI): '{hub_text_hi}'")
            print(f"  Hub Display Container (HI): '{hub_display_hi}'")

            assert runner_name_hi == "कमल सिंह", f"Expected 'कमल सिंह', got '{runner_name_hi}'"
            assert "रामपुर क्लस्टर हब" in hub_text_hi, f"Expected 'रामपुर क्लस्टर हब' in '{hub_text_hi}'"
            print("  ✓ PASS: Hindi Header Profile & Hub Text verified!")

            # -------------------------------------------------------------
            # TEST 2: ENGLISH MODE (Header Elements)
            # -------------------------------------------------------------
            print("\n[TEST 2]: Verifying Elements in ENGLISH Mode...")
            page.evaluate("RunnerStore.lang = 'en'; applyRunnerLanguageUI();")
            page.wait_for_timeout(300)

            runner_name_en = page.inner_text("#runner-name-display").strip()
            hub_text_en = page.inner_text("#runner-hub-name-text").strip()
            hub_display_en = page.inner_text("#runner-hub-display").strip()

            print(f"  Runner Name (EN): '{runner_name_en}'")
            print(f"  Hub Text (EN): '{hub_text_en}'")
            print(f"  Hub Display Container (EN): '{hub_display_en}'")

            assert runner_name_en == "Kamal Singh", f"Expected 'Kamal Singh', got '{runner_name_en}'"
            assert hub_text_en == "Rampur Cluster Hub", f"Expected 'Rampur Cluster Hub', got '{hub_text_en}'"
            assert "Rampur Cluster Hub" in hub_display_en, f"Expected 'Rampur Cluster Hub' in '{hub_display_en}'"

            # Strict 0% Hindi check
            for text_val, label in [(runner_name_en, "Runner Name"), (hub_text_en, "Hub Text"), (hub_display_en, "Hub Display")]:
                has_hindi = any('\u0900' <= char <= '\u097f' for char in text_val)
                assert not has_hindi, f"Hindi character found in English mode for {label}: '{text_val}'"
            print("  ✓ PASS: English Header Profile & Hub Text verified with 0% Hindi!")

            # -------------------------------------------------------------
            # TEST 3: INTERACTIVE LANGUAGE TOGGLE CLICK
            # -------------------------------------------------------------
            print("\n[TEST 3]: Testing Interactive Language Toggle Click...")
            # Click toggle (EN -> HI)
            page.click("#lang-toggle-btn")
            page.wait_for_timeout(300)
            name_toggled_hi = page.inner_text("#runner-name-display").strip()
            hub_toggled_hi = page.inner_text("#runner-hub-name-text").strip()
            assert name_toggled_hi == "कमल सिंह", f"Expected 'कमल सिंह' after toggle, got '{name_toggled_hi}'"
            assert "रामपुर क्लस्टर हब" in hub_toggled_hi, f"Expected 'रामपुर क्लस्टर हब' after toggle, got '{hub_toggled_hi}'"

            # Click toggle again (HI -> EN)
            page.click("#lang-toggle-btn")
            page.wait_for_timeout(300)
            name_toggled_en = page.inner_text("#runner-name-display").strip()
            hub_toggled_en = page.inner_text("#runner-hub-name-text").strip()
            assert name_toggled_en == "Kamal Singh", f"Expected 'Kamal Singh' after toggle, got '{name_toggled_en}'"
            assert hub_toggled_en == "Rampur Cluster Hub", f"Expected 'Rampur Cluster Hub' after toggle, got '{hub_toggled_en}'"
            print("  ✓ PASS: Interactive language toggle button switches header text correctly!")

            # -------------------------------------------------------------
            # TEST 4: SAVED BANK ACCOUNT CARD LOCALIZATION
            # -------------------------------------------------------------
            print("\n[TEST 4]: Verifying Saved Bank Account Card Localization...")
            # Switch to settings tab
            page.evaluate("switchTab('settings')")
            page.wait_for_timeout(500)

            # Ensure masked info card is visible
            page.evaluate("""() => {
                const card = document.getElementById('runner-bank-masked-info');
                if (card) {
                    card.classList.remove('hidden');
                    card.style.display = 'flex';
                }
            }""")
            page.wait_for_timeout(200)

            # Test English mode on bank card
            page.evaluate("RunnerStore.lang = 'en'; applyRunnerLanguageUI();")
            page.wait_for_timeout(200)

            saved_acc_lbl_en = page.inner_text("#lbl-runner-saved-acc").strip()
            active_badge_en = page.inner_text("#runner-bank-active-badge").strip()
            masked_card_text_en = page.inner_text("#runner-bank-masked-info")

            print(f"  Saved Account Label (EN): '{saved_acc_lbl_en}'")
            print(f"  Active Badge (EN): '{active_badge_en}'")
            print(f"  Masked Card Text (EN):\n{masked_card_text_en}")

            assert saved_acc_lbl_en == "Saved Account:", f"Expected 'Saved Account:', got '{saved_acc_lbl_en}'"
            assert active_badge_en == "Active", f"Expected 'Active', got '{active_badge_en}'"

            # Strict 0% Hindi check
            for text_val, label in [(saved_acc_lbl_en, "Saved Account Label"), (active_badge_en, "Active Badge")]:
                has_hindi = any('\u0900' <= char <= '\u097f' for char in text_val)
                assert not has_hindi, f"Hindi character found in English mode for {label}: '{text_val}'"
            print("  ✓ PASS: Saved Bank Account Card in English mode verified with 0% Hindi!")

            # Test Hindi mode on bank card
            page.evaluate("RunnerStore.lang = 'hi'; applyRunnerLanguageUI();")
            page.wait_for_timeout(200)

            saved_acc_lbl_hi = page.inner_text("#lbl-runner-saved-acc").strip()
            active_badge_hi = page.inner_text("#runner-bank-active-badge").strip()

            print(f"  Saved Account Label (HI): '{saved_acc_lbl_hi}'")
            print(f"  Active Badge (HI): '{active_badge_hi}'")

            assert saved_acc_lbl_hi == "सहेजा गया खाता:", f"Expected 'सहेजा गया खाता:', got '{saved_acc_lbl_hi}'"
            assert active_badge_hi == "सक्रिय", f"Expected 'सक्रिय', got '{active_badge_hi}'"
            print("  ✓ PASS: Saved Bank Account Card in Hindi mode verified!")

            print("\n" + "=" * 80)
            print("ALL RUNNER HEADER & SAVED BANK CARD LOCALIZATION TESTS PASSED!")
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

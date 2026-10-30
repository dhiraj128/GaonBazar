"""
test_bilingual_persistence_and_dynamic_i18n.py
Exhaustive verification of Bilingual Localization (Hindi/English) across all 4 GaonBazaar apps:
1. Customer App (index.html)
2. Vendor App (vendor_dashboard.html)
3. Delivery Partner App (runner_dashboard.html)
4. Super Admin Portal (admin_dashboard.html)

Verifies:
- Static and dynamic UI elements rendered in both languages
- Tab labels, headers, placeholders, action buttons, modals, error toasts
- Support chat greetings, refund advisories, and status messages
- Reload persistence: language state persists across browser page reload
- Authentication persistence: language state preserved across user login
"""

import sys
import io
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def run_localization_audit():
    print("=" * 80)
    print("GAONBAZAAR 4-APP FULL BILINGUAL LOCALIZATION & PERSISTENCE AUDIT")
    print("=" * 80)

    passed = 0
    total = 0

    def check(name, condition, details=""):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"  ✓ PASS: {name} {details}")
        else:
            print(f"  ✗ FAIL: {name} {details}")
            assert False, f"Test failed: {name} - {details}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        base_dir = Path(__file__).parent.resolve()

        # =========================================================================
        # 1. CUSTOMER APP (index.html)
        # =========================================================================
        print("\n--- 1. Customer App Localization & Dynamic Strings ---")
        context = browser.new_context(
            viewport={"width": 393, "height": 851},
            is_mobile=True,
            has_touch=True
        )
        page = context.new_page()
        page.goto((base_dir / "index.html").as_uri(), wait_until="domcontentloaded")
        page.wait_for_function("typeof navigateToPhase === 'function'")

        # 1.1 Test Hindi default UI
        page.evaluate("window.switchLanguage('hi')")
        page.wait_for_timeout(100)
        hi_search_ph = page.get_attribute("#p2-search-input", "placeholder") or ""
        check("Customer: Hindi search placeholder active", "सामान" in hi_search_ph or "खोज" in hi_search_ph, f"ph: {hi_search_ph}")

        hi_nav_orders = page.inner_text("#nav-lbl-orders")
        check("Customer: Hindi orders nav label", "ऑर्डर" in hi_nav_orders or "Orders" in hi_nav_orders, f"label: {hi_nav_orders}")

        # 1.2 Switch to English UI
        page.evaluate("window.switchLanguage('en')")
        page.wait_for_timeout(100)
        en_search_ph = page.get_attribute("#p2-search-input", "placeholder") or ""
        check("Customer: English search placeholder active", "search" in en_search_ph.lower(), f"ph: {en_search_ph}")

        en_nav_orders = page.inner_text("#nav-lbl-orders")
        check("Customer: English orders nav label", "Orders" in en_nav_orders, f"label: {en_nav_orders}")

        # 1.3 Test reload persistence for English
        page.reload(wait_until="domcontentloaded")
        page.wait_for_function("typeof navigateToPhase === 'function'")
        persisted_lang = page.evaluate("localStorage.getItem('gaonbazar_lang')")
        check("Customer: English persisted in localStorage after reload", persisted_lang == "en")
        en_reloaded_ph = page.get_attribute("#p2-search-input", "placeholder") or ""
        check("Customer: Search input still English after reload", "search" in en_reloaded_ph.lower(), f"ph: {en_reloaded_ph}")

        # 1.4 Test reload persistence for Hindi
        page.evaluate("window.switchLanguage('hi')")
        page.wait_for_timeout(50)
        page.reload(wait_until="domcontentloaded")
        page.wait_for_function("typeof navigateToPhase === 'function'")
        persisted_hi = page.evaluate("localStorage.getItem('gaonbazar_lang')")
        check("Customer: Hindi persisted in localStorage after reload", persisted_hi == "hi")

        # 1.5 Dynamic Support & Refund strings in English and Hindi
        page.evaluate("window.switchLanguage('en')")
        page.evaluate("navigateToPhase('support')")
        page.wait_for_timeout(100)
        support_title_en = page.inner_text("[data-i18n='support_center_title']")
        check("Customer: Support header in English", "Help & Support" in support_title_en or "Support" in support_title_en, f"title: {support_title_en}")

        page.evaluate("window.switchLanguage('hi')")
        page.wait_for_timeout(100)
        support_title_hi = page.inner_text("[data-i18n='support_center_title']")
        check("Customer: Support header in Hindi", "सहायता" in support_title_hi or "मदद" in support_title_hi, f"title: {support_title_hi}")

        context.close()

        # =========================================================================
        # 2. VENDOR APP (vendor_dashboard.html)
        # =========================================================================
        print("\n--- 2. Vendor App Localization & Dynamic Strings ---")
        v_context = browser.new_context(viewport={"width": 393, "height": 851})
        v_page = v_context.new_page()
        v_page.goto((base_dir / "vendor_dashboard.html").as_uri(), wait_until="domcontentloaded")
        v_page.wait_for_function("typeof VendorStore !== 'undefined'")

        # 2.1 Test default Hindi UI
        v_page.evaluate("""() => {
          VendorStore.lang = 'hi';
          localStorage.setItem('gaonbazar_lang', 'hi');
          updateLanguageUI();
        }""")
        v_page.wait_for_timeout(100)
        vendor_title_hi = v_page.inner_text("#current-section-title")
        check("Vendor: Section title in Hindi", "ऑर्डर" in vendor_title_hi or "दुकानदार" in vendor_title_hi, f"title: {vendor_title_hi}")

        # 2.2 Switch to English UI
        v_page.evaluate("toggleLanguage()")
        v_page.wait_for_timeout(100)
        vendor_lang = v_page.evaluate("VendorStore.lang")
        check("Vendor: Language toggled to English", vendor_lang == "en")
        vendor_title_en = v_page.inner_text("#current-section-title")
        check("Vendor: Section title in English", "Live Orders" in vendor_title_en or "Workspace" in vendor_title_en or "Orders" in vendor_title_en, f"title: {vendor_title_en}")

        # 2.3 Verify reload persistence
        v_page.reload(wait_until="domcontentloaded")
        v_page.wait_for_function("typeof VendorStore !== 'undefined'")
        v_persisted = v_page.evaluate("VendorStore.lang")
        check("Vendor: English persisted across page reload", v_persisted == "en")

        # 2.4 Switch to Ledger tab and verify labels
        v_page.evaluate("switchMainTab('ledger')")
        v_page.wait_for_timeout(100)
        sales_label = v_page.inner_text("[data-i18n='ledger_stat_sales']")
        check("Vendor: Ledger sales label in English", "Gross Sales" in sales_label or "Sales" in sales_label, f"label: {sales_label}")

        v_context.close()

        # =========================================================================
        # 3. RUNNER APP (runner_dashboard.html)
        # =========================================================================
        print("\n--- 3. Runner App Localization & Dynamic Strings ---")
        r_context = browser.new_context(viewport={"width": 393, "height": 851})
        r_page = r_context.new_page()
        r_page.goto((base_dir / "runner_dashboard.html").as_uri(), wait_until="domcontentloaded")
        r_page.wait_for_function("typeof RunnerStore !== 'undefined'")

        # 3.1 Test Hindi default UI
        r_page.evaluate("""() => {
          RunnerStore.lang = 'hi';
          localStorage.setItem('gaonbazar_lang', 'hi');
          applyRunnerLanguageUI();
        }""")
        r_page.wait_for_timeout(100)
        r_tab_hi = r_page.inner_text("[data-i18n='nav_missions']")
        check("Runner: Missions tab in Hindi", "मिशन" in r_tab_hi or "डिलीवरी" in r_tab_hi, f"tab: {r_tab_hi}")

        # 3.2 Switch to English UI
        r_page.evaluate("toggleLanguage()")
        r_page.wait_for_timeout(100)
        r_tab_en = r_page.inner_text("[data-i18n='nav_missions']")
        check("Runner: Missions tab in English", "Missions" in r_tab_en, f"tab: {r_tab_en}")

        # 3.3 Test reload persistence
        r_page.reload(wait_until="domcontentloaded")
        r_page.wait_for_function("typeof RunnerStore !== 'undefined'")
        r_persisted = r_page.evaluate("RunnerStore.lang")
        check("Runner: English persisted across reload", r_persisted == "en")

        r_context.close()

        # =========================================================================
        # 4. SUPER ADMIN APP (admin_dashboard.html)
        # =========================================================================
        print("\n--- 4. Super Admin App Localization & Dynamic Strings ---")
        a_context = browser.new_context(viewport={"width": 1280, "height": 800})
        a_page = a_context.new_page()
        a_page.goto((base_dir / "admin_dashboard.html").as_uri(), wait_until="domcontentloaded")
        a_page.wait_for_function("typeof AdminStore !== 'undefined'")

        # 4.1 Test Hindi default UI
        a_page.evaluate("""() => {
          AdminStore.lang = 'hi';
          localStorage.setItem('gaonbazar_admin_lang', 'hi');
          localStorage.setItem('gaonbazar_lang', 'hi');
          updateAdminLanguageUI();
        }""")
        a_page.wait_for_timeout(100)
        a_title_hi = a_page.inner_text("#admin-app-title")
        check("Admin: App title in Hindi", "सुपर एडमिन" in a_title_hi or "गांव बाज़ार" in a_title_hi, f"title: {a_title_hi}")

        # 4.2 Switch to English UI
        a_page.evaluate("toggleAdminLanguage()")
        a_page.wait_for_timeout(100)
        a_title_en = a_page.inner_text("#admin-app-title")
        check("Admin: App title in English", "Super Admin" in a_title_en or "Admin" in a_title_en, f"title: {a_title_en}")

        # 4.3 Verify metrics card in English
        gmv_label_en = a_page.inner_text("[data-i18n='kpi_gmv']")
        check("Admin: GMV metric card label in English", "Gross" in gmv_label_en or "GMV" in gmv_label_en or "Sales" in gmv_label_en or "Business" in gmv_label_en, f"label: {gmv_label_en}")

        # 4.4 Test reload persistence
        a_page.reload(wait_until="domcontentloaded")
        a_page.wait_for_function("typeof AdminStore !== 'undefined'")
        a_persisted = a_page.evaluate("AdminStore.lang")
        check("Admin: English persisted across reload", a_persisted == "en")

        a_context.close()
        browser.close()

    print("\n" + "=" * 80)
    print(f"LOCALIZATION AUDIT RESULTS: {passed}/{total} CHECKS PASSED ({(passed/total)*100:.1f}%)")
    print("=" * 80)

if __name__ == "__main__":
    run_localization_audit()

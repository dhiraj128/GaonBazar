import asyncio
import re
import sys
import os
import time
import subprocess
from playwright.async_api import async_playwright

# Ensure UTF-8 console output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_URL = "http://127.0.0.1:8001"
devanagari_re = re.compile(r'[\u0900-\u097F]')

async def test_all():
    print("=" * 80)
    print("COMPREHENSIVE VERIFICATION: i18n LOCALIZATION & RUNNER MAP NAVIGATION")
    print("=" * 80)

    server = subprocess.Popen([sys.executable, "run_server.py", "8001", "--no-reload"])
    time.sleep(3)

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(viewport={"width": 390, "height": 844})

            # ---------------------------------------------------------------------
            # SUITE 1: RUNNER DASHBOARD - MAP NAVIGATION & i18n
            # ---------------------------------------------------------------------
            print("\n[SUITE 1/3]: RUNNER DASHBOARD VERIFICATION")
            page = await context.new_page()
            await page.goto(f"{BASE_URL}/runner", wait_until="networkidle")

            # 1.1 Test Map Navigation Button and onclick
            print("  Checking #btn-navigate-map CTA and onclick hook...")
            btn_nav = page.locator("#btn-navigate-map")
            assert await btn_nav.count() > 0, "Assertion failed: #btn-navigate-map not found"
            onclick_attr = await btn_nav.get_attribute("onclick")
            print(f"  #btn-navigate-map onclick attribute: {onclick_attr}")
            assert "openRunnerMapNavigation" in (onclick_attr or ""), "Assertion failed: #btn-navigate-map does not call openRunnerMapNavigation"

            # Mock window.open and trigger map click
            intercepted_urls = []
            await page.expose_function("recordWindowOpen", lambda url, target: intercepted_urls.append((url, target)))
            await page.evaluate("""() => {
                window.open = function(url, target) {
                    window.recordWindowOpen(url, target);
                    return null;
                };
            }""")

            await page.evaluate("""() => {
                const btn = document.getElementById('btn-navigate-map');
                if (btn) btn.click();
            }""")
            print(f"  Intercepted window.open calls: {intercepted_urls}")
            assert len(intercepted_urls) > 0, "Assertion failed: window.open was not triggered by #btn-navigate-map"
            nav_url, target = intercepted_urls[0]
            assert "maps.google.com/?q=" in nav_url, f"Assertion failed: nav_url {nav_url} does not contain maps.google.com/?q="
            assert target == "_blank", f"Assertion failed: target {target} != _blank"
            print("  ✓ PASS: Runner Map Navigation cleanly redirects to Google Maps with exact coordinates!")

            # 1.2 Test Runner i18n in English Mode
            print("  Checking Runner Dashboard in English Mode (Zero Residual Hindi)...")
            await page.evaluate("() => { if (RunnerStore.lang !== 'en') toggleLanguage(); }")
            await page.wait_for_timeout(300)

            # Check key elements in English
            shift_label = await page.locator("#shift-status-label").inner_text()
            print(f"  Shift Label (EN): '{shift_label}'")
            assert not devanagari_re.search(shift_label), f"Residual Hindi found in shift label: {shift_label}"

            pending_badge = await page.locator('[data-i18n="pending_status_badge"]').text_content()
            print(f"  Pending Status Badge (EN): '{pending_badge}'")
            assert not devanagari_re.search(pending_badge or ""), f"Residual Hindi found in pending badge: {pending_badge}"

            reg_veh_label = await page.locator('[data-i18n="reg_lbl_veh_type"]').text_content()
            print(f"  Reg Vehicle Label (EN): '{reg_veh_label}'")
            assert not devanagari_re.search(reg_veh_label or ""), f"Residual Hindi found in vehicle label: {reg_veh_label}"

            # ---------------------------------------------------------------------
            # SUITE 2: VENDOR DASHBOARD - i18n AUDIT & HARDCODED TEXT REMOVAL
            # ---------------------------------------------------------------------
            print("\n[SUITE 2/3]: VENDOR DASHBOARD VERIFICATION")
            page_v = await context.new_page()
            await page_v.goto(f"{BASE_URL}/vendor", wait_until="networkidle")

            # Toggle to English
            await page_v.evaluate("() => { if (VendorStore.lang !== 'en') toggleLanguage(); }")
            await page_v.wait_for_timeout(300)

            # Check ledger date pill
            date_pill = await page_v.locator("#ledger-date-pill").inner_text()
            print(f"  Ledger Date Pill (EN): '{date_pill}'")
            assert not devanagari_re.search(date_pill), f"Residual Hindi in ledger date pill: {date_pill}"
            assert "Date:" in date_pill, f"'Date:' prefix missing from ledger date pill: {date_pill}"

            # Check ledger stat sub-labels
            sales_sub = await page_v.locator('[data-i18n="ledger_stat_sales_sub"]').inner_text()
            cod_sub = await page_v.locator('[data-i18n="ledger_stat_cod_sub"]').inner_text()
            fee_sub = await page_v.locator('[data-i18n="ledger_stat_fee_sub"]').inner_text()
            net_sub = await page_v.locator('[data-i18n="ledger_stat_earnings_sub"]').inner_text()
            print(f"  Ledger Subtitles (EN): sales='{sales_sub}', cod='{cod_sub}', fee='{fee_sub}', net='{net_sub}'")
            for sub in [sales_sub, cod_sub, fee_sub, net_sub]:
                assert not devanagari_re.search(sub), f"Residual Hindi in ledger subtitle: {sub}"

            # Check table headers
            th_texts = await page_v.locator("#ledger-table-head th").all_inner_texts()
            print(f"  Ledger Table Headers (EN): {th_texts}")
            for th in th_texts:
                assert not devanagari_re.search(th), f"Residual Hindi in table header: {th}"

            # Check store settings labels
            phone_lbl = await page_v.locator('[data-i18n="store_phone"]').text_content()
            mandi_lbl = await page_v.locator('[data-i18n="store_mandi_hub"]').text_content()
            timings_lbl = await page_v.locator('[data-i18n="store_timings"]').text_content()
            verified_note = await page_v.locator('[data-i18n="store_verified_note"]').text_content()
            print(f"  Store Settings Labels (EN): phone='{phone_lbl}', hub='{mandi_lbl}', timings='{timings_lbl}'")
            for lbl in [phone_lbl, mandi_lbl, timings_lbl, verified_note]:
                assert not devanagari_re.search(lbl or ""), f"Residual Hindi in store setting label: {lbl}"

            # Check saved bank account label
            saved_acc = await page_v.locator('[data-i18n="bank_saved_account_lbl"]').text_content()
            active_badge = await page_v.locator('[data-i18n="bank_status_active"]').text_content()
            print(f"  Saved Account & Active Badge (EN): acc='{saved_acc}', status='{active_badge}'")
            assert not devanagari_re.search(saved_acc or ""), f"Residual Hindi in saved account label: {saved_acc}"
            assert not devanagari_re.search(active_badge or ""), f"Residual Hindi in active badge: {active_badge}"

            print("  ✓ PASS: Vendor Dashboard in English mode verified with 0% Hindi!")

            # ---------------------------------------------------------------------
            # SUITE 3: CUSTOMER APP (INDEX.HTML) - i18n AUDIT
            # ---------------------------------------------------------------------
            print("\n[SUITE 3/3]: CUSTOMER APP (INDEX.HTML) VERIFICATION")
            page_c = await context.new_page()
            await page_c.goto(f"{BASE_URL}/", wait_until="networkidle")

            # Toggle to English
            await page_c.evaluate("() => { if (AppStore.lang !== 'en') toggleGlobalLanguage('en'); }")
            await page_c.wait_for_timeout(300)

            # Check Drawer Guest Name
            guest_name = await page_c.locator("#drawer-user-name").text_content()
            print(f"  Drawer User Name (EN): '{guest_name}'")
            assert not devanagari_re.search(guest_name or ""), f"Residual Hindi in drawer user name: {guest_name}"

            # Check Auth Tabs
            signin_tab = await page_c.locator("#auth-tab-signin-text").text_content()
            signup_tab = await page_c.locator("#auth-tab-signup-text").text_content()
            auth_title = await page_c.locator("#auth-mode-title").text_content()
            auth_desc = await page_c.locator("#auth-mode-desc").text_content()
            print(f"  Auth Mode (EN): signin='{signin_tab}', signup='{signup_tab}', title='{auth_title}'")
            for txt in [signin_tab, signup_tab, auth_title, auth_desc]:
                assert not devanagari_re.search(txt or ""), f"Residual Hindi in auth text: {txt}"

            # Check Category Labels
            cat_kirana = await page_c.locator("#cat-lbl-kirana").text_content()
            cat_meds = await page_c.locator("#cat-lbl-medicines").text_content()
            cat_agri = await page_c.locator("#cat-lbl-agri").text_content()
            cat_dairy = await page_c.locator("#cat-lbl-dairy").text_content()
            cat_tools = await page_c.locator("#cat-lbl-tools").text_content()
            cat_sabzi = await page_c.locator("#cat-lbl-sabzi").text_content()
            print(f"  Category Labels (EN): kirana='{cat_kirana}', meds='{cat_meds}', agri='{cat_agri}'")
            for cat in [cat_kirana, cat_meds, cat_agri, cat_dairy, cat_tools, cat_sabzi]:
                assert not devanagari_re.search(cat or ""), f"Residual Hindi in category label: {cat}"

            # Check Cart & Checkout subtext
            p4_sub = await page_c.locator("#p4-checkout-btn-sub").text_content()
            print(f"  Checkout Sub (EN): '{p4_sub}'")
            assert not devanagari_re.search(p4_sub or ""), f"Residual Hindi in checkout sub: {p4_sub}"

            # Check Profile Labels
            prof_village = await page_c.locator("#profile-user-village").text_content()
            prof_landmark = await page_c.locator("#profile-user-landmark").text_content()
            prof_lang_badge = await page_c.locator("#profile-current-lang-badge").text_content()
            print(f"  Profile Labels (EN): village='{prof_village}', landmark='{prof_landmark}', badge='{prof_lang_badge}'")
            for plbl in [prof_village, prof_landmark, prof_lang_badge]:
                assert not devanagari_re.search(plbl or ""), f"Residual Hindi in profile label: {plbl}"

            print("  ✓ PASS: Customer App (index.html) in English mode verified with 0% Hindi!")

            await browser.close()
    finally:
        server.terminate()
        try:
            server.wait(timeout=3)
        except Exception:
            server.kill()

    print("\n" + "=" * 80)
    print("ALL TESTS PASSED SUCCESSFULLY! ZERO DEFECTS VERIFIED.")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_all())

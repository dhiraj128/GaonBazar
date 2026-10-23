"""
Comprehensive QA Automation: Localization and Dynamic Empty State Verification
Validates:
1. Live Tracking UI & Vector Route Trail Bilingual Localization (Hindi <-> English)
2. Purge of Fake Dummy Data & Clean Empty State Rendering
"""

import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

TOTAL_CHECKS = 0
PASSED_CHECKS = 0
FAILED_CHECKS = 0

def check(test_name, condition, detail=""):
    global TOTAL_CHECKS, PASSED_CHECKS, FAILED_CHECKS
    TOTAL_CHECKS += 1
    if condition:
        PASSED_CHECKS += 1
        print(f"  [PASS]: {test_name} {f'({detail})' if detail else ''}", flush=True)
    else:
        FAILED_CHECKS += 1
        print(f"  [FAIL]: {test_name} {f'({detail})' if detail else ''}", flush=True)

def run_tests():
    global TOTAL_CHECKS, PASSED_CHECKS, FAILED_CHECKS
    print("=" * 80, flush=True)
    print("GAONBAZAAR LOCALIZATION & EMPTY STATE VERIFICATION SUITE", flush=True)
    print("=" * 80, flush=True)

    base_dir = Path(__file__).resolve().parent
    customer_html = (base_dir / "index.html").as_uri()
    vendor_html = (base_dir / "vendor_dashboard.html").as_uri()
    runner_html = (base_dir / "runner_dashboard.html").as_uri()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 360, "height": 800})

        # ---------------------------------------------------------------------
        # TEST 1: Initial HTML Cleanliness & Purge of Dummy Stores / Orders
        # ---------------------------------------------------------------------
        print("\n[STEP 1]: Verifying DOM Initial State & Zero Dummy Data in index.html", flush=True)
        page.goto(customer_html, wait_until="domcontentloaded")
        page.wait_for_timeout(300)

        # Verify no hardcoded dummy order in initial order id span
        initial_order_id = page.inner_text("#p5-order-id").strip()
        check("Initial Order ID is not #RUR-9482", initial_order_id != "#RUR-9482", f"Value: '{initial_order_id}'")

        # Navigate to dashboard to make #p2-stores-list visible
        page.evaluate("navigateToPhase('dashboard')")
        page.wait_for_timeout(300)

        # Verify #p2-stores-empty-state exists when empty
        page.evaluate("renderDashboardStoresFeed([])")
        empty_visible = page.is_visible("#p2-stores-empty-state")
        check("Clean Empty State rendered for Empty Stores Array", empty_visible, "#p2-stores-empty-state is visible")

        open_count_text = page.inner_text("#p2-open-stores-count").strip()
        check("Open Stores Count shows 0 when empty", "0" in open_count_text, f"Text: '{open_count_text}'")

        # ---------------------------------------------------------------------
        # TEST 2: Dynamic Live Tracking Localization (Hindi State)
        # ---------------------------------------------------------------------
        print("\n[STEP 2]: Testing Live Tracking UI & Route Trail in Hindi (hi)", flush=True)
        page.evaluate("""
            AppStore.lang = 'hi';
            AppStore.activeStore = null;
            AppStore.user.landmark = '';
            window.applyBilingualState();
            navigateToPhase('tracking');
        """)
        page.wait_for_timeout(300)

        # Check landmarks in Hindi
        lm_store_hi = page.inner_text("#p5-lm-store").strip()
        lm_transit_hi = page.inner_text("#p5-lm-transit").strip()
        lm_dest_hi = page.inner_text("#p5-lm-dest").strip()
        route_lbl_hi = page.inner_text("#p5-route-lbl").strip()

        check("Store Landmark in Hindi", lm_store_hi == "शर्मा किराना", f"Text: '{lm_store_hi}'")
        check("Transit Landmark in Hindi", lm_transit_hi == "शिव मंदिर", f"Text: '{lm_transit_hi}'")
        check("Destination Landmark in Hindi", lm_dest_hi == "आपका घर", f"Text: '{lm_dest_hi}'")
        check("Route Label in Hindi", "रास्ता" in route_lbl_hi, f"Text: '{route_lbl_hi}'")

        # Check Timeline descriptions in Hindi
        st1_desc_hi = page.locator('[data-i18n="p5_stage_1_desc"]').inner_text().strip()
        st2_desc_hi = page.locator('[data-i18n="p5_stage_2_desc"]').inner_text().strip()
        st3_desc_hi = page.locator('[data-i18n="p5_stage_3_desc"]').inner_text().strip()
        st4_desc_hi = page.locator('[data-i18n="p5_stage_4_desc"]').inner_text().strip()
        st5_desc_hi = page.locator('[data-i18n="p5_stage_5_desc"]').inner_text().strip()

        check("Stage 1 Desc in Hindi", "पुष्टि" in st1_desc_hi, f"Text: '{st1_desc_hi}'")
        check("Stage 2 Desc in Hindi", "मंडी" in st2_desc_hi, f"Text: '{st2_desc_hi}'")
        check("Stage 3 Desc in Hindi", "मोहन लाल" in st3_desc_hi, f"Text: '{st3_desc_hi}'")
        check("Stage 4 Desc in Hindi", "शिव मंदिर" in st4_desc_hi, f"Text: '{st4_desc_hi}'")
        check("Stage 5 Desc in Hindi", "डिलीवरी" in st5_desc_hi, f"Text: '{st5_desc_hi}'")

        # ---------------------------------------------------------------------
        # TEST 3: Dynamic Live Tracking Localization (English State)
        # ---------------------------------------------------------------------
        print("\n[STEP 3]: Testing Live Tracking UI & Route Trail in English (en)", flush=True)
        page.evaluate("""
            AppStore.lang = 'en';
            AppStore.activeStore = null;
            AppStore.user.landmark = '';
            window.applyBilingualState();
        """)
        page.wait_for_timeout(300)

        # Check landmarks in English
        lm_store_en = page.inner_text("#p5-lm-store").strip()
        lm_transit_en = page.inner_text("#p5-lm-transit").strip()
        lm_dest_en = page.inner_text("#p5-lm-dest").strip()
        route_lbl_en = page.inner_text("#p5-route-lbl").strip()

        check("Store Landmark in English", lm_store_en == "Sharma Kirana", f"Text: '{lm_store_en}'")
        check("Transit Landmark in English", lm_transit_en == "Shiv Mandir", f"Text: '{lm_transit_en}'")
        check("Destination Landmark in English", lm_dest_en == "Your Home", f"Text: '{lm_dest_en}'")
        check("Route Label in English", "Route Trail" in route_lbl_en, f"Text: '{route_lbl_en}'")

        # Check Timeline descriptions in English
        st1_desc_en = page.locator('[data-i18n="p5_stage_1_desc"]').inner_text().strip()
        st2_desc_en = page.locator('[data-i18n="p5_stage_2_desc"]').inner_text().strip()
        st3_desc_en = page.locator('[data-i18n="p5_stage_3_desc"]').inner_text().strip()
        st4_desc_en = page.locator('[data-i18n="p5_stage_4_desc"]').inner_text().strip()
        st5_desc_en = page.locator('[data-i18n="p5_stage_5_desc"]').inner_text().strip()

        check("Stage 1 Desc in English", "Confirmed by Sharma Brothers Kirana" in st1_desc_en, f"Text: '{st1_desc_en}'")
        check("Stage 2 Desc in English", "Verified at local market inventory" in st2_desc_en, f"Text: '{st2_desc_en}'")
        check("Stage 3 Desc in English", "Handed over to Gaon Mitra" in st3_desc_en, f"Text: '{st3_desc_en}'")
        check("Stage 4 Desc in English", "Approaching Shiv Mandir" in st4_desc_en, f"Text: '{st4_desc_en}'")
        check("Stage 5 Desc in English", "Delivered safely with cash receipt" in st5_desc_en, f"Text: '{st5_desc_en}'")

        # ---------------------------------------------------------------------
        # TEST 4: Dynamic Store Feed Rendering (Real Stores vs Empty State)
        # ---------------------------------------------------------------------
        print("\n[STEP 4]: Testing Real Data Feed & Dynamic Bilingual State", flush=True)
        # Call renderDashboardStoresFeed with real store items
        mock_real_stores = [
            {
                "id": "sharma_brothers",
                "name": "Sharma Brothers Kirana",
                "hindi_name": "शर्मा ब्रदर्स किराना",
                "store_type": "kirana",
                "rating": 4.8,
                "is_open": True,
                "distance_km": 1.2,
                "eta_mins": "30 Mins"
            },
            {
                "id": "kisan_seva",
                "name": "Kisan Seva Kendra & Agri",
                "hindi_name": "किसान सेवा केंद्र",
                "store_type": "agri",
                "rating": 4.9,
                "is_open": True,
                "distance_km": 2.4,
                "eta_mins": "30 Mins"
            }
        ]
        page.evaluate("(stores) => { AppStore.stores = stores; renderDashboardStoresFeed(stores); }", mock_real_stores)
        page.wait_for_timeout(200)

        s1_title = page.locator('div[onclick*="sharma_brothers"] h4').inner_text().strip()
        check("Real Store 1 Rendered Dynamically in English", s1_title == "Sharma Brothers Kirana", f"Title: '{s1_title}'")

        s1_eta = page.inner_text("#store-1-eta").strip()
        check("Store 1 Dynamic ETA ID Populated", s1_eta == "30 Mins", f"ETA: '{s1_eta}'")

        # Switch to Hindi and re-render
        page.evaluate("""
            AppStore.lang = 'hi';
            window.applyBilingualState();
        """)
        page.wait_for_timeout(200)

        s1_title_hi = page.locator('div[onclick*="sharma_brothers"] h4').inner_text().strip()
        check("Real Store 1 Title Dynamically Localized to Hindi", "शर्मा" in s1_title_hi, f"Title: '{s1_title_hi}'")

        # ---------------------------------------------------------------------
        # TEST 5: User Order History Empty State Verification
        # ---------------------------------------------------------------------
        print("\n[STEP 5]: Testing User Past Orders Clean Empty State", flush=True)
        page.evaluate("""
            loadUserOrderHistory();
        """)
        page.wait_for_timeout(300)
        history_html = page.inner_text("#profile-order-history-list")
        check("No Hardcoded #RUR-9482 in Order History", "#RUR-9482" not in history_html, "Clean history")
        check("Empty state message displayed", "कोई पिछला ऑर्डर नहीं मिला" in history_html or "No past orders" in history_html, "Clean Empty State rendered")

        # ---------------------------------------------------------------------
        # TEST 6: Vendor & Runner Dashboards Purge Verification
        # ---------------------------------------------------------------------
        print("\n[STEP 6]: Checking Vendor & Runner Dashboard Initial HTML", flush=True)
        page.goto(vendor_html, wait_until="domcontentloaded")
        page.wait_for_timeout(200)
        v_toast = page.inner_text("#toast-subtitle").strip()
        check("Vendor Toast subtitle has no #RUR-9482", "#RUR-9482" not in v_toast, f"Subtitle: '{v_toast}'")

        page.goto(runner_html, wait_until="domcontentloaded")
        page.wait_for_timeout(200)
        r_order = page.inner_text("#detail-order-id").strip()
        check("Runner Detail Order ID has no #RUR-0000", "#RUR-0000" not in r_order, f"Order: '{r_order}'")

        browser.close()

    print("\n" + "=" * 80, flush=True)
    print(f"VERIFICATION RESULTS: {PASSED_CHECKS}/{TOTAL_CHECKS} CHECKS PASSED", flush=True)
    print("=" * 80, flush=True)
    if FAILED_CHECKS > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_tests()

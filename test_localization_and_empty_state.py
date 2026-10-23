"""
Comprehensive QA Automation: Localization and Dynamic Empty State Verification
Validates:
1. Live Tracking UI Purge & Default Empty State (when no active order exists)
2. Dynamic Live Tracking Rendering & Bilingual Localization (when real API order is received)
3. Store Feed Dynamic Empty State vs Real Data Feed
4. User Order History Clean Empty State
5. Vendor & Runner Dashboards Purged Initial State
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
        # STEP 1: Live Tracking Default Empty State & Purge of Static Data
        # ---------------------------------------------------------------------
        print("\n[STEP 1]: Verifying Default Empty State in Live Tracking UI", flush=True)
        page.goto(customer_html, wait_until="domcontentloaded")
        page.wait_for_timeout(300)

        # Navigate to tracking without an active order
        page.evaluate("navigateToPhase('tracking')")
        page.wait_for_timeout(200)

        # 1. Assert Empty State is visible by default
        empty_state_visible = page.is_visible("#p5-tracking-empty-state")
        check("Tracking Empty State container is visible by default", empty_state_visible, "#p5-tracking-empty-state displayed")

        # 2. Assert Active Tracking container is hidden by default
        active_content_visible = page.is_visible("#p5-active-tracking-content")
        check("Tracking Active Content is hidden when no active order exists", not active_content_visible, "#p5-active-tracking-content hidden")

        # 3. Assert Empty State text in Hindi
        empty_text_hi = page.inner_text("#p5-tracking-empty-state")
        check("Empty State displays Hindi prompt", "सक्रिय ऑर्डर नहीं है" in empty_text_hi, "Hindi empty state text")

        # 4. Switch to English and verify bilingual Empty State text
        page.evaluate("""
            AppStore.lang = 'en';
            window.applyBilingualState();
        """)
        page.wait_for_timeout(200)
        empty_text_en = page.inner_text("#p5-tracking-empty-state")
        check("Empty State displays exact English prompt", "No active orders right now. Go to Stores to place an order." in empty_text_en or ("No active orders" in empty_text_en and "Go to Stores" in empty_text_en), f"English empty state: '{empty_text_en.replace(chr(10), ' ')}'")

        # 5. Assert static dummy values are purged
        p5_amount = page.inner_text("#p5-order-amount").strip()
        p5_eta = page.inner_text("#p5-eta-time").strip()
        p5_otp_html = page.inner_html("#p5-delivery-otp-digits").strip()
        check("Static dummy amount ₹568.00 purged", p5_amount != "₹568.00", f"Amount: '{p5_amount}'")
        check("Static dummy ETA 30 Mins purged when no order exists", p5_eta != "30 Mins", f"ETA: '{p5_eta}'")
        check("Static delivery OTP digits purged", "4821" not in p5_otp_html and len(p5_otp_html) == 0, "OTP digits container is empty")

        # 6. Verify Empty State CTA button navigates to dashboard
        page.click("#p5-empty-goto-stores-btn")
        page.wait_for_timeout(200)
        check("Empty State CTA navigates to Dashboard", page.is_visible("#view-p2-dashboard"), "Dashboard visible after clicking CTA")

        # ---------------------------------------------------------------------
        # STEP 2: Dynamic Live Tracking Rendering on Real Order API Data
        # ---------------------------------------------------------------------
        print("\n[STEP 2]: Testing Dynamic Live Tracking Rendering & Bilingual Localization", flush=True)
        mock_order = {
            "order_id": "#RUR-3829",
            "status": "In Progress",
            "timeline_stage": 4,
            "delivery_otp": "7294",
            "total_amount": 258.0,
            "payment_mode": "COD",
            "store_name": "Sharma Brothers Kirana",
            "landmark": "Near Shiv Mandir",
            "distance_km": 1.2,
            "eta_mins": "30 Mins"
        }

        # Populate tracking UI with mock order and navigate to tracking in Hindi
        page.evaluate("""(order) => {
            AppStore.lang = 'hi';
            populateTrackingUI(order);
            navigateToPhase('tracking');
            window.applyBilingualState();
        }""", mock_order)
        page.wait_for_timeout(300)

        # Assert Active Tracking is now visible and Empty State is hidden
        check("Active Tracking visible after receiving order data", page.is_visible("#p5-active-tracking-content"), "Active content shown")
        check("Empty State hidden after receiving order data", not page.is_visible("#p5-tracking-empty-state"), "Empty state hidden")

        # Check Order ID, Amount, ETA, OTP
        active_order_id = page.inner_text("#p5-order-id").strip()
        active_amount = page.inner_text("#p5-order-amount").strip()
        active_eta = page.inner_text("#p5-eta-time").strip()
        active_otp = page.inner_text("#p5-delivery-otp-digits").replace("\n", "").replace(" ", "").strip()

        check("Dynamic Order ID populated", active_order_id == "#RUR-3829", f"Order ID: '{active_order_id}'")
        check("Dynamic Total Amount populated", "258" in active_amount, f"Amount: '{active_amount}'")
        check("Dynamic ETA populated", "30 Mins" in active_eta, f"ETA: '{active_eta}'")
        check("Dynamic 4-Digit Delivery OTP populated", active_otp == "7294", f"OTP: '{active_otp}'")

        # Check Landmarks & Route Label in Hindi
        lm_store_hi = page.inner_text("#p5-lm-store").strip()
        lm_transit_hi = page.inner_text("#p5-lm-transit").strip()
        lm_dest_hi = page.inner_text("#p5-lm-dest").strip()
        route_lbl_hi = page.inner_text("#p5-route-lbl").strip()

        check("Store Landmark in Hindi", "शर्मा" in lm_store_hi, f"Text: '{lm_store_hi}'")
        check("Transit Landmark in Hindi", "शिव मंदिर" in lm_transit_hi, f"Text: '{lm_transit_hi}'")
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
        # STEP 3: Dynamic Live Tracking in English
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

        check("Store Landmark in English", lm_store_en == "Sharma Kirana" or "Sharma" in lm_store_en, f"Text: '{lm_store_en}'")
        check("Transit Landmark in English", "Shiv Mandir" in lm_transit_en, f"Text: '{lm_transit_en}'")
        check("Destination Landmark in English", lm_dest_en == "Your Home", f"Text: '{lm_dest_en}'")
        check("Route Label in English", "Route Trail" in route_lbl_en, f"Text: '{route_lbl_en}'")

        # Check Timeline descriptions in English
        st1_desc_en = page.locator('[data-i18n="p5_stage_1_desc"]').inner_text().strip()
        st2_desc_en = page.locator('[data-i18n="p5_stage_2_desc"]').inner_text().strip()
        st3_desc_en = page.locator('[data-i18n="p5_stage_3_desc"]').inner_text().strip()
        st4_desc_en = page.locator('[data-i18n="p5_stage_4_desc"]').inner_text().strip()
        st5_desc_en = page.locator('[data-i18n="p5_stage_5_desc"]').inner_text().strip()

        check("Stage 1 Desc in English", "Confirmed by" in st1_desc_en, f"Text: '{st1_desc_en}'")
        check("Stage 2 Desc in English", "Verified at local market inventory" in st2_desc_en, f"Text: '{st2_desc_en}'")
        check("Stage 3 Desc in English", "Handed over to Gaon Mitra" in st3_desc_en, f"Text: '{st3_desc_en}'")
        check("Stage 4 Desc in English", "Approaching" in st4_desc_en, f"Text: '{st4_desc_en}'")
        check("Stage 5 Desc in English", "Delivered safely with cash receipt" in st5_desc_en, f"Text: '{st5_desc_en}'")

        # ---------------------------------------------------------------------
        # STEP 4: Dynamic Store Feed Rendering (Real Stores vs Empty State)
        # ---------------------------------------------------------------------
        print("\n[STEP 4]: Testing Real Data Feed & Dynamic Bilingual State", flush=True)
        page.evaluate("navigateToPhase('dashboard')")
        page.wait_for_timeout(200)

        # 1. Stores Empty State
        page.evaluate("renderDashboardStoresFeed([])")
        check("Stores Feed Empty State visible", page.is_visible("#p2-stores-empty-state"), "Clean empty stores state")
        open_count_text = page.inner_text("#p2-open-stores-count").strip()
        check("Open Stores Count shows 0 when empty", "0" in open_count_text, f"Text: '{open_count_text}'")

        # 2. Stores Feed Populated with Real Stores
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
        # STEP 5: User Order History Empty State Verification
        # ---------------------------------------------------------------------
        print("\n[STEP 5]: Testing User Past Orders Clean Empty State", flush=True)
        page.evaluate("loadUserOrderHistory();")
        page.wait_for_timeout(300)
        history_html = page.inner_text("#profile-order-history-list")
        check("No Hardcoded #RUR-9482 in Order History", "#RUR-9482" not in history_html, "Clean history")
        check("Empty state message displayed", "कोई पिछला ऑर्डर नहीं मिला" in history_html or "No past orders" in history_html, "Clean Empty State rendered")

        # ---------------------------------------------------------------------
        # STEP 6: Vendor & Runner Dashboards Purge Verification
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

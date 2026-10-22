"""
Phase 3 Store View & Dynamic Category Verification Test Suite
============================================================
Automated Playwright test suite to verify:
1. Blank Product Render Bug Fix (instant rendering, no empty screen).
2. Dynamic Store Categories (linked dynamically to Store_Type: Kirana vs Pharma vs Agri vs Dairy).
3. Complete Fake Data Purge (no hardcoded '4.8' or '18 Years Trust', dynamic badges or null for new stores).
4. Sticky Category Tabs during vertical scrolling.
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

# Reconfigure console output for UTF-8
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

BASE_DIR = Path(__file__).parent.resolve()
HTML_FILE_PATH = BASE_DIR / "index.html"
SCREENSHOTS_DIR = BASE_DIR / "screenshots" / "store_view"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

TOTAL_CHECKS = 0
PASSED_CHECKS = 0
FAILED_CHECKS = 0

def check(name: str, condition: bool, detail: str = ""):
    global TOTAL_CHECKS, PASSED_CHECKS, FAILED_CHECKS
    TOTAL_CHECKS += 1
    if condition:
        PASSED_CHECKS += 1
        print(f"  ✓ PASS: {name} ({detail})", flush=True)
    else:
        FAILED_CHECKS += 1
        print(f"  ✗ FAIL: {name} ({detail})", flush=True)

def run_tests():
    global TOTAL_CHECKS, PASSED_CHECKS, FAILED_CHECKS
    print("=" * 80, flush=True)
    print("GAONBAZAAR PHASE 3 STORE VIEW & DYNAMIC CATEGORIES QA SUITE", flush=True)
    print("=" * 80, flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 393, "height": 852},
            has_touch=True,
            is_mobile=True,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148"
        )
        page = context.new_page()

        file_url = HTML_FILE_PATH.as_uri()
        print(f"\n[STEP 1]: Loading Application from {file_url}", flush=True)
        page.goto(file_url, timeout=30000)
        page.wait_for_timeout(500)

        # Transition directly to Dashboard
        print("\n[STEP 2]: Fast-track Authentication to Phase 2 Dashboard", flush=True)
        page.evaluate("""
            AppStore.user.phone = '9876543210';
            AppStore.user.name = 'Ramesh Patel';
            navigateToPhase('dashboard');
        """)
        page.wait_for_timeout(400)

        dash_visible = page.is_visible("#view-p2-dashboard")
        check("Transition to Dashboard", dash_visible, "User logged in to Phase 2")

        # =========================================================================
        # TEST 1: PHARMACY STORE VIEW (Rampur Jan Aushadhi Kendra)
        # =========================================================================
        print("\n[STEP 3]: Testing Rampur Jan Aushadhi Kendra (Pharmacy)", flush=True)
        page.evaluate("openStoreView('rampur_dawa')")
        page.wait_for_timeout(400)

        store_visible = page.is_visible("#view-p3-store")
        check("Store View Displayed", store_visible, "Phase 3 is active")

        store_name = page.inner_text("#p3-store-name").strip()
        check("Pharma Store Name", "Rampur" in store_name or "रामपुर" in store_name, f"Name: {store_name}")

        trust_badge = page.inner_text("#p3-trust-lbl").strip()
        check("Pharma Trust Badge Dynamic", "Generic Medicines" in trust_badge or "जन औषधि" in trust_badge, f"Badge: {trust_badge}")
        check("Scrubbed Old Fake Trust Badge", "18 Years" not in trust_badge, "No 18 Years Trust leak")

        rating_badge = page.inner_text("#p3-store-rating-badge").strip()
        check("Pharma Dynamic Rating", "4.7" in rating_badge, f"Rating: {rating_badge}")

        call_btn_href = page.get_attribute("#p3-store-call-btn", "href") or ""
        check("Pharma Direct Dukandaar Call CTA", "9876543212" in call_btn_href, f"Tel: {call_btn_href}")

        # Category Tabs Check for Pharmacy
        cat_pills = page.query_selector_all("#p3-category-tabs-container .cat-pill")
        cat_texts = [p.inner_text().strip() for p in cat_pills]
        print(f"    Pharmacy Category Tabs: {cat_texts}", flush=True)
        check("Pharma Category Count", len(cat_pills) >= 4, f"{len(cat_pills)} category tabs generated")

        # CRITICAL ASSERTION: Pharmacy must NOT sell flour/dal/spices/oil
        all_cats_text = " ".join(cat_texts).lower()
        has_kirana_cats = any(bad in all_cats_text for bad in ["आटा", "दाल", "मसाले", "सरसों", "flour", "grain"])
        check("Strict Pharmacy Domain Isolation", not has_kirana_cats, "Zero kirana/grain categories in Pharmacy")

        has_pharma_cats = any(good in all_cats_text for good in ["दवा", "med", "hygiene", "स्वच्छता", "first aid", "चिकित्सा"])
        check("Healthcare Categories Present", has_pharma_cats, "Pharma-specific categories generated")

        # Products Check for Pharmacy
        prod_cards = page.query_selector_all("#p3-product-list [id^='prod-card-']")
        check("Pharma Instant Products Populated", len(prod_cards) >= 4, f"Rendered {len(prod_cards)} products instantly without blank screen")

        first_prod_text = prod_cards[0].inner_text()
        check("Pharma Medication Product", "Paracetamol" in first_prod_text or "पैरासिटामोल" in first_prod_text, "Paracetamol rendered")

        # Click Hygiene Category Tab
        print("    Testing category filter: Clicking Hygiene Tab...", flush=True)
        hygiene_btn = page.query_selector("#p3-category-tabs-container [data-cat-id='hygiene']")
        if hygiene_btn:
            hygiene_btn.click()
            page.wait_for_timeout(300)
            filtered_cards = page.query_selector_all("#p3-product-list [id^='prod-card-']")
            filtered_text = " ".join([c.inner_text() for c in filtered_cards])
            check("Hygiene Category Filter Active", "Dettol" in filtered_text or "डेटॉल" in filtered_text, "Dettol displayed in Hygiene tab")
            check("Paracetamol Filtered Out of Hygiene", "Paracetamol" not in filtered_text and "पैरासिटामोल" not in filtered_text, "Paracetamol correctly filtered out")

        page.screenshot(path=str(SCREENSHOTS_DIR / "01_pharma_store_view.png"))

        # =========================================================================
        # TEST 2: AGRI & SEEDS STORE VIEW (Kisan Seva Kendra)
        # =========================================================================
        print("\n[STEP 4]: Testing Kisan Seva Kendra & Agri", flush=True)
        page.evaluate("openStoreView('kisan_seva')")
        page.wait_for_timeout(400)

        kisan_name = page.inner_text("#p3-store-name").strip()
        check("Agri Store Name", "Kisan" in kisan_name or "किसान" in kisan_name, f"Name: {kisan_name}")

        kisan_trust = page.inner_text("#p3-trust-lbl").strip()
        check("Agri Trust Badge Dynamic", "Agri & Seeds" in kisan_trust or "कृषि सेवा" in kisan_trust, f"Badge: {kisan_trust}")

        kisan_cat_pills = page.query_selector_all("#p3-category-tabs-container .cat-pill")
        kisan_cat_texts = [p.inner_text().strip() for p in kisan_cat_pills]
        print(f"    Agri Category Tabs: {kisan_cat_texts}", flush=True)
        kisan_all_cats = " ".join(kisan_cat_texts).lower()

        check("Agri Domain Isolation (No Pharma)", "dawa" not in kisan_all_cats and "दवा" not in kisan_all_cats, "No medicine categories in Agri store")
        check("Agri Categories Present", any(k in kisan_all_cats for k in ["खाद", "बीज", "fertilizer", "seed", "औजार", "tools"]), "Fertilizer/Seed/Tool categories present")

        agri_prods = page.query_selector_all("#p3-product-list [id^='prod-card-']")
        check("Agri Instant Products Populated", len(agri_prods) >= 3, f"Rendered {len(agri_prods)} agri products instantly")
        agri_text = " ".join([c.inner_text() for c in agri_prods])
        check("Agri Farm Products Rendered", any(term in agri_text for term in ["DAP", "खाद", "Pioneer", "बीज", "Sprayer", "पंप"]), "Real farming products rendered")

        page.screenshot(path=str(SCREENSHOTS_DIR / "02_agri_store_view.png"))

        # =========================================================================
        # TEST 3: PURE VILLAGE DAIRY STORE VIEW (Apna Dugdh Dairy)
        # =========================================================================
        print("\n[STEP 5]: Testing Apna Dugdh Dairy Point", flush=True)
        page.evaluate("openStoreView('apna_dairy')")
        page.wait_for_timeout(400)

        dairy_name = page.inner_text("#p3-store-name").strip()
        check("Dairy Store Name", "Dairy" in dairy_name or "डेयरी" in dairy_name, f"Name: {dairy_name}")

        dairy_trust = page.inner_text("#p3-trust-lbl").strip()
        check("Dairy Trust Badge Dynamic", "Pure Village Dairy" in dairy_trust or "ताज़ा दुग्ध" in dairy_trust, f"Badge: {dairy_trust}")

        dairy_prods = page.query_selector_all("#p3-product-list [id^='prod-card-']")
        check("Dairy Products Populated", len(dairy_prods) >= 3, f"Rendered {len(dairy_prods)} dairy products instantly")
        dairy_text = " ".join([c.inner_text() for c in dairy_prods])
        check("Fresh Milk & Paneer Rendered", any(term in dairy_text for term in ["Milk", "दूध", "Paneer", "पनीर", "Chaas", "छाछ"]), "Fresh dairy products rendered")

        page.screenshot(path=str(SCREENSHOTS_DIR / "03_dairy_store_view.png"))

        # =========================================================================
        # TEST 4: KIRANA STORE VIEW (Sharma Brothers Kirana)
        # =========================================================================
        print("\n[STEP 6]: Testing Sharma Brothers Kirana", flush=True)
        page.evaluate("openStoreView('sharma_brothers')")
        page.wait_for_timeout(400)

        sharma_name = page.inner_text("#p3-store-name").strip()
        check("Kirana Store Name", "Sharma" in sharma_name or "शर्मा" in sharma_name, f"Name: {sharma_name}")

        sharma_trust = page.inner_text("#p3-trust-lbl").strip()
        check("Kirana Trust Badge Dynamic", "Verified Village Dukandaar" in sharma_trust or "सत्यापित किराना" in sharma_trust, f"Badge: {sharma_trust}")

        sharma_prods = page.query_selector_all("#p3-product-list [id^='prod-card-']")
        check("Kirana Products Populated", len(sharma_prods) >= 4, f"Rendered {len(sharma_prods)} kirana products instantly")

        # =========================================================================
        # TEST 5: STICKY CATEGORY TABS SCROLL VERIFICATION
        # =========================================================================
        print("\n[STEP 7]: Testing Sticky Category Tabs Scroll Pinning", flush=True)
        page.set_viewport_size({"width": 360, "height": 550})
        page.evaluate("""
            const storeEl = document.getElementById('view-p3-store');
            if (storeEl) storeEl.scrollTop = 250;
        """)
        page.wait_for_timeout(200)

        sticky_bounds = page.evaluate("""
            (() => {
                const wrapper = document.getElementById('p3-category-tabs-sticky-wrapper');
                const storeEl = document.getElementById('view-p3-store');
                const wrapRect = wrapper.getBoundingClientRect();
                const storeRect = storeEl.getBoundingClientRect();
                return {
                    wrapperTop: wrapRect.top,
                    storeTop: storeRect.top,
                    scrollTop: storeEl.scrollTop,
                    visible: wrapRect.height > 0 && wrapRect.width > 0
                };
            })()
        """)
        check("Store View Scrolled", sticky_bounds["scrollTop"] > 100, f"ScrollTop: {sticky_bounds['scrollTop']}px")
        check("Sticky Category Wrapper Pinned at Top", sticky_bounds["wrapperTop"] >= sticky_bounds["storeTop"] - 5, f"Pinned at relative top ({sticky_bounds['wrapperTop']} vs {sticky_bounds['storeTop']})")
        check("Sticky Category Wrapper Visible During Scroll", sticky_bounds["visible"], "Category tabs visible during deep vertical scroll")

        page.screenshot(path=str(SCREENSHOTS_DIR / "04_sticky_category_scroll.png"))

        # =========================================================================
        # TEST 6: NEW STORE WITH NULL/EMPTY RATING & TRUST BADGE (Zero Fake Data)
        # =========================================================================
        print("\n[STEP 8]: Testing Zero Fake Data / Null Ratings for New Stores", flush=True)
        new_store_eval = page.evaluate("""
            (() => {
                const dummyNewStore = {
                    id: 'new_panchayat_store',
                    name: 'Gupta General Store (New)',
                    hindi_name: 'गुप्ता जनरल स्टोर (नया)',
                    store_type: 'kirana',
                    rating: null,
                    total_orders: 0,
                    trust_badge: null,
                    phone: null,
                    distance_km: 0.5,
                    eta_mins: '15 Mins'
                };
                renderStoreHeaderDetails(dummyNewStore, 'new_panchayat_store');
                const trustHidden = document.getElementById('p3-trust-badge-container').classList.contains('hidden');
                const ratingBadgeText = document.getElementById('p3-store-rating-badge').innerText;
                const callBtnHidden = document.getElementById('p3-store-call-btn').classList.contains('hidden');
                return {
                    trustHidden,
                    ratingBadgeText,
                    callBtnHidden
                };
            })()
        """)
        check("New Store Trust Badge Hidden", new_store_eval["trustHidden"], "Empty trust badge correctly hidden")
        check("New Store Rating Badge Shows 'New Store'", "New Store" in new_store_eval["ratingBadgeText"] or "नया स्टोर" in new_store_eval["ratingBadgeText"], f"Badge: {new_store_eval['ratingBadgeText']}")
        check("New Store Without Phone Call CTA Hidden", new_store_eval["callBtnHidden"], "Call CTA safely hidden when phone is null")

        browser.close()

    print("\n" + "=" * 80, flush=True)
    print(f"STORE VIEW QA RESULTS: {PASSED_CHECKS}/{TOTAL_CHECKS} CHECKS PASSED", flush=True)
    print("=" * 80, flush=True)

    if FAILED_CHECKS > 0:
        print(f"\n❌ FAILED WITH {FAILED_CHECKS} REGRESSIONS", flush=True)
        sys.exit(1)
    else:
        print("\n✅ ZERO REGRESSIONS: PHASE 3 STORE VIEW FULLY VERIFIED (100% PASS)", flush=True)
        sys.exit(0)

if __name__ == "__main__":
    run_tests()

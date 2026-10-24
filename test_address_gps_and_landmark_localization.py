import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent

def run_tests():
    print("=" * 80)
    print("GAONBAZAAR: ADDRESS GPS REVERSE GEOCODING & STRICT LANDMARK LOCALIZATION AUDIT")
    print("=" * 80)

    html_file = ROOT_DIR / "index.html"
    file_url = f"file:///{html_file.as_posix()}"

    passed = 0
    total = 0

    def check(desc, condition, detail=""):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"  ✓ PASS: {desc}" + (f" - {detail}" if detail else ""))
        else:
            print(f"  ✗ FAIL: {desc}" + (f" - {detail}" if detail else ""))
            raise AssertionError(f"Check failed: {desc}. Detail: {detail}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Mobile viewport (iPhone 14 / Pixel 7 style)
        context = browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=2,
            is_mobile=True,
            has_touch=True,
            geolocation={"latitude": 29.1324, "longitude": 77.0125},
            permissions=["geolocation"]
        )
        page = context.new_page()
        page.goto(file_url)
        page.wait_for_timeout(600)

        # Navigate directly to the landmark / address setup view
        page.evaluate("navigateToPhase('landmark')")
        page.wait_for_timeout(400)

        # -------------------------------------------------------------
        # MODULE 1: STRICT LANGUAGE ISOLATION IN ENGLISH
        # -------------------------------------------------------------
        print("\n--- 1. Testing Strict Language Isolation in English ---")
        page.evaluate("window.toggleGlobalLanguage('en')")
        page.wait_for_timeout(400)

        # Verify Landmark Label
        lm_label = page.inner_text("label[data-i18n='p1_lm_field_label']").strip()
        check("English Landmark Label is Pure English", lm_label == "Prominent Village Landmark *", f"Label: '{lm_label}'")
        check("No Parenthesized 'Exact Landmark' in English Label", "(Exact Landmark)" not in lm_label)

        # Verify Counter (Empty State)
        counter_en = page.inner_text("#p1-lm-counter").strip()
        check("English Counter shows 'Min 10 chars'", counter_en == "Min 10 chars", f"Counter: '{counter_en}'")

        # Verify Textarea Placeholder
        ph_en = page.get_attribute("#p1-landmark-text", "placeholder")
        check("English Textarea Placeholder", ph_en == "e.g., Near Shiv Mandir, Behind Primary School", f"Placeholder: '{ph_en}'")

        # Verify Suggestion Chips in English
        chip_shiv = page.inner_text("#p1-chip-shiv").strip()
        chip_school = page.inner_text("#p1-chip-school").strip()
        chip_tank = page.inner_text("#p1-chip-tank").strip()
        chip_choupal = page.inner_text("#p1-chip-choupal").strip()

        check("Chip 1 English: 'Shiv Mandir'", "Shiv Mandir" in chip_shiv, f"Text: '{chip_shiv}'")
        check("Chip 2 English: 'Primary School'", "Primary School" in chip_school, f"Text: '{chip_school}'")
        check("Chip 3 English: 'Water Tank'", "Water Tank" in chip_tank, f"Text: '{chip_tank}'")
        check("Chip 4 English: 'Choupal'", "Choupal" in chip_choupal, f"Text: '{chip_choupal}'")

        # Click chip and check English text insertion & dynamic counter
        page.click("#p1-chip-shiv")
        page.wait_for_timeout(200)
        lm_val = page.input_value("#p1-landmark-text")
        check("Clicking Chip in EN appends English Landmark", "Near Shiv Mandir" in lm_val, f"Value: '{lm_val}'")

        counter_typed = page.inner_text("#p1-lm-counter").strip()
        check("Counter in EN shows '${len} / 10 chars'", "/ 10 chars" in counter_typed, f"Counter: '{counter_typed}'")

        # -------------------------------------------------------------
        # MODULE 2: STRICT LANGUAGE ISOLATION IN HINDI
        # -------------------------------------------------------------
        print("\n--- 2. Testing Strict Language Isolation in Hindi ---")
        page.evaluate("window.toggleGlobalLanguage('hi')")
        page.wait_for_timeout(400)

        # Verify Landmark Label in Hindi
        lm_label_hi = page.inner_text("label[data-i18n='p1_lm_field_label']").strip()
        check("Hindi Landmark Label is Pure Hindi", "गाँव का मुख्य पहचान चिन्ह" in lm_label_hi, f"Label: '{lm_label_hi}'")
        check("No English Parentheses in Hindi Landmark Label", "Exact" not in lm_label_hi and "Landmark" not in lm_label_hi)

        # Clear textarea to check empty counter in Hindi
        page.fill("#p1-landmark-text", "")
        page.evaluate("onLandmarkChange(document.getElementById('p1-landmark-text'))")
        page.wait_for_timeout(200)
        counter_hi = page.inner_text("#p1-lm-counter").strip()
        check("Hindi Counter shows 'कम से कम 10 अक्षर'", counter_hi == "कम से कम 10 अक्षर", f"Counter: '{counter_hi}'")

        # Verify Textarea Placeholder in Hindi
        ph_hi = page.get_attribute("#p1-landmark-text", "placeholder")
        check("Hindi Textarea Placeholder", "शिव मंदिर के पास" in ph_hi, f"Placeholder: '{ph_hi}'")

        # Verify Suggestion Chips in Hindi
        chip_shiv_hi = page.inner_text("#p1-chip-shiv").strip()
        chip_school_hi = page.inner_text("#p1-chip-school").strip()
        chip_tank_hi = page.inner_text("#p1-chip-tank").strip()
        chip_choupal_hi = page.inner_text("#p1-chip-choupal").strip()

        check("Chip 1 Hindi: 'शिव मंदिर'", "शिव मंदिर" in chip_shiv_hi, f"Text: '{chip_shiv_hi}'")
        check("Chip 2 Hindi: 'प्राथमिक स्कूल'", "प्राथमिक स्कूल" in chip_school_hi, f"Text: '{chip_school_hi}'")
        check("Chip 3 Hindi: 'पानी की टंकी'", "पानी की टंकी" in chip_tank_hi, f"Text: '{chip_tank_hi}'")
        check("Chip 4 Hindi: 'चौपाल'", "चौपाल" in chip_choupal_hi, f"Text: '{chip_choupal_hi}'")

        # Click chip in Hindi
        page.click("#p1-chip-tank")
        page.wait_for_timeout(200)
        lm_val_hi = page.input_value("#p1-landmark-text")
        check("Clicking Chip in HI appends Hindi Landmark", "पानी की टंकी" in lm_val_hi, f"Value: '{lm_val_hi}'")

        # -------------------------------------------------------------
        # MODULE 3: REVERSE GEOCODING FOR GPS (No Raw Coordinates)
        # -------------------------------------------------------------
        print("\n--- 3. Testing Reverse Geocoding for GPS ---")
        # Test in English mode
        page.evaluate("window.toggleGlobalLanguage('en')")
        page.wait_for_timeout(300)

        # Clear inputs first
        page.fill("#p1-district-input", "")
        page.fill("#p1-village-input", "")

        # Click GPS button
        page.click("#p1-locate-btn")
        # Wait for async reverse geocoding to resolve
        page.wait_for_timeout(2000)

        # 3.1 Badge check: No raw Lat: xx, Lng: xx coordinates displayed
        badge_text = page.inner_text("#p1-gps-badge").strip()
        check("GPS Badge Does NOT Contain Raw 'Lat:' prefix", "lat:" not in badge_text.lower(), f"Badge: '{badge_text}'")
        check("GPS Badge Does NOT Contain Raw 'Lng:' prefix", "lng:" not in badge_text.lower(), f"Badge: '{badge_text}'")
        check("GPS Badge Displays Readable Location Name", any(loc in badge_text.lower() for loc in ["chatursi", "ganaur", "gannaur", "sonipat", "haryana"]), f"Badge: '{badge_text}'")

        # 3.2 GPS Button Label check: Shows "📍 [Village] Detected"
        btn_text = page.inner_text("#p1-locate-text").strip()
        check("GPS Button Label Shows Location Detected (e.g. '📍 Chatursi Detected')", "detected" in btn_text.lower() and "📍" in btn_text, f"Button: '{btn_text}'")

        # 3.3 Auto-fill Inputs check: District / Tehsil and Village / Panchayat filled
        dist_val = page.input_value("#p1-district-input").strip()
        vill_val = page.input_value("#p1-village-input").strip()

        check("Auto-filled District / Tehsil input field", len(dist_val) > 0, f"District: '{dist_val}'")
        check("Auto-filled Village / Panchayat input field", len(vill_val) > 0, f"Village: '{vill_val}'")
        check("District is a valid name (e.g. Sonipat / Ganaur)", any(d in dist_val.lower() for d in ["sonipat", "ganaur", "gannaur"]), f"District: '{dist_val}'")

        # 3.4 Language Toggle with Detected Location
        print("\n--- 4. Testing Language Switch with Detected GPS ---")
        page.evaluate("window.toggleGlobalLanguage('hi')")
        page.wait_for_timeout(300)

        btn_text_hi = page.inner_text("#p1-locate-text").strip()
        check("GPS Button Label in Hindi Shows 'पहचाना गया'", "पहचाना गया" in btn_text_hi and "📍" in btn_text, f"Button HI: '{btn_text_hi}'")

        browser.close()

    print("\n" + "=" * 80)
    print(f"RESULTS: {passed}/{total} AUDITS PASSED (100.0%)")
    print("=" * 80)

if __name__ == "__main__":
    run_tests()

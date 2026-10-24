import sys
import time
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent

def run_tests():
    print("=" * 80)
    print("GAONBAZAAR: COMPREHENSIVE PROFILE / MY ACCOUNT UI/UX OVERHAUL AUDIT")
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
        context = browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=2,
            is_mobile=True,
            has_touch=True
        )
        page = context.new_page()
        page.goto(file_url)
        page.wait_for_timeout(600)

        # ---------------------------------------------------------------------
        # 1. NAVIGATION & GENERAL ARCHITECTURE CHECKS
        # ---------------------------------------------------------------------
        print("\n--- 1. Testing Profile View Navigation & Architecture ---")
        page.evaluate("navigateToPhase('profile')")
        page.wait_for_timeout(400)

        is_profile_visible = page.is_visible("#view-profile")
        check("Profile view is visible", is_profile_visible)

        # Clutter isolation check (Must not contain deprecated cards inside #view-profile)
        clutter_cards_count = page.locator("#view-profile #profile-support-entry-card").count() + \
                              page.locator("#view-profile #profile-saved-payments-section").count()
        check("No deprecated clutter cards inside #view-profile", clutter_cards_count == 0, f"Count: {clutter_cards_count}")

        # Check for non-hostile UI (No trust score or strikes visible to customers)
        profile_text = page.inner_text("#view-profile").lower()
        has_hostile_terms = any(term in profile_text for term in ["trust score", "strike", "cancellation count"])
        check("Profile is 100% free of internal risk/hostile terms", not has_hostile_terms)

        # ---------------------------------------------------------------------
        # 2. SECTION 1: PROFILE HEADER & PERSONAL INFO
        # ---------------------------------------------------------------------
        print("\n--- 2. Testing Section 1: Profile Header & Personal Info ---")
        avatar_initial = page.inner_text("#profile-user-avatar-initial").strip()
        check("Avatar initial element exists and is non-empty", len(avatar_initial) > 0, f"Initial: '{avatar_initial}'")

        user_name_disp = page.inner_text("#profile-user-name").strip()
        check("User name display element exists", len(user_name_disp) > 0, f"Name: '{user_name_disp}'")

        # Verified badge
        has_verified_badge = page.locator("#profile-user-card span[data-i18n='profile_verified_badge']").count() > 0
        check("Verified Customer badge rendered", has_verified_badge)

        # Non-editable Mobile Phone
        phone_el = page.inner_text("#profile-user-phone").strip()
        check("Mobile number displays +91 format", "+91" in phone_el, f"Phone: '{phone_el}'")
        phone_input_count = page.locator("input#profile-user-phone").count()
        check("Mobile number is locked (NOT an input element)", phone_input_count == 0)

        # Editable fields
        check("Full Name input exists", page.locator("#profile-user-name-input").count() == 1)
        check("Email ID input exists", page.locator("#profile-email-input").count() == 1)
        check("Date of Birth input exists", page.locator("#profile-dob-input").count() == 1)
        check("Gender select exists", page.locator("#profile-gender-select").count() == 1)

        # Test Editing Personal Info & Saving
        test_new_name = "Vikram Sharma"
        test_new_email = "vikram.sharma@gaonbazar.in"
        test_new_dob = "1992-08-20"
        test_new_gender = "male"

        page.fill("#profile-user-name-input", test_new_name)
        page.fill("#profile-email-input", test_new_email)
        page.fill("#profile-dob-input", test_new_dob)
        page.select_option("#profile-gender-select", test_new_gender)

        page.click("#profile-save-details-btn")
        page.wait_for_timeout(400)

        updated_name = page.inner_text("#profile-user-name").strip()
        check("Header user name updated reactively", updated_name == test_new_name, f"Updated Name: '{updated_name}'")

        updated_initial = page.inner_text("#profile-user-avatar-initial").strip()
        check("Avatar initial updated to 'V'", updated_initial == "V", f"Initial: '{updated_initial}'")

        saved_user_str = page.evaluate("localStorage.getItem('gaonbazar_user')")
        check("Local storage user data persisted", saved_user_str is not None)
        if saved_user_str:
            saved_user = json.loads(saved_user_str)
            check("Local storage reflects saved name", saved_user.get("name") == test_new_name)
            check("Local storage reflects saved email", saved_user.get("email") == test_new_email)
            check("Local storage reflects saved dob", saved_user.get("dob") == test_new_dob)
            check("Local storage reflects saved gender", saved_user.get("gender") == test_new_gender)

        # ---------------------------------------------------------------------
        # 3. SECTION 2: QUICK LINKS (SAVED DATA)
        # ---------------------------------------------------------------------
        print("\n--- 3. Testing Section 2: Quick Links (Saved Data) ---")
        check("Saved Addresses row exists", page.locator("#profile-row-saved-addresses").count() == 1)
        check("Saved Addresses row contains village element", page.locator("#profile-user-village").count() == 1)
        check("Saved Addresses row contains landmark element", page.locator("#profile-user-landmark").count() == 1)

        check("Saved Payments row exists", page.locator("#profile-row-saved-payments").count() == 1)
        
        # Test clicking Saved Payments opens Add Payment modal
        page.click("#profile-row-saved-payments")
        page.wait_for_timeout(300)
        is_pay_modal_open = page.is_visible("#modal-add-payment-method")
        check("Clicking Saved Payments opens payment modal", is_pay_modal_open)
        
        page.evaluate("closeAddPaymentModal()")
        page.wait_for_timeout(300)
        check("Payment modal closed cleanly", not page.is_visible("#modal-add-payment-method"))

        # ---------------------------------------------------------------------
        # 4. SECTION 3: SETTINGS & PREFERENCES (LANGUAGE & NOTIFICATIONS)
        # ---------------------------------------------------------------------
        print("\n--- 4. Testing Section 3: Settings & Preferences ---")
        check("Language Hi button exists", page.locator("#btn-profile-lang-hi").count() == 1)
        check("Language En button exists", page.locator("#btn-profile-lang-en").count() == 1)

        # Test Switch to English
        page.click("#btn-profile-lang-en")
        page.wait_for_timeout(400)
        lang_state = page.evaluate("AppStore.lang")
        check("Language switched to 'en'", lang_state == "en")

        saved_sec_en = page.inner_text("h3[data-i18n='profile_sec_saved']").strip()
        check("Saved Data section translated to English", saved_sec_en.upper() == "SAVED DATA", f"Title: '{saved_sec_en}'")

        danger_sec_en = page.inner_text("span[data-i18n='profile_danger_zone']").strip()
        check("Danger Zone label translated to English", danger_sec_en.upper() == "DANGER ZONE", f"Title: '{danger_sec_en}'")

        # Test Switch to Hindi
        page.click("#btn-profile-lang-hi")
        page.wait_for_timeout(400)
        lang_state_hi = page.evaluate("AppStore.lang")
        check("Language switched to 'hi'", lang_state_hi == "hi")

        saved_sec_hi = page.inner_text("h3[data-i18n='profile_sec_saved']").strip()
        check("Saved Data section translated to Hindi", "सहेजा गया" in saved_sec_hi, f"Title: '{saved_sec_hi}'")

        # Test Notification Toggles
        check("Push notification toggle exists", page.locator("#toggle-notif-push").count() == 1)
        check("SMS notification toggle exists", page.locator("#toggle-notif-sms").count() == 1)
        check("Email notification toggle exists", page.locator("#toggle-notif-email").count() == 1)

        # Toggle email notifications on
        page.evaluate("document.getElementById('toggle-notif-email').click()")
        page.wait_for_timeout(300)
        notifs_saved = json.loads(page.evaluate("localStorage.getItem('gaonbazar_notifs')") or "{}")
        check("Notification toggle preference saved to localStorage", notifs_saved.get("email") is True)

        # ---------------------------------------------------------------------
        # 5. SECTION 4: SUPPORT & ENGAGEMENT
        # ---------------------------------------------------------------------
        print("\n--- 5. Testing Section 4: Support & Engagement ---")
        check("Help & Support row exists", page.locator("#profile-row-help-support").count() == 1)
        check("Share App row exists", page.locator("#profile-row-share-app").count() == 1)
        check("Rate Us row exists", page.locator("#profile-row-rate-app").count() == 1)
        check("About Us row exists", page.locator("#profile-row-about-app").count() == 1)

        # Rate Us action test (triggers toast)
        page.click("#profile-row-rate-app")
        page.wait_for_timeout(300)
        toast_visible = page.is_visible("#app-audio-toast")
        check("Rating app triggers friendly feedback toast", toast_visible)
        toast_text = page.inner_text("#toast-msg")
        check("Toast contains 5-star appreciation message", "5-स्टार" in toast_text or "5 stars" in toast_text, f"Toast: '{toast_text}'")

        # About Us Modal Test
        page.click("#profile-row-about-app")
        page.wait_for_timeout(300)
        check("Clicking About Us opens About Modal", page.is_visible("#modal-about-us"))
        about_text = page.inner_text("#modal-about-us")
        check("About Modal contains GaonBazaar version 2.4.0", "v2.4.0" in about_text or "Version 2.4.0" in about_text)

        # Dismiss About Modal
        page.click("#modal-about-us button[aria-label='Close About Modal']")
        page.wait_for_timeout(300)
        check("About Modal dismissed successfully", not page.is_visible("#modal-about-us"))

        # ---------------------------------------------------------------------
        # 6. SECTION 5: LEGAL & SECURITY (DANGER ZONE)
        # ---------------------------------------------------------------------
        print("\n--- 6. Testing Section 5: Legal & Security (Danger Zone) ---")
        check("Privacy Policy row exists", page.locator("#profile-row-privacy").count() == 1)
        check("Terms & Conditions row exists", page.locator("#profile-row-terms").count() == 1)
        check("Logout button exists", page.locator("#profile-primary-logout-btn").count() == 1)
        check("Delete Account button exists", page.locator("#profile-delete-account-btn").count() == 1)

        # Privacy Policy Modal Test
        page.click("#profile-row-privacy")
        page.wait_for_timeout(300)
        check("Clicking Privacy Policy opens Privacy Modal", page.is_visible("#modal-privacy-policy"))
        privacy_text = page.inner_text("#modal-privacy-policy")
        check("Privacy Modal contains DPDP Act 2023 compliance info", "DPDP" in privacy_text)

        # Backdrop click to dismiss Privacy Modal
        page.evaluate("document.getElementById('modal-privacy-policy').click()")
        page.wait_for_timeout(300)
        check("Privacy Modal dismisses on backdrop tap", not page.is_visible("#modal-privacy-policy"))

        # Terms Modal Test
        page.click("#profile-row-terms")
        page.wait_for_timeout(300)
        check("Clicking Terms opens Terms Modal", page.is_visible("#modal-terms-conditions"))
        page.evaluate("closeTermsModal()")
        page.wait_for_timeout(300)
        check("Terms Modal closed successfully", not page.is_visible("#modal-terms-conditions"))

        # Delete Account Modal Test
        page.click("#profile-delete-account-btn")
        page.wait_for_timeout(300)
        check("Clicking Delete Account opens confirmation modal", page.is_visible("#modal-delete-account"))
        del_text = page.inner_text("#modal-delete-account")
        check("Delete Modal contains irreversible warning", "अपरिवर्तनीय" in del_text or "cannot be undone" in del_text)

        # Cancel Delete Modal
        page.click("#modal-delete-account button[data-i18n='del_cancel_btn']")
        page.wait_for_timeout(300)
        check("Delete Modal closes when user clicks cancel", not page.is_visible("#modal-delete-account"))

        browser.close()

    print("\n" + "=" * 80)
    print(f"RESULTS: {passed}/{total} AUDITS PASSED ({passed/total*100:.1f}%)")
    print("=" * 80)

if __name__ == "__main__":
    run_tests()

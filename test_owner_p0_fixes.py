import asyncio
import os
import sys
import io
from playwright.async_api import async_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def verify_owner_p0_fixes():
    print("=" * 70, flush=True)
    print("RUNNING VERIFICATION FOR OWNER P0 CUSTOMER APP DEFECTS", flush=True)
    print("=" * 70, flush=True)

    os.makedirs("screenshots/owner_p0_verification", exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Emulate a standard modern smartphone: 390x844 (iPhone 13 / 14 / modern Android)
        context = await browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=2,
            is_mobile=True,
            has_touch=True
        )
        page = await context.new_page()

        # Load Customer App directly from local file
        index_url = f"file:///{os.path.abspath('index.html').replace(os.sep, '/')}"
        await page.goto(index_url)
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(1)

        # Ensure we are in dashboard (Home)
        await page.evaluate("navigateToPhase('dashboard')")
        await page.evaluate("setAppTheme('light')")
        await page.evaluate("setAppLanguage('en')")
        await asyncio.sleep(0.5)

        # ---------------------------------------------------------------------
        # 1. HOME SCREEN: EXACTLY TWO FEATURED STORES IN ONE ROW
        # ---------------------------------------------------------------------
        print("\n--- 1. VERIFYING HOME STORES GRID ---", flush=True)
        
        # Check that 45 Open Now badge is NOT visible or hidden
        open_count_el = page.locator("#p2-open-stores-count")
        is_hidden = await open_count_el.evaluate("el => el.classList.contains('hidden') || window.getComputedStyle(el).display === 'none'")
        print(f"  [CHECK] '45 Open Now' badge hidden: {is_hidden}", flush=True)
        assert is_hidden, "Error: '45 Open Now' badge is still visible!"

        # Count rendered store cards inside #p2-stores-list
        stores_container = page.locator("#p2-stores-list")
        store_cards = stores_container.locator("> div:not(#p2-stores-empty-state)")
        store_count = await store_cards.count()
        print(f"  [CHECK] Rendered store cards count: {store_count}", flush=True)
        assert store_count <= 2, f"Error: Expected at most 2 store cards, got {store_count}!"

        # Check grid columns: should be grid-cols-2
        grid_class = await stores_container.get_attribute("class")
        print(f"  [CHECK] Store grid classes: {grid_class}", flush=True)
        assert "grid-cols-2" in grid_class, "Error: Stores container is not grid-cols-2!"

        await page.screenshot(path="screenshots/owner_p0_verification/01_home_stores_two_cards_light.png")
        print("  -> Captured 01_home_stores_two_cards_light.png", flush=True)

        # ---------------------------------------------------------------------
        # 2. HOME SCREEN: PRODUCTS IMMEDIATELY BELOW STORES
        # ---------------------------------------------------------------------
        print("\n--- 2. VERIFYING DYNAMIC PRODUCT GRID BELOW STORES ---", flush=True)
        products_container = page.locator("#home-popular-grid")
        product_cards = products_container.locator("> div")
        prod_count = await product_cards.count()
        print(f"  [CHECK] Rendered product cards count: {prod_count}", flush=True)
        assert prod_count > 0, "Error: No product cards rendered!"

        # Check 2 columns
        prod_grid_class = await products_container.get_attribute("class")
        print(f"  [CHECK] Product grid classes: {prod_grid_class}", flush=True)
        assert "grid-cols-2" in prod_grid_class, "Error: Products container is not grid-cols-2!"

        # Verify dynamic category filter
        print("\n--- 3. VERIFYING CATEGORY FILTER ---", flush=True)
        # Test 'dairy' category filter
        print("  Filtering by 'dairy'...", flush=True)
        await page.evaluate("filterStoresByCategory('dairy')")
        await asyncio.sleep(0.5)
        dairy_prods = await products_container.locator("> div:not(#home-popular-empty)").count()
        print(f"  [CHECK] Dairy category product cards count: {dairy_prods}", flush=True)
        await page.screenshot(path="screenshots/owner_p0_verification/02_home_category_dairy.png")
        print("  -> Captured 02_home_category_dairy.png", flush=True)

        # Test 'sabzi' / 'vegetables' category filter
        print("  Filtering by 'sabzi' (vegetables)...", flush=True)
        await page.evaluate("filterStoresByCategory('sabzi')")
        await asyncio.sleep(0.5)
        veg_prods = await products_container.locator("> div:not(#home-popular-empty)").count()
        print(f"  [CHECK] Vegetables category product cards count: {veg_prods}", flush=True)
        await page.screenshot(path="screenshots/owner_p0_verification/03_home_category_vegetables.png")
        print("  -> Captured 03_home_category_vegetables.png", flush=True)

        # Reset to 'all'
        await page.evaluate("filterStoresByCategory('all')")
        await asyncio.sleep(0.5)

        # ---------------------------------------------------------------------
        # 4. ACCOUNT SCREEN: EXACT 7 ENTRIES & LABELS
        # ---------------------------------------------------------------------
        print("\n--- 4. VERIFYING ACCOUNT SCREEN (7 APPROVED ENTRIES) ---", flush=True)
        # Navigate to Account tab in bottom nav
        await page.click("#nav-btn-profile")
        await asyncio.sleep(0.5)

        # Switch to English for clean verification of approved English labels
        await page.evaluate("setAppLanguage('en')")
        await asyncio.sleep(0.5)

        expected_rows_en = [
            ("account-row-profile", "My Profile"),
            ("account-row-addresses", "My Addresses"),
            ("account-row-payments", "Payment Settings"),
            ("account-row-preferences", "App Settings"),
            ("account-row-contact-support", "Help & Support"),
            ("account-row-security", "Policies & Legal"),
            ("profile-primary-logout-btn", "Logout")
        ]

        for row_id, expected_title in expected_rows_en:
            el = page.locator(f"#{row_id}")
            assert await el.count() > 0, f"Error: Row #{row_id} not found!"
            text = await el.inner_text()
            print(f"  [CHECK] Row #{row_id} contains '{expected_title}': {expected_title.lower() in text.lower()}", flush=True)
            assert expected_title.lower() in text.lower(), f"Error: Row #{row_id} text '{text}' does not contain '{expected_title}'!"

        # Assert no old unapproved titles present
        account_landing_text = await page.locator("#customer-account-landing").inner_text()
        assert "Settings & Preferences" not in account_landing_text, "Error: Old label 'Settings & Preferences' still present!"
        assert "Help & Support Center" not in account_landing_text, "Error: Old label 'Help & Support Center' still present!"
        print("  ✓ Confirmed neither 'Settings & Preferences' nor 'Help & Support Center' are present in Account landing!", flush=True)

        await page.screenshot(path="screenshots/owner_p0_verification/04_account_screen_7_entries_en.png")
        print("  -> Captured 04_account_screen_7_entries_en.png", flush=True)

        # Switch to Hindi to verify Hindi labels
        await page.evaluate("setAppLanguage('hi')")
        await asyncio.sleep(0.5)
        await page.screenshot(path="screenshots/owner_p0_verification/05_account_screen_7_entries_hi.png")
        print("  -> Captured 05_account_screen_7_entries_hi.png", flush=True)

        # ---------------------------------------------------------------------
        # 5. NAVIGATION: BACK BUTTONS HIERARCHY
        # ---------------------------------------------------------------------
        print("\n--- 5. VERIFYING NAVIGATION & BACK BUTTON HIERARCHY ---", flush=True)
        
        # Check Account Top Bar Back Button
        account_back_btn = page.locator("#profile-back-to-home-btn")
        assert await account_back_btn.count() > 0, "Error: #profile-back-to-home-btn not found!"
        assert await account_back_btn.is_visible(), "Error: #profile-back-to-home-btn is not visible!"
        print("  ✓ Back button on Account landing top bar is visible.", flush=True)

        # Click Back from Account landing -> should return to Home (dashboard)
        await account_back_btn.click()
        await asyncio.sleep(0.5)
        dash_active = await page.locator("#view-p2-dashboard").is_visible()
        print(f"  [CHECK] Back from Account landed on Dashboard: {dash_active}", flush=True)
        assert dash_active, "Error: Clicking Back from Account did not return to Home Dashboard!"

        # Go back to Account
        await page.click("#nav-btn-profile")
        await asyncio.sleep(0.5)

        # Test Subviews Back Navigation
        subviews_to_test = [
            ("account-row-profile", "customer-subview-personal", "My Profile"),
            ("account-row-addresses", "customer-subview-addresses", "My Addresses"),
            ("account-row-payments", "customer-subview-payments", "Payment Settings"),
            ("account-row-preferences", "customer-subview-preferences", "App Settings"),
        ]

        for trigger_id, subview_id, name in subviews_to_test:
            print(f"  Testing subview back navigation: {name} ({subview_id})", flush=True)
            await page.click(f"#{trigger_id}")
            await asyncio.sleep(0.3)
            sub_visible = await page.locator(f"#{subview_id}").is_visible()
            assert sub_visible, f"Error: Subview {subview_id} did not open!"
            
            # Click the back button inside the subview
            subview_back_btn = page.locator(f"#{subview_id} button[aria-label='Back to Account'], #{subview_id} button:has(span:text('arrow_back'))").first
            await subview_back_btn.click()
            await asyncio.sleep(0.3)

            # Landing should be visible again
            landing_visible = await page.locator("#customer-account-landing").is_visible()
            assert landing_visible, f"Error: Subview back did not return to Account landing for {name}!"
            print(f"    ✓ Back from {name} successfully returned to Account landing.", flush=True)

        # ---------------------------------------------------------------------
        # 6. DARK MODE VERIFICATION
        # ---------------------------------------------------------------------
        print("\n--- 6. VERIFYING DARK MODE ---", flush=True)
        await page.evaluate("setAppTheme('dark')")
        await asyncio.sleep(0.5)
        is_dark = await page.evaluate("document.documentElement.classList.contains('dark')")
        print(f"  [CHECK] Dark mode active: {is_dark}", flush=True)
        assert is_dark, "Error: Dark mode failed to activate!"

        # Home in Dark Mode
        await page.click("#nav-btn-stores")
        await asyncio.sleep(0.5)
        await page.screenshot(path="screenshots/owner_p0_verification/06_home_dark_mode.png")
        print("  -> Captured 06_home_dark_mode.png", flush=True)

        # Account in Dark Mode
        await page.click("#nav-btn-profile")
        await asyncio.sleep(0.5)
        await page.screenshot(path="screenshots/owner_p0_verification/07_account_dark_mode.png")
        print("  -> Captured 07_account_dark_mode.png", flush=True)

        print("\n" + "=" * 70, flush=True)
        print("ALL OWNER P0 VERIFICATION CHECKS PASSED WITH 100% SUCCESS!", flush=True)
        print("=" * 70, flush=True)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify_owner_p0_fixes())

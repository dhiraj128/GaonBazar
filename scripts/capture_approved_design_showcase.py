import os
import sys
import time
from PIL import Image
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')
os.makedirs('screenshots/design_freeze_verification', exist_ok=True)
os.makedirs('screenshots/design_freeze_verification/side_by_side', exist_ok=True)

print("================================================================================")
print("  GAONBAZAAR — APPROVED DESIGN FREEZE CAPTURE & SIDE-BY-SIDE VERIFICATION")
print("================================================================================")

VIEWPORT = {"width": 393, "height": 852}
BASE_URL = "http://127.0.0.1:8001"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport=VIEWPORT,
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15"
    )
    page = context.new_page()

    # =========================================================================
    # 1. CUSTOMER APPLICATION
    # =========================================================================
    print("\n--- 1. Capturing Customer App ---")
    page.goto(f"{BASE_URL}/", wait_until="load")
    page.wait_for_timeout(800)

    # Login customer if needed
    if page.is_visible("#view-p1-login"):
        try:
            page.fill("#p1-phone-input", "9876543210")
            page.click("#p1-send-otp-btn")
            page.wait_for_timeout(400)
            for idx, digit in enumerate("582941"):
                page.fill(f'.otp-cell[data-idx="{idx}"]', digit)
            page.wait_for_timeout(400)
            page.click("#p1-verify-otp-btn")
            page.wait_for_timeout(800)
        except Exception as e:
            print("Login helper note:", e)

    # Ensure dashboard is visible
    page.evaluate("if (typeof navigateToPhase === 'function') navigateToPhase('dashboard');")
    page.wait_for_timeout(600)

    # Populate cart with reference items (Tomato 2kg, Amul Milk 1L, Onion 1kg)
    page.evaluate("""
        if (typeof AppStore !== 'undefined' && AppStore.catalog) {
            AppStore.catalog.forEach(i => i.qty = 0);
            const t = AppStore.catalog.find(i => i.id === 'item_tomato');
            if (t) t.qty = 2;
            const m = AppStore.catalog.find(i => i.id === 'item_milk');
            if (m) m.qty = 1;
            const o = AppStore.catalog.find(i => i.id === 'item_onion');
            if (o) o.qty = 1;
            if (typeof updateCartUI === 'function') updateCartUI();
        }
    """)

    # 1.1 Customer Home - Light & Dark
    page.evaluate("document.documentElement.classList.remove('dark'); localStorage.setItem('theme', 'light');")
    page.wait_for_timeout(300)
    page.screenshot(path="screenshots/design_freeze_verification/cust_01_home_light.png")
    
    page.evaluate("document.documentElement.classList.add('dark'); localStorage.setItem('theme', 'dark');")
    page.wait_for_timeout(300)
    page.screenshot(path="screenshots/design_freeze_verification/cust_01_home_dark.png")
    page.evaluate("document.documentElement.classList.remove('dark');")

    # 1.2 Customer AI Voice Shopping - Light & Dark
    page.evaluate("if (typeof navigateToPhase === 'function') navigateToPhase('ai-commerce');")
    page.wait_for_timeout(600)
    page.screenshot(path="screenshots/design_freeze_verification/cust_02_ai_light.png")

    page.evaluate("document.documentElement.classList.add('dark');")
    page.wait_for_timeout(300)
    page.screenshot(path="screenshots/design_freeze_verification/cust_02_ai_dark.png")
    page.evaluate("document.documentElement.classList.remove('dark');")

    # 1.3 Customer Cart & Checkout - Light & Dark
    page.evaluate("if (typeof navigateToPhase === 'function') navigateToPhase('cart');")
    page.wait_for_timeout(600)
    page.screenshot(path="screenshots/design_freeze_verification/cust_03_cart_light.png")

    page.evaluate("document.documentElement.classList.add('dark');")
    page.wait_for_timeout(300)
    page.screenshot(path="screenshots/design_freeze_verification/cust_03_cart_dark.png")
    page.evaluate("document.documentElement.classList.remove('dark');")

    # 1.4 Customer Tracking - Light & Dark
    page.evaluate("""
        if (typeof navigateToPhase === 'function') navigateToPhase('tracking');
        const emptyEl = document.getElementById('p5-tracking-empty-state');
        const activeEl = document.getElementById('p5-active-tracking-content');
        if (emptyEl) emptyEl.classList.add('hidden');
        if (activeEl) {
            activeEl.classList.remove('hidden');
            activeEl.style.display = 'flex';
        }
    """)
    page.wait_for_timeout(600)
    page.screenshot(path="screenshots/design_freeze_verification/cust_04_tracking_light.png")

    page.evaluate("document.documentElement.classList.add('dark');")
    page.wait_for_timeout(300)
    page.screenshot(path="screenshots/design_freeze_verification/cust_04_tracking_dark.png")
    page.evaluate("document.documentElement.classList.remove('dark');")

    # 1.5 Customer Side Drawer - Light & Dark
    page.evaluate("if (typeof openSidebarDrawer === 'function') openSidebarDrawer();")
    page.wait_for_timeout(600)
    page.screenshot(path="screenshots/design_freeze_verification/cust_05_drawer_light.png")

    page.evaluate("document.documentElement.classList.add('dark');")
    page.wait_for_timeout(300)
    page.screenshot(path="screenshots/design_freeze_verification/cust_05_drawer_dark.png")
    page.evaluate("document.documentElement.classList.remove('dark'); if (typeof closeSidebarDrawer === 'function') closeSidebarDrawer();")

    # =========================================================================
    # 2. VENDOR APPLICATION
    # =========================================================================
    print("\n--- 2. Capturing Vendor App ---")
    vpage = context.new_page()
    vpage.goto(f"{BASE_URL}/vendor", wait_until="load")
    vpage.wait_for_timeout(800)

    # Bypass/login vendor if gate visible
    if vpage.is_visible("#vendor-login-gate"):
        try:
            vpage.fill("#vendor-auth-phone", "9876500001")
            vpage.click("#vendor-auth-submit")
            vpage.wait_for_timeout(500)
            for i in range(1, 5):
                if vpage.is_visible(f"#vendor-otp-{i}"):
                    vpage.fill(f"#vendor-otp-{i}", "1")
            if vpage.is_visible("#vendor-otp-verify-btn"):
                vpage.click("#vendor-otp-verify-btn")
            vpage.wait_for_timeout(800)
        except Exception as e:
            print("Vendor login note:", e)

    # 2.1 Vendor Orders Queue - Light & Dark
    vpage.evaluate("document.documentElement.classList.remove('dark'); if (typeof switchMainTab === 'function') switchMainTab('orders');")
    vpage.wait_for_timeout(500)
    vpage.screenshot(path="screenshots/design_freeze_verification/vend_01_orders_light.png")

    vpage.evaluate("document.documentElement.classList.add('dark');")
    vpage.wait_for_timeout(300)
    vpage.screenshot(path="screenshots/design_freeze_verification/vend_01_orders_dark.png")
    vpage.evaluate("document.documentElement.classList.remove('dark');")

    # 2.2 Vendor Order Details - Light & Dark
    vpage.evaluate("""
        const detailModal = document.getElementById('modal-order-detail');
        if (detailModal) {
            detailModal.classList.remove('hidden');
            detailModal.style.display = 'flex';
        }
    """)
    vpage.wait_for_timeout(500)
    vpage.screenshot(path="screenshots/design_freeze_verification/vend_02_details_light.png")

    vpage.evaluate("document.documentElement.classList.add('dark');")
    vpage.wait_for_timeout(300)
    vpage.screenshot(path="screenshots/design_freeze_verification/vend_02_details_dark.png")
    vpage.evaluate("""
        document.documentElement.classList.remove('dark');
        const detailModal = document.getElementById('modal-order-detail');
        if (detailModal) {
            detailModal.classList.add('hidden');
            detailModal.style.display = 'none';
        }
    """)

    # 2.3 Vendor Stock & Inventory - Light & Dark
    vpage.evaluate("if (typeof switchMainTab === 'function') switchMainTab('inventory');")
    vpage.wait_for_timeout(500)
    vpage.screenshot(path="screenshots/design_freeze_verification/vend_03_inventory_light.png")

    vpage.evaluate("document.documentElement.classList.add('dark');")
    vpage.wait_for_timeout(300)
    vpage.screenshot(path="screenshots/design_freeze_verification/vend_03_inventory_dark.png")
    vpage.evaluate("document.documentElement.classList.remove('dark');")

    # 2.4 Vendor Assigned Runner Handover - Light & Dark
    vpage.evaluate("""
        const handoverModal = document.getElementById('modal-runner-handover');
        if (handoverModal) {
            handoverModal.classList.remove('hidden');
            handoverModal.style.display = 'flex';
        }
    """)
    vpage.wait_for_timeout(500)
    vpage.screenshot(path="screenshots/design_freeze_verification/vend_04_handover_light.png")

    vpage.evaluate("document.documentElement.classList.add('dark');")
    vpage.wait_for_timeout(300)
    vpage.screenshot(path="screenshots/design_freeze_verification/vend_04_handover_dark.png")
    vpage.evaluate("""
        document.documentElement.classList.remove('dark');
        const handoverModal = document.getElementById('modal-runner-handover');
        if (handoverModal) {
            handoverModal.classList.add('hidden');
            handoverModal.style.display = 'none';
        }
    """)

    # 2.5 Vendor Menu / Settings - Light & Dark
    vpage.evaluate("if (typeof openVendorMenuDrawer === 'function') openVendorMenuDrawer(); else if (typeof switchMainTab === 'function') switchMainTab('settings');")
    vpage.wait_for_timeout(500)
    vpage.screenshot(path="screenshots/design_freeze_verification/vend_05_menu_light.png")

    vpage.evaluate("document.documentElement.classList.add('dark');")
    vpage.wait_for_timeout(300)
    vpage.screenshot(path="screenshots/design_freeze_verification/vend_05_menu_dark.png")
    vpage.evaluate("document.documentElement.classList.remove('dark');")

    # =========================================================================
    # 3. RUNNER / DELIVERY PARTNER APPLICATION
    # =========================================================================
    print("\n--- 3. Capturing Runner App ---")
    rpage = context.new_page()
    rpage.goto(f"{BASE_URL}/runner", wait_until="load")
    rpage.wait_for_timeout(800)

    # Bypass/login runner if gate visible
    if rpage.is_visible("#runner-login-gate"):
        try:
            rpage.fill("#runner-auth-phone", "9876511111")
            rpage.click("#runner-auth-submit")
            rpage.wait_for_timeout(500)
            for i in range(1, 5):
                if rpage.is_visible(f"#runner-otp-{i}"):
                    rpage.fill(f"#runner-otp-{i}", "1")
            if rpage.is_visible("#runner-otp-verify-btn"):
                rpage.click("#runner-otp-verify-btn")
            rpage.wait_for_timeout(800)
        except Exception as e:
            print("Runner login note:", e)

    # 3.1 Runner Missions Dashboard - Light & Dark
    rpage.evaluate("document.documentElement.classList.remove('dark'); if (typeof switchTab === 'function') switchTab('missions');")
    rpage.wait_for_timeout(500)
    rpage.screenshot(path="screenshots/design_freeze_verification/runn_01_missions_light.png")

    rpage.evaluate("document.documentElement.classList.add('dark');")
    rpage.wait_for_timeout(300)
    rpage.screenshot(path="screenshots/design_freeze_verification/runn_01_missions_dark.png")
    rpage.evaluate("document.documentElement.classList.remove('dark');")

    # 3.2 Runner Pickup Details - Light & Dark
    rpage.evaluate("if (typeof switchTab === 'function') switchTab('detail');")
    rpage.wait_for_timeout(500)
    rpage.screenshot(path="screenshots/design_freeze_verification/runn_02_pickup_light.png")

    rpage.evaluate("document.documentElement.classList.add('dark');")
    rpage.wait_for_timeout(300)
    rpage.screenshot(path="screenshots/design_freeze_verification/runn_02_pickup_dark.png")
    rpage.evaluate("document.documentElement.classList.remove('dark');")

    # 3.3 Runner On the Way / Navigation - Light & Dark
    rpage.evaluate("""
        const navSection = document.getElementById('runner-active-navigation-view') || document.getElementById('tab-detail');
        if (typeof showRunnerMapView === 'function') showRunnerMapView();
    """)
    rpage.wait_for_timeout(500)
    rpage.screenshot(path="screenshots/design_freeze_verification/runn_03_navigation_light.png")

    rpage.evaluate("document.documentElement.classList.add('dark');")
    rpage.wait_for_timeout(300)
    rpage.screenshot(path="screenshots/design_freeze_verification/runn_03_navigation_dark.png")
    rpage.evaluate("document.documentElement.classList.remove('dark');")

    # 3.4 Runner Delivery Completion - Light & Dark
    rpage.evaluate("""
        const successModal = document.getElementById('modal-delivery-success');
        if (successModal) {
            successModal.classList.remove('hidden');
            successModal.style.display = 'flex';
        }
    """)
    rpage.wait_for_timeout(500)
    rpage.screenshot(path="screenshots/design_freeze_verification/runn_04_completion_light.png")

    rpage.evaluate("document.documentElement.classList.add('dark');")
    rpage.wait_for_timeout(300)
    rpage.screenshot(path="screenshots/design_freeze_verification/runn_04_completion_dark.png")
    rpage.evaluate("""
        document.documentElement.classList.remove('dark');
        const successModal = document.getElementById('modal-delivery-success');
        if (successModal) {
            successModal.classList.add('hidden');
            successModal.style.display = 'none';
        }
    """)

    # 3.5 Runner Profile / Menu / Earnings - Light & Dark
    rpage.evaluate("if (typeof switchTab === 'function') switchTab('settings');")
    rpage.wait_for_timeout(500)
    rpage.screenshot(path="screenshots/design_freeze_verification/runn_05_profile_light.png")

    rpage.evaluate("document.documentElement.classList.add('dark');")
    rpage.wait_for_timeout(300)
    rpage.screenshot(path="screenshots/design_freeze_verification/runn_05_profile_dark.png")
    rpage.evaluate("document.documentElement.classList.remove('dark');")

    browser.close()

# =========================================================================
# 4. GENERATE SIDE-BY-SIDE COMPARISON IMAGES
# =========================================================================
print("\n--- 4. Generating Side-by-Side Visual Comparison Boards ---")

def create_side_by_side(ref_path, actual_path, out_path, title):
    if not os.path.exists(ref_path) or not os.path.exists(actual_path):
        print(f"Skipping {title}: Missing {ref_path} or {actual_path}")
        return
    ref = Image.open(ref_path).convert('RGB')
    act = Image.open(actual_path).convert('RGB')
    
    # Scale ref and act to same height (e.g. 852 px)
    h = 852
    ref_w = int(ref.width * (h / ref.height))
    act_w = int(act.width * (h / act.height))
    
    ref_resized = ref.resize((ref_w, h), Image.Resampling.LANCZOS)
    act_resized = act.resize((act_w, h), Image.Resampling.LANCZOS)
    
    # Combined canvas: ref | gap | act
    gap = 20
    combined = Image.new('RGB', (ref_w + gap + act_w, h), (240, 243, 246))
    combined.paste(ref_resized, (0, 0))
    combined.paste(act_resized, (ref_w + gap, 0))
    combined.save(out_path)
    print(f"  ✓ Created side-by-side: {out_path}")

# Customer Comparisons
for i, name in enumerate(['01_home', '02_ai', '03_cart', '04_tracking', '05_drawer'], 1):
    ref_file = f"scratch/customer_frames/frame_{i}.png"
    act_file = f"screenshots/design_freeze_verification/cust_{name}_light.png"
    out_file = f"screenshots/design_freeze_verification/side_by_side/compare_cust_{name}.png"
    create_side_by_side(ref_file, act_file, out_file, f"Customer {name}")

# Vendor Comparisons
for i, name in enumerate(['01_orders', '02_details', '03_inventory', '04_handover', '05_menu'], 1):
    ref_file = f"scratch/vendor_frames/frame_{i}.png"
    act_file = f"screenshots/design_freeze_verification/vend_{name}_light.png"
    out_file = f"screenshots/design_freeze_verification/side_by_side/compare_vend_{name}.png"
    create_side_by_side(ref_file, act_file, out_file, f"Vendor {name}")

# Runner Comparisons
for i, name in enumerate(['01_missions', '02_pickup', '03_navigation', '04_completion', '05_profile'], 1):
    ref_file = f"scratch/runner_frames/frame_{i}.png"
    act_file = f"screenshots/design_freeze_verification/runn_{name}_light.png"
    out_file = f"screenshots/design_freeze_verification/side_by_side/compare_runn_{name}.png"
    create_side_by_side(ref_file, act_file, out_file, f"Runner {name}")

print("\n================================================================================")
print("  ALL VERIFICATION SCREENSHOTS AND SIDE-BY-SIDE BOARDS GENERATED!")
print("================================================================================")

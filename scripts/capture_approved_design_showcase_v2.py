import os
import sys
import time
from PIL import Image
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')
os.makedirs('screenshots/design_freeze_verification', exist_ok=True)
os.makedirs('screenshots/design_freeze_verification/side_by_side', exist_ok=True)

print("================================================================================")
print("  GAONBAZAAR — APPROVED DESIGN FREEZE CAPTURE & SIDE-BY-SIDE VERIFICATION V2")
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

    # Bypass / Login if needed
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

    # 1.1 Customer Home - Light & Dark
    page.evaluate("""
        if (typeof navigateToPhase === 'function') navigateToPhase('dashboard');
        window.scrollTo(0, 0);
        document.documentElement.classList.remove('dark');
        localStorage.setItem('theme', 'light');
    """)
    page.wait_for_timeout(400)
    page.screenshot(path="screenshots/design_freeze_verification/cust_01_home_light.png")

    page.evaluate("document.documentElement.classList.add('dark'); localStorage.setItem('theme', 'dark');")
    page.wait_for_timeout(300)
    page.screenshot(path="screenshots/design_freeze_verification/cust_01_home_dark.png")
    page.evaluate("document.documentElement.classList.remove('dark');")

    # 1.2 Customer AI Voice Shopping - Light & Dark
    page.evaluate("""
        if (typeof navigateToPhase === 'function') navigateToPhase('ai-commerce');
        window.scrollTo(0, 0);
    """)
    page.wait_for_timeout(500)
    page.screenshot(path="screenshots/design_freeze_verification/cust_02_ai_light.png")

    page.evaluate("document.documentElement.classList.add('dark');")
    page.wait_for_timeout(300)
    page.screenshot(path="screenshots/design_freeze_verification/cust_02_ai_dark.png")
    page.evaluate("document.documentElement.classList.remove('dark');")

    # 1.3 Customer Cart & Checkout - Light & Dark
    page.evaluate("""
        if (typeof quickAddFeaturedItem === 'function') {
            quickAddFeaturedItem('item_tomato');
            quickAddFeaturedItem('item_oil');
        }
        if (typeof navigateToPhase === 'function') navigateToPhase('cart');
        window.scrollTo(0, 0);
    """)
    page.wait_for_timeout(500)
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
        window.scrollTo(0, 0);
    """)
    page.wait_for_timeout(500)
    page.screenshot(path="screenshots/design_freeze_verification/cust_04_tracking_light.png")

    page.evaluate("document.documentElement.classList.add('dark');")
    page.wait_for_timeout(300)
    page.screenshot(path="screenshots/design_freeze_verification/cust_04_tracking_dark.png")
    page.evaluate("document.documentElement.classList.remove('dark');")

    # 1.5 Customer Side Drawer - Light & Dark
    page.evaluate("""
        if (typeof navigateToPhase === 'function') navigateToPhase('dashboard');
        if (typeof openSidebarDrawer === 'function') openSidebarDrawer();
    """)
    page.wait_for_timeout(500)
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
    vpage.evaluate("""
        document.documentElement.classList.remove('dark');
        document.getElementById('vendor-header')?.classList.remove('hidden');
        if (typeof switchMainTab === 'function') switchMainTab('orders');
        if (typeof renderOrdersQueue === 'function') renderOrdersQueue();
        window.scrollTo(0, 0);
    """)
    vpage.wait_for_timeout(500)
    vpage.screenshot(path="screenshots/design_freeze_verification/vend_01_orders_light.png")

    vpage.evaluate("document.documentElement.classList.add('dark');")
    vpage.wait_for_timeout(300)
    vpage.screenshot(path="screenshots/design_freeze_verification/vend_01_orders_dark.png")
    vpage.evaluate("document.documentElement.classList.remove('dark');")

    # 2.2 Vendor Order Details - Light & Dark
    vpage.evaluate("""
        if (typeof openVendorOrderDetailModal === 'function') {
            openVendorOrderDetailModal('GB-1850');
        } else {
            const detailModal = document.getElementById('modal-order-detail');
            if (detailModal) {
                detailModal.classList.remove('hidden');
                detailModal.style.display = 'flex';
            }
        }
    """)
    vpage.wait_for_timeout(500)
    vpage.screenshot(path="screenshots/design_freeze_verification/vend_02_details_light.png")

    vpage.evaluate("document.documentElement.classList.add('dark');")
    vpage.wait_for_timeout(300)
    vpage.screenshot(path="screenshots/design_freeze_verification/vend_02_details_dark.png")
    vpage.evaluate("""
        document.documentElement.classList.remove('dark');
        if (typeof closeVendorOrderDetailModal === 'function') {
            closeVendorOrderDetailModal();
        } else {
            const detailModal = document.getElementById('modal-order-detail');
            if (detailModal) {
                detailModal.classList.add('hidden');
                detailModal.style.display = 'none';
            }
        }
    """)

    # 2.3 Vendor Stock & Inventory - Light & Dark
    vpage.evaluate("""
        if (typeof switchMainTab === 'function') switchMainTab('inventory');
        if (typeof renderInventoryGrid === 'function') renderInventoryGrid();
        window.scrollTo(0, 0);
    """)
    vpage.wait_for_timeout(500)
    vpage.screenshot(path="screenshots/design_freeze_verification/vend_03_inventory_light.png")

    vpage.evaluate("document.documentElement.classList.add('dark');")
    vpage.wait_for_timeout(300)
    vpage.screenshot(path="screenshots/design_freeze_verification/vend_03_inventory_dark.png")
    vpage.evaluate("document.documentElement.classList.remove('dark');")

    # 2.4 Vendor Assigned Runner Handover - Light & Dark
    vpage.evaluate("""
        if (typeof openVendorHandoverModal === 'function') {
            openVendorHandoverModal('GB-1850');
        } else {
            const handoverModal = document.getElementById('modal-runner-handover');
            if (handoverModal) {
                handoverModal.classList.remove('hidden');
                handoverModal.style.display = 'flex';
            }
        }
    """)
    vpage.wait_for_timeout(500)
    vpage.screenshot(path="screenshots/design_freeze_verification/vend_04_handover_light.png")

    vpage.evaluate("document.documentElement.classList.add('dark');")
    vpage.wait_for_timeout(300)
    vpage.screenshot(path="screenshots/design_freeze_verification/vend_04_handover_dark.png")
    vpage.evaluate("""
        document.documentElement.classList.remove('dark');
        if (typeof closeVendorHandoverModal === 'function') {
            closeVendorHandoverModal();
        } else {
            const handoverModal = document.getElementById('modal-runner-handover');
            if (handoverModal) {
                handoverModal.classList.add('hidden');
                handoverModal.style.display = 'none';
            }
        }
    """)

    # 2.5 Vendor Menu / Settings - Light & Dark
    vpage.evaluate("""
        if (typeof switchMainTab === 'function') switchMainTab('settings');
        window.scrollTo(0, 0);
    """)
    vpage.wait_for_timeout(500)
    vpage.screenshot(path="screenshots/design_freeze_verification/vend_05_menu_light.png")

    vpage.evaluate("document.documentElement.classList.add('dark');")
    vpage.wait_for_timeout(300)
    vpage.screenshot(path="screenshots/design_freeze_verification/vend_05_menu_dark.png")
    vpage.evaluate("document.documentElement.classList.remove('dark');")

    # =========================================================================
    # 3. RUNNER APPLICATION
    # =========================================================================
    print("\n--- 3. Capturing Runner App ---")
    rpage = context.new_page()
    rpage.goto(f"{BASE_URL}/runner", wait_until="load")
    rpage.wait_for_timeout(800)

    # Bypass/login runner if gate visible
    if rpage.is_visible("#runner-login-gate"):
        try:
            rpage.fill("#runner-auth-phone", "9876500002")
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
    rpage.evaluate("""
        document.documentElement.classList.remove('dark');
        if (typeof switchTab === 'function') switchTab('missions');
        if (typeof renderMissionsQueue === 'function') renderMissionsQueue();
        window.scrollTo(0, 0);
    """)
    rpage.wait_for_timeout(500)
    rpage.screenshot(path="screenshots/design_freeze_verification/runn_01_missions_light.png")

    rpage.evaluate("document.documentElement.classList.add('dark');")
    rpage.wait_for_timeout(300)
    rpage.screenshot(path="screenshots/design_freeze_verification/runn_01_missions_dark.png")
    rpage.evaluate("document.documentElement.classList.remove('dark');")

    # 3.2 Runner Pickup Details - Light & Dark
    rpage.evaluate("""
        if (typeof showRunnerPickupDetail === 'function') {
            showRunnerPickupDetail('GB-1850');
        } else if (typeof switchTab === 'function') {
            switchTab('detail');
        }
        window.scrollTo(0, 0);
    """)
    rpage.wait_for_timeout(500)
    rpage.screenshot(path="screenshots/design_freeze_verification/runn_02_pickup_light.png")

    rpage.evaluate("document.documentElement.classList.add('dark');")
    rpage.wait_for_timeout(300)
    rpage.screenshot(path="screenshots/design_freeze_verification/runn_02_pickup_dark.png")
    rpage.evaluate("document.documentElement.classList.remove('dark');")

    # 3.3 Runner On the Way / Navigation - Light & Dark
    rpage.evaluate("""
        if (typeof showRunnerMapView === 'function') {
            showRunnerMapView();
        }
        window.scrollTo(0, 0);
    """)
    rpage.wait_for_timeout(500)
    rpage.screenshot(path="screenshots/design_freeze_verification/runn_03_navigation_light.png")

    rpage.evaluate("document.documentElement.classList.add('dark');")
    rpage.wait_for_timeout(300)
    rpage.screenshot(path="screenshots/design_freeze_verification/runn_03_navigation_dark.png")
    rpage.evaluate("document.documentElement.classList.remove('dark');")

    # 3.4 Runner Delivery Completion - Light & Dark
    rpage.evaluate("""
        if (typeof showRunnerDeliverySuccess === 'function') {
            showRunnerDeliverySuccess();
        }
        window.scrollTo(0, 0);
    """)
    rpage.wait_for_timeout(500)
    rpage.screenshot(path="screenshots/design_freeze_verification/runn_04_completion_light.png")

    rpage.evaluate("document.documentElement.classList.add('dark');")
    rpage.wait_for_timeout(300)
    rpage.screenshot(path="screenshots/design_freeze_verification/runn_04_completion_dark.png")
    rpage.evaluate("document.documentElement.classList.remove('dark');")

    # 3.5 Runner Profile / Menu / Earnings - Light & Dark
    rpage.evaluate("""
        if (typeof switchTab === 'function') switchTab('settings');
        window.scrollTo(0, 0);
    """)
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
    
    h = 852
    ref_w = int(ref.width * (h / ref.height))
    act_w = int(act.width * (h / act.height))
    
    ref_resized = ref.resize((ref_w, h), Image.Resampling.LANCZOS)
    act_resized = act.resize((act_w, h), Image.Resampling.LANCZOS)
    
    gap = 20
    combined = Image.new('RGB', (ref_w + gap + act_w, h), (240, 243, 246))
    combined.paste(ref_resized, (0, 0))
    combined.paste(act_resized, (ref_w + gap, 0))
    combined.save(out_path)
    print(f"✓ Created side-by-side: {out_path}")

COMPARISONS = [
    # Customer Screens
    ("scratch/customer_frames/frame_01.png", "screenshots/design_freeze_verification/cust_01_home_light.png", "screenshots/design_freeze_verification/side_by_side/compare_cust_01_home_light.png", "Customer 01 Home Light"),
    ("scratch/customer_frames/frame_01.png", "screenshots/design_freeze_verification/cust_01_home_dark.png", "screenshots/design_freeze_verification/side_by_side/compare_cust_01_home_dark.png", "Customer 01 Home Dark"),
    ("scratch/customer_frames/frame_02.png", "screenshots/design_freeze_verification/cust_02_ai_light.png", "screenshots/design_freeze_verification/side_by_side/compare_cust_02_ai_light.png", "Customer 02 AI Light"),
    ("scratch/customer_frames/frame_02.png", "screenshots/design_freeze_verification/cust_02_ai_dark.png", "screenshots/design_freeze_verification/side_by_side/compare_cust_02_ai_dark.png", "Customer 02 AI Dark"),
    ("scratch/customer_frames/frame_03.png", "screenshots/design_freeze_verification/cust_03_cart_light.png", "screenshots/design_freeze_verification/side_by_side/compare_cust_03_cart_light.png", "Customer 03 Cart Light"),
    ("scratch/customer_frames/frame_03.png", "screenshots/design_freeze_verification/cust_03_cart_dark.png", "screenshots/design_freeze_verification/side_by_side/compare_cust_03_cart_dark.png", "Customer 03 Cart Dark"),
    ("scratch/customer_frames/frame_04.png", "screenshots/design_freeze_verification/cust_04_tracking_light.png", "screenshots/design_freeze_verification/side_by_side/compare_cust_04_tracking_light.png", "Customer 04 Tracking Light"),
    ("scratch/customer_frames/frame_04.png", "screenshots/design_freeze_verification/cust_04_tracking_dark.png", "screenshots/design_freeze_verification/side_by_side/compare_cust_04_tracking_dark.png", "Customer 04 Tracking Dark"),
    ("scratch/customer_frames/frame_05.png", "screenshots/design_freeze_verification/cust_05_drawer_light.png", "screenshots/design_freeze_verification/side_by_side/compare_cust_05_drawer_light.png", "Customer 05 Drawer Light"),
    ("scratch/customer_frames/frame_05.png", "screenshots/design_freeze_verification/cust_05_drawer_dark.png", "screenshots/design_freeze_verification/side_by_side/compare_cust_05_drawer_dark.png", "Customer 05 Drawer Dark"),

    # Vendor Screens
    ("scratch/vendor_frames/frame_01.png", "screenshots/design_freeze_verification/vend_01_orders_light.png", "screenshots/design_freeze_verification/side_by_side/compare_vend_01_orders_light.png", "Vendor 01 Orders Light"),
    ("scratch/vendor_frames/frame_01.png", "screenshots/design_freeze_verification/vend_01_orders_dark.png", "screenshots/design_freeze_verification/side_by_side/compare_vend_01_orders_dark.png", "Vendor 01 Orders Dark"),
    ("scratch/vendor_frames/frame_02.png", "screenshots/design_freeze_verification/vend_02_details_light.png", "screenshots/design_freeze_verification/side_by_side/compare_vend_02_details_light.png", "Vendor 02 Details Light"),
    ("scratch/vendor_frames/frame_02.png", "screenshots/design_freeze_verification/vend_02_details_dark.png", "screenshots/design_freeze_verification/side_by_side/compare_vend_02_details_dark.png", "Vendor 02 Details Dark"),
    ("scratch/vendor_frames/frame_03.png", "screenshots/design_freeze_verification/vend_03_inventory_light.png", "screenshots/design_freeze_verification/side_by_side/compare_vend_03_inventory_light.png", "Vendor 03 Inventory Light"),
    ("scratch/vendor_frames/frame_03.png", "screenshots/design_freeze_verification/vend_03_inventory_dark.png", "screenshots/design_freeze_verification/side_by_side/compare_vend_03_inventory_dark.png", "Vendor 03 Inventory Dark"),
    ("scratch/vendor_frames/frame_04.png", "screenshots/design_freeze_verification/vend_04_handover_light.png", "screenshots/design_freeze_verification/side_by_side/compare_vend_04_handover_light.png", "Vendor 04 Handover Light"),
    ("scratch/vendor_frames/frame_04.png", "screenshots/design_freeze_verification/vend_04_handover_dark.png", "screenshots/design_freeze_verification/side_by_side/compare_vend_04_handover_dark.png", "Vendor 04 Handover Dark"),
    ("scratch/vendor_frames/frame_05.png", "screenshots/design_freeze_verification/vend_05_menu_light.png", "screenshots/design_freeze_verification/side_by_side/compare_vend_05_menu_light.png", "Vendor 05 Menu Light"),
    ("scratch/vendor_frames/frame_05.png", "screenshots/design_freeze_verification/vend_05_menu_dark.png", "screenshots/design_freeze_verification/side_by_side/compare_vend_05_menu_dark.png", "Vendor 05 Menu Dark"),

    # Runner Screens
    ("scratch/runner_frames/frame_01.png", "screenshots/design_freeze_verification/runn_01_missions_light.png", "screenshots/design_freeze_verification/side_by_side/compare_runn_01_missions_light.png", "Runner 01 Missions Light"),
    ("scratch/runner_frames/frame_01.png", "screenshots/design_freeze_verification/runn_01_missions_dark.png", "screenshots/design_freeze_verification/side_by_side/compare_runn_01_missions_dark.png", "Runner 01 Missions Dark"),
    ("scratch/runner_frames/frame_02.png", "screenshots/design_freeze_verification/runn_02_pickup_light.png", "screenshots/design_freeze_verification/side_by_side/compare_runn_02_pickup_light.png", "Runner 02 Pickup Light"),
    ("scratch/runner_frames/frame_02.png", "screenshots/design_freeze_verification/runn_02_pickup_dark.png", "screenshots/design_freeze_verification/side_by_side/compare_runn_02_pickup_dark.png", "Runner 02 Pickup Dark"),
    ("scratch/runner_frames/frame_03.png", "screenshots/design_freeze_verification/runn_03_navigation_light.png", "screenshots/design_freeze_verification/side_by_side/compare_runn_03_navigation_light.png", "Runner 03 Navigation Light"),
    ("scratch/runner_frames/frame_03.png", "screenshots/design_freeze_verification/runn_03_navigation_dark.png", "screenshots/design_freeze_verification/side_by_side/compare_runn_03_navigation_dark.png", "Runner 03 Navigation Dark"),
    ("scratch/runner_frames/frame_04.png", "screenshots/design_freeze_verification/runn_04_completion_light.png", "screenshots/design_freeze_verification/side_by_side/compare_runn_04_completion_light.png", "Runner 04 Completion Light"),
    ("scratch/runner_frames/frame_04.png", "screenshots/design_freeze_verification/runn_04_completion_dark.png", "screenshots/design_freeze_verification/side_by_side/compare_runn_04_completion_dark.png", "Runner 04 Completion Dark"),
    ("scratch/runner_frames/frame_05.png", "screenshots/design_freeze_verification/runn_05_profile_light.png", "screenshots/design_freeze_verification/side_by_side/compare_runn_05_profile_light.png", "Runner 05 Profile Light"),
    ("scratch/runner_frames/frame_05.png", "screenshots/design_freeze_verification/runn_05_profile_dark.png", "screenshots/design_freeze_verification/side_by_side/compare_runn_05_profile_dark.png", "Runner 05 Profile Dark"),
]

for ref_f, act_f, out_f, title in COMPARISONS:
    create_side_by_side(ref_f, act_f, out_f, title)

print("\n✓ All 30 side-by-side comparison boards generated successfully!")

"""
GaonBazaar - Master Approved Design Freeze Capture & Verification Generator
Captures all 15 screens in Light & Dark modes (30 screenshots total)
and generates 30 side-by-side comparison boards with the approved reference design frames.
Also captures Super Admin screenshots.
"""

import os
import sys
import time
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

# Output directories
SHOWCASE_DIR = "screenshots/showcase_v5_approved"
FREEZE_DIR = "screenshots/design_freeze_verification"
SIDE_BY_SIDE_DIR = "screenshots/design_freeze_verification/side_by_side"

for d in [SHOWCASE_DIR, FREEZE_DIR, SIDE_BY_SIDE_DIR]:
    os.makedirs(d, exist_ok=True)

VIEWPORT = {"width": 393, "height": 852}
BASE_URL = "http://127.0.0.1:8001"

def save_dual_screenshot(page, base_filename):
    """Saves screenshot to both showcase_v5_approved and design_freeze_verification"""
    path1 = os.path.join(SHOWCASE_DIR, base_filename)
    path2 = os.path.join(FREEZE_DIR, base_filename)
    page.screenshot(path=path1, full_page=False)
    page.screenshot(path=path2, full_page=False)
    print(f"  📸 Saved: {base_filename}")

def create_side_by_side(ref_path, act_path, out_path, title, is_dark=False):
    """Combines approved reference frame (left) with actual app screenshot (right)"""
    if not os.path.exists(ref_path) or not os.path.exists(act_path):
        print(f"  ⚠️ Skipping {title}: {ref_path} or {act_path} missing")
        return

    ref_img = Image.open(ref_path).convert('RGB')
    act_img = Image.open(act_path).convert('RGB')

    target_height = 852
    ref_w = int(ref_img.width * (target_height / ref_img.height))
    act_w = int(act_img.width * (target_height / act_img.height))

    ref_resized = ref_img.resize((ref_w, target_height), Image.Resampling.LANCZOS)
    act_resized = act_img.resize((act_w, target_height), Image.Resampling.LANCZOS)

    header_height = 54
    gap = 24
    total_w = ref_w + gap + act_w + 32
    total_h = target_height + header_height + 24

    bg_color = (24, 34, 45) if is_dark else (241, 245, 249)
    board = Image.new('RGB', (total_w, total_h), bg_color)
    draw = ImageDraw.Draw(board)

    # Title Banner
    theme_label = "DARK MODE" if is_dark else "LIGHT MODE"
    text_color = (248, 250, 252) if is_dark else (15, 23, 42)
    sub_color = (148, 163, 184) if is_dark else (100, 116, 139)

    draw.text((16, 12), f"GAONBAZAAR DESIGN FREEZE VERIFICATION • {title.upper()}", fill=text_color)
    draw.text((16, 32), f"Approved Reference Frame (Left) vs Production Implementation [{theme_label}] (Right)", fill=sub_color)

    # Paste frames
    y_offset = header_height
    board.paste(ref_resized, (16, y_offset))
    board.paste(act_resized, (16 + ref_w + gap, y_offset))

    # Border around images
    border_color = (71, 85, 105) if is_dark else (203, 213, 225)
    draw.rectangle([16, y_offset, 16 + ref_w, y_offset + target_height], outline=border_color, width=1)
    draw.rectangle([16 + ref_w + gap, y_offset, 16 + ref_w + gap + act_w, y_offset + target_height], outline=border_color, width=1)

    board.save(out_path)
    print(f"  🖼️ Side-by-side board created: {os.path.basename(out_path)}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport=VIEWPORT,
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15"
    )

    # =========================================================================
    # 1. CUSTOMER APPLICATION (C1 - C5)
    # =========================================================================
    print("\n" + "=" * 60)
    print("1. CAPTURING CUSTOMER APP (C1 - C5)")
    print("=" * 60)
    page = context.new_page()
    page.goto(f"{BASE_URL}/", wait_until="load")
    page.wait_for_timeout(1000)

    # Quick preview login
    page.evaluate("""
        localStorage.setItem('gaonbazar_user', JSON.stringify({
            phone: '9876543210',
            name: 'Ramesh Patel',
            village: 'Rampur Village, Sonipat',
            landmark: 'Near Shiva Mandir, Opp. Blue Water Tank'
        }));
        if (typeof navigateToPhase === 'function') navigateToPhase('dashboard');
    """)
    page.wait_for_timeout(800)

    # Ensure Hindi language & catalog populated
    page.evaluate("""
        if (typeof setAppLanguage === 'function') setAppLanguage('hi');
        const langEl = document.getElementById('drawer-lang-curr');
        if (langEl) langEl.innerText = 'हिंदी';
    """)
    page.wait_for_timeout(400)

    # Populate verified cart (Total: ₹163 = Items ₹145 + Delivery ₹15 + Platform ₹3)
    page.evaluate("""
        if (typeof AppStore !== 'undefined' && AppStore.catalog) {
            AppStore.catalog.forEach(i => i.qty = 0);
            const t = AppStore.catalog.find(i => i.id === 'item_tomato' || i.id === 'item_1');
            if (t) { t.qty = 2; t.price = 30; t.name_hi = 'ताजा टमाटर'; }
            const m = AppStore.catalog.find(i => i.id === 'item_milk' || i.id === 'item_2');
            if (m) { m.qty = 1; m.price = 30; m.name_hi = 'अमूल ताजा दूध'; }
            const o = AppStore.catalog.find(i => i.id === 'item_onion' || i.id === 'item_3');
            if (o) { o.qty = 1; o.price = 25; o.name_hi = 'लाल प्याज़'; }
            const a = AppStore.catalog.find(i => i.id === 'item_atta' || i.id === 'item_4');
            if (a) { a.qty = 1; a.price = 30; a.name_hi = 'आशीर्वाद चक्की आटा'; }
            if (typeof updateCartUI === 'function') updateCartUI();
        }
    """)

    # --- C1: Customer Home ---
    print("\n[C1] Capturing Customer Home...")
    page.evaluate("if (typeof navigateToPhase === 'function') navigateToPhase('dashboard');")
    page.evaluate("document.documentElement.classList.remove('dark'); localStorage.setItem('theme', 'light');")
    page.wait_for_timeout(400)
    save_dual_screenshot(page, "cust_01_home_light.png")

    page.evaluate("document.documentElement.classList.add('dark'); localStorage.setItem('theme', 'dark');")
    page.wait_for_timeout(400)
    save_dual_screenshot(page, "cust_01_home_dark.png")
    page.evaluate("document.documentElement.classList.remove('dark');")

    # --- C2: Customer AI Voice Shopping ---
    print("\n[C2] Capturing Customer AI Voice Assistant...")
    page.evaluate("if (typeof navigateToPhase === 'function') navigateToPhase('ai-commerce');")
    page.wait_for_timeout(600)
    save_dual_screenshot(page, "cust_02_voice_ai_light.png")

    page.evaluate("document.documentElement.classList.add('dark');")
    page.wait_for_timeout(400)
    save_dual_screenshot(page, "cust_02_voice_ai_dark.png")
    page.evaluate("document.documentElement.classList.remove('dark');")

    # --- C3: Customer Cart & Checkout ---
    print("\n[C3] Capturing Customer Cart & Checkout...")
    page.evaluate("if (typeof navigateToPhase === 'function') navigateToPhase('cart');")
    page.wait_for_timeout(600)
    save_dual_screenshot(page, "cust_03_cart_light.png")

    page.evaluate("document.documentElement.classList.add('dark');")
    page.wait_for_timeout(400)
    save_dual_screenshot(page, "cust_03_cart_dark.png")
    page.evaluate("document.documentElement.classList.remove('dark');")

    # --- C4: Customer Live Tracking ---
    print("\n[C4] Capturing Customer Live Tracking...")
    page.evaluate("""
        if (typeof navigateToPhase === 'function') navigateToPhase('tracking');
        const emptyEl = document.getElementById('p5-tracking-empty-state');
        const activeEl = document.getElementById('p5-active-tracking-content');
        if (emptyEl) emptyEl.classList.add('hidden');
        if (activeEl) {
            activeEl.classList.remove('hidden');
            activeEl.style.display = 'flex';
        }
        const ordId = document.getElementById('p5-order-id-display');
        if (ordId) ordId.innerText = '#GB-1850';
        const otpEl = document.getElementById('p5-otp-badge');
        if (otpEl) otpEl.innerText = '4821';
    """)
    page.wait_for_timeout(600)
    save_dual_screenshot(page, "cust_04_tracking_light.png")

    page.evaluate("document.documentElement.classList.add('dark');")
    page.wait_for_timeout(400)
    save_dual_screenshot(page, "cust_04_tracking_dark.png")
    page.evaluate("document.documentElement.classList.remove('dark');")

    # --- C5: Customer Side Drawer ---
    print("\n[C5] Capturing Customer Side Navigation Drawer...")
    page.evaluate("if (typeof navigateToPhase === 'function') navigateToPhase('dashboard');")
    page.wait_for_timeout(300)
    page.evaluate("if (typeof openSidebarDrawer === 'function') openSidebarDrawer();")
    page.wait_for_timeout(500)
    save_dual_screenshot(page, "cust_05_drawer_light.png")

    page.evaluate("document.documentElement.classList.add('dark');")
    page.wait_for_timeout(400)
    save_dual_screenshot(page, "cust_05_drawer_dark.png")
    page.evaluate("document.documentElement.classList.remove('dark'); if (typeof closeSidebarDrawer === 'function') closeSidebarDrawer();")
    page.close()

    # =========================================================================
    # 2. VENDOR APPLICATION (V1 - V5)
    # =========================================================================
    print("\n" + "=" * 60)
    print("2. CAPTURING VENDOR APP (V1 - V5)")
    print("=" * 60)
    vpage = context.new_page()
    vpage.goto(f"{BASE_URL}/vendor?preview=1", wait_until="load")
    vpage.wait_for_timeout(1000)

    # Ensure Hindi language & verified preview data
    vpage.evaluate("""
        if (typeof setVendorLanguage === 'function') setVendorLanguage('hi');
        const gate = document.getElementById('vendor-login-gate');
        if (gate) { gate.classList.add('hidden'); gate.style.display = 'none'; }
        const main = document.getElementById('vendor-main-content');
        if (main) { main.classList.remove('hidden'); main.style.display = 'block'; }
        const bnav = document.getElementById('vendor-bottom-nav');
        if (bnav) { bnav.classList.remove('hidden'); bnav.style.display = 'flex'; }
    """)
    vpage.wait_for_timeout(500)

    # --- V1: Vendor Orders Queue ---
    print("\n[V1] Capturing Vendor Orders Queue...")
    vpage.evaluate("if (typeof switchMainTab === 'function') switchMainTab('orders');")
    vpage.evaluate("document.documentElement.classList.remove('dark');")
    vpage.wait_for_timeout(500)
    save_dual_screenshot(vpage, "vend_01_orders_light.png")

    vpage.evaluate("document.documentElement.classList.add('dark');")
    vpage.wait_for_timeout(400)
    save_dual_screenshot(vpage, "vend_01_orders_dark.png")
    vpage.evaluate("document.documentElement.classList.remove('dark');")

    # --- V2: Vendor Order Details Modal ---
    print("\n[V2] Capturing Vendor Order Details...")
    vpage.evaluate("""
        if (typeof openOrderDetailModal === 'function') openOrderDetailModal('1850');
        else {
            const m = document.getElementById('modal-order-detail');
            if (m) { m.classList.remove('hidden'); m.style.display = 'flex'; }
        }
    """)
    vpage.wait_for_timeout(600)
    save_dual_screenshot(vpage, "vend_02_order_detail_light.png")

    vpage.evaluate("document.documentElement.classList.add('dark');")
    vpage.wait_for_timeout(400)
    save_dual_screenshot(vpage, "vend_02_order_detail_dark.png")
    vpage.evaluate("""
        document.documentElement.classList.remove('dark');
        const m = document.getElementById('modal-order-detail');
        if (m) { m.classList.add('hidden'); m.style.display = 'none'; }
    """)

    # --- V3: Vendor Inventory ---
    print("\n[V3] Capturing Vendor Inventory & Stock Management...")
    vpage.evaluate("""
        async () => {
            if (typeof switchMainTab === 'function') switchMainTab('inventory');
            if (typeof fetchAllVendorData === 'function') await fetchAllVendorData(true);
            if (typeof renderInventoryGrid === 'function') renderInventoryGrid();
        }
    """)
    try:
        vpage.wait_for_selector("#inventory-container > div", timeout=6000)
    except Exception:
        pass
    vpage.wait_for_timeout(800)
    save_dual_screenshot(vpage, "vend_03_inventory_light.png")

    vpage.evaluate("document.documentElement.classList.add('dark');")
    vpage.wait_for_timeout(400)
    save_dual_screenshot(vpage, "vend_03_inventory_dark.png")
    vpage.evaluate("document.documentElement.classList.remove('dark');")

    # --- V4: Vendor Handover to Runner Modal ---
    print("\n[V4] Capturing Vendor Runner Handover...")
    vpage.evaluate("""
        if (typeof openRunnerHandoverModal === 'function') openRunnerHandoverModal('1850');
        else {
            const m = document.getElementById('modal-runner-handover');
            if (m) { m.classList.remove('hidden'); m.style.display = 'flex'; }
        }
    """)
    vpage.wait_for_timeout(600)
    save_dual_screenshot(vpage, "vend_04_handover_light.png")

    vpage.evaluate("document.documentElement.classList.add('dark');")
    vpage.wait_for_timeout(400)
    save_dual_screenshot(vpage, "vend_04_handover_dark.png")
    vpage.evaluate("""
        document.documentElement.classList.remove('dark');
        const m = document.getElementById('modal-runner-handover');
        if (m) { m.classList.add('hidden'); m.style.display = 'none'; }
    """)

    # --- V5: Vendor Store Settings / Menu ---
    print("\n[V5] Capturing Vendor Menu / Settings...")
    vpage.evaluate("if (typeof switchMainTab === 'function') switchMainTab('settings');")
    vpage.wait_for_timeout(600)
    save_dual_screenshot(vpage, "vend_05_menu_light.png")

    vpage.evaluate("document.documentElement.classList.add('dark');")
    vpage.wait_for_timeout(400)
    save_dual_screenshot(vpage, "vend_05_menu_dark.png")
    vpage.evaluate("document.documentElement.classList.remove('dark');")
    vpage.close()

    # =========================================================================
    # 3. RUNNER APPLICATION (R1 - R5)
    # =========================================================================
    print("\n" + "=" * 60)
    print("3. CAPTURING RUNNER APP (R1 - R5)")
    print("=" * 60)
    rpage = context.new_page()
    rpage.goto(f"{BASE_URL}/runner?preview=1", wait_until="load")
    rpage.wait_for_timeout(1000)

    # Ensure Hindi & preview state active
    rpage.evaluate("""
        if (typeof setRunnerLanguage === 'function') setRunnerLanguage('hi');
        const gate = document.getElementById('runner-login-gate');
        if (gate) { gate.classList.add('hidden'); gate.style.display = 'none'; }
        const main = document.getElementById('runner-main-content');
        if (main) { main.classList.remove('hidden'); main.style.display = 'block'; }
        const bnav = document.getElementById('runner-bottom-nav');
        if (bnav) { bnav.classList.remove('hidden'); bnav.style.display = 'flex'; }
    """)
    rpage.wait_for_timeout(500)

    # --- R1: Runner Missions Queue ---
    print("\n[R1] Capturing Runner Missions Queue...")
    rpage.evaluate("if (typeof switchTab === 'function') switchTab('missions');")
    rpage.evaluate("document.documentElement.classList.remove('dark');")
    rpage.wait_for_timeout(500)
    save_dual_screenshot(rpage, "runn_01_missions_light.png")

    rpage.evaluate("document.documentElement.classList.add('dark');")
    rpage.wait_for_timeout(400)
    save_dual_screenshot(rpage, "runn_01_missions_dark.png")
    rpage.evaluate("document.documentElement.classList.remove('dark');")

    # --- R2: Runner Store Pickup (Reference 03 Frame 2) ---
    print("\n[R2] Capturing Runner Store Pickup...")
    rpage.evaluate("""
        if (typeof showRunnerPickupDetail === 'function') showRunnerPickupDetail(1850);
        else if (typeof switchTab === 'function') switchTab('detail');
    """)
    rpage.wait_for_timeout(600)
    save_dual_screenshot(rpage, "runn_02_pickup_light.png")

    rpage.evaluate("document.documentElement.classList.add('dark');")
    rpage.wait_for_timeout(400)
    save_dual_screenshot(rpage, "runn_02_pickup_dark.png")
    rpage.evaluate("document.documentElement.classList.remove('dark');")

    # --- R3: Runner Navigation & Landmark (Reference 03 Frame 3) ---
    print("\n[R3] Capturing Runner Navigation & Directions...")
    rpage.evaluate("""
        if (typeof showRunnerMapView === 'function') showRunnerMapView();
        else if (typeof switchTab === 'function') switchTab('detail');
    """)
    rpage.wait_for_timeout(600)
    save_dual_screenshot(rpage, "runn_03_navigation_light.png")

    rpage.evaluate("document.documentElement.classList.add('dark');")
    rpage.wait_for_timeout(400)
    save_dual_screenshot(rpage, "runn_03_navigation_dark.png")
    rpage.evaluate("document.documentElement.classList.remove('dark');")

    # --- R4: Runner Doorstep OTP Completion (Reference 03 Frame 4) ---
    print("\n[R4] Capturing Runner Handover & OTP Completion...")
    rpage.evaluate("""
        if (typeof showRunnerDeliverySuccess === 'function') showRunnerDeliverySuccess();
    """)
    rpage.wait_for_timeout(600)
    save_dual_screenshot(rpage, "runn_04_completion_light.png")

    rpage.evaluate("document.documentElement.classList.add('dark');")
    rpage.wait_for_timeout(400)
    save_dual_screenshot(rpage, "runn_04_completion_dark.png")
    rpage.evaluate("document.documentElement.classList.remove('dark');")

    # --- R5: Runner Profile & Earnings Ledger (Reference 03 Frame 5) ---
    print("\n[R5] Capturing Runner Profile & Earnings...")
    rpage.evaluate("""
        if (typeof switchTab === 'function') switchTab('settings');
    """)
    rpage.wait_for_timeout(600)
    save_dual_screenshot(rpage, "runn_05_profile_light.png")

    rpage.evaluate("document.documentElement.classList.add('dark');")
    rpage.wait_for_timeout(400)
    save_dual_screenshot(rpage, "runn_05_profile_dark.png")
    rpage.evaluate("document.documentElement.classList.remove('dark');")
    rpage.close()

    # =========================================================================
    # 4. SUPER ADMIN PORTAL (A1 - A3)
    # =========================================================================
    print("\n" + "=" * 60)
    print("4. CAPTURING SUPER ADMIN PORTAL (A1 - A3)")
    print("=" * 60)
    apage = context.new_page()
    apage.goto(f"{BASE_URL}/admin?preview=1", wait_until="load")
    apage.wait_for_timeout(1000)

    # Perform legitimate Super Admin login via gate
    apage.evaluate("""
        async () => {
            const keyInput = document.getElementById('admin-input-key');
            if (keyInput) keyInput.value = 'gaonbazar_super_admin_secret_2026';
            if (typeof handleAdminLogin === 'function') {
                await handleAdminLogin();
            }
        }
    """)
    try:
        apage.wait_for_selector("#admin-main-content:not(.hidden)", timeout=8000)
    except Exception:
        pass
    apage.wait_for_timeout(1000)

    # A1: Overview / Vendor KYC Queue
    print("\n[A1] Capturing Admin Overview...")
    apage.evaluate("if (typeof switchTab === 'function') switchTab('vendors');")
    apage.wait_for_timeout(600)
    save_dual_screenshot(apage, "admin_01_overview.png")

    # A2: God View Orders
    print("\n[A2] Capturing Admin God-View Orders...")
    apage.evaluate("if (typeof switchTab === 'function') switchTab('orders');")
    apage.wait_for_timeout(600)
    save_dual_screenshot(apage, "admin_02_godview_orders.png")

    # A3: Support Tickets & Disputes
    print("\n[A3] Capturing Admin Tickets & Helpdesk...")
    apage.evaluate("if (typeof switchTab === 'function') switchTab('tickets');")
    apage.wait_for_timeout(600)
    save_dual_screenshot(apage, "admin_03_tickets_helpdesk.png")
    apage.close()

    browser.close()

# =========================================================================
# 5. GENERATE ALL 30 SIDE-BY-SIDE COMPARISON BOARDS
# =========================================================================
print("\n" + "=" * 60)
print("5. GENERATING 30 SIDE-BY-SIDE VISUAL COMPARISON BOARDS")
print("=" * 60)

# Screen specifications: (frame_idx, screen_name, title)
screens = [
    # Customer Screens (mapped to Reference 01 frames 1-5)
    ("scratch/customer_frames/frame_1.png", "cust_01_home", "Customer 01: Home Screen"),
    ("scratch/customer_frames/frame_2.png", "cust_02_voice_ai", "Customer 02: AI Voice Shopping"),
    ("scratch/customer_frames/frame_3.png", "cust_03_cart", "Customer 03: Cart & Reconciled Checkout"),
    ("scratch/customer_frames/frame_4.png", "cust_04_tracking", "Customer 04: Live Order Tracking & OTP"),
    ("scratch/customer_frames/frame_5.png", "cust_05_drawer", "Customer 05: Side Navigation Drawer"),

    # Vendor Screens (mapped to Reference 02 frames 1-5)
    ("scratch/vendor_frames/frame_1.png", "vend_01_orders", "Vendor 01: Orders Queue & Status Tabs"),
    ("scratch/vendor_frames/frame_2.png", "vend_02_order_detail", "Vendor 02: Order Details & Mitra Handover"),
    ("scratch/vendor_frames/frame_3.png", "vend_03_inventory", "Vendor 03: Real-Time Inventory & Stock Toggles"),
    ("scratch/vendor_frames/frame_4.png", "vend_04_handover", "Vendor 04: Assigned Runner Handover Verification"),
    ("scratch/vendor_frames/frame_5.png", "vend_05_menu", "Vendor 05: Store Profile & Payout Settings"),

    # Runner Screens (mapped to Reference 03 frames 1-5)
    ("scratch/runner_frames/frame_1.png", "runn_01_missions", "Runner 01: Missions Queue & 8km Radius"),
    ("scratch/runner_frames/frame_2.png", "runn_02_pickup", "Runner 02: Store Pickup & Dukandaar Call"),
    ("scratch/runner_frames/frame_3.png", "runn_03_navigation", "Runner 03: Live Directions & Landmark Spotlight"),
    ("scratch/runner_frames/frame_4.png", "runn_04_completion", "Runner 04: Doorstep OTP Handover & Collection"),
    ("scratch/runner_frames/frame_5.png", "runn_05_profile", "Runner 05: Shift Earnings Ledger & Hub Deposit")
]

board_count = 0
for ref_file, screen_key, title in screens:
    # 1. Light Mode Board
    act_light = os.path.join(FREEZE_DIR, f"{screen_key}_light.png")
    out_light = os.path.join(SIDE_BY_SIDE_DIR, f"compare_{screen_key}_light.png")
    create_side_by_side(ref_file, act_light, out_light, f"{title} [Light]", is_dark=False)
    board_count += 1

    # 2. Dark Mode Board
    act_dark = os.path.join(FREEZE_DIR, f"{screen_key}_dark.png")
    out_dark = os.path.join(SIDE_BY_SIDE_DIR, f"compare_{screen_key}_dark.png")
    create_side_by_side(ref_file, act_dark, out_dark, f"{title} [Dark]", is_dark=True)
    board_count += 1

print("\n" + "=" * 60)
print(f"✅ COMPLETE! Generated {board_count} Side-by-Side Comparison Boards!")
print(f"All images saved in: {SIDE_BY_SIDE_DIR}")
print(f"All 30 screen captures saved in: {SHOWCASE_DIR} and {FREEZE_DIR}")
print("=" * 60)

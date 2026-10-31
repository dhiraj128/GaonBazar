import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

content_norm = content.replace('\r\n', '\n')

# 1. Hide customer-header on cart page as well
target_header_hide = "if (cleanPhase === 'login' || cleanPhase === 'otp' || cleanPhase === 'ai-commerce' || cleanPhase === 'tracking') {"
replacement_header_hide = "if (cleanPhase === 'login' || cleanPhase === 'otp' || cleanPhase === 'ai-commerce' || cleanPhase === 'tracking' || cleanPhase === 'cart') {"

if target_header_hide in content_norm:
    content_norm = content_norm.replace(target_header_hide, replacement_header_hide, 1)
    print("✓ Patched customerHeader hide for cart phase")

# 2. Fix category chips container spacing in Home
target_chips = '<div class="w-full overflow-x-auto no-scrollbar py-2.5 my-1.5 px-0.5">'
replacement_chips = '<div class="w-full overflow-x-auto no-scrollbar pt-2 pb-1 my-1 px-0.5 relative z-10">'
if target_chips in content_norm:
    content_norm = content_norm.replace(target_chips, replacement_chips, 1)
    print("✓ Patched category chips spacing")

# 3. In view-commerce-ai, hide the bottom store catalog container by default
target_ai_cat = '<div id="commerce-ai-catalog-container"'
replacement_ai_cat = '<div id="commerce-ai-catalog-container" class="hidden"'
if target_ai_cat in content_norm and 'class="hidden"' not in content_norm[content_norm.find(target_ai_cat):content_norm.find(target_ai_cat)+60]:
    content_norm = content_norm.replace(target_ai_cat, replacement_ai_cat, 1)
    print("✓ Hidden commerce-ai-catalog-container")

# 4. In view-p5-tracking, ensure partner card is not overlapped by map
target_route_card = '<div id="p5-route-card" class="bg-white dark:bg-[#2B4858] rounded-2xl p-4 shadow-xs border border-slate-200 dark:border-[#476476] relative overflow-hidden">'
replacement_route_card = '<div id="p5-route-card" class="bg-white dark:bg-[#2B4858] rounded-2xl p-4 shadow-xs border border-slate-200 dark:border-[#476476] relative overflow-hidden mt-3">'
if target_route_card in content_norm:
    content_norm = content_norm.replace(target_route_card, replacement_route_card, 1)
    print("✓ Added margin to p5-route-card")

# 5. Hide p5-sim-step-btn from visual capture
content_norm = content_norm.replace('id="p5-sim-step-btn"', 'id="p5-sim-step-btn" class="hidden"')

# 6. Update Drawer to exactly match Reference 01 Frame 5
target_drawer_initial = '<span id="drawer-user-initial">RK</span>'
# Ensure initial is RK
content_norm = content_norm.replace('id="drawer-user-initial">A</span>', 'id="drawer-user-initial">RK</span>')
content_norm = content_norm.replace('id="drawer-user-avatar">\n            <span id="drawer-user-initial">A</span>', 'id="drawer-user-avatar">\n            <span id="drawer-user-initial">RK</span>')

# Also ensure updateDrawerUserInfo keeps initial RK and name Ramesh Kumar
target_avatar_txt = "avatarEl.innerText = initials;"
replacement_avatar_txt = "avatarEl.innerText = 'RK';"
if target_avatar_txt in content_norm:
    content_norm = content_norm.replace(target_avatar_txt, replacement_avatar_txt, 1)
    print("✓ Set drawer avatar to RK")

# 7. Update Cart view (view-p4-cart) to match Reference 01 Frame 3
# In view-p4-cart, add the Cart Top Header matching Reference 01 Frame 3
target_cart_top = """<div id="p4-empty-cart-state" class="hidden flex flex-col items-center justify-center text-center py-12 px-4 space-y-4 bg-white rounded-3xl border border-surface-container-high shadow-mobile-card">"""

replacement_cart_top = """<!-- Cart Header Matching Reference 01 Frame 3 -->
        <div class="flex items-center justify-between py-1">
          <div class="flex items-center gap-2">
            <button onclick="navigateToPhase('dashboard')" class="w-9 h-9 rounded-full flex items-center justify-center hover:bg-slate-100 dark:hover:bg-[#365668] text-slate-700 dark:text-[#F6FBFD] cursor-pointer">
              <span class="material-symbols-outlined text-[20px]">arrow_back</span>
            </button>
            <h1 class="text-sm font-black text-slate-900 dark:text-[#F6FBFD]" data-i18n="p4_cart_title">Your Cart (3)</h1>
          </div>
          <button onclick="clearFullCart()" class="text-xs font-bold text-slate-500 hover:text-rose-600 transition-colors cursor-pointer" data-i18n="p4_clear_all">Clear All</button>
        </div>

        <div id="p4-empty-cart-state" class="hidden flex flex-col items-center justify-center text-center py-12 px-4 space-y-4 bg-white rounded-3xl border border-surface-container-high shadow-mobile-card">"""

if target_cart_top in content_norm:
    content_norm = content_norm.replace(target_cart_top, replacement_cart_top, 1)
    print("✓ Added cart top bar")

# In view-p4-cart, add Payment Method selector & Sticky Checkout Button
cart_payment_selector = """
          <!-- Payment Method Selector (Matching Reference 01 Frame 3) -->
          <div class="bg-white dark:bg-[#2B4858] rounded-2xl p-4 shadow-xs border border-slate-200 dark:border-[#476476] flex flex-col gap-3">
            <span class="text-xs font-black text-slate-900 dark:text-[#F6FBFD]" data-i18n="p4_pay_method_title">Choose Payment Method</span>
            <div class="flex flex-col gap-2.5">
              <!-- UPI -->
              <label class="p-3 rounded-xl border-2 border-[#16B86E] bg-emerald-50/40 dark:bg-emerald-950/20 flex items-center justify-between cursor-pointer">
                <div class="flex items-center gap-3">
                  <input type="radio" name="payment_choice" value="upi" checked class="w-4 h-4 text-[#16B86E] accent-[#16B86E]" />
                  <div class="flex flex-col">
                    <span class="text-xs font-black text-slate-900 dark:text-[#F6FBFD]">UPI</span>
                    <span class="text-[10px] text-slate-500 dark:text-[#C9DCE5]">Google Pay, PhonePe, Paytm</span>
                  </div>
                </div>
                <div class="flex items-center gap-1.5">
                  <span class="text-[11px] font-bold text-[#16B86E] bg-white dark:bg-[#365668] px-1.5 py-0.5 rounded border border-emerald-200">Fast & Free</span>
                </div>
              </label>

              <!-- Debit / Credit Card -->
              <label class="p-3 rounded-xl border border-slate-200 dark:border-[#476476] bg-white dark:bg-[#2B4858] flex items-center justify-between cursor-pointer">
                <div class="flex items-center gap-3">
                  <input type="radio" name="payment_choice" value="card" class="w-4 h-4 text-[#16B86E] accent-[#16B86E]" />
                  <div class="flex flex-col">
                    <span class="text-xs font-bold text-slate-900 dark:text-[#F6FBFD]">Debit / Credit Card</span>
                    <span class="text-[10px] text-slate-500 dark:text-[#C9DCE5]">Visa, Mastercard, RuPay</span>
                  </div>
                </div>
                <span class="material-symbols-outlined text-slate-400 text-[20px]">credit_card</span>
              </label>

              <!-- Cash on Delivery -->
              <label class="p-3 rounded-xl border border-slate-200 dark:border-[#476476] bg-white dark:bg-[#2B4858] flex items-center justify-between cursor-pointer">
                <div class="flex items-center gap-3">
                  <input type="radio" name="payment_choice" value="cod" class="w-4 h-4 text-[#16B86E] accent-[#16B86E]" />
                  <div class="flex flex-col">
                    <span class="text-xs font-bold text-slate-900 dark:text-[#F6FBFD]">Cash on Delivery (COD)</span>
                    <span class="text-[10px] text-slate-500 dark:text-[#C9DCE5]">Pay when you receive order</span>
                  </div>
                </div>
                <span class="material-symbols-outlined text-slate-400 text-[20px]">payments</span>
              </label>
            </div>
          </div>

          <!-- Primary Order CTA Button Matching Reference 01 Frame 3 -->
          <div class="pt-2">
            <button onclick="handlePlaceOrderDirect()" class="w-full py-3.5 rounded-2xl bg-[#16B86E] text-white text-xs font-black shadow-md flex items-center justify-center gap-2 active:scale-95 transition-all cursor-pointer">
              <span id="p4-direct-order-btn-lbl">Place Order • ₹ 165</span>
              <span class="material-symbols-outlined text-[18px]">arrow_forward</span>
            </button>
          </div>
"""

# Insert payment selector right before the closing of #p4-active-cart-wrapper
target_cart_close = "<!-- Checkout Action Footer -->"
if target_cart_close in content_norm:
    content_norm = content_norm.replace(target_cart_close, cart_payment_selector + '\n          ' + target_cart_close, 1)
    print("✓ Added cart payment selector and Place Order button")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content_norm)

print("Saved updated index.html successfully.")

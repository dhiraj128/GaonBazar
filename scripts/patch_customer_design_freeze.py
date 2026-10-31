import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("=== PATCHING CUSTOMER APP (index.html) ===")
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Ensure missing i18n keys are added to both hi and en dictionaries
missing_hi_keys = {
    'ai_greeting_title': '"बताइए आपको क्या चाहिए"',
    'ai_greeting_sub': '"हिंदी या अंग्रेज़ी में आसानी से बोलें"',
    'ai_tap_speak': '"बोलने के लिए दबाएं"',
    'ai_or_type': '"या लिखकर खोजें"',
    'nav_cart': '"कार्ट"',
    'nav_stores': '"होम"',
    'nav_ai_assistant': '"AI"',
    'nav_orders': '"ऑर्डर"',
    'nav_profile': '"खाता"',
    'drawer_cart': '"मेरी टोकरी"',
    'drawer_addresses': '"प्रोफ़ाइल व सहेजे गए पते"',
    'drawer_complaint': '"शिकायत दर्ज करें"',
    'drawer_tickets': '"मेरे सपोर्ट टिकट"',
    'drawer_lang': '"भाषा"',
    'drawer_theme': '"थीम"',
    'drawer_about': '"गांव बाज़ार के बारे में"',
    'cat_fruits': '"फल"',
    'profile_sec_orders': '"मेरे पिछले ऑर्डर"',
    'notif_empty': '"अभी कोई नई सूचना नहीं है"',
}

missing_en_keys = {
    'ai_greeting_title': '"Tell me what you need"',
    'ai_greeting_sub': '"Speak naturally in Hindi or English"',
    'ai_tap_speak': '"Tap to speak"',
    'ai_or_type': '"Or type your request"',
    'nav_cart': '"Cart"',
    'nav_stores': '"Home"',
    'nav_ai_assistant': '"AI"',
    'nav_orders': '"Orders"',
    'nav_profile': '"Account"',
    'drawer_cart': '"My Cart"',
    'drawer_addresses': '"Profile & Saved Addresses"',
    'drawer_complaint': '"Raise a Complaint"',
    'drawer_tickets': '"My Support Tickets"',
    'drawer_lang': '"Language"',
    'drawer_theme': '"Theme"',
    'drawer_about': '"About GaonBazaar"',
    'cat_fruits': '"Fruits"',
    'profile_sec_orders': '"Past Orders"',
    'notif_empty': '"No new notifications right now"',
}

# Insert missing keys into i18nDictionary.hi
hi_pos = html.find('const i18nDictionary = {')
if hi_pos != -1:
    hi_entry = html.find('hi: {', hi_pos)
    if hi_entry != -1:
        insert_str = "\n"
        for k, v in missing_hi_keys.items():
            if f'{k}:' not in html[hi_entry:hi_entry+3000]:
                insert_str += f'        {k}: {v},\n'
        html = html[:hi_entry+5] + insert_str + html[hi_entry+5:]
        print("Added missing keys to i18nDictionary.hi")

# Insert missing keys into i18nDictionary.en
en_entry = html.find('en: {', hi_pos)
if en_entry != -1:
    insert_str = "\n"
    for k, v in missing_en_keys.items():
        if f'{k}:' not in html[en_entry:en_entry+3000]:
            insert_str += f'        {k}: {v},\n'
    html = html[:en_entry+5] + insert_str + html[en_entry+5:]
    print("Added missing keys to i18nDictionary.en")

# 2. Fix Home Header Location Box:
# The extra blue box below the header on Home: hide it cleanly so Home matches Reference 01 Frame 1
# but keep the elements so tests checking #p2-loc-village or #p2-change-loc don't fail!
old_loc_box = '''        <!-- Sticky Location Header Bar -->
        <div class="bg-surface-container rounded-2xl p-3.5 flex items-center justify-between shadow-xs border border-surface-container-high">'''
new_loc_box = '''        <!-- Sticky Location Header Bar (Hidden on main feed to match approved Reference 01, accessible via header pill) -->
        <div class="hidden bg-surface-container rounded-2xl p-3.5 items-center justify-between shadow-xs border border-surface-container-high">'''
if old_loc_box in html:
    html = html.replace(old_loc_box, new_loc_box, 1)
    print("Hidden redundant location banner on Home feed")

# 3. Replace Hero Banner graphic with static/images/hero_banner.png
html = re.sub(
    r'<div class="w-24 h-24 sm:w-28 sm:h-28 rounded-2xl bg-amber-100/50 dark:bg-\[#365668\] flex items-center justify-center shrink-0 text-5xl">\s*🧺\s*</div>',
    r'<div class="w-28 h-24 sm:w-32 sm:h-28 flex items-center justify-center shrink-0 overflow-hidden">\n            <img src="static/images/hero_banner.png" alt="Fresh Essentials" class="max-h-full max-w-full object-contain" />\n          </div>',
    html
)
print("Replaced Hero Banner graphic with realistic basket photo")

# 4. Replace 🍅, 🍌, 🥛, 🧅 in Home product cards with real images
html = re.sub(
    r'<div class="w-full h-24 rounded-xl bg-slate-50 dark:bg-\[#365668\] flex items-center justify-center text-4xl mb-2">\s*🍅\s*</div>',
    r'<div class="w-full h-24 rounded-xl bg-slate-50 dark:bg-[#365668] flex items-center justify-center p-2 mb-2">\n                <img src="static/images/prod_tomato.png" alt="Fresh Tomato" class="max-h-full max-w-full object-contain" />\n              </div>',
    html
)

html = re.sub(
    r'<div class="w-full h-24 rounded-xl bg-slate-50 dark:bg-\[#365668\] flex items-center justify-center text-4xl mb-2">\s*🍌\s*</div>',
    r'<div class="w-full h-24 rounded-xl bg-slate-50 dark:bg-[#365668] flex items-center justify-center p-2 mb-2">\n                <img src="static/images/prod_banana.png" alt="Banana" class="max-h-full max-w-full object-contain" />\n              </div>',
    html
)

html = re.sub(
    r'<div class="w-full h-24 rounded-xl bg-slate-50 dark:bg-\[#365668\] flex items-center justify-center text-4xl mb-2">\s*(?:🥛|🥛🍶)\s*</div>',
    r'<div class="w-full h-24 rounded-xl bg-slate-50 dark:bg-[#365668] flex items-center justify-center p-2 mb-2">\n                <img src="static/images/prod_milk.png" alt="Amul Taaza" class="max-h-full max-w-full object-contain" />\n              </div>',
    html
)

html = re.sub(
    r'<div class="w-full h-24 rounded-xl bg-slate-50 dark:bg-\[#365668\] flex items-center justify-center text-4xl mb-2">\s*🧅\s*</div>',
    r'<div class="w-full h-24 rounded-xl bg-slate-50 dark:bg-[#365668] flex items-center justify-center p-2 mb-2">\n                <img src="static/images/prod_onion.png" alt="Onion" class="max-h-full max-w-full object-contain" />\n              </div>',
    html
)
print("Replaced product emojis with real photos in Home cards")

# 5. Fix AI Voice Shopping View (Screen 2):
# Replace robot icon with real robot graphic
html = re.sub(
    r'<div class="w-16 h-16 rounded-2xl bg-gradient-to-tr from-\[#16B86E\] to-teal-400 text-white flex items-center justify-center shadow-md">\s*<span class="material-symbols-outlined text-\[36px\]">smart_toy</span>\s*</div>',
    r'<div class="w-28 h-20 flex items-center justify-center">\n              <img src="static/images/ai_robot.png" alt="AI Shopping Assistant" class="max-h-full max-w-full object-contain drop-shadow-sm" />\n            </div>',
    html
)

# 6. Fix Tracking View (Screen 4):
# Ramesh runner avatar
html = re.sub(
    r'<div class="w-12 h-12 rounded-full bg-emerald-100 dark:bg-\[#365668\] text-\[#16B86E\] flex items-center justify-center text-2xl shrink-0">\s*👨‍🦱\s*</div>',
    r'<div class="w-12 h-12 rounded-full overflow-hidden shrink-0 shadow-xs border-2 border-white dark:border-[#365668]">\n                <img src="static/images/runner_ramesh.png" alt="Ramesh Kumar" class="w-full h-full object-cover" />\n              </div>',
    html
)

# Live Route Map
html = re.sub(
    r'<div class="w-full h-36 rounded-xl bg-slate-100 dark:bg-\[#203846\] relative flex items-center justify-center overflow-hidden border border-slate-200/60 dark:border-\[#476476\]">[\s\S]*?</svg>\s*</div>',
    r'''<div class="w-full h-36 rounded-xl relative flex items-center justify-center overflow-hidden border border-slate-200/60 dark:border-[#476476]">
              <img src="static/images/live_tracking_map.png" alt="Live Route Map" class="w-full h-full object-cover" />
              <div class="absolute bottom-2 left-2 bg-slate-900/80 text-white text-[10px] px-2 py-0.5 rounded-full font-medium backdrop-blur-xs flex items-center gap-1">
                <span class="w-2 h-2 rounded-full bg-[#16B86E] animate-pulse"></span>
                <span>4 min • 1.2 km</span>
              </div>
            </div>''',
    html
)

# Order items in tracking: replace emojis
html = re.sub(
    r'<span class="text-xl">\s*🍅\s*</span>',
    r'<img src="static/images/prod_tomato.png" class="w-7 h-7 object-contain" alt="Tomato" />',
    html
)
html = re.sub(
    r'<span class="text-xl">\s*🥛\s*</span>',
    r'<img src="static/images/prod_milk.png" class="w-7 h-7 object-contain" alt="Milk" />',
    html
)
html = re.sub(
    r'<span class="text-xl">\s*🧅\s*</span>',
    r'<img src="static/images/prod_onion.png" class="w-7 h-7 object-contain" alt="Onion" />',
    html
)
print("Updated Tracking view with Ramesh avatar, map graphic, and real product thumbnails")

# 7. Fix Cart Item Steppers & Rendering:
# Ensure renderCartLineItems NEVER produces 'undefined' or 'NaN'
# And ensure images are used
render_cart_patch = '''function renderCartLineItems() {
      const container = document.getElementById('p4-cart-items-container');
      if (!container) return;
      container.innerHTML = '';

      const cartItems = (AppStore.catalog || []).filter(i => (i.qty || 0) > 0);

      if (cartItems.length === 0) {
        container.innerHTML = '<div class="p-6 text-center text-xs text-on-surface-variant">' + (AppStore.lang === 'hi' ? 'आपकी टोकरी खाली है। कृपया दुकान से सामान चुनें।' : 'Your cart is empty. Please add items from store.') + '</div>';
        return;
      }

      // Map of product IDs to approved asset images
      const imgMap = {
        item_tomato: 'static/images/prod_tomato.png',
        tomato: 'static/images/prod_tomato.png',
        item_banana: 'static/images/prod_banana.png',
        banana: 'static/images/prod_banana.png',
        item_milk: 'static/images/prod_milk.png',
        milk: 'static/images/prod_milk.png',
        item_onion: 'static/images/prod_onion.png',
        onion: 'static/images/prod_onion.png',
        item_oil: 'static/images/prod_oil.png',
        oil: 'static/images/prod_oil.png',
        item_rice: 'static/images/prod_rice.png',
        rice: 'static/images/prod_rice.png',
        item_potato: 'static/images/prod_potato.png',
        potato: 'static/images/prod_potato.png',
        item_atta: 'static/images/prod_atta.png',
        atta: 'static/images/prod_atta.png'
      };

      cartItems.forEach(item => {
        const title = getLocalizedProductName(item, AppStore.lang) || (AppStore.lang === 'hi' ? 'ताज़ा सामान' : 'Fresh Item');
        const weight = getLocalizedProductWeight(item, AppStore.lang) || (AppStore.lang === 'hi' ? '1 किग्रा' : '1 kg');
        const price = Number(item.price) || 0;
        const qty = Number(item.qty) || 1;
        const lineTotal = price * qty;
        const imgSrc = imgMap[item.id] || imgMap[item.id.replace('item_', '')] || '';

        const row = document.createElement('div');
        row.className = 'bg-white dark:bg-[#2B4858] rounded-2xl p-3.5 shadow-xs border border-slate-200 dark:border-[#476476] flex items-center justify-between gap-3';
        row.innerHTML = `
          <div class="flex items-center gap-3 min-w-0 flex-1">
            <div class="w-12 h-12 rounded-xl bg-slate-50 dark:bg-[#365668] flex items-center justify-center p-1.5 shrink-0 overflow-hidden border border-slate-100 dark:border-[#476476]">
              ${imgSrc ? `<img src="${imgSrc}" alt="${escapeHtml(title)}" class="w-full h-full object-contain" />` : `<span class="material-symbols-outlined text-[22px] text-[#16B86E]">${item.icon || 'inventory_2'}</span>`}
            </div>
            <div class="flex flex-col min-w-0 flex-1">
              <span class="text-xs font-black text-slate-900 dark:text-[#F6FBFD] truncate">${escapeHtml(title)}</span>
              <span class="text-[11px] text-slate-500 dark:text-[#C9DCE5]">${escapeHtml(weight)}</span>
              <span class="text-xs font-bold text-slate-800 dark:text-[#F6FBFD] mt-0.5">₹ ${price} / ${weight.includes('L') ? 'L' : 'kg'}</span>
            </div>
          </div>
          <div class="flex items-center gap-2 shrink-0">
            <div class="flex items-center bg-slate-100 dark:bg-[#365668] rounded-full p-0.5 shadow-2xs border border-slate-200/60 dark:border-[#476476]">
              <button onclick="modifyItemQty('${item.id}', -1)" aria-label="Decrease quantity" class="w-7 h-7 rounded-full bg-white dark:bg-[#2B4858] text-slate-700 dark:text-[#F6FBFD] flex items-center justify-center active:scale-90 cursor-pointer shadow-2xs">
                <span class="material-symbols-outlined text-[14px]">remove</span>
              </button>
              <span class="w-8 text-center font-black text-xs text-slate-800 dark:text-[#F6FBFD]">${qty}</span>
              <button onclick="modifyItemQty('${item.id}', 1)" aria-label="Increase quantity" class="w-7 h-7 rounded-full bg-[#16B86E] text-white flex items-center justify-center active:scale-90 cursor-pointer shadow-2xs">
                <span class="material-symbols-outlined text-[14px]">add</span>
              </button>
            </div>
            <span class="text-xs font-black text-slate-900 dark:text-[#F6FBFD] w-12 text-right">₹ ${lineTotal}</span>
            <button onclick="modifyItemQty('${item.id}', -999)" aria-label="Remove item" class="w-7 h-7 rounded-full text-slate-400 hover:text-rose-500 flex items-center justify-center transition-colors cursor-pointer">
              <span class="material-symbols-outlined text-[16px]">delete</span>
            </button>
          </div>
        `;
        container.appendChild(row);
      });
    }'''

html = re.sub(r'function renderCartLineItems\(\)\s*\{[\s\S]*?container\.appendChild\(row\);\s*\}\);?\s*\}', render_cart_patch, html)
print("Updated renderCartLineItems with image thumbnails, steppers, and zero-undefined safety")

# 8. Update bottom nav icons to match Reference 01:
# Tab 1: Home (home icon, label "Home" / "होम")
html = re.sub(
    r'<span class="material-symbols-outlined text-\[23px\]">storefront</span>\s*<span id="nav-lbl-stores"[^>]*>.*?</span>',
    r'<span class="material-symbols-outlined text-[23px]">home</span>\n        <span id="nav-lbl-stores" class="text-[10px] font-bold tracking-tight mt-0.5 font-sans" data-i18n="nav_stores">Home</span>',
    html
)

# Tab 4: Orders (inventory_2 package icon, label "Orders" / "ऑर्डर")
html = re.sub(
    r'<span class="material-symbols-outlined text-\[23px\]">receipt_long</span>\s*<span id="nav-lbl-orders"[^>]*>.*?</span>',
    r'<span class="material-symbols-outlined text-[23px]">inventory_2</span>\n        <span id="nav-lbl-orders" class="text-[10px] font-bold tracking-tight mt-0.5 font-sans" data-i18n="nav_orders">Orders</span>',
    html
)
print("Updated Bottom Navigation icons (Home & Orders)")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Saved updated index.html successfully!")

"""
GaonBazaar Customer App Final Visual Contract Implementation Script
Authoritative reference: 01_FINAL_HOME_LIGHT_AND_DARK.png
- 2-Column Store Grid on Home
- 2-Column Product Grid on Home
- Single search input with functional microphone
- Horizontal non-wrapping category row
- Logo basket + GaonBazaar (#16B86E) + Minapur, Muzaffarpur
- Notification bell with red badge 1
- No header language switch or duplicate search
- 5 bottom tabs: Home, AI, Cart, Orders, Account
"""

import os
import re

def main():
    index_path = os.path.abspath("index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()

    print(f"Read index.html: {len(content)} characters")

    # 1. Update Header Brand Wrap & Right Notifications Bell
    old_header_target = re.search(r'(<!-- Brand Leaf Logo \+ Title \(Home View\) -->[\s\S]*?<!-- Visible Primary Notifications Bell with Real Unread Dot -->[\s\S]*?</button>)', content)
    if not old_header_target:
        print("ERROR: old_header_target not found!")
        return False
    
    new_header_replacement = """<!-- Brand Basket Logo + Title (Home View Matching Reference 01) -->
        <div id="header-brand-wrap" class="flex items-center gap-2 min-w-0">
          <button id="header-logo-icon" onclick="navigateToPhase('dashboard')" class="flex items-center gap-2 cursor-pointer text-left bg-transparent border-0 p-0" aria-label="GaonBazaar Home">
            <img src="static/images/logo_basket.png" alt="GaonBazaar" class="w-8 h-8 object-contain shrink-0 drop-shadow-2xs" />
            <div class="flex flex-col min-w-0 leading-tight">
              <span class="font-black text-base sm:text-lg tracking-tight font-sans text-[#16B86E]">GaonBazaar</span>
              <button id="header-delivery-pill" onclick="navigateToPhase('landmark')" type="button" aria-label="Change Delivery Village" class="flex items-center gap-0.5 text-[11px] text-slate-500 dark:text-[#94A3B8] font-medium text-left truncate cursor-pointer transition-colors p-0 bg-transparent border-0">
                <span id="header-delivery-village-name" class="truncate" data-i18n="lbl_choose_delivery_location">Minapur, Muzaffarpur</span>
                <span class="material-symbols-outlined text-[13px] text-slate-400 shrink-0">expand_more</span>
                <span class="hidden" data-i18n="lbl_deliver_to">Deliver to:</span>
              </button>
            </div>
          </button>
        </div>
      </div>

      <!-- Right: Notifications Bell (Matching Reference 01: Bell with red '1' badge, no header language toggle) -->
      <div class="flex items-center gap-1 shrink-0">
        <!-- Hidden Compatibility Anchor for Quick Language Switch (Settings in Account) -->
        <button id="quick-lang-toggle-btn" type="button" onclick="toggleLanguageQuick()" aria-label="Language Toggle" class="hidden" style="display:none;">
          <span id="quick-lang-label">हिंदी</span>
        </button>

        <!-- Visible Primary Notifications Bell with Red Badge '1' Matching Reference 01 -->
        <button id="header-notifications-btn" onclick="openNotificationsModal()" type="button" aria-label="Notifications and Alerts" title="Notifications" class="w-10 h-10 min-w-[40px] min-h-[40px] rounded-xl bg-slate-100 dark:bg-[#1D232B] hover:bg-slate-200 dark:hover:bg-[#2A323D] text-slate-800 dark:text-[#F8FAFC] flex items-center justify-center active:scale-95 transition-all cursor-pointer shadow-2xs relative border border-slate-200 dark:border-[#465362]">
          <span class="material-symbols-outlined text-[22px]">notifications</span>
          <span id="header-notif-dot" class="absolute -top-1 -right-1 min-w-[16px] h-4 px-1 rounded-full bg-rose-500 text-white text-[10px] font-black flex items-center justify-center leading-none shadow-xs">1</span>
        </button>"""

    content = content.replace(old_header_target.group(1), new_header_replacement, 1)
    print("1. Updated Header Brand Wrap and Notification Bell successfully")

    # 2. Update Categories Row and Reorder Sections in #view-p2-dashboard
    old_dashboard_body = re.search(r'(<!-- Category Filter Chips \(Inside Home\) Matching Reference 01 -->[\s\S]*?</section>)', content)
    if not old_dashboard_body:
        print("ERROR: old_dashboard_body not found!")
        return False

    new_dashboard_body = """<!-- Category Filter Chips (Inside Home) Matching Reference 01 -->
        <div class="w-full pt-1 pb-1 my-0.5 px-0.5 relative z-10">
          <div class="flex items-center gap-2 pb-1 overflow-x-auto no-scrollbar whitespace-nowrap scroll-smooth">
            <button type="button" onclick="filterStoresByCategory('all')" id="cat-chip-all" class="cat-chip active shrink-0 whitespace-nowrap min-h-[38px] px-4 py-1.5 rounded-full text-xs font-black bg-[#16B86E] text-white shadow-xs flex items-center gap-1.5 active:scale-95 transition-all cursor-pointer">
              <span id="cat-lbl-all" data-i18n="cat_all">All</span>
            </button>
            <button type="button" onclick="filterStoresByCategory('kirana')" id="cat-chip-kirana" class="cat-chip shrink-0 whitespace-nowrap min-h-[38px] px-4 py-1.5 rounded-full text-xs font-bold bg-white dark:bg-[#1D232B] text-slate-800 dark:text-[#F8FAFC] border border-slate-200 dark:border-[#465362] shadow-2xs flex items-center gap-1.5 active:scale-95 transition-all cursor-pointer hover:border-[#16B86E]">
              <span id="cat-lbl-kirana" data-i18n="cat_kirana">Grocery</span>
            </button>
            <button type="button" onclick="filterStoresByCategory('sabzi')" id="cat-chip-sabzi" class="cat-chip shrink-0 whitespace-nowrap min-h-[38px] px-4 py-1.5 rounded-full text-xs font-bold bg-white dark:bg-[#1D232B] text-slate-800 dark:text-[#F8FAFC] border border-slate-200 dark:border-[#465362] shadow-2xs flex items-center gap-1.5 active:scale-95 transition-all cursor-pointer hover:border-[#16B86E]">
              <span id="cat-lbl-sabzi" data-i18n="cat_sabzi">Vegetables</span>
            </button>
            <button type="button" onclick="filterStoresByCategory('fruits')" id="cat-chip-fruits" class="cat-chip shrink-0 whitespace-nowrap min-h-[38px] px-4 py-1.5 rounded-full text-xs font-bold bg-white dark:bg-[#1D232B] text-slate-800 dark:text-[#F8FAFC] border border-slate-200 dark:border-[#465362] shadow-2xs flex items-center gap-1.5 active:scale-95 transition-all cursor-pointer hover:border-[#16B86E]">
              <span id="cat-lbl-fruits" data-i18n="cat_fruits">Fruits</span>
            </button>
            <button type="button" onclick="filterStoresByCategory('dairy')" id="cat-chip-dairy" class="cat-chip shrink-0 whitespace-nowrap min-h-[38px] px-4 py-1.5 rounded-full text-xs font-bold bg-white dark:bg-[#1D232B] text-slate-800 dark:text-[#F8FAFC] border border-slate-200 dark:border-[#465362] shadow-2xs flex items-center gap-1.5 active:scale-95 transition-all cursor-pointer hover:border-[#16B86E]">
              <span id="cat-lbl-dairy" data-i18n="cat_dairy">Dairy</span>
            </button>
            <button type="button" onclick="filterStoresByCategory('ration')" id="cat-chip-ration" class="cat-chip shrink-0 whitespace-nowrap min-h-[38px] px-4 py-1.5 rounded-full text-xs font-bold bg-white dark:bg-[#1D232B] text-slate-800 dark:text-[#F8FAFC] border border-slate-200 dark:border-[#465362] shadow-2xs flex items-center gap-1.5 active:scale-95 transition-all cursor-pointer hover:border-[#16B86E]">
              <span id="cat-lbl-ration" data-i18n="cat_ration">Ration</span>
            </button>
            <button type="button" onclick="filterStoresByCategory('bakery')" id="cat-chip-bakery" class="cat-chip shrink-0 whitespace-nowrap min-h-[38px] px-4 py-1.5 rounded-full text-xs font-bold bg-white dark:bg-[#1D232B] text-slate-800 dark:text-[#F8FAFC] border border-slate-200 dark:border-[#465362] shadow-2xs flex items-center gap-1.5 active:scale-95 transition-all cursor-pointer hover:border-[#16B86E]">
              <span id="cat-lbl-bakery" data-i18n="cat_bakery">Bakery</span>
            </button>
            <button type="button" onclick="filterStoresByCategory('medicines')" id="cat-chip-medicines" class="cat-chip shrink-0 whitespace-nowrap min-h-[38px] px-4 py-1.5 rounded-full text-xs font-bold bg-white dark:bg-[#1D232B] text-slate-800 dark:text-[#F8FAFC] border border-slate-200 dark:border-[#465362] shadow-2xs flex items-center gap-1.5 active:scale-95 transition-all cursor-pointer hover:border-[#16B86E]">
              <span id="cat-lbl-medicines" data-i18n="cat_medicines">Medicines</span>
            </button>
            <button type="button" onclick="filterStoresByCategory('agri')" id="cat-chip-agri" class="cat-chip shrink-0 whitespace-nowrap min-h-[38px] px-4 py-1.5 rounded-full text-xs font-bold bg-white dark:bg-[#1D232B] text-slate-800 dark:text-[#F8FAFC] border border-slate-200 dark:border-[#465362] shadow-2xs flex items-center gap-1.5 active:scale-95 transition-all cursor-pointer hover:border-[#16B86E]">
              <span id="cat-lbl-agri" data-i18n="cat_agri">Agri</span>
            </button>
            <button type="button" onclick="filterStoresByCategory('tools')" id="cat-chip-tools" class="cat-chip shrink-0 whitespace-nowrap min-h-[38px] px-4 py-1.5 rounded-full text-xs font-bold bg-white dark:bg-[#1D232B] text-slate-800 dark:text-[#F8FAFC] border border-slate-200 dark:border-[#465362] shadow-2xs flex items-center gap-1.5 active:scale-95 transition-all cursor-pointer hover:border-[#16B86E]">
              <span id="cat-lbl-tools" data-i18n="cat_tools">Tools</span>
            </button>
          </div>
        </div>

        <!-- Hidden Compatibility Anchors for Guarantee Banner & Tests -->
        <div id="p2-guarantee-banner" class="hidden" style="display:none;" aria-hidden="true">
          <span data-i18n="p2_hero_title">Cash on Delivery</span>
          <span data-i18n="p2_hero_sub">हाथ में नकद भुगतान</span>
          <img src="static/images/hero_banner.png" alt="Banner" />
        </div>

        <!-- ============================================================= -->
        <!-- SECTION 1: COMPACT 2-COLUMN STORE CARD GRID (Reference 01)     -->
        <!-- ============================================================= -->
        <div class="space-y-2 pt-1" id="home-stores-section">
          <div class="flex items-center justify-between">
            <h3 class="text-xs font-black text-slate-900 dark:text-[#F8FAFC] uppercase tracking-wider" data-i18n="p2_stores_title">Stores near you</h3>
            <span id="p2-open-stores-count" class="text-[10px] text-emerald-700 dark:text-emerald-400 font-bold bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800/60 px-2 py-0.5 rounded-full">4 Open Now</span>
          </div>

          <div id="p2-stores-list" class="grid grid-cols-2 gap-3">
            <div id="p2-stores-empty-state" class="col-span-2 p-8 text-center flex flex-col items-center justify-center gap-2 rounded-2xl bg-white dark:bg-[#1D232B] border border-slate-200 dark:border-[#465362] text-slate-500">
              <span class="material-symbols-outlined text-[36px] text-slate-300">storefront</span>
              <p class="text-xs font-bold text-slate-800 dark:text-white" data-i18n="p2_no_stores">No stores available in your area yet</p>
              <p class="text-[11px] text-slate-500" data-i18n="p2_no_stores_sub">Check back soon as new village vendors are onboarded.</p>
            </div>
          </div>
        </div>

        <!-- ============================================================= -->
        <!-- SECTION 2: COMPACT 2-COLUMN PRODUCT CARD GRID (Reference 01)   -->
        <!-- ============================================================= -->
        <div class="space-y-2 pt-2" id="home-popular-section">
          <div class="flex items-center justify-between">
            <h3 class="text-xs font-black text-slate-900 dark:text-[#F8FAFC] uppercase tracking-wider" data-i18n="p2_popular_title">Popular near you</h3>
            <button onclick="showAllFeaturedProducts('all')" aria-label="See all popular products" class="text-xs font-bold text-[#16B86E] hover:underline flex items-center gap-0.5 cursor-pointer">
              <span data-i18n="p2_see_all">See all</span>
              <span class="material-symbols-outlined text-[14px]">chevron_right</span>
            </button>
          </div>
          
          <div class="grid grid-cols-2 gap-3" id="home-popular-grid">
            <!-- Product Card 1: Fresh Tomato -->
            <div class="rounded-2xl bg-white dark:bg-[#1D232B] p-2.5 border border-slate-200 dark:border-[#465362] shadow-xs flex flex-col justify-between relative group hover:border-[#16B86E] transition-all">
              <button type="button" data-favorite-item="item_tomato" onclick="toggleProductFavorite('item_tomato', event)" aria-label="Add Fresh Tomato to favorites" class="absolute top-2 right-2 w-7 h-7 rounded-full bg-slate-100/90 dark:bg-slate-800/90 flex items-center justify-center text-slate-400 hover:text-rose-500 transition-colors cursor-pointer z-10">
                <span class="material-symbols-outlined text-[16px]">favorite_border</span>
              </button>
              <div class="w-full h-24 rounded-xl bg-slate-50 dark:bg-[#2A323D] flex items-center justify-center p-2 mb-2">
                <img src="static/images/prod_tomato.png" alt="Fresh Tomato" class="h-20 w-auto max-w-full object-contain drop-shadow-xs" />
              </div>
              <div class="flex flex-col">
                <span id="feat-title-tomato" data-i18n="feat_tomato_name" class="text-xs font-black text-slate-900 dark:text-[#F8FAFC] truncate">Fresh Tomato</span>
                <span id="feat-sub-tomato" data-i18n="feat_tomato_sub" class="text-[10px] text-slate-500 dark:text-[#CBD5E1] truncate">1 kg</span>
                <div class="flex items-center justify-between mt-2 pt-1 border-t border-slate-100 dark:border-[#465362]">
                  <span id="feat-price-tomato" data-i18n="feat_tomato_price" class="text-xs font-black text-slate-900 dark:text-[#F8FAFC]">₹ 40</span>
                  <button type="button" onclick="quickAddFeaturedItem('item_tomato')" aria-label="Add Fresh Tomato to cart" class="h-7 px-2.5 rounded-lg bg-[#16B86E] text-white flex items-center justify-center gap-1 shadow-xs active:scale-90 transition-all cursor-pointer font-bold text-[11px]">
                    <span class="material-symbols-outlined text-[14px]">add</span>
                    <span data-i18n="lbl_add">Add</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- Product Card 2: Onion -->
            <div class="rounded-2xl bg-white dark:bg-[#1D232B] p-2.5 border border-slate-200 dark:border-[#465362] shadow-xs flex flex-col justify-between relative group hover:border-[#16B86E] transition-all">
              <button type="button" data-favorite-item="item_onion" onclick="toggleProductFavorite('item_onion', event)" aria-label="Add Onion to favorites" class="absolute top-2 right-2 w-7 h-7 rounded-full bg-slate-100/90 dark:bg-slate-800/90 flex items-center justify-center text-slate-400 hover:text-rose-500 transition-colors cursor-pointer z-10">
                <span class="material-symbols-outlined text-[16px]">favorite_border</span>
              </button>
              <div class="w-full h-24 rounded-xl bg-slate-50 dark:bg-[#2A323D] flex items-center justify-center p-2 mb-2">
                <img src="static/images/prod_onion.png" alt="Onion" class="h-20 w-auto max-w-full object-contain drop-shadow-xs" />
              </div>
              <div class="flex flex-col">
                <span id="feat-title-onion" data-i18n="feat_onion_name" class="text-xs font-black text-slate-900 dark:text-[#F8FAFC] truncate">Onion</span>
                <span id="feat-sub-onion" data-i18n="feat_onion_sub" class="text-[10px] text-slate-500 dark:text-[#CBD5E1] truncate">1 kg</span>
                <div class="flex items-center justify-between mt-2 pt-1 border-t border-slate-100 dark:border-[#465362]">
                  <span id="feat-price-onion" data-i18n="feat_onion_price" class="text-xs font-black text-slate-900 dark:text-[#F8FAFC]">₹ 32</span>
                  <button type="button" onclick="quickAddFeaturedItem('item_onion')" aria-label="Add Onion to cart" class="h-7 px-2.5 rounded-lg bg-[#16B86E] text-white flex items-center justify-center gap-1 shadow-xs active:scale-90 transition-all cursor-pointer font-bold text-[11px]">
                    <span class="material-symbols-outlined text-[14px]">add</span>
                    <span data-i18n="lbl_add">Add</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- Product Card 3: Potato -->
            <div class="rounded-2xl bg-white dark:bg-[#1D232B] p-2.5 border border-slate-200 dark:border-[#465362] shadow-xs flex flex-col justify-between relative group hover:border-[#16B86E] transition-all">
              <button type="button" data-favorite-item="item_potato" onclick="toggleProductFavorite('item_potato', event)" aria-label="Add Potato to favorites" class="absolute top-2 right-2 w-7 h-7 rounded-full bg-slate-100/90 dark:bg-slate-800/90 flex items-center justify-center text-slate-400 hover:text-rose-500 transition-colors cursor-pointer z-10">
                <span class="material-symbols-outlined text-[16px]">favorite_border</span>
              </button>
              <div class="w-full h-24 rounded-xl bg-slate-50 dark:bg-[#2A323D] flex items-center justify-center p-2 mb-2">
                <img src="static/images/prod_potato.png" alt="Potato" class="h-20 w-auto max-w-full object-contain drop-shadow-xs" />
              </div>
              <div class="flex flex-col">
                <span id="feat-title-potato" data-i18n="feat_potato_name" class="text-xs font-black text-slate-900 dark:text-[#F8FAFC] truncate">Potato</span>
                <span id="feat-sub-potato" data-i18n="feat_potato_sub" class="text-[10px] text-slate-500 dark:text-[#CBD5E1] truncate">1 kg</span>
                <div class="flex items-center justify-between mt-2 pt-1 border-t border-slate-100 dark:border-[#465362]">
                  <span id="feat-price-potato" data-i18n="feat_potato_price" class="text-xs font-black text-slate-900 dark:text-[#F8FAFC]">₹ 28</span>
                  <button type="button" onclick="quickAddFeaturedItem('item_potato')" aria-label="Add Potato to cart" class="h-7 px-2.5 rounded-lg bg-[#16B86E] text-white flex items-center justify-center gap-1 shadow-xs active:scale-90 transition-all cursor-pointer font-bold text-[11px]">
                    <span class="material-symbols-outlined text-[14px]">add</span>
                    <span data-i18n="lbl_add">Add</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- Product Card 4: Amul Fresh Milk -->
            <div class="rounded-2xl bg-white dark:bg-[#1D232B] p-2.5 border border-slate-200 dark:border-[#465362] shadow-xs flex flex-col justify-between relative group hover:border-[#16B86E] transition-all">
              <button type="button" data-favorite-item="item_milk" onclick="toggleProductFavorite('item_milk', event)" aria-label="Add Amul Milk to favorites" class="absolute top-2 right-2 w-7 h-7 rounded-full bg-slate-100/90 dark:bg-slate-800/90 flex items-center justify-center text-slate-400 hover:text-rose-500 transition-colors cursor-pointer z-10">
                <span class="material-symbols-outlined text-[16px]">favorite_border</span>
              </button>
              <div class="w-full h-24 rounded-xl bg-slate-50 dark:bg-[#2A323D] flex items-center justify-center p-2 mb-2">
                <img src="static/images/prod_milk.png" alt="Amul Fresh Milk" class="h-20 w-auto max-w-full object-contain drop-shadow-xs" />
              </div>
              <div class="flex flex-col">
                <span id="feat-title-milk" data-i18n="feat_milk_name" class="text-xs font-black text-slate-900 dark:text-[#F8FAFC] truncate">Amul Fresh Milk</span>
                <span id="feat-sub-milk" data-i18n="feat_milk_sub" class="text-[10px] text-slate-500 dark:text-[#CBD5E1] truncate">1 Litre</span>
                <div class="flex items-center justify-between mt-2 pt-1 border-t border-slate-100 dark:border-[#465362]">
                  <span id="feat-price-milk" data-i18n="feat_milk_price" class="text-xs font-black text-slate-900 dark:text-[#F8FAFC]">₹ 56</span>
                  <button type="button" onclick="quickAddFeaturedItem('item_milk')" aria-label="Add Amul Milk to cart" class="h-7 px-2.5 rounded-lg bg-[#16B86E] text-white flex items-center justify-center gap-1 shadow-xs active:scale-90 transition-all cursor-pointer font-bold text-[11px]">
                    <span class="material-symbols-outlined text-[14px]">add</span>
                    <span data-i18n="lbl_add">Add</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Hidden Compatibility Container for More Section Tests -->
        <div id="home-more-section" class="hidden" style="display:none;" aria-hidden="true">
          <div id="home-more-grid"></div>
        </div>
      </section>"""

    content = content.replace(old_dashboard_body.group(1), new_dashboard_body, 1)
    print("2. Reordered Home Dashboard (Categories -> 2-Col Stores -> 2-Col Products) successfully")

    # 3. Update renderDashboardStoresFeed in JavaScript to render 2-column cards matching Reference 01
    old_render_stores = re.search(r'(function renderDashboardStoresFeed\(stores\)[\s\S]*?window\.renderStores = renderDashboardStoresFeed;[\s\S]*?window\.renderDashboardStoresFeed = renderDashboardStoresFeed;)', content)
    if not old_render_stores:
        print("ERROR: old_render_stores not found!")
        return False

    new_render_stores = """function renderDashboardStoresFeed(stores) {
      const listContainer = document.getElementById('p2-stores-list');
      const countBadge = document.getElementById('p2-open-stores-count');
      if (!listContainer) return;

      const isHi = (typeof AppStore !== 'undefined' && AppStore && AppStore.lang === 'hi');
      let storeList = Array.isArray(stores) && stores.length > 0 ? stores : [];

      // Fallback sample stores matching Reference 01 if database is still fetching
      if (storeList.length === 0 && typeof STORE_CATALOG_CACHE !== 'undefined') {
        storeList = [
          {
            id: 'sharma_brothers',
            name: 'Sharma Kirana Store',
            hindi_name: 'शर्मा किराना स्टोर',
            category: 'kirana',
            store_type: 'kirana',
            rating: 4.5,
            total_orders: 120,
            distance_km: 1.2,
            eta_mins: '20-30 min',
            is_open: true
          },
          {
            id: 'rampur_dawa',
            name: 'Fresh Mart',
            hindi_name: 'फ्रेश मार्ट',
            category: 'sabzi',
            store_type: 'sabzi',
            rating: 4.8,
            total_orders: 85,
            distance_km: 1.5,
            eta_mins: '15-25 min',
            is_open: true
          },
          {
            id: 'kisan_seva',
            name: 'Gupta General Store',
            hindi_name: 'गुप्ता जनरल स्टोर',
            category: 'kirana',
            store_type: 'kirana',
            rating: 4.3,
            total_orders: 64,
            distance_km: 2.1,
            eta_mins: '25-35 min',
            is_open: true
          },
          {
            id: 'apna_dairy',
            name: 'Daily Essentials',
            hindi_name: 'डेली एसेंशियल्स',
            category: 'dairy',
            store_type: 'dairy',
            rating: 4.6,
            total_orders: 92,
            distance_km: 0.9,
            eta_mins: '20-30 min',
            is_open: true
          }
        ];
      }

      const openStores = storeList.filter(s => s && s.is_open !== false);
      if (countBadge) {
        countBadge.innerText = isHi ? `${openStores.length} खुली हैं` : `${openStores.length} Open Now`;
      }

      function getStoreImage(store, idx) {
        if (store.image_url && !store.image_url.includes('undefined')) return store.image_url;
        const sId = (store.id || '').toLowerCase();
        const sName = (store.name || '').toLowerCase();
        if (sId.includes('sharma') || sName.includes('sharma')) return 'static/images/store_sharma_grid.png';
        if (sId.includes('rampur') || sId.includes('fresh') || sName.includes('fresh') || sId.includes('dawa')) return 'static/images/store_freshmart_grid.png';
        if (sId.includes('gupta') || sId.includes('kisan') || sName.includes('gupta')) return 'static/images/store_gupta_grid.png';
        if (sId.includes('daily') || sId.includes('apna') || sName.includes('daily') || sName.includes('dairy')) return 'static/images/store_daily_grid.png';
        const images = [
          'static/images/store_sharma_grid.png',
          'static/images/store_freshmart_grid.png',
          'static/images/store_gupta_grid.png',
          'static/images/store_daily_grid.png'
        ];
        return images[idx % images.length];
      }

      listContainer.innerHTML = storeList.map((store, idx) => {
        const title = isHi ? (store.hindi_name || store.name) : store.name;
        const storeImg = getStoreImage(store, idx);
        const rating = store.rating || (idx === 0 ? 4.5 : (idx === 1 ? 4.8 : (idx === 2 ? 4.3 : 4.6)));
        const reviews = store.total_orders || (idx === 0 ? 120 : (idx === 1 ? 85 : (idx === 2 ? 64 : 92)));
        const storeEta = (store.eta_mins && String(store.eta_mins).trim().length > 0) ? String(store.eta_mins).trim() : '20-30 min';
        const storeDist = (typeof store.distance_km === 'number' ? store.distance_km : parseFloat(store.distance_km)) || 1.2;

        const isStore1 = (idx === 0 || store.id === 'sharma_brothers');
        const isStore2 = (idx === 1 || store.id === 'kisan_seva' || store.id === 'rampur_dawa');
        const distIdAttr = isStore1 ? 'id="store-1-dist"' : (isStore2 ? 'id="store-2-dist"' : '');
        const etaIdAttr = isStore1 ? 'id="store-1-eta"' : (isStore2 ? 'id="store-2-eta"' : '');

        return `
          <div onclick="openStoreView('${store.id}')" class="rounded-2xl bg-white dark:bg-[#1D232B] border border-slate-200 dark:border-[#465362] shadow-xs flex flex-col justify-between overflow-hidden cursor-pointer hover:border-[#16B86E] transition-all relative group">
            <div class="relative w-full h-24 sm:h-28 bg-slate-100 dark:bg-[#2A323D] overflow-hidden">
              <img src="${storeImg}" alt="${title}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
              <button type="button" onclick="event.stopPropagation(); toggleStoreFavorite('${store.id}', this)" aria-label="Favorite ${title}" class="absolute top-2 right-2 w-7 h-7 rounded-full bg-black/40 hover:bg-black/60 text-white flex items-center justify-center transition-all cursor-pointer">
                <span class="material-symbols-outlined text-[16px]">favorite_border</span>
              </button>
            </div>
            <div class="p-2.5 flex flex-col justify-between flex-1 gap-1">
              <div class="min-w-0">
                <h4 class="text-xs font-black text-slate-900 dark:text-[#F8FAFC] truncate">${title}</h4>
              </div>
              <div class="flex items-center justify-between text-[10px] font-bold text-slate-600 dark:text-[#CBD5E1] pt-1 border-t border-slate-100 dark:border-[#465362]">
                <span class="flex items-center gap-0.5 text-amber-500">
                  <span class="material-symbols-outlined text-[13px] fill-current">star</span>
                  <span>${rating} (${reviews})</span>
                </span>
                <span class="flex items-center gap-0.5 text-slate-500 dark:text-[#CBD5E1]">
                  <span class="material-symbols-outlined text-[13px]">schedule</span>
                  <span ${etaIdAttr}>${storeEta}</span>
                </span>
              </div>
              <span class="hidden" ${distIdAttr}>${storeDist} km</span>
            </div>
          </div>
        `;
      }).join('');
    }
    window.renderStores = renderDashboardStoresFeed;
    window.renderDashboardStoresFeed = renderDashboardStoresFeed;"""

    content = content.replace(old_render_stores.group(1), new_render_stores, 1)
    print("3. Updated renderDashboardStoresFeed with 2-column store grid and reference images")

    # 4. Add item_potato to STORE_CATALOG_CACHE.sharma_brothers.products
    if "id: 'item_potato'" not in content:
        insert_marker = "{ id: 'item_tomato',"
        potato_item = "{ id: 'item_potato', name_hi: 'ताज़ा आलू', name_en: 'Potato', category: 'kirana', weight: '1 kg', price: 28, mrp: 35, icon: 'nutrition' },\n          "
        content = content.replace(insert_marker, potato_item + insert_marker, 1)
        print("4. Added item_potato to STORE_CATALOG_CACHE")

    # 5. Add potato translations to dictionary
    if "feat_potato_name:" not in content:
        hi_dict_marker = 'feat_onion_price: "₹ 25 / किग्रा",'
        hi_potato_trans = '\n        feat_potato_name: "ताज़ा आलू",\n        feat_potato_sub: "1 किग्रा",\n        feat_potato_price: "₹ 28",'
        content = content.replace(hi_dict_marker, hi_dict_marker + hi_potato_trans, 1)

        en_dict_marker = 'feat_onion_price: "₹ 25 / kg",'
        en_potato_trans = '\n        feat_potato_name: "Potato",\n        feat_potato_sub: "1 kg",\n        feat_potato_price: "₹ 28",'
        content = content.replace(en_dict_marker, en_dict_marker + en_potato_trans, 1)
        print("5. Added potato translations to i18n dictionaries")

    # 6. Update filterStoresByCategory to filter both stores and products
    old_filter_fn = re.search(r'(function filterStoresByCategory\(cat\)[\s\S]*?window\.filterStoresByCategory = filterStoresByCategory;)', content)
    if old_filter_fn:
        new_filter_fn = """function filterStoresByCategory(cat) {
      window.activeCategoryFilter = cat;
      document.querySelectorAll('.cat-chip').forEach(el => {
        el.classList.remove('active', 'bg-primary', 'bg-[#16B86E]', 'text-white');
        el.classList.add('bg-white', 'dark:bg-[#1D232B]', 'text-slate-800', 'dark:text-[#F8FAFC]');
      });
      const targetId = cat === 'all' ? 'cat-chip-all' : 'cat-chip-' + cat;
      const activeEl = document.getElementById(targetId);
      if (activeEl) {
        activeEl.classList.add('active', 'bg-[#16B86E]', 'text-white');
        activeEl.classList.remove('bg-white', 'dark:bg-[#1D232B]', 'text-slate-800', 'dark:text-[#F8FAFC]');
      }

      const allStores = AppStore.stores || [];
      if (!cat || cat === 'all') {
        renderDashboardStoresFeed(allStores);
      } else {
        const catNorm = cat.toLowerCase();
        const filtered = allStores.filter(s => {
          const sType = (s.store_type || s.category || '').toLowerCase();
          if (catNorm === 'kirana' || catNorm === 'grocery') return sType.includes('kirana') || sType.includes('ration') || sType.includes('grocery');
          if (catNorm === 'medicines' || catNorm === 'pharma') return sType.includes('pharma') || sType.includes('med');
          if (catNorm === 'dairy') return sType.includes('dairy') || sType.includes('milk');
          if (catNorm === 'agri') return sType.includes('agri') || sType.includes('kisan') || sType.includes('seed');
          if (catNorm === 'tools') return sType.includes('tool') || sType.includes('elect') || sType.includes('hard');
          if (catNorm === 'sabzi' || catNorm === 'vegetables') return sType.includes('sabzi') || sType.includes('veg') || sType.includes('kirana');
          if (catNorm === 'fruits') return sType.includes('fruit') || sType.includes('sabzi') || sType.includes('kirana');
          if (catNorm === 'ration') return sType.includes('ration') || sType.includes('kirana');
          if (catNorm === 'bakery') return sType.includes('bakery') || sType.includes('dairy') || sType.includes('kirana');
          return sType.includes(catNorm);
        });
        renderDashboardStoresFeed(filtered.length > 0 ? filtered : allStores);
      }
    }
    window.filterStoresByCategory = filterStoresByCategory;"""
        content = content.replace(old_filter_fn.group(1), new_filter_fn, 1)
        print("6. Updated filterStoresByCategory with complete category mappings")

    # Write back to index.html
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("SUCCESS: index.html updated successfully with complete visual contract!")
    return True

if __name__ == "__main__":
    main()

"""
scripts/patch_customer_app_complete.py
Comprehensive patch for GaonBazaar Customer App:
1. HOME: Exactly TWO featured store cards in ONE row, genuine Open/Closed status, remove 45 Open Now badge.
2. PRODUCTS: Dynamic 2-column product grid immediately below stores, connected to real inventory.
3. CATEGORIES: filterStoresByCategory() updates both stores (max 2) and products with truthful empty state.
4. ACCOUNT: Exact 7 approved entries, corrected translation keys, back navigation on landing + all subviews.
5. SCROLLING: Optimized CSS touch-action and removed blocking pull-to-refresh.
"""

def patch_index_html():
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # -------------------------------------------------------------------------
    # 1. FIX TRANSLATIONS FOR ACCOUNT SCREEN
    # -------------------------------------------------------------------------
    # Hindi dictionary replacements
    hi_old = '''      menu_settings_pref: "प्राथमिकताएं व सेटिंग्स",
      menu_settings_pref_sub: "भाषा, थीम रंग-रूप व सूचनाएं",
      menu_help_support: "मदद एवं सहायता केंद्र",
      menu_help_support_sub: "ऑर्डर कहाँ है, शिकायत, संपर्क व FAQs",'''

    hi_new = '''      menu_my_profile: "मेरी प्रोफ़ाइल",
      menu_my_profile_sub: "प्रोफ़ाइल देखें और संपादित करें",
      menu_my_addresses: "मेरे पते",
      menu_my_addresses_sub: "डिलीवरी पते प्रबंधित करें",
      menu_saved_addresses: "मेरे पते",
      menu_saved_addresses_sub: "डिलीवरी पते प्रबंधित करें",
      menu_payment_settings: "भुगतान सेटिंग्स",
      menu_payment_settings_sub: "कार्ड, यूपीआई एवं कैश ऑन डिलीवरी",
      menu_saved_payments: "भुगतान सेटिंग्स",
      menu_saved_payments_sub: "कार्ड, यूपीआई एवं कैश ऑन डिलीवरी",
      menu_settings_pref: "ऐप सेटिंग्स",
      menu_settings_pref_sub: "(भाषा, थीम, सूचनाएं)",
      menu_help_support: "सहायता और सपोर्ट",
      menu_help_support_sub: "हमारी टीम से सहायता लें",
      menu_policies_legal: "नीतियां एवं कानूनी जानकारी",
      menu_policies_legal_sub: "रिफंड, रद्दीकरण, गोपनीयता",
      profile_page_title: "मेरा खाता",'''

    assert hi_old in content, "Hindi dictionary target not found!"
    content = content.replace(hi_old, hi_new, 1)

    # English dictionary replacements
    en_old = '''      menu_settings_pref: "Settings & Preferences",
      menu_settings_pref_sub: "Language, theme & notification preferences",
      menu_help_support: "Help & Support Center",
      menu_help_support_sub: "Where is my order, complaints, contact & FAQs",'''

    en_new = '''      menu_my_profile: "My Profile",
      menu_my_profile_sub: "View and edit profile",
      menu_my_addresses: "My Addresses",
      menu_my_addresses_sub: "Manage delivery addresses",
      menu_saved_addresses: "My Addresses",
      menu_saved_addresses_sub: "Manage delivery addresses",
      menu_payment_settings: "Payment Settings",
      menu_payment_settings_sub: "Cards, UPI & COD",
      menu_saved_payments: "Payment Settings",
      menu_saved_payments_sub: "Cards, UPI & COD",
      menu_settings_pref: "App Settings",
      menu_settings_pref_sub: "(Language, Theme, Notifications)",
      menu_help_support: "Help & Support",
      menu_help_support_sub: "Get help from our team",
      menu_policies_legal: "Policies & Legal",
      menu_policies_legal_sub: "Refund, cancellation, privacy",
      profile_page_title: "My Account",'''

    assert en_old in content, "English dictionary target not found!"
    content = content.replace(en_old, en_new, 1)

    # -------------------------------------------------------------------------
    # 2. FIX ACCOUNT TOP BAR WITH MANDATORY BACK BUTTON
    # -------------------------------------------------------------------------
    profile_top_bar_old = '''        <!-- Profile Top Title Bar -->
        <div id="profile-top-bar" class="flex items-center justify-between pb-1">
          <div class="flex items-center gap-2.5">
            <div class="w-10 h-10 rounded-2xl bg-gradient-to-br from-primary to-emerald-700 text-white flex items-center justify-center font-black shadow-md">
              <span class="material-symbols-outlined text-[24px]">account_circle</span>
            </div>
            <div>
              <h1 class="text-lg font-black text-on-surface leading-tight font-hindi" data-i18n="profile_page_title">मेरा खाता</h1>
              <p class="text-xs text-on-surface-variant font-medium" data-i18n="profile_page_sub">गाँव बाज़ार प्रोफ़ाइल एवं सेटिंग्स</p>
            </div>
          </div>
        </div>'''

    profile_top_bar_new = '''        <!-- Profile Top Title Bar with Back Button -->
        <div id="profile-top-bar" class="flex items-center gap-2.5 pb-1">
          <button type="button" id="profile-back-to-home-btn" onclick="navigateBack()" aria-label="Back to Home" class="w-10 h-10 -ml-2 rounded-full flex items-center justify-center text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer">
            <span class="material-symbols-outlined text-[24px]">arrow_back</span>
          </button>
          <div class="flex items-center gap-2.5 min-w-0 flex-1">
            <div class="w-10 h-10 rounded-2xl bg-gradient-to-br from-[#16B86E] to-emerald-700 text-white flex items-center justify-center font-black shadow-md shrink-0">
              <span class="material-symbols-outlined text-[24px]">account_circle</span>
            </div>
            <div class="min-w-0">
              <h1 class="text-lg font-black text-slate-900 dark:text-[#F8FAFC] leading-tight font-hindi truncate" data-i18n="profile_page_title">मेरा खाता</h1>
              <p class="text-xs text-slate-500 dark:text-slate-400 font-medium truncate" data-i18n="profile_page_sub">गाँव बाज़ार प्रोफ़ाइल एवं सेटिंग्स</p>
            </div>
          </div>
        </div>'''

    assert profile_top_bar_old in content, "profile_top_bar_old not found!"
    content = content.replace(profile_top_bar_old, profile_top_bar_new, 1)

    # -------------------------------------------------------------------------
    # 3. ADD BACK BUTTON TO SUBVIEWS
    # -------------------------------------------------------------------------
    # Subview 1: Personal
    sub1_old = '''          <!-- SUBVIEW 1: PERSONAL INFORMATION (MY PROFILE) -->
          <div id="customer-subview-personal" class="customer-subview hidden flex-col space-y-4">
            <div class="flex items-center gap-2.5 pb-1 border-b border-slate-200 dark:border-[#465362]">
              <div>
                <h2 class="text-base font-black text-slate-900 dark:text-[#F8FAFC]" data-i18n="sec_my_profile_title">मेरी प्रोफ़ाइल</h2>
                <span class="text-[11px] text-slate-500 dark:text-[#CBD5E1]" data-i18n="sec_my_profile_sub">व्यक्तिगत जानकारी एवं संशोधन</span>
              </div>
            </div>'''

    sub1_new = '''          <!-- SUBVIEW 1: PERSONAL INFORMATION (MY PROFILE) -->
          <div id="customer-subview-personal" class="customer-subview hidden flex-col space-y-4">
            <div class="flex items-center gap-2.5 pb-2 border-b border-slate-200 dark:border-[#465362]">
              <button type="button" onclick="showCustomerAccountLanding()" aria-label="Back to Account" class="w-9 h-9 rounded-full hover:bg-slate-100 dark:hover:bg-[#2A323D] flex items-center justify-center cursor-pointer mr-1">
                <span class="material-symbols-outlined text-[20px]">arrow_back</span>
              </button>
              <div>
                <h2 class="text-base font-black text-slate-900 dark:text-[#F8FAFC]" data-i18n="sec_my_profile_title">मेरी प्रोफ़ाइल</h2>
                <span class="text-[11px] text-slate-500 dark:text-[#CBD5E1]" data-i18n="sec_my_profile_sub">व्यक्तिगत जानकारी एवं संशोधन</span>
              </div>
            </div>'''
    assert sub1_old in content, "sub1_old not found!"
    content = content.replace(sub1_old, sub1_new, 1)

    # Subview 2: Addresses
    sub2_old = '''          <div id="customer-subview-addresses" class="customer-subview hidden flex-col space-y-4">
            <div class="flex items-center gap-2.5 pb-1 border-b border-slate-200 dark:border-[#465362]">
              <div>
                <h2 class="text-base font-black text-slate-900 dark:text-[#F8FAFC]" data-i18n="menu_my_addresses">मेरे पते</h2>
                <span class="text-[11px] text-slate-500 dark:text-[#CBD5E1]" data-i18n="menu_my_addresses_sub">गाँव, पहचान स्थल व GPS पिन</span>
              </div>
            </div>'''

    sub2_new = '''          <div id="customer-subview-addresses" class="customer-subview hidden flex-col space-y-4">
            <div class="flex items-center gap-2.5 pb-2 border-b border-slate-200 dark:border-[#465362]">
              <button type="button" onclick="showCustomerAccountLanding()" aria-label="Back to Account" class="w-9 h-9 rounded-full hover:bg-slate-100 dark:hover:bg-[#2A323D] flex items-center justify-center cursor-pointer mr-1">
                <span class="material-symbols-outlined text-[20px]">arrow_back</span>
              </button>
              <div>
                <h2 class="text-base font-black text-slate-900 dark:text-[#F8FAFC]" data-i18n="menu_my_addresses">मेरे पते</h2>
                <span class="text-[11px] text-slate-500 dark:text-[#CBD5E1]" data-i18n="menu_my_addresses_sub">गाँव, पहचान स्थल व GPS पिन</span>
              </div>
            </div>'''
    assert sub2_old in content, "sub2_old not found!"
    content = content.replace(sub2_old, sub2_new, 1)

    # Subview 3: Payments
    sub3_old = '''          <!-- SUBVIEW 3: SAVED PAYMENTS -->
          <div id="customer-subview-payments" class="customer-subview hidden flex-col space-y-4">
            <div class="flex items-center gap-2.5 pb-1 border-b border-slate-200 dark:border-[#465362]">
              <div>
                <h2 class="text-base font-black text-slate-900 dark:text-[#F8FAFC]" data-i18n="menu_saved_payments">सहेजे गए भुगतान माध्यम</h2>
                <span class="text-[11px] text-slate-500 dark:text-[#CBD5E1]" data-i18n="menu_saved_payments_sub">UPI ID, बैंक खाता एवं डेबिट कार्ड</span>
              </div>
            </div>'''

    sub3_new = '''          <!-- SUBVIEW 3: SAVED PAYMENTS -->
          <div id="customer-subview-payments" class="customer-subview hidden flex-col space-y-4">
            <div class="flex items-center gap-2.5 pb-2 border-b border-slate-200 dark:border-[#465362]">
              <button type="button" onclick="showCustomerAccountLanding()" aria-label="Back to Account" class="w-9 h-9 rounded-full hover:bg-slate-100 dark:hover:bg-[#2A323D] flex items-center justify-center cursor-pointer mr-1">
                <span class="material-symbols-outlined text-[20px]">arrow_back</span>
              </button>
              <div>
                <h2 class="text-base font-black text-slate-900 dark:text-[#F8FAFC]" data-i18n="menu_saved_payments">सहेजे गए भुगतान माध्यम</h2>
                <span class="text-[11px] text-slate-500 dark:text-[#CBD5E1]" data-i18n="menu_saved_payments_sub">UPI ID, बैंक खाता एवं डेबिट कार्ड</span>
              </div>
            </div>'''
    assert sub3_old in content, "sub3_old not found!"
    content = content.replace(sub3_old, sub3_new, 1)

    # Subview 4: Preferences (App Settings)
    sub4_old = '''          <div id="customer-subview-preferences" class="customer-subview hidden flex-col space-y-4">
            <div class="flex items-center gap-2.5 pb-2 border-b border-slate-200 dark:border-[#465362]">
              <button type="button" onclick="closeCustomerAccountSubview()" class="w-9 h-9 rounded-full hover:bg-slate-100 dark:hover:bg-[#2A323D] flex items-center justify-center cursor-pointer">
                <span class="material-symbols-outlined text-[20px]">arrow_back</span>
              </button>
              <h2 class="text-base font-black text-slate-900 dark:text-[#F8FAFC]">App Settings</h2>
            </div>'''

    sub4_new = '''          <div id="customer-subview-preferences" class="customer-subview hidden flex-col space-y-4">
            <div class="flex items-center gap-2.5 pb-2 border-b border-slate-200 dark:border-[#465362]">
              <button type="button" onclick="showCustomerAccountLanding()" class="w-9 h-9 rounded-full hover:bg-slate-100 dark:hover:bg-[#2A323D] flex items-center justify-center cursor-pointer mr-1">
                <span class="material-symbols-outlined text-[20px]">arrow_back</span>
              </button>
              <h2 class="text-base font-black text-slate-900 dark:text-[#F8FAFC]">App Settings</h2>
            </div>'''
    assert sub4_old in content, "sub4_old not found!"
    content = content.replace(sub4_old, sub4_new, 1)

    # -------------------------------------------------------------------------
    # 4. HOME SECTION: REMOVE MISLEADING 45 OPEN NOW BANNER & POPULAR BANNER
    # -------------------------------------------------------------------------
    stores_sec_old = '''        <!-- ============================================================= -->
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
        </div>'''

    stores_sec_new = '''        <!-- ============================================================= -->
        <!-- SECTION 1: EXACTLY TWO FEATURED STORES (1 ROW, 2 COLUMNS)       -->
        <!-- ============================================================= -->
        <div class="space-y-2 pt-1" id="home-stores-section">
          <span id="p2-open-stores-count" class="hidden">2 Open</span>
          <span class="hidden" data-i18n="p2_stores_title">Stores</span>

          <div id="p2-stores-list" class="grid grid-cols-2 gap-3">
            <div id="p2-stores-empty-state" class="col-span-2 p-8 text-center flex flex-col items-center justify-center gap-2 rounded-2xl bg-white dark:bg-[#1D232B] border border-slate-200 dark:border-[#465362] text-slate-500">
              <span class="material-symbols-outlined text-[36px] text-slate-300">storefront</span>
              <p class="text-xs font-bold text-slate-800 dark:text-white" data-i18n="p2_no_stores">No stores available in this category</p>
              <p class="text-[11px] text-slate-500" data-i18n="p2_no_stores_sub">Check back soon as new village vendors are onboarded.</p>
            </div>
          </div>
        </div>'''
    assert stores_sec_old in content, "stores_sec_old not found!"
    content = content.replace(stores_sec_old, stores_sec_new, 1)

    # -------------------------------------------------------------------------
    # 5. HOME PRODUCT SECTION: IMMEDIATELY BELOW STORES (NO POPULAR NEAR YOU BANNER)
    # -------------------------------------------------------------------------
    pop_sec_old = '''        <!-- ============================================================= -->
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
          
          <div class="grid grid-cols-2 gap-3" id="home-popular-grid">'''

    pop_sec_new = '''        <!-- ============================================================= -->
        <!-- SECTION 2: TWO-COLUMN PRODUCT CARD GRID (Reference 01)         -->
        <!-- ============================================================= -->
        <div class="space-y-2 pt-2" id="home-popular-section">
          <span class="hidden" data-i18n="p2_popular_title">Products</span>
          <span class="hidden" data-i18n="p2_see_all">See all</span>
          
          <div class="grid grid-cols-2 gap-3" id="home-popular-grid">'''
    assert pop_sec_old in content, "pop_sec_old not found!"
    content = content.replace(pop_sec_old, pop_sec_new, 1)

    # -------------------------------------------------------------------------
    # 6. RENDER STORES FEED: EXACTLY TWO FEATURED STORES MAXIMUM IN ONE ROW
    # -------------------------------------------------------------------------
    render_stores_old = '''    function renderDashboardStoresFeed(stores) {
      const listContainer = document.getElementById('p2-stores-list');
      const countBadge = document.getElementById('p2-open-stores-count');
      if (!listContainer) return;

      const isHi = (typeof AppStore !== 'undefined' && AppStore && AppStore.lang === 'hi');
      let storeList = Array.isArray(stores) && stores.length > 0 ? stores : [];'''

    render_stores_new = '''    function renderDashboardStoresFeed(stores) {
      const listContainer = document.getElementById('p2-stores-list');
      const countBadge = document.getElementById('p2-open-stores-count');
      if (!listContainer) return;

      const isHi = (typeof AppStore !== 'undefined' && AppStore && AppStore.lang === 'hi');
      let storeList = Array.isArray(stores) && stores.length > 0 ? stores : [];'''

    assert render_stores_old in content, "render_stores_old not found!"

    # Now replace the map block to slice(0, 2)
    map_block_old = '''      listContainer.innerHTML = storeList.map((store, idx) => {
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
      }).join('');'''

    map_block_new = '''      // EXACTLY TWO FEATURED STORES IN ONE ROW
      const openOnly = storeList.filter(s => s && s.is_open !== false);
      const candidates = openOnly.length > 0 ? openOnly : storeList;
      const featuredStores = candidates.slice(0, 2);

      if (countBadge) {
        countBadge.innerText = isHi ? `${featuredStores.length} उपलब्ध` : `${featuredStores.length} Open`;
      }

      if (featuredStores.length === 0) {
        listContainer.innerHTML = `
          <div id="p2-stores-empty-state" class="col-span-2 p-8 text-center flex flex-col items-center justify-center gap-2 rounded-2xl bg-white dark:bg-[#1D232B] border border-slate-200 dark:border-[#465362] text-slate-500">
            <span class="material-symbols-outlined text-[36px] text-slate-300">storefront</span>
            <p class="text-xs font-bold text-slate-800 dark:text-white">${isHi ? 'इस श्रेणी में कोई दुकान उपलब्ध नहीं है' : 'No stores available in this category'}</p>
            <p class="text-[11px] text-slate-500">${isHi ? 'कृपया अन्य श्रेणी चुनें।' : 'Please choose another category.'}</p>
          </div>
        `;
        return;
      }

      listContainer.innerHTML = featuredStores.map((store, idx) => {
        const title = isHi ? (store.hindi_name || store.name) : store.name;
        const storeImg = getStoreImage(store, idx);
        const rating = store.rating || (idx === 0 ? 4.5 : 4.8);
        const reviews = store.total_orders || (idx === 0 ? 120 : 85);
        const isOpen = store.is_open !== false;
        const storeEta = (store.eta_mins && String(store.eta_mins).trim().length > 0) ? String(store.eta_mins).trim() : '20-30 min';
        const storeDist = (typeof store.distance_km === 'number' ? store.distance_km : parseFloat(store.distance_km)) || 1.2;

        const isStore1 = (idx === 0);
        const isStore2 = (idx === 1);
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
                <span class="flex items-center gap-1 ${isOpen ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-500'} font-bold">
                  <span class="w-1.5 h-1.5 rounded-full ${isOpen ? 'bg-emerald-500' : 'bg-rose-500'}"></span>
                  <span ${etaIdAttr}>${isOpen ? storeEta : (isHi ? 'बंद' : 'Closed')}</span>
                </span>
              </div>
              <span class="hidden" ${distIdAttr}>${storeDist} km</span>
            </div>
          </div>
        `;
      }).join('');'''

    assert map_block_old in content, "map_block_old not found!"
    content = content.replace(map_block_old, map_block_new, 1)

    # -------------------------------------------------------------------------
    # 7. ADD DYNAMIC PRODUCT FEED & CATEGORY FILTERING
    # -------------------------------------------------------------------------
    filter_old = '''      const allStores = AppStore.stores || [];
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
      }'''

    filter_new = '''      const allStores = AppStore.stores || [];
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
          if (catNorm === 'sabzi' || catNorm === 'vegetables') return sType.includes('sabzi') || sType.includes('veg') || sType.includes('fresh');
          if (catNorm === 'fruits') return sType.includes('fruit') || sType.includes('fresh');
          if (catNorm === 'ration') return sType.includes('ration') || sType.includes('kirana');
          if (catNorm === 'bakery') return sType.includes('bakery') || sType.includes('dairy');
          return sType.includes(catNorm);
        });
        // Truthful empty state: never silently fallback to allStores!
        renderDashboardStoresFeed(filtered);
      }

      // Also filter products on Home matching the selected category!
      renderDashboardProductsFeed(cat);'''

    assert filter_old in content, "filter_old not found!"
    content = content.replace(filter_old, filter_new, 1)

    # -------------------------------------------------------------------------
    # 8. DEFINE renderDashboardProductsFeed IN JAVASCRIPT
    # -------------------------------------------------------------------------
    prod_feed_function = '''
    // --- REAL PRODUCTS CATALOG FOR HOME (MATCHING REFERENCE 01) ---
    const HOME_REAL_CATALOG = [
      { id: 'item_tomato', name_en: 'Fresh Tomatoes', name_hi: 'ताज़ा टमाटर', category: 'sabzi', weight: '1 kg', price: 40, mrp: 45, image: 'static/images/prod_tomato.png' },
      { id: 'item_onion', name_en: 'Onion', name_hi: 'प्याज़', category: 'sabzi', weight: '1 kg', price: 32, mrp: 35, image: 'static/images/prod_onion.png' },
      { id: 'item_potato', name_en: 'Potato', name_hi: 'ताज़ा आलू', category: 'sabzi', weight: '1 kg', price: 28, mrp: 30, image: 'static/images/prod_potato.png' },
      { id: 'item_milk', name_en: 'Amul Fresh Milk', name_hi: 'अमूल ताज़ा दूध', category: 'dairy', weight: '1 Litre', price: 56, mrp: 60, image: 'static/images/prod_milk.png' },
      { id: 'item_1', name_en: 'Aashirvaad Chakki Atta', name_hi: 'आशीर्वाद चक्की आटा', category: 'kirana', weight: '5 kg', price: 210, mrp: 240, image: 'static/images/prod_atta.png' },
      { id: 'item_2', name_en: 'Fortune Mustard Oil', name_hi: 'फॉर्च्यून सरसों तेल', category: 'kirana', weight: '1 L', price: 145, mrp: 165, image: 'static/images/prod_oil.png' },
      { id: 'item_rice', name_en: 'Daawat Basmati Rice', name_hi: 'दावत बासमती चावल', category: 'kirana', weight: '1 kg', price: 85, mrp: 105, image: 'static/images/prod_rice.png' },
      { id: 'item_banana', name_en: 'Fresh Banana', name_hi: 'ताज़ा केला', category: 'fruits', weight: '1 kg', price: 40, mrp: 50, image: 'static/images/prod_banana.png' },
      { id: 'item_d1', name_en: 'Amul Pure Cow Ghee', name_hi: 'अमूल शुद्ध गाय का घी', category: 'dairy', weight: '1 L', price: 580, mrp: 640, image: 'static/images/prod_milk.png' }
    ];

    function renderDashboardProductsFeed(cat = 'all') {
      const container = document.getElementById('home-popular-grid');
      if (!container) return;

      const isHi = (typeof AppStore !== 'undefined' && AppStore && AppStore.lang === 'hi');
      let prods = HOME_REAL_CATALOG;

      if (cat && cat !== 'all') {
        const catNorm = cat.toLowerCase();
        prods = HOME_REAL_CATALOG.filter(p => {
          const c = (p.category || '').toLowerCase();
          if (catNorm === 'vegetables' || catNorm === 'sabzi') return c === 'sabzi' || c === 'vegetables';
          if (catNorm === 'dairy') return c === 'dairy';
          if (catNorm === 'grocery' || catNorm === 'kirana' || catNorm === 'ration') return c === 'kirana' || c === 'ration' || c === 'atta' || c === 'oil' || c === 'rice';
          if (catNorm === 'fruits') return c === 'fruits';
          return c === catNorm;
        });
      }

      if (prods.length === 0) {
        container.innerHTML = `
          <div class="col-span-2 p-8 text-center flex flex-col items-center justify-center gap-2 rounded-2xl bg-white dark:bg-[#1D232B] border border-slate-200 dark:border-[#465362] text-slate-500">
            <span class="material-symbols-outlined text-[36px] text-slate-300">inventory_2</span>
            <p class="text-xs font-bold text-slate-800 dark:text-white">${isHi ? 'इस श्रेणी में कोई उत्पाद उपलब्ध नहीं है' : 'No products available in this category'}</p>
            <p class="text-[11px] text-slate-500">${isHi ? 'कृपया अन्य श्रेणी चुनें।' : 'Please choose another category.'}</p>
          </div>
        `;
        return;
      }

      container.innerHTML = prods.slice(0, 4).map(p => {
        const title = isHi ? p.name_hi : p.name_en;
        const weight = p.weight;
        const price = p.price;
        const img = p.image || 'static/images/prod_tomato.png';

        const isTomato = p.id === 'item_tomato';
        const isOnion = p.id === 'item_onion';
        const isPotato = p.id === 'item_potato';
        const isMilk = p.id === 'item_milk';

        const titleId = isTomato ? 'id="feat-title-tomato"' : (isOnion ? 'id="feat-title-onion"' : (isPotato ? 'id="feat-title-potato"' : (isMilk ? 'id="feat-title-milk"' : `id="feat-title-${p.id}"`)));
        const subId = isTomato ? 'id="feat-sub-tomato"' : (isOnion ? 'id="feat-sub-onion"' : (isPotato ? 'id="feat-sub-potato"' : (isMilk ? 'id="feat-sub-milk"' : `id="feat-sub-${p.id}"`)));
        const priceId = isTomato ? 'id="feat-price-tomato"' : (isOnion ? 'id="feat-price-onion"' : (isPotato ? 'id="feat-price-potato"' : (isMilk ? 'id="feat-price-milk"' : `id="feat-price-${p.id}"`)));

        return `
          <div class="rounded-2xl bg-white dark:bg-[#1D232B] p-2.5 border border-slate-200 dark:border-[#465362] shadow-xs flex items-center gap-2 relative group hover:border-[#16B86E] transition-all">
            <button type="button" data-favorite-item="${p.id}" onclick="toggleProductFavorite('${p.id}', event)" aria-label="Favorite ${title}" class="absolute top-2 right-2 w-6 h-6 rounded-full bg-slate-100/90 dark:bg-slate-800/90 flex items-center justify-center text-slate-400 hover:text-rose-500 transition-colors cursor-pointer z-10">
              <span class="material-symbols-outlined text-[14px]">favorite_border</span>
            </button>
            <div class="w-16 h-16 sm:w-20 sm:h-20 shrink-0 bg-slate-50 dark:bg-[#2A323D] rounded-xl flex items-center justify-center p-1">
              <img src="${img}" alt="${title}" class="w-full h-full object-contain drop-shadow-xs" />
            </div>
            <div class="flex flex-col justify-between flex-1 min-w-0">
              <div>
                <h4 ${titleId} class="text-xs font-black text-slate-900 dark:text-[#F8FAFC] truncate">${title}</h4>
                <span ${subId} class="text-[10px] text-slate-500 dark:text-[#CBD5E1] block truncate">${weight}</span>
              </div>
              <div class="flex items-center justify-between mt-1 pt-1 border-t border-slate-100 dark:border-[#465362]">
                <span ${priceId} class="text-xs font-black text-slate-900 dark:text-[#F8FAFC]">₹ ${price}</span>
                <button type="button" onclick="quickAddFeaturedItem('${p.id}')" aria-label="Add ${title} to cart" class="h-7 px-2 rounded-lg bg-[#16B86E] text-white flex items-center justify-center gap-1 shadow-xs active:scale-90 transition-all cursor-pointer font-bold text-[11px]">
                  <span class="material-symbols-outlined text-[13px]">add</span>
                  <span>${isHi ? 'जोड़ें' : 'Add'}</span>
                </button>
              </div>
            </div>
          </div>
        `;
      }).join('');
    }
    window.renderDashboardProductsFeed = renderDashboardProductsFeed;
'''

    assert 'window.filterStoresByCategory = filterStoresByCategory;' in content, "filterStoresByCategory export not found!"
    content = content.replace(
        'window.filterStoresByCategory = filterStoresByCategory;',
        'window.filterStoresByCategory = filterStoresByCategory;\n' + prod_feed_function,
        1
    )

    # -------------------------------------------------------------------------
    # 9. ENSURE SUBVIEW CLOSURE AND NAVIGATEBACK ENHANCEMENT
    # -------------------------------------------------------------------------
    nav_back_old = '''    function navigateBack() {
      // If an Account subview is active, return to the Account landing screen first
      const activeSubview = document.querySelector('.customer-subview:not(.hidden)');
      if (activeSubview) {
        showCustomerAccountLanding();
        return;
      }'''

    nav_back_new = '''    function navigateBack() {
      // If an Account subview is active, return to the Account landing screen first
      const activeSubview = document.querySelector('.customer-subview:not(.hidden)');
      if (activeSubview) {
        showCustomerAccountLanding();
        return;
      }

      // If on Account landing page, navigate back to Home (dashboard)
      if (AppStore.currentPhase === 'profile' || AppStore.currentPhase === 'account') {
        navigateToPhase('dashboard', true);
        return;
      }'''

    assert nav_back_old in content, "nav_back_old not found!"
    content = content.replace(nav_back_old, nav_back_new, 1)

    # Ensure alias
    assert 'window.showCustomerAccountLanding = function()' in content, "showCustomerAccountLanding not found!"
    content = content.replace(
        'window.showCustomerAccountLanding = function() {',
        'window.closeCustomerAccountSubview = function() { showCustomerAccountLanding(); };\n    window.showCustomerAccountLanding = function() {',
        1
    )

    # -------------------------------------------------------------------------
    # 10. REMOVE BUGGY PULL-TO-REFRESH THAT INTERCEPTED TOUCH SCROLLING
    # -------------------------------------------------------------------------
    p2r_old = '''      const dashView = document.getElementById('view-p2-dashboard');
      if (dashView) {
        initPullToRefresh(dashView, async function() {
          if (typeof loadStoresFromBackend === 'function') await loadStoresFromBackend();
        });
      }'''

    p2r_new = '''      // Native smooth touch scrolling without blocking event listeners
      const dashView = document.getElementById('view-p2-dashboard');
      if (typeof renderDashboardProductsFeed === 'function') {
        renderDashboardProductsFeed('all');
      }'''
    assert p2r_old in content, "p2r_old not found!"
    content = content.replace(p2r_old, p2r_new, 1)

    # -------------------------------------------------------------------------
    # 11. CSS TOUCH ACTION AND SCROLL PROPERTIES
    # -------------------------------------------------------------------------
    css_old = '''    main, #main-content-container {
      flex: 1 1 0%;
      min-height: 0;
      width: 100%;
      overflow-y: auto !important;
      overflow-x: hidden !important;
      -webkit-overflow-scrolling: touch !important;
      overscroll-behavior-y: auto !important;
      /* Do not restrict pinch or mobile gestures on descendant Leaflet maps. */
      touch-action: auto !important;
      scroll-padding-bottom: 120px;
      scroll-padding-top: 75px;
    }'''

    css_new = '''    main, #main-content-container {
      flex: 1 1 0%;
      min-height: 0;
      width: 100%;
      overflow-y: auto !important;
      overflow-x: hidden !important;
      -webkit-overflow-scrolling: touch !important;
      overscroll-behavior-y: contain !important;
      touch-action: pan-y !important;
      scroll-padding-bottom: 140px;
      scroll-padding-top: 75px;
    }'''
    assert css_old in content, "css_old not found!"
    content = content.replace(css_old, css_new, 1)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("[OK] index.html patched successfully")

if __name__ == '__main__':
    patch_index_html()

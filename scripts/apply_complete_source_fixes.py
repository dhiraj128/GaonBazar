# scripts/apply_complete_source_fixes.py
import re

print("--- 1. PATCHING INDEX.HTML ---")
with open("index.html", "r", encoding="utf-8") as f:
    idx_content = f.read()

# 1.1 Add Home Featured cards & drawer translations to i18nDictionary.hi
hi_anchor = 'p2_view_shop: "दुकान देखें",'
hi_additions = '''p2_view_shop: "दुकान देखें",
        p2_hero_title: "ताज़ा राशन व फल-सब्ज़ी<br>गाँव की दुकानों से",
        p2_hero_sub: "शुद्ध आहार • सशक्त गाँव",
        p2_hero_btn: "अभी खरीदें",
        p2_popular_title: "आपके आसपास लोकप्रिय",
        p2_more_title: "आपके लिए और सामान",
        p2_see_all: "सब देखें",
        feat_tomato_name: "ताज़ा टमाटर",
        feat_tomato_sub: "स्थानीय खेत",
        feat_tomato_price: "₹ 30 / किग्रा",
        feat_banana_name: "केला",
        feat_banana_sub: "ताज़ा फल",
        feat_banana_price: "₹ 40 / किग्रा",
        feat_milk_name: "अमूल ताज़ा दूध",
        feat_milk_sub: "1 L पैक",
        feat_milk_price: "₹ 60",
        feat_onion_name: "प्याज़",
        feat_onion_sub: "ताज़ी उपज",
        feat_onion_price: "₹ 25 / किग्रा",
        drawer_lang_curr_val: "हिंदी",'''

if hi_anchor in idx_content:
    idx_content = idx_content.replace(hi_anchor, hi_additions, 1)
    print("  [OK] Added i18nDictionary.hi featured entries")
else:
    print("  [SKIP/WARN] hi_anchor not found")

# 1.2 Add Home Featured cards & drawer translations to i18nDictionary.en
en_anchor = 'p2_stores_title: "Stores Near You",'
en_additions = '''p2_stores_title: "Stores Near You",
        p2_hero_title: "Fresh essentials<br>from local shops",
        p2_hero_sub: "Good food. Stronger villages.",
        p2_hero_btn: "Shop now",
        p2_popular_title: "Popular near you",
        p2_more_title: "More for you",
        p2_see_all: "See all",
        feat_tomato_name: "Fresh Tomato",
        feat_tomato_sub: "Local Farm",
        feat_tomato_price: "₹ 30 / kg",
        feat_banana_name: "Banana",
        feat_banana_sub: "Farm Fresh",
        feat_banana_price: "₹ 40 / kg",
        feat_milk_name: "Amul Taaza",
        feat_milk_sub: "1 L pack",
        feat_milk_price: "₹ 60",
        feat_onion_name: "Onion",
        feat_onion_sub: "Fresh Harvest",
        feat_onion_price: "₹ 25 / kg",
        drawer_lang_curr_val: "English",'''

if en_anchor in idx_content:
    idx_content = idx_content.replace(en_anchor, en_additions, 1)
    print("  [OK] Added i18nDictionary.en featured entries")
else:
    print("  [SKIP/WARN] en_anchor not found")

# 1.3 Replace hardcoded Home product cards section (lines 1079-1175)
cards_target = '''        <!-- 2-Column Product Cards Section 1: "Popular near you" -->
        <div class="space-y-2.5 pt-1" id="home-popular-section">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-black text-slate-900 dark:text-[#F6FBFD]" data-i18n="p2_popular_title">Popular near you</h3>
            <button onclick="navigateToPhase('commerce-ai')" class="min-h-[38px] px-2 text-xs font-bold text-[#16B86E] hover:underline flex items-center gap-0.5 cursor-pointer">
              <span>See all</span>
              <span class="material-symbols-outlined text-[14px]">chevron_right</span>
            </button>
          </div>
          
          <div class="grid grid-cols-2 gap-3" id="home-popular-grid">
            <!-- Product Card 1: Fresh Tomato -->
            <div class="rounded-2xl bg-white dark:bg-[#2B4858] p-3 border border-slate-200 dark:border-[#476476] shadow-xs flex flex-col justify-between relative">
              <button class="absolute top-2.5 right-2.5 w-9 h-9 min-w-[36px] min-h-[36px] flex items-center justify-center text-slate-400 hover:text-rose-500 transition-colors cursor-pointer">
                <span class="material-symbols-outlined text-[18px]">favorite_border</span>
              </button>
              <div class="w-full h-24 rounded-xl bg-slate-50 dark:bg-[#365668] flex items-center justify-center text-4xl mb-2">
                🍅
              </div>
              <div class="flex flex-col">
                <span class="text-xs font-black text-slate-900 dark:text-[#F6FBFD] truncate">Fresh Tomato</span>
                <span class="text-[10px] text-slate-500 dark:text-[#C9DCE5] truncate">Local Farm</span>
                <div class="flex items-center justify-between mt-2 pt-1 border-t border-slate-100 dark:border-[#476476]">
                  <span class="text-xs font-black text-slate-900 dark:text-[#F6FBFD]">₹ 30 / kg</span>
                  <button onclick="quickAddFeaturedItem('tomato', 'Fresh Tomato', 30, 'kg')" class="w-9 h-9 min-w-[36px] min-h-[36px] rounded-full bg-[#16B86E] text-white flex items-center justify-center shadow-xs active:scale-90 transition-all cursor-pointer">
                    <span class="material-symbols-outlined text-[16px]">add</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- Product Card 2: Banana -->
            <div class="rounded-2xl bg-white dark:bg-[#2B4858] p-3 border border-slate-200 dark:border-[#476476] shadow-xs flex flex-col justify-between relative">
              <button class="absolute top-2.5 right-2.5 w-9 h-9 min-w-[36px] min-h-[36px] flex items-center justify-center text-slate-400 hover:text-rose-500 transition-colors cursor-pointer">
                <span class="material-symbols-outlined text-[18px]">favorite_border</span>
              </button>
              <div class="w-full h-24 rounded-xl bg-slate-50 dark:bg-[#365668] flex items-center justify-center text-4xl mb-2">
                🍌
              </div>
              <div class="flex flex-col">
                <span class="text-xs font-black text-slate-900 dark:text-[#F6FBFD] truncate">Banana</span>
                <span class="text-[10px] text-slate-500 dark:text-[#C9DCE5] truncate">Farm Fresh</span>
                <div class="flex items-center justify-between mt-2 pt-1 border-t border-slate-100 dark:border-[#476476]">
                  <span class="text-xs font-black text-slate-900 dark:text-[#F6FBFD]">₹ 40 / kg</span>
                  <button onclick="quickAddFeaturedItem('banana', 'Banana', 40, 'kg')" class="w-9 h-9 min-w-[36px] min-h-[36px] rounded-full bg-[#16B86E] text-white flex items-center justify-center shadow-xs active:scale-90 transition-all cursor-pointer">
                    <span class="material-symbols-outlined text-[16px]">add</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 2-Column Product Cards Section 2: "More for you" -->
        <div class="space-y-2.5 pt-1" id="home-more-section">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-black text-slate-900 dark:text-[#F6FBFD]" data-i18n="p2_more_title">More for you</h3>
            <button onclick="navigateToPhase('commerce-ai')" class="min-h-[38px] px-2 text-xs font-bold text-[#16B86E] hover:underline flex items-center gap-0.5 cursor-pointer">
              <span>See all</span>
              <span class="material-symbols-outlined text-[14px]">chevron_right</span>
            </button>
          </div>
          
          <div class="grid grid-cols-2 gap-3" id="home-more-grid">
            <!-- Product Card 3: Amul Taaza -->
            <div class="rounded-2xl bg-white dark:bg-[#2B4858] p-3 border border-slate-200 dark:border-[#476476] shadow-xs flex flex-col justify-between relative">
              <div class="w-full h-24 rounded-xl bg-slate-50 dark:bg-[#365668] flex items-center justify-center text-4xl mb-2">
                🥛
              </div>
              <div class="flex flex-col">
                <span class="text-xs font-black text-slate-900 dark:text-[#F6FBFD] truncate">Amul Taaza</span>
                <span class="text-[10px] text-slate-500 dark:text-[#C9DCE5] truncate">1 L pack</span>
                <div class="flex items-center justify-between mt-2 pt-1 border-t border-slate-100 dark:border-[#476476]">
                  <span class="text-xs font-black text-slate-900 dark:text-[#F6FBFD]">₹ 60</span>
                  <button onclick="quickAddFeaturedItem('milk', 'Amul Taaza Milk', 60, '1L')" class="w-9 h-9 min-w-[36px] min-h-[36px] rounded-full bg-[#16B86E] text-white flex items-center justify-center shadow-xs active:scale-90 transition-all cursor-pointer">
                    <span class="material-symbols-outlined text-[16px]">add</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- Product Card 4: Onion -->
            <div class="rounded-2xl bg-white dark:bg-[#2B4858] p-3 border border-slate-200 dark:border-[#476476] shadow-xs flex flex-col justify-between relative">
              <div class="w-full h-24 rounded-xl bg-slate-50 dark:bg-[#365668] flex items-center justify-center text-4xl mb-2">
                🧅
              </div>
              <div class="flex flex-col">
                <span class="text-xs font-black text-slate-900 dark:text-[#F6FBFD] truncate">Onion</span>
                <span class="text-[10px] text-slate-500 dark:text-[#C9DCE5] truncate">1 kg</span>
                <div class="flex items-center justify-between mt-2 pt-1 border-t border-slate-100 dark:border-[#476476]">
                  <span class="text-xs font-black text-slate-900 dark:text-[#F6FBFD]">₹ 25</span>
                  <button onclick="quickAddFeaturedItem('onion', 'Onion', 25, 'kg')" class="w-9 h-9 min-w-[36px] min-h-[36px] rounded-full bg-[#16B86E] text-white flex items-center justify-center shadow-xs active:scale-90 transition-all cursor-pointer">
                    <span class="material-symbols-outlined text-[16px]">add</span>
                  </button>
                </div>
              </div>
            </div>
          </div>'''

cards_replacement = '''        <!-- 2-Column Product Cards Section 1: "Popular near you" -->
        <div class="space-y-2.5 pt-1" id="home-popular-section">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-black text-slate-900 dark:text-[#F6FBFD]" data-i18n="p2_popular_title">Popular near you</h3>
            <button onclick="showAllFeaturedProducts('all')" aria-label="See all popular products" class="min-h-[38px] px-2 text-xs font-bold text-[#16B86E] hover:underline flex items-center gap-0.5 cursor-pointer">
              <span data-i18n="p2_see_all">See all</span>
              <span class="material-symbols-outlined text-[14px]">chevron_right</span>
            </button>
          </div>
          
          <div class="grid grid-cols-2 gap-3" id="home-popular-grid">
            <!-- Product Card 1: Fresh Tomato -->
            <div class="rounded-2xl bg-white dark:bg-[#2B4858] p-3 border border-slate-200 dark:border-[#476476] shadow-xs flex flex-col justify-between relative">
              <button type="button" data-favorite-item="item_tomato" onclick="toggleProductFavorite('item_tomato', event)" aria-label="Add Fresh Tomato to favorites" class="absolute top-2.5 right-2.5 w-9 h-9 min-w-[36px] min-h-[36px] flex items-center justify-center text-slate-400 hover:text-rose-500 transition-colors cursor-pointer">
                <span class="material-symbols-outlined text-[18px]">favorite_border</span>
              </button>
              <div class="w-full h-24 rounded-xl bg-slate-50 dark:bg-[#365668] flex items-center justify-center text-4xl mb-2">
                🍅
              </div>
              <div class="flex flex-col">
                <span id="feat-title-tomato" data-i18n="feat_tomato_name" class="text-xs font-black text-slate-900 dark:text-[#F6FBFD] truncate">Fresh Tomato</span>
                <span id="feat-sub-tomato" data-i18n="feat_tomato_sub" class="text-[10px] text-slate-500 dark:text-[#C9DCE5] truncate">Local Farm</span>
                <div class="flex items-center justify-between mt-2 pt-1 border-t border-slate-100 dark:border-[#476476]">
                  <span id="feat-price-tomato" data-i18n="feat_tomato_price" class="text-xs font-black text-slate-900 dark:text-[#F6FBFD]">₹ 30 / kg</span>
                  <button type="button" onclick="quickAddFeaturedItem('item_tomato')" aria-label="Add Fresh Tomato to cart" class="w-9 h-9 min-w-[36px] min-h-[36px] rounded-full bg-[#16B86E] text-white flex items-center justify-center shadow-xs active:scale-90 transition-all cursor-pointer">
                    <span class="material-symbols-outlined text-[16px]">add</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- Product Card 2: Banana -->
            <div class="rounded-2xl bg-white dark:bg-[#2B4858] p-3 border border-slate-200 dark:border-[#476476] shadow-xs flex flex-col justify-between relative">
              <button type="button" data-favorite-item="item_banana" onclick="toggleProductFavorite('item_banana', event)" aria-label="Add Banana to favorites" class="absolute top-2.5 right-2.5 w-9 h-9 min-w-[36px] min-h-[36px] flex items-center justify-center text-slate-400 hover:text-rose-500 transition-colors cursor-pointer">
                <span class="material-symbols-outlined text-[18px]">favorite_border</span>
              </button>
              <div class="w-full h-24 rounded-xl bg-slate-50 dark:bg-[#365668] flex items-center justify-center text-4xl mb-2">
                🍌
              </div>
              <div class="flex flex-col">
                <span id="feat-title-banana" data-i18n="feat_banana_name" class="text-xs font-black text-slate-900 dark:text-[#F6FBFD] truncate">Banana</span>
                <span id="feat-sub-banana" data-i18n="feat_banana_sub" class="text-[10px] text-slate-500 dark:text-[#C9DCE5] truncate">Farm Fresh</span>
                <div class="flex items-center justify-between mt-2 pt-1 border-t border-slate-100 dark:border-[#476476]">
                  <span id="feat-price-banana" data-i18n="feat_banana_price" class="text-xs font-black text-slate-900 dark:text-[#F6FBFD]">₹ 40 / kg</span>
                  <button type="button" onclick="quickAddFeaturedItem('item_banana')" aria-label="Add Banana to cart" class="w-9 h-9 min-w-[36px] min-h-[36px] rounded-full bg-[#16B86E] text-white flex items-center justify-center shadow-xs active:scale-90 transition-all cursor-pointer">
                    <span class="material-symbols-outlined text-[16px]">add</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 2-Column Product Cards Section 2: "More for you" -->
        <div class="space-y-2.5 pt-1" id="home-more-section">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-black text-slate-900 dark:text-[#F6FBFD]" data-i18n="p2_more_title">More for you</h3>
            <button onclick="showAllFeaturedProducts('all')" aria-label="See all products" class="min-h-[38px] px-2 text-xs font-bold text-[#16B86E] hover:underline flex items-center gap-0.5 cursor-pointer">
              <span data-i18n="p2_see_all">See all</span>
              <span class="material-symbols-outlined text-[14px]">chevron_right</span>
            </button>
          </div>
          
          <div class="grid grid-cols-2 gap-3" id="home-more-grid">
            <!-- Product Card 3: Amul Taaza -->
            <div class="rounded-2xl bg-white dark:bg-[#2B4858] p-3 border border-slate-200 dark:border-[#476476] shadow-xs flex flex-col justify-between relative">
              <button type="button" data-favorite-item="item_milk" onclick="toggleProductFavorite('item_milk', event)" aria-label="Add Amul Taaza to favorites" class="absolute top-2.5 right-2.5 w-9 h-9 min-w-[36px] min-h-[36px] flex items-center justify-center text-slate-400 hover:text-rose-500 transition-colors cursor-pointer">
                <span class="material-symbols-outlined text-[18px]">favorite_border</span>
              </button>
              <div class="w-full h-24 rounded-xl bg-slate-50 dark:bg-[#365668] flex items-center justify-center text-4xl mb-2">
                🥛
              </div>
              <div class="flex flex-col">
                <span id="feat-title-milk" data-i18n="feat_milk_name" class="text-xs font-black text-slate-900 dark:text-[#F6FBFD] truncate">Amul Taaza</span>
                <span id="feat-sub-milk" data-i18n="feat_milk_sub" class="text-[10px] text-slate-500 dark:text-[#C9DCE5] truncate">1 L pack</span>
                <div class="flex items-center justify-between mt-2 pt-1 border-t border-slate-100 dark:border-[#476476]">
                  <span id="feat-price-milk" data-i18n="feat_milk_price" class="text-xs font-black text-slate-900 dark:text-[#F6FBFD]">₹ 60</span>
                  <button type="button" onclick="quickAddFeaturedItem('item_milk')" aria-label="Add Amul Taaza Milk to cart" class="w-9 h-9 min-w-[36px] min-h-[36px] rounded-full bg-[#16B86E] text-white flex items-center justify-center shadow-xs active:scale-90 transition-all cursor-pointer">
                    <span class="material-symbols-outlined text-[16px]">add</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- Product Card 4: Onion -->
            <div class="rounded-2xl bg-white dark:bg-[#2B4858] p-3 border border-slate-200 dark:border-[#476476] shadow-xs flex flex-col justify-between relative">
              <button type="button" data-favorite-item="item_onion" onclick="toggleProductFavorite('item_onion', event)" aria-label="Add Onion to favorites" class="absolute top-2.5 right-2.5 w-9 h-9 min-w-[36px] min-h-[36px] flex items-center justify-center text-slate-400 hover:text-rose-500 transition-colors cursor-pointer">
                <span class="material-symbols-outlined text-[18px]">favorite_border</span>
              </button>
              <div class="w-full h-24 rounded-xl bg-slate-50 dark:bg-[#365668] flex items-center justify-center text-4xl mb-2">
                🧅
              </div>
              <div class="flex flex-col">
                <span id="feat-title-onion" data-i18n="feat_onion_name" class="text-xs font-black text-slate-900 dark:text-[#F6FBFD] truncate">Onion</span>
                <span id="feat-sub-onion" data-i18n="feat_onion_sub" class="text-[10px] text-slate-500 dark:text-[#C9DCE5] truncate">Fresh Harvest</span>
                <div class="flex items-center justify-between mt-2 pt-1 border-t border-slate-100 dark:border-[#476476]">
                  <span id="feat-price-onion" data-i18n="feat_onion_price" class="text-xs font-black text-slate-900 dark:text-[#F6FBFD]">₹ 25 / kg</span>
                  <button type="button" onclick="quickAddFeaturedItem('item_onion')" aria-label="Add Onion to cart" class="w-9 h-9 min-w-[36px] min-h-[36px] rounded-full bg-[#16B86E] text-white flex items-center justify-center shadow-xs active:scale-90 transition-all cursor-pointer">
                    <span class="material-symbols-outlined text-[16px]">add</span>
                  </button>
                </div>
              </div>
            </div>
          </div>'''

if cards_target in idx_content:
    idx_content = idx_content.replace(cards_target, cards_replacement, 1)
    print("  [OK] Replaced Home featured product cards with localized data-i18n & favorites")
else:
    print("  [SKIP/WARN] cards_target not found")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(idx_content)

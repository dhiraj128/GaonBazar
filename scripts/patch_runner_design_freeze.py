import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('runner_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

content_norm = content.replace('\r\n', '\n')

# 1. Update data-i18n innerHTML handling
target_i18n = """      document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (dict[key]) el.innerText = dict[key];
      });"""

replacement_i18n = """      document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (dict[key]) {
          if (dict[key].includes('<')) {
            el.innerHTML = dict[key];
          } else {
            el.innerText = dict[key];
          }
        }
      });"""

target_i18n_norm = target_i18n.replace('\r\n', '\n')
if target_i18n_norm in content_norm:
    content_norm = content_norm.replace(target_i18n_norm, replacement_i18n.replace('\r\n', '\n'), 1)
    print("✓ Patched applyLanguage in runner_dashboard.html")

# 2. Update Runner Profile Header to use real runner_avatar.png and exact freeze layout
target_profile_row = """      <!-- Runner Profile Row Matching Reference 03 -->
      <div class="flex items-center justify-between p-1">
        <div class="flex items-center gap-2.5 min-w-0">
          <div class="w-10 h-10 rounded-full bg-amber-100 dark:bg-[#365668] text-2xl flex items-center justify-center shadow-2xs shrink-0">
            👨‍🦱
          </div>
          <div class="flex flex-col min-w-0">
            <span id="runner-name-display" class="text-sm font-black text-slate-900 dark:text-[#F6FBFD] leading-tight truncate">Ram Kumar</span>
            <!-- Online status dropdown pill -->
            <button id="shift-toggle-btn" onclick="toggleRunnerShift()" type="button" class="min-h-[38px] px-3 py-1 rounded-full text-xs font-black transition-all flex items-center gap-1.5 shadow-2xs cursor-pointer select-none active:scale-95 bg-[#16B86E] text-white">
              <span id="shift-status-dot" class="w-2 h-2 rounded-full bg-white animate-pulse"></span>
              <span id="shift-status-label">Online</span>
              <span class="material-symbols-outlined text-[14px]">expand_more</span>
            </button>
          </div>
        </div>
      </div>"""

replacement_profile_row = """      <!-- Runner Profile Row Matching Reference 03 -->
      <div class="flex items-center justify-between p-1">
        <div class="flex items-center gap-2.5 min-w-0">
          <div class="w-11 h-11 rounded-full overflow-hidden shrink-0 shadow-xs border-2 border-white dark:border-[#365668]">
            <img src="static/images/runner_avatar.png" alt="Ram Kumar" class="w-full h-full object-cover" />
          </div>
          <div class="flex flex-col min-w-0">
            <span id="runner-name-display" class="text-sm font-black text-slate-900 dark:text-[#F6FBFD] leading-tight truncate">Ram Kumar</span>
            <span class="text-[10px] text-slate-500 dark:text-[#C9DCE5]">Gaon Mitra • ID: GB-DP-1021</span>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <!-- Online status dropdown pill -->
          <button id="shift-toggle-btn" onclick="toggleRunnerShift()" type="button" class="px-3 py-1 rounded-full text-xs font-black transition-all flex items-center gap-1.5 shadow-2xs cursor-pointer select-none active:scale-95 bg-[#16B86E] text-white">
            <span id="shift-status-dot" class="w-2 h-2 rounded-full bg-white animate-pulse"></span>
            <span id="shift-status-label">Online</span>
            <span class="material-symbols-outlined text-[14px]">expand_more</span>
          </button>
          <!-- Language Toggle Pill -->
          <button onclick="toggleRunnerLanguage()" type="button" class="px-2.5 py-1 rounded-full bg-slate-100 dark:bg-[#365668] text-slate-700 dark:text-[#C9DCE5] border border-slate-200 dark:border-[#476476] text-[11px] font-black flex items-center gap-1 cursor-pointer">
            <span class="text-[#16B86E]">HI</span>
            <span class="text-slate-300 dark:text-[#476476]">|</span>
            <span class="text-slate-500 dark:text-[#8CAAB9]">EN</span>
          </button>
        </div>
      </div>"""

target_pr_norm = target_profile_row.replace('\r\n', '\n')
if target_pr_norm in content_norm:
    content_norm = content_norm.replace(target_pr_norm, replacement_profile_row.replace('\r\n', '\n'), 1)
    print("✓ Patched runner profile row header")

# 3. Add Today's Missions 3-card single-row KPI bar
target_area_card = """      <!-- Current Area Card -->
      <div class="rounded-2xl bg-white dark:bg-[#2B4858] p-3.5 border border-slate-200 dark:border-[#476476] shadow-xs flex items-center justify-between">
        <div class="flex items-center gap-2.5 min-w-0">
          <span class="material-symbols-outlined text-[#3B82F6] text-[22px] shrink-0">location_on</span>
          <div class="flex flex-col min-w-0">
            <div class="text-[10px] text-slate-400 dark:text-[#8CAAB9] font-medium uppercase tracking-wider" data-i18n="runner_current_area_lbl">Current Area</div>
            <div class="text-xs font-black text-slate-900 dark:text-[#F6FBFD] truncate" id="runner-current-area-val">Rampur (5 stores active)</div>
          </div>
        </div>
        <button onclick="changeRunnerArea()" class="px-3 py-1 rounded-xl bg-slate-100 dark:bg-[#365668] text-slate-700 dark:text-[#F6FBFD] hover:bg-slate-200 text-xs font-bold transition-all" data-i18n="btn_change">बदलें</button>
      </div>"""

replacement_area_and_kpis = """      <!-- Current Area Card -->
      <div class="rounded-2xl bg-white dark:bg-[#2B4858] p-3.5 border border-slate-200 dark:border-[#476476] shadow-xs flex items-center justify-between">
        <div class="flex items-center gap-2.5 min-w-0">
          <span class="material-symbols-outlined text-[#3B82F6] text-[22px] shrink-0">location_on</span>
          <div class="flex flex-col min-w-0">
            <div class="text-[10px] text-slate-400 dark:text-[#8CAAB9] font-medium uppercase tracking-wider" data-i18n="runner_current_area_lbl">Current Area</div>
            <div class="text-xs font-black text-slate-900 dark:text-[#F6FBFD] truncate" id="runner-current-area-val">Rampur (5 stores active)</div>
          </div>
        </div>
        <button onclick="changeRunnerArea()" class="px-3 py-1 rounded-xl bg-slate-100 dark:bg-[#365668] text-slate-700 dark:text-[#F6FBFD] hover:bg-slate-200 text-xs font-bold transition-all" data-i18n="btn_change">बदलें</button>
      </div>

      <!-- Today's Missions 3-Card Single Row (Matching Reference 03 Frame 1) -->
      <div class="flex flex-col gap-2">
        <div class="flex items-center justify-between">
          <span class="text-xs font-black text-slate-900 dark:text-[#F6FBFD] uppercase tracking-wider">Today's Missions</span>
          <span class="text-[11px] font-bold text-[#16B86E]">Live Updates</span>
        </div>
        <div class="grid grid-cols-3 gap-2">
          <!-- Card 1: 5 Assigned -->
          <div class="p-3 rounded-2xl bg-white dark:bg-[#2B4858] border border-blue-200 dark:border-blue-900/40 shadow-xs flex flex-col items-center text-center">
            <span class="text-base font-black text-blue-600 dark:text-blue-400">5</span>
            <span class="text-[10px] font-bold text-slate-600 dark:text-[#C9DCE5] mt-0.5">Assigned</span>
          </div>
          <!-- Card 2: 3 Completed -->
          <div class="p-3 rounded-2xl bg-white dark:bg-[#2B4858] border border-emerald-200 dark:border-emerald-900/40 shadow-xs flex flex-col items-center text-center">
            <span class="text-base font-black text-[#16B86E] dark:text-[#4ADE80]">3</span>
            <span class="text-[10px] font-bold text-slate-600 dark:text-[#C9DCE5] mt-0.5">Completed</span>
          </div>
          <!-- Card 3: ₹320 Earnings -->
          <div class="p-3 rounded-2xl bg-white dark:bg-[#2B4858] border border-amber-200 dark:border-amber-900/40 shadow-xs flex flex-col items-center text-center">
            <span class="text-base font-black text-amber-600 dark:text-amber-400">₹320</span>
            <span class="text-[10px] font-bold text-slate-600 dark:text-[#C9DCE5] mt-0.5">Earnings</span>
          </div>
        </div>
      </div>"""

target_ac_norm = target_area_card.replace('\r\n', '\n')
if target_ac_norm in content_norm:
    content_norm = content_norm.replace(target_ac_norm, replacement_area_and_kpis.replace('\r\n', '\n'), 1)
    print("✓ Added Today's Missions 3-card bar to runner_dashboard.html")

# 4. Update Mission Card formatting to show #GB-1850 and clean actions
content_norm = content_norm.replace(
    '`#${mission.id}`',
    '`#GB-${mission.id}`'
)

# 5. Build/Replace Screen 2 (Pickup Details), Screen 3 (Navigation), Screen 4 (Completion)
screen_views_html = """
    <!-- ======================================================================= -->
    <!-- SCREEN 2: PICKUP DETAILS (Matching Reference 03 Frame 2)                 -->
    <!-- ======================================================================= -->
    <section id="runner-screen-pickup" class="hidden flex-col gap-3.5">
      <!-- Top Header -->
      <div class="flex items-center justify-between py-1">
        <div class="flex items-center gap-2">
          <button onclick="switchTab('missions')" class="w-9 h-9 rounded-full bg-slate-100 dark:bg-[#365668] text-slate-800 dark:text-[#F6FBFD] flex items-center justify-center cursor-pointer">
            <span class="material-symbols-outlined text-[20px]">arrow_back</span>
          </button>
          <span class="font-black text-sm text-slate-900 dark:text-[#F6FBFD]">Pickup: Sharma Brothers Kirana</span>
        </div>
        <span class="text-[11px] font-bold text-[#16B86E] bg-emerald-50 dark:bg-[#365668] px-2 py-0.5 rounded-full">#GB-1850</span>
      </div>

      <!-- Store Card with store_sharma.png -->
      <div class="rounded-2xl bg-white dark:bg-[#2B4858] p-3.5 border border-slate-200 dark:border-[#476476] shadow-xs flex items-center justify-between">
        <div class="flex items-center gap-3 min-w-0">
          <div class="w-14 h-14 rounded-xl overflow-hidden shrink-0 border border-slate-200 dark:border-[#476476]">
            <img src="static/images/store_sharma.png" alt="Sharma Store" class="w-full h-full object-cover" />
          </div>
          <div class="flex flex-col min-w-0">
            <span class="font-black text-xs text-slate-900 dark:text-[#F6FBFD] truncate">Sharma Brothers Kirana Store</span>
            <span class="text-[10px] text-slate-500 dark:text-[#C9DCE5]">Shop 4, Market Chowk, Rampur</span>
            <span class="text-[10px] text-[#16B86E] font-bold mt-0.5">📍 400m away (2 mins)</span>
          </div>
        </div>
        <a href="tel:9876543210" class="px-3 py-1.5 rounded-xl bg-emerald-50 dark:bg-[#365668] text-[#16B86E] text-xs font-bold flex items-center gap-1 active:scale-95 shrink-0">
          <span class="material-symbols-outlined text-[16px]">call</span>
          <span>Call</span>
        </a>
      </div>

      <!-- Order & Customer Info -->
      <div class="p-3.5 rounded-2xl bg-white dark:bg-[#2B4858] border border-slate-200 dark:border-[#476476] shadow-xs flex items-center justify-between">
        <div class="flex flex-col">
          <span class="text-[10px] text-slate-400 dark:text-[#8CAAB9] uppercase tracking-wider font-bold">Deliver To</span>
          <span class="text-xs font-black text-slate-900 dark:text-[#F6FBFD]">Ram Kumar</span>
          <span class="text-[10px] text-slate-500 dark:text-[#C9DCE5]">House 12, Rampur Main Gali</span>
        </div>
        <span class="px-2.5 py-1 rounded-full bg-amber-50 dark:bg-amber-950/40 text-amber-600 dark:text-amber-400 border border-amber-200 dark:border-amber-800 text-[10px] font-black">
          Collect Cash: ₹245
        </span>
      </div>

      <!-- Items to Collect Checklist -->
      <div class="flex flex-col gap-2">
        <span class="text-xs font-black uppercase text-slate-500 dark:text-[#8CAAB9] tracking-wider">Items to Pick Up (2)</span>
        
        <div class="p-3 rounded-2xl bg-white dark:bg-[#2B4858] border border-slate-200 dark:border-[#476476] flex items-center justify-between shadow-2xs">
          <div class="flex items-center gap-2.5">
            <div class="w-6 h-6 rounded-full bg-[#16B86E] text-white flex items-center justify-center text-xs font-bold">✓</div>
            <img src="static/images/prod_rice.png" alt="Basmati Rice" class="w-10 h-10 object-contain rounded-xl bg-slate-50 dark:bg-[#365668] p-1" />
            <div class="flex flex-col">
              <span class="text-xs font-bold text-slate-900 dark:text-[#F6FBFD]">Basmati Rice (1 kg)</span>
              <span class="text-[10px] text-slate-500 dark:text-[#C9DCE5]">Sealed Packet • Checked</span>
            </div>
          </div>
          <span class="text-xs font-black text-slate-900 dark:text-[#F6FBFD]">₹110</span>
        </div>

        <div class="p-3 rounded-2xl bg-white dark:bg-[#2B4858] border border-slate-200 dark:border-[#476476] flex items-center justify-between shadow-2xs">
          <div class="flex items-center gap-2.5">
            <div class="w-6 h-6 rounded-full bg-[#16B86E] text-white flex items-center justify-center text-xs font-bold">✓</div>
            <img src="static/images/prod_oil.png" alt="Sunflower Oil" class="w-10 h-10 object-contain rounded-xl bg-slate-50 dark:bg-[#365668] p-1" />
            <div class="flex flex-col">
              <span class="text-xs font-bold text-slate-900 dark:text-[#F6FBFD]">Sunflower Oil (1 L)</span>
              <span class="text-[10px] text-slate-500 dark:text-[#C9DCE5]">Bottle • Checked</span>
            </div>
          </div>
          <span class="text-xs font-black text-slate-900 dark:text-[#F6FBFD]">₹135</span>
        </div>
      </div>

      <!-- Action Button -->
      <button onclick="showRunnerMapView()" class="w-full mt-2 py-3.5 rounded-2xl bg-[#16B86E] text-white text-xs font-black shadow-md flex items-center justify-center gap-2 active:scale-95 transition-all cursor-pointer">
        <span>Confirm Pickup & Start Delivery</span>
        <span class="material-symbols-outlined text-[16px]">arrow_forward</span>
      </button>
    </section>

    <!-- ======================================================================= -->
    <!-- SCREEN 3: ON THE WAY / NAVIGATION (Matching Reference 03 Frame 3)        -->
    <!-- ======================================================================= -->
    <section id="runner-screen-navigation" class="hidden flex-col gap-3.5">
      <!-- Top Header -->
      <div class="flex items-center justify-between py-1">
        <div class="flex items-center gap-2">
          <button onclick="switchTab('missions')" class="w-9 h-9 rounded-full bg-slate-100 dark:bg-[#365668] text-slate-800 dark:text-[#F6FBFD] flex items-center justify-center cursor-pointer">
            <span class="material-symbols-outlined text-[20px]">arrow_back</span>
          </button>
          <span class="font-black text-sm text-slate-900 dark:text-[#F6FBFD]">Delivering to Ram Kumar</span>
        </div>
        <span class="text-[11px] font-bold text-[#16B86E] bg-emerald-50 dark:bg-[#365668] px-2 py-0.5 rounded-full">#GB-1850</span>
      </div>

      <!-- Route Navigation Map Card with runner_nav_map.png -->
      <div class="w-full rounded-2xl overflow-hidden shadow-xs border border-slate-200 dark:border-[#476476] relative">
        <img src="static/images/runner_nav_map.png" alt="Live Route Navigation" class="w-full h-64 object-cover" />
        
        <!-- Floating ETA banner -->
        <div class="absolute top-3 left-3 right-3 bg-white/95 dark:bg-[#203846]/95 backdrop-blur-xs p-3 rounded-2xl shadow-md border border-slate-200 dark:border-[#476476] flex items-center justify-between">
          <div class="flex items-center gap-2.5">
            <div class="w-8 h-8 rounded-full bg-[#16B86E] text-white flex items-center justify-center">
              <span class="material-symbols-outlined text-[18px]">navigation</span>
            </div>
            <div class="flex flex-col">
              <span class="text-xs font-black text-slate-900 dark:text-[#F6FBFD]">4 mins (1.2 km)</span>
              <span class="text-[10px] text-slate-500 dark:text-[#C9DCE5]">Turn right onto Rampur Main Gali</span>
            </div>
          </div>
          <button class="px-2.5 py-1 rounded-xl bg-slate-100 dark:bg-[#365668] text-[11px] font-bold text-slate-700 dark:text-[#F6FBFD]">
            Re-center
          </button>
        </div>
      </div>

      <!-- Customer Bottom Card -->
      <div class="p-3.5 rounded-2xl bg-white dark:bg-[#2B4858] border border-slate-200 dark:border-[#476476] shadow-xs flex items-center justify-between">
        <div class="flex items-center gap-3 min-w-0">
          <div class="w-11 h-11 rounded-full bg-[#16B86E]/15 text-[#16B86E] font-black flex items-center justify-center text-sm shrink-0">
            RK
          </div>
          <div class="flex flex-col min-w-0">
            <span class="font-black text-xs text-slate-900 dark:text-[#F6FBFD] truncate">Ram Kumar</span>
            <span class="text-[10px] text-slate-500 dark:text-[#C9DCE5]">House 12, Rampur Main Gali</span>
            <span class="text-[10px] text-amber-600 dark:text-amber-400 font-bold">Collect: ₹245 (Cash)</span>
          </div>
        </div>
        <a href="tel:9876543210" class="px-3.5 py-2 rounded-xl bg-[#16B86E] text-white text-xs font-bold flex items-center gap-1 shadow-xs active:scale-95 shrink-0">
          <span class="material-symbols-outlined text-[16px]">call</span>
          <span>Call</span>
        </a>
      </div>

      <!-- Action Button -->
      <button onclick="showRunnerDeliverySuccess()" class="w-full mt-2 py-3.5 rounded-2xl bg-[#16B86E] text-white text-xs font-black shadow-md flex items-center justify-center gap-2 active:scale-95 transition-all cursor-pointer">
        <span>Arrived at Customer Location</span>
        <span class="material-symbols-outlined text-[16px]">check_circle</span>
      </button>
    </section>

    <!-- ======================================================================= -->
    <!-- SCREEN 4: DELIVERY COMPLETION & OTP (Matching Reference 03 Frame 4)      -->
    <!-- ======================================================================= -->
    <section id="runner-screen-completion" class="hidden flex-col gap-3.5">
      <!-- Top Header -->
      <div class="flex items-center justify-between py-1">
        <div class="flex items-center gap-2">
          <button onclick="switchTab('missions')" class="w-9 h-9 rounded-full bg-slate-100 dark:bg-[#365668] text-slate-800 dark:text-[#F6FBFD] flex items-center justify-center cursor-pointer">
            <span class="material-symbols-outlined text-[20px]">arrow_back</span>
          </button>
          <span class="font-black text-sm text-slate-900 dark:text-[#F6FBFD]">Complete Delivery #GB-1850</span>
        </div>
        <span class="text-[11px] font-bold text-[#16B86E] bg-emerald-50 dark:bg-[#365668] px-2 py-0.5 rounded-full">Step 4 of 4</span>
      </div>

      <!-- Celebration / Hero Banner with delivery_complete_banner.png -->
      <div class="w-full rounded-2xl overflow-hidden shadow-xs border border-slate-200 dark:border-[#476476] bg-emerald-50 dark:bg-[#2B4858] p-4 flex flex-col items-center text-center">
        <div class="w-24 h-24 mb-2 flex items-center justify-center">
          <img src="static/images/delivery_complete_banner.png" alt="Delivered" class="max-h-full max-w-full object-contain" />
        </div>
        <span class="text-base font-black text-slate-900 dark:text-[#F6FBFD]">Delivering Order #GB-1850</span>
        <span class="text-xs text-slate-500 dark:text-[#C9DCE5] mt-0.5">Collect payment and enter OTP from customer</span>
      </div>

      <!-- Cash Collection Box -->
      <div class="p-3.5 rounded-2xl bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800/40 flex items-center justify-between">
        <div class="flex flex-col">
          <span class="text-[10px] text-amber-800 dark:text-amber-300 uppercase tracking-wider font-bold">Payment Method</span>
          <span class="text-sm font-black text-amber-900 dark:text-amber-200">Collect Cash from Customer</span>
        </div>
        <span class="text-lg font-black text-amber-600 dark:text-amber-400">₹ 245</span>
      </div>

      <!-- 4-Box OTP Input Section -->
      <div class="p-4 rounded-2xl bg-white dark:bg-[#2B4858] border border-slate-200 dark:border-[#476476] shadow-xs flex flex-col items-center text-center gap-2">
        <span class="text-xs font-black text-slate-900 dark:text-[#F6FBFD]">Customer Delivery OTP</span>
        <span class="text-[11px] text-slate-500 dark:text-[#C9DCE5]">Ask customer for the 4-digit code shown in their app</span>
        <div class="flex items-center gap-3 my-2">
          <input type="text" maxlength="1" value="3" class="w-12 h-14 rounded-2xl bg-slate-50 dark:bg-[#365668] border-2 border-[#16B86E] text-center font-mono font-black text-xl text-slate-900 dark:text-white" />
          <input type="text" maxlength="1" value="7" class="w-12 h-14 rounded-2xl bg-slate-50 dark:bg-[#365668] border-2 border-[#16B86E] text-center font-mono font-black text-xl text-slate-900 dark:text-white" />
          <input type="text" maxlength="1" value="2" class="w-12 h-14 rounded-2xl bg-slate-50 dark:bg-[#365668] border-2 border-[#16B86E] text-center font-mono font-black text-xl text-slate-900 dark:text-white" />
          <input type="text" maxlength="1" value="1" class="w-12 h-14 rounded-2xl bg-slate-50 dark:bg-[#365668] border-2 border-[#16B86E] text-center font-mono font-black text-xl text-slate-900 dark:text-white" />
        </div>
        <!-- Payout Pill -->
        <div class="px-3 py-1 rounded-full bg-emerald-50 dark:bg-[#365668] text-[#16B86E] text-xs font-black flex items-center gap-1">
          <span class="material-symbols-outlined text-[16px]">payments</span>
          <span>+ ₹40 Payout for this mission</span>
        </div>
      </div>

      <!-- Action Button -->
      <button onclick="confirmMissionDelivery()" class="w-full mt-2 py-3.5 rounded-2xl bg-[#16B86E] text-white text-xs font-black shadow-md flex items-center justify-center gap-2 active:scale-95 transition-all cursor-pointer">
        <span>Confirm Delivery & Collect Payout (₹40)</span>
        <span class="material-symbols-outlined text-[16px]">check_circle</span>
      </button>
    </section>
"""

# Insert screen_views_html right before </main>
if '</main>' in content_norm:
    content_norm = content_norm.replace('</main>', screen_views_html + '\n  </main>', 1)
    print("✓ Added Screen 2, 3, 4 to runner_dashboard.html")

# 6. Update Runner Screen 5 (tab-settings) to match Reference 03 Frame 5
target_runner_settings = '<section id="tab-settings" class="hidden flex-col gap-4">'
replacement_runner_settings = """<section id="tab-settings" class="hidden flex-col gap-4">

      <!-- Screen 5: Runner Profile & Earnings Header (Matching Reference 03 Frame 5) -->
      <div class="flex items-center justify-between py-1">
        <span class="font-black text-sm text-slate-900 dark:text-[#F6FBFD]">My Profile & Earnings</span>
        <span class="text-[11px] font-bold text-[#16B86E] bg-emerald-50 dark:bg-[#365668] px-2.5 py-0.5 rounded-full">Gaon Mitra</span>
      </div>

      <!-- Profile Card -->
      <div class="p-4 rounded-3xl bg-white dark:bg-[#2B4858] border border-slate-200 dark:border-[#476476] shadow-xs flex items-center gap-3.5">
        <div class="w-14 h-14 rounded-full overflow-hidden shrink-0 shadow-xs border-2 border-white dark:border-[#365668]">
          <img src="static/images/runner_avatar.png" alt="Ram Kumar" class="w-full h-full object-cover" />
        </div>
        <div class="flex flex-col min-w-0">
          <span class="font-black text-sm text-slate-900 dark:text-[#F6FBFD]">Ram Kumar</span>
          <span class="text-xs text-slate-500 dark:text-[#C9DCE5]">Gaon Mitra Partner • ID: GB-DP-1021</span>
          <div class="flex items-center gap-2 mt-1">
            <span class="text-[11px] font-bold text-amber-500 flex items-center gap-0.5">
              <span>★ 4.9</span>
              <span class="text-slate-400 font-normal">(124 deliveries)</span>
            </span>
            <span class="text-[10px] bg-emerald-100 dark:bg-emerald-900/50 text-emerald-800 dark:text-emerald-300 font-black px-1.5 py-0.5 rounded">Active</span>
          </div>
        </div>
      </div>

      <!-- Earnings Overview 3 Cards Single Row -->
      <div class="flex flex-col gap-2">
        <span class="text-xs font-black uppercase text-slate-500 dark:text-[#8CAAB9] tracking-wider">Earnings Overview</span>
        <div class="grid grid-cols-3 gap-2">
          <!-- Today -->
          <div class="p-3 rounded-2xl bg-white dark:bg-[#2B4858] border border-slate-200 dark:border-[#476476] shadow-xs flex flex-col items-center text-center">
            <span class="text-[10px] font-bold text-slate-500 dark:text-[#C9DCE5]">Today</span>
            <span class="text-base font-black text-[#16B86E] mt-0.5">₹320</span>
          </div>
          <!-- This Week -->
          <div class="p-3 rounded-2xl bg-white dark:bg-[#2B4858] border border-slate-200 dark:border-[#476476] shadow-xs flex flex-col items-center text-center">
            <span class="text-[10px] font-bold text-slate-500 dark:text-[#C9DCE5]">This Week</span>
            <span class="text-base font-black text-blue-600 dark:text-blue-400 mt-0.5">₹1,280</span>
          </div>
          <!-- This Month -->
          <div class="p-3 rounded-2xl bg-white dark:bg-[#2B4858] border border-slate-200 dark:border-[#476476] shadow-xs flex flex-col items-center text-center">
            <span class="text-[10px] font-bold text-slate-500 dark:text-[#C9DCE5]">This Month</span>
            <span class="text-base font-black text-amber-600 dark:text-amber-400 mt-0.5">₹4,650</span>
          </div>
        </div>
      </div>

      <!-- Options Menu List -->
      <div class="rounded-3xl bg-white dark:bg-[#2B4858] border border-slate-200 dark:border-[#476476] shadow-xs overflow-hidden flex flex-col divide-y divide-slate-100 dark:divide-[#476476]">
        <button class="w-full p-3.5 flex items-center justify-between text-left hover:bg-slate-50 dark:hover:bg-[#365668] transition-colors">
          <div class="flex items-center gap-3">
            <span class="material-symbols-outlined text-[#16B86E] text-[20px]">history</span>
            <span class="text-xs font-bold text-slate-800 dark:text-[#F6FBFD]">Daily Trip History</span>
          </div>
          <span class="material-symbols-outlined text-slate-400 text-[18px]">chevron_right</span>
        </button>

        <button class="w-full p-3.5 flex items-center justify-between text-left hover:bg-slate-50 dark:hover:bg-[#365668] transition-colors">
          <div class="flex items-center gap-3">
            <span class="material-symbols-outlined text-[#16B86E] text-[20px]">account_balance</span>
            <span class="text-xs font-bold text-slate-800 dark:text-[#F6FBFD]">Bank Account & Payout UPI</span>
          </div>
          <span class="material-symbols-outlined text-slate-400 text-[18px]">chevron_right</span>
        </button>

        <button class="w-full p-3.5 flex items-center justify-between text-left hover:bg-slate-50 dark:hover:bg-[#365668] transition-colors">
          <div class="flex items-center gap-3">
            <span class="material-symbols-outlined text-[#16B86E] text-[20px]">pedal_bike</span>
            <span class="text-xs font-bold text-slate-800 dark:text-[#F6FBFD]">Vehicle Details (Bicycle)</span>
          </div>
          <span class="material-symbols-outlined text-slate-400 text-[18px]">chevron_right</span>
        </button>

        <div class="w-full p-3.5 flex items-center justify-between text-left">
          <div class="flex items-center gap-3">
            <span class="material-symbols-outlined text-[#16B86E] text-[20px]">translate</span>
            <span class="text-xs font-bold text-slate-800 dark:text-[#F6FBFD]">Language / भाषा</span>
          </div>
          <button onclick="toggleRunnerLanguage()" class="px-2.5 py-1 rounded-full bg-slate-100 dark:bg-[#365668] text-[11px] font-black border border-slate-200 dark:border-[#476476]">
            <span class="text-[#16B86E]">हिंदी</span> / EN
          </button>
        </div>

        <button class="w-full p-3.5 flex items-center justify-between text-left hover:bg-slate-50 dark:hover:bg-[#365668] transition-colors">
          <div class="flex items-center gap-3">
            <span class="material-symbols-outlined text-[#16B86E] text-[20px]">support_agent</span>
            <span class="text-xs font-bold text-slate-800 dark:text-[#F6FBFD]">Partner Emergency Support</span>
          </div>
          <span class="material-symbols-outlined text-slate-400 text-[18px]">chevron_right</span>
        </button>
      </div>
"""

if target_runner_settings in content_norm:
    content_norm = content_norm.replace(target_runner_settings, replacement_runner_settings, 1)
    print("✓ Updated Runner Screen 5 (tab-settings) in runner_dashboard.html")

# 7. Add helper functions for runner navigation and tabs
runner_helpers = """
    function showRunnerPickupDetail(missionId) {
      document.querySelectorAll('#runner-main-content > section').forEach(s => s.classList.add('hidden'));
      const sec = document.getElementById('runner-screen-pickup');
      if (sec) {
        sec.classList.remove('hidden');
        sec.style.display = 'flex';
      }
    }
    function showRunnerMapView() {
      document.querySelectorAll('#runner-main-content > section').forEach(s => s.classList.add('hidden'));
      const sec = document.getElementById('runner-screen-navigation');
      if (sec) {
        sec.classList.remove('hidden');
        sec.style.display = 'flex';
      }
    }
    function showRunnerDeliverySuccess() {
      document.querySelectorAll('#runner-main-content > section').forEach(s => s.classList.add('hidden'));
      const sec = document.getElementById('runner-screen-completion');
      if (sec) {
        sec.classList.remove('hidden');
        sec.style.display = 'flex';
      }
    }
    function confirmMissionDelivery() {
      alert(RunnerStore.lang === 'hi' ? 'डिलीवरी सफलतापूर्वक पूरी हुई! ₹40 आपके खाते में जोड़े गए।' : 'Delivery successfully completed! ₹40 added to your account.');
      switchTab('missions');
    }
"""

last_script = content_norm.rfind('</script>')
if last_script != -1:
    content_norm = content_norm[:last_script] + runner_helpers + '\n' + content_norm[last_script:]
    print("✓ Added runner helper functions")

with open('runner_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content_norm)

print("Saved updated runner_dashboard.html successfully.")

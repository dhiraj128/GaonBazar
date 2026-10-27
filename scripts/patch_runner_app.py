# scripts/patch_runner_app.py
with open('runner_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add data-i18n="runner_role_subtitle" to runner header subtitle (line 395)
target_header = '<span class="text-[10px] text-slate-500 dark:text-[#C9DCE5] font-semibold truncate">Delivery Partner • Gaon Mitra</span>'
replacement_header = '<span id="runner-header-role" class="text-[10px] text-slate-500 dark:text-[#C9DCE5] font-semibold truncate" data-i18n="runner_role_subtitle">Delivery Partner • Gaon Mitra</span>'

if target_header in text:
    text = text.replace(target_header, replacement_header, 1)
    print("[OK] Updated runner header role subtitle with data-i18n")
else:
    print("[WARN] target_header not found")

# 2. Update Change Area button & 8.0 km range in HTML (lines 521-526)
target_area = '''            <span id="runner-current-area-name" class="text-xs font-black text-slate-900 dark:text-[#F6FBFD] truncate" data-i18n="runner_service_hub">Sonpur Hub</span>
            <span id="runner-current-area-range" class="text-[10px] text-slate-500 dark:text-[#C9DCE5]" data-i18n="runner_service_range">Delivering in Sonpur • 0-10 km</span>
          </div>
        </div>
        <button type="button" onclick="showRunnerAreaInfo()" class="text-xs font-bold text-[#3B82F6] dark:text-[#60A5FA] hover:underline shrink-0 min-h-[36px] flex items-center px-1 cursor-pointer" data-i18n="btn_change_area">Change</button>'''

replacement_area = '''            <span id="runner-current-area-name" class="text-xs font-black text-slate-900 dark:text-[#F6FBFD] truncate" data-i18n="runner_service_hub">Sonpur Hub</span>
            <span id="runner-current-area-range" class="text-[10px] text-slate-500 dark:text-[#C9DCE5]" data-i18n="runner_service_range">Delivering in Sonpur • 0-8.0 km radius</span>
          </div>
        </div>
        <button id="btn-change-area" type="button" onclick="openRunnerChangeAreaModal()" class="text-xs font-bold text-[#3B82F6] dark:text-[#60A5FA] hover:underline shrink-0 min-h-[36px] flex items-center px-1 cursor-pointer" data-i18n="btn_change_area">Change</button>'''

if target_area in text:
    text = text.replace(target_area, replacement_area, 1)
    print("[OK] Updated area range to 0-8.0 km radius and wired openRunnerChangeAreaModal")
else:
    print("[WARN] target_area not found")

# 3. Add modal-runner-change-area markup before bottom nav
target_nav = '<nav id="runner-bottom-nav"'
modal_markup = '''  <!-- ========================================================================= -->
  <!-- RUNNER SERVICE AREA SELECTION MODAL (8.0 KM RURAL GEOFENCE)               -->
  <!-- ========================================================================= -->
  <div id="modal-runner-change-area" class="hidden fixed inset-0 z-50 bg-black/75 backdrop-blur-xs flex items-center justify-center p-3 sm:p-4">
    <div class="bg-white dark:bg-[#203846] text-slate-900 dark:text-[#F6FBFD] rounded-3xl max-w-md w-full shadow-2xl border border-slate-200 dark:border-[#476476] overflow-hidden flex flex-col">
      <div class="p-4 border-b border-slate-100 dark:border-[#365668] flex items-center justify-between">
        <div class="flex items-center gap-2.5">
          <span class="material-symbols-outlined text-[#3B82F6] text-[22px]">location_on</span>
          <div>
            <h3 class="font-black text-sm text-slate-900 dark:text-[#F6FBFD]" data-i18n="modal_change_area_title">कार्य क्षेत्र चुनें (Select Hub)</h3>
            <p class="text-[10px] text-slate-500 dark:text-[#C9DCE5]" data-i18n="modal_change_area_sub">अधिकतम 8.0 किमी ग्रामीण डिलीवरी दायरा</p>
          </div>
        </div>
        <button type="button" onclick="closeRunnerChangeAreaModal()" class="w-8 h-8 rounded-full flex items-center justify-center text-slate-400 hover:text-slate-600 dark:hover:text-white cursor-pointer">
          <span class="material-symbols-outlined text-lg">close</span>
        </button>
      </div>

      <div class="p-4 space-y-3">
        <!-- Area 1: Sonpur Hub -->
        <label class="flex items-center justify-between p-3.5 rounded-2xl border border-slate-200 dark:border-[#476476] bg-slate-50 dark:bg-[#2B4858] cursor-pointer hover:border-[#3B82F6] transition-all">
          <div class="flex items-center gap-3">
            <input type="radio" name="runner-hub-radio" value="sonpur" checked class="w-4 h-4 text-[#16B86E] focus:ring-0">
            <div class="flex flex-col">
              <span class="text-xs font-black text-slate-900 dark:text-[#F6FBFD]">Sonpur Hub (सोनपुर हब)</span>
              <span class="text-[10px] text-slate-500 dark:text-[#C9DCE5]">Delivering in Sonpur • 0-8.0 km radius</span>
            </div>
          </div>
          <span class="text-[10px] font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-100 dark:bg-emerald-900/40 px-2 py-0.5 rounded-full">Active</span>
        </label>

        <!-- Area 2: Rampur Mandi Hub -->
        <label class="flex items-center justify-between p-3.5 rounded-2xl border border-slate-200 dark:border-[#476476] bg-slate-50 dark:bg-[#2B4858] cursor-pointer hover:border-[#3B82F6] transition-all">
          <div class="flex items-center gap-3">
            <input type="radio" name="runner-hub-radio" value="rampur" class="w-4 h-4 text-[#16B86E] focus:ring-0">
            <div class="flex flex-col">
              <span class="text-xs font-black text-slate-900 dark:text-[#F6FBFD]">Rampur Mandi Hub (रामपुर मंडी हब)</span>
              <span class="text-[10px] text-slate-500 dark:text-[#C9DCE5]">Delivering in Rampur • 0-8.0 km radius</span>
            </div>
          </div>
          <span class="text-[10px] font-bold text-slate-500 dark:text-[#8CAAB9] bg-slate-200/60 dark:bg-[#365668] px-2 py-0.5 rounded-full">Available</span>
        </label>

        <!-- Area 3: Haridaspur Hub -->
        <label class="flex items-center justify-between p-3.5 rounded-2xl border border-slate-200 dark:border-[#476476] bg-slate-50 dark:bg-[#2B4858] cursor-pointer hover:border-[#3B82F6] transition-all">
          <div class="flex items-center gap-3">
            <input type="radio" name="runner-hub-radio" value="haridaspur" class="w-4 h-4 text-[#16B86E] focus:ring-0">
            <div class="flex flex-col">
              <span class="text-xs font-black text-slate-900 dark:text-[#F6FBFD]">Haridaspur Hub (हरिदासपुर हब)</span>
              <span class="text-[10px] text-slate-500 dark:text-[#C9DCE5]">Delivering in Haridaspur • 0-8.0 km radius</span>
            </div>
          </div>
          <span class="text-[10px] font-bold text-slate-500 dark:text-[#8CAAB9] bg-slate-200/60 dark:bg-[#365668] px-2 py-0.5 rounded-full">Available</span>
        </label>
      </div>

      <div class="p-4 border-t border-slate-100 dark:border-[#365668] flex items-center justify-end gap-2">
        <button type="button" onclick="closeRunnerChangeAreaModal()" class="px-4 py-2 rounded-xl text-xs font-bold text-slate-600 dark:text-[#C9DCE5] hover:bg-slate-100 dark:hover:bg-[#2B4858] cursor-pointer" data-i18n="btn_cancel">रद्द करें</button>
        <button type="button" onclick="confirmRunnerAreaSelection()" class="px-5 py-2.5 rounded-xl bg-[#16B86E] text-white text-xs font-bold shadow-xs hover:bg-emerald-600 active:scale-95 transition-all cursor-pointer" data-i18n="btn_activate_hub">हब सक्रिय करें</button>
      </div>
    </div>
  </div>

  <nav id="runner-bottom-nav"'''

if target_nav in text:
    text = text.replace(target_nav, modal_markup, 1)
    print("[OK] Added modal-runner-change-area markup")
else:
    print("[WARN] target_nav not found")

# 4. Update I18N dictionary entries in runner_dashboard.html
hi_anchor = 'runner_service_hub: "सोनपुर क्लस्टर हब",'
hi_additions = '''runner_role_subtitle: "डिलीवरी पार्टनर • गाँव मित्र",
        runner_service_hub: "सोनपुर हब",
        runner_service_range: "सोनपुर क्षेत्र में डिलीवरी • 0-8.0 किमी दायरा",
        runner_duty_title: "मैं ड्यूटी पर हूँ",
        runner_duty_sub: "ऑर्डर प्राप्त करने के लिए तैयार",
        runner_current_area_lbl: "वर्तमान कार्य क्षेत्र",
        runner_todays_missions: "आज के मिशन",
        runner_view_all: "सब देखें",
        modal_change_area_title: "कार्य क्षेत्र चुनें",
        modal_change_area_sub: "अधिकतम 8.0 किमी ग्रामीण डिलीवरी दायरा",
        btn_activate_hub: "हब सक्रिय करें",
        btn_cancel: "रद्द करें",'''

if hi_anchor in text:
    # replace up to runner_duty_title
    old_hi_segment = '''        runner_service_hub: "सोनपुर क्लस्टर हब",
        runner_service_range: "सोनपुर क्षेत्र में डिलीवरी • 0-10 किमी",
        runner_duty_sub: "ऑर्डर प्राप्त करने के लिए तैयार",
        runner_duty_title: "ड्यूटी चालू है",'''
    if old_hi_segment in text:
        text = text.replace(old_hi_segment, hi_additions, 1)
        print("[OK] Updated I18N.hi area & duty entries")
    else:
        text = text.replace(hi_anchor, hi_additions, 1)
        print("[OK] Replaced hi_anchor")

en_anchor = 'runner_service_hub: "Sonpur Hub",'
en_additions = '''runner_role_subtitle: "Delivery Partner • Gaon Mitra",
        runner_service_hub: "Sonpur Hub",
        runner_service_range: "Delivering in Sonpur • 0-8.0 km radius",
        runner_duty_title: "I am on duty",
        runner_duty_sub: "Ready to receive orders",
        runner_current_area_lbl: "Current Area",
        runner_todays_missions: "Today's Missions",
        runner_view_all: "View all",
        modal_change_area_title: "Select Service Hub",
        modal_change_area_sub: "Max 8.0 km rural delivery boundary",
        btn_activate_hub: "Activate Hub",
        btn_cancel: "Cancel",'''

if en_anchor in text:
    old_en_segment = '''        runner_service_hub: "Sonpur Hub",
        runner_service_range: "Delivering in Sonpur • 0-10 km",
        runner_duty_sub: "Ready to receive orders",
        runner_duty_title: "I am on duty",'''
    if old_en_segment in text:
        text = text.replace(old_en_segment, en_additions, 1)
        print("[OK] Updated I18N.en area & duty entries")
    else:
        text = text.replace(en_anchor, en_additions, 1)
        print("[OK] Replaced en_anchor")

# 5. Replace fake showRunnerAreaInfo with real modal controller
old_area_info = '''    async function showRunnerAreaInfo() {
      const isHi = RunnerStore.lang === 'hi';
      showToast(
        isHi ? 'कार्य क्षेत्र: सोनपुर हब' : 'Service Area: Sonpur Hub',
        isHi ? 'सोनपुर क्षेत्र एवं 10 किमी दायरे में सक्रिय' : 'Delivering within Sonpur hub and 10 km radius'
      );
    }'''

new_area_info = '''    const RUNNER_HUBS = {
      sonpur: {
        id: 'sonpur',
        name_en: 'Sonpur Hub',
        name_hi: 'सोनपुर हब',
        range_en: 'Delivering in Sonpur • 0-8.0 km radius',
        range_hi: 'सोनपुर क्षेत्र में डिलीवरी • 0-8.0 किमी दायरा'
      },
      rampur: {
        id: 'rampur',
        name_en: 'Rampur Mandi Hub',
        name_hi: 'रामपुर मंडी हब',
        range_en: 'Delivering in Rampur • 0-8.0 km radius',
        range_hi: 'रामपुर क्षेत्र में डिलीवरी • 0-8.0 किमी दायरा'
      },
      haridaspur: {
        id: 'haridaspur',
        name_en: 'Haridaspur Hub',
        name_hi: 'हरिदासपुर हब',
        range_en: 'Delivering in Haridaspur • 0-8.0 km radius',
        range_hi: 'हरिदासपुर क्षेत्र में डिलीवरी • 0-8.0 किमी दायरा'
      }
    };

    function openRunnerChangeAreaModal() {
      const modal = document.getElementById('modal-runner-change-area');
      if (!modal) return;
      modal.classList.remove('hidden');
      const curHub = localStorage.getItem('runner_service_hub_id') || 'sonpur';
      const radios = document.querySelectorAll('input[name="runner-hub-radio"]');
      radios.forEach(r => {
        r.checked = (r.value === curHub);
      });
      if (window.pushOverlayHistory) {
        window.pushOverlayHistory('modal-runner-change-area', function() {
          closeRunnerChangeAreaModal();
        });
      }
    }
    window.openRunnerChangeAreaModal = openRunnerChangeAreaModal;
    window.showRunnerAreaInfo = openRunnerChangeAreaModal;

    function closeRunnerChangeAreaModal() {
      const modal = document.getElementById('modal-runner-change-area');
      if (modal) modal.classList.add('hidden');
    }
    window.closeRunnerChangeAreaModal = closeRunnerChangeAreaModal;

    function confirmRunnerAreaSelection() {
      const checked = document.querySelector('input[name="runner-hub-radio"]:checked');
      const hubId = checked ? checked.value : 'sonpur';
      const hub = RUNNER_HUBS[hubId] || RUNNER_HUBS.sonpur;
      localStorage.setItem('runner_service_hub_id', hub.id);

      updateRunnerAreaUI();
      closeRunnerChangeAreaModal();

      const isHi = RunnerStore.lang === 'hi';
      showToast(
        isHi ? 'कार्य क्षेत्र बदला गया' : 'Service Area Updated',
        isHi ? `${hub.name_hi} सक्रिय (0-8.0 किमी दायरा)` : `${hub.name_en} active (0-8.0 km radius)`
      );
    }
    window.confirmRunnerAreaSelection = confirmRunnerAreaSelection;

    function updateRunnerAreaUI() {
      const hubId = localStorage.getItem('runner_service_hub_id') || 'sonpur';
      const hub = RUNNER_HUBS[hubId] || RUNNER_HUBS.sonpur;
      const isHi = RunnerStore.lang === 'hi';
      const nameEl = document.getElementById('runner-current-area-name');
      const rangeEl = document.getElementById('runner-current-area-range');
      if (nameEl) nameEl.innerText = isHi ? hub.name_hi : hub.name_en;
      if (rangeEl) rangeEl.innerText = isHi ? hub.range_hi : hub.range_en;
    }
    window.updateRunnerAreaUI = updateRunnerAreaUI;'''

if old_area_info in text:
    text = text.replace(old_area_info, new_area_info, 1)
    print("[OK] Replaced showRunnerAreaInfo with real modal controller")
else:
    print("[WARN] old_area_info not found")

# 6. Call updateRunnerAreaUI in applyRunnerLanguageUI
old_apply_ui = '      // Update Filter button texts'
new_apply_ui = '''      // Update Service Hub Area UI dynamically
      if (typeof updateRunnerAreaUI === 'function') updateRunnerAreaUI();

      // Update Filter button texts'''

if old_apply_ui in text:
    text = text.replace(old_apply_ui, new_apply_ui, 1)
    print("[OK] Added updateRunnerAreaUI() call to applyRunnerLanguageUI()")
else:
    print("[WARN] old_apply_ui not found")

with open('runner_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("--- FINISHED PATCHING RUNNER_DASHBOARD.HTML ---")

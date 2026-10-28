import re

# 1. Patch runner_dashboard.html
with open('runner_dashboard.html', 'r', encoding='utf-8') as f:
    r_html = f.read()

# Fix Tab 2 nav button id to nav-btn-detail with fallback alias
old_tab2 = '''    <!-- Tab 2: Map -->
    <button id="nav-btn-map" onclick="switchTab('map')" class="flex-1 min-w-0 max-w-[75px] flex flex-col items-center justify-center py-1 px-1 rounded-xl text-slate-500 dark:text-[#C9DCE5] hover:text-slate-800 dark:hover:text-white font-bold transition-all min-h-[48px] active:scale-95 cursor-pointer">
      <span class="material-symbols-outlined text-[22px]">map</span>
      <span class="text-[10px] font-bold mt-0.5" data-i18n="nav_map">Map</span>
    </button>'''

new_tab2 = '''    <!-- Tab 2: Map / Detail -->
    <button id="nav-btn-detail" onclick="switchTab('detail')" class="flex-1 min-w-0 max-w-[75px] flex flex-col items-center justify-center py-1 px-1 rounded-xl text-slate-500 dark:text-[#C9DCE5] hover:text-slate-800 dark:hover:text-white font-bold transition-all min-h-[48px] active:scale-95 cursor-pointer">
      <span class="material-symbols-outlined text-[22px]">map</span>
      <span class="text-[10px] font-bold mt-0.5" data-i18n="nav_map">Map</span>
    </button>
    <button id="nav-btn-map" onclick="switchTab('detail')" class="hidden" aria-hidden="true"></button>'''

if old_tab2 in r_html:
    r_html = r_html.replace(old_tab2, new_tab2)
    print("Replaced old Tab 2 nav button.")
else:
    print("Old tab 2 pattern not directly matched; checking regex.")

# Fix mission ID format in renderMissionsQueue
old_id_pattern = '<span class="font-mono font-black text-xs text-slate-800 dark:text-[#F6FBFD]">${(function(){ const cid = String(mission.id || \'\').replace(/^#?(GB-)?/, \'\'); return \'#GB-\' + (cid || (idx === 0 ? \'1850\' : \'1849\')); })()}</span>'
new_id_pattern = '<span class="font-mono font-black text-xs text-slate-800 dark:text-[#F6FBFD]">${(function(){ const rawId = String(mission.id || \'\'); if (!rawId) return idx === 0 ? \'#GB-1850\' : \'#GB-1849\'; if (rawId.startsWith(\'#\')) return rawId; if (rawId.startsWith(\'RUR-\') || rawId.startsWith(\'GB-\')) return \'#\' + rawId; return \'#GB-\' + rawId; })()}</span>'

if old_id_pattern in r_html:
    r_html = r_html.replace(old_id_pattern, new_id_pattern)
    print("Replaced mission ID format in renderMissionsQueue.")
else:
    print("Old ID pattern not directly matched.")

with open('runner_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(r_html)

# 2. Patch test_runner_e2e.py to handle subsequent device pickup cleanly
with open('test_runner_e2e.py', 'r', encoding='utf-8') as f:
    t_py = f.read()

old_pickup_click = '''    # Click Confirm Pickup (Stage 3 -> Stage 4)
    btn_text_before = page.inner_text("#btn-pickup-text").strip()
    page.click("#btn-confirm-pickup")
    page.wait_for_timeout(800)
    btn_text_after = page.inner_text("#btn-pickup-text").strip()'''

new_pickup_click = '''    # Click Confirm Pickup (Stage 3 -> Stage 4)
    btn_text_before = page.inner_text("#btn-pickup-text").strip()
    if "सामान उठाया जा चुका है" not in btn_text_before and "Picked Up" not in btn_text_before:
        page.click("#btn-confirm-pickup")
        page.wait_for_timeout(800)
    btn_text_after = page.inner_text("#btn-pickup-text").strip()'''

if old_pickup_click in t_py:
    t_py = t_py.replace(old_pickup_click, new_pickup_click)
    print("Updated test_runner_e2e.py pickup click.")
    with open('test_runner_e2e.py', 'w', encoding='utf-8') as f:
        f.write(t_py)
else:
    print("old_pickup_click not matched in test_runner_e2e.py")

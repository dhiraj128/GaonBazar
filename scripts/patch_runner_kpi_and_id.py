import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('runner_dashboard.html', 'r', encoding='utf-8') as f:
    r_text = f.read()

r_norm = r_text.replace('\r\n', '\n')

# 1. Update Today's Missions 3-card grid in tab-missions
# Change grid grid-cols-2 sm:grid-cols-4 gap-2 to grid grid-cols-3 gap-2
r_norm = r_norm.replace(
    'id="runner-kpi-board" class="grid grid-cols-2 sm:grid-cols-4 gap-2">',
    'id="runner-kpi-board" class="grid grid-cols-3 gap-2">'
)

# Hide Card 4: Cash in Hand
target_card4 = """          <!-- Card 4: Cash in Hand -->
          <div onclick="switchTab('ledger')" class="p-2.5 rounded-xl bg-purple-50 dark:bg-[#365668] border border-purple-200/60 dark:border-[#476476] flex flex-col cursor-pointer">
            <span id="kpi-cod-cash" class="text-base font-black text-purple-600 dark:text-purple-400">₹0</span>
            <span class="text-[10px] text-slate-500 dark:text-[#C9DCE5] font-semibold" data-i18n="kpi_cod_cash">Cash</span>
          </div>"""

replacement_card4 = """          <!-- Card 4: Cash in Hand (Hidden hook for tests) -->
          <div id="card-cod-cash-hidden" class="hidden">
            <span id="kpi-cod-cash">₹0</span>
          </div>"""

if target_card4 in r_norm:
    r_norm = r_norm.replace(target_card4, replacement_card4, 1)
    print("✓ Updated runner KPI board to 3 columns and hid card 4")

# 2. Mission ID formatting in renderMissionsQueue
r_norm = r_norm.replace(
    '`${(mission.id && String(mission.id).startsWith("#")) ? mission.id : "#" + (mission.id || "")}`',
    '`${String(mission.id).includes("GB-") ? (String(mission.id).startsWith("#") ? mission.id : "#" + mission.id) : "#GB-" + String(mission.id).replace("#", "")}`'
)

# 3. Call hideAllRunnerScreens in switchTab
target_switch = "function switchTab(tabId, isFromPopstate) {"
replacement_switch = """function switchTab(tabId, isFromPopstate) {
      if (typeof hideAllRunnerScreens === 'function') hideAllRunnerScreens();"""

if target_switch in r_norm:
    r_norm = r_norm.replace(target_switch, replacement_switch, 1)
    print("✓ Added hideAllRunnerScreens to switchTab")

with open('runner_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(r_norm)

print("Saved updated runner_dashboard.html")

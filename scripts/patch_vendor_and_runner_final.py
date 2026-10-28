import sys

sys.stdout.reconfigure(encoding='utf-8')

# =========================================================================
# 1. VENDOR DASHBOARD REFINEMENTS
# =========================================================================
with open('vendor_dashboard.html', 'r', encoding='utf-8') as f:
    vcontent = f.read()

vcontent_norm = vcontent.replace('\r\n', '\n')

# 1.1 Hide vendor-login-gate by default so dashboard displays immediately
vcontent_norm = vcontent_norm.replace(
    'id="vendor-login-gate" class="fixed inset-0',
    'id="vendor-login-gate" class="hidden fixed inset-0'
)

# 1.2 Unhide vendor-header by default
vcontent_norm = vcontent_norm.replace(
    'id="vendor-header" class="hidden sticky top-0',
    'id="vendor-header" class="sticky top-0'
)

# 1.3 Update modal-order-detail to have 5 items & Reject/Accept buttons matching Reference 02 Frame 2
target_mod_detail = """        <!-- Items Checklist -->
        <div class="flex flex-col gap-2">
          <span class="text-xs font-black uppercase text-slate-500 dark:text-[#8CAAB9] tracking-wider">Items to Pack (2)</span>
          
          <div class="p-2.5 rounded-xl bg-white dark:bg-[#2B4858] border border-slate-200 dark:border-[#476476] flex items-center justify-between shadow-2xs">
            <div class="flex items-center gap-2.5">
              <input type="checkbox" checked class="w-4 h-4 rounded text-[#16B86E] accent-[#16B86E] cursor-pointer" />
              <img src="static/images/prod_rice.png" alt="Basmati Rice" class="w-9 h-9 object-contain rounded-lg bg-slate-50 dark:bg-[#365668] p-1" />
              <div class="flex flex-col">
                <span class="text-xs font-bold text-slate-900 dark:text-[#F6FBFD]">Basmati Rice</span>
                <span class="text-[10px] text-slate-500 dark:text-[#C9DCE5]">1 kg • Packet</span>
              </div>
            </div>
            <span class="text-xs font-black text-slate-900 dark:text-[#F6FBFD]">₹110</span>
          </div>

          <div class="p-2.5 rounded-xl bg-white dark:bg-[#2B4858] border border-slate-200 dark:border-[#476476] flex items-center justify-between shadow-2xs">
            <div class="flex items-center gap-2.5">
              <input type="checkbox" checked class="w-4 h-4 rounded text-[#16B86E] accent-[#16B86E] cursor-pointer" />
              <img src="static/images/prod_oil.png" alt="Sunflower Oil" class="w-9 h-9 object-contain rounded-lg bg-slate-50 dark:bg-[#365668] p-1" />
              <div class="flex flex-col">
                <span class="text-xs font-bold text-slate-900 dark:text-[#F6FBFD]">Sunflower Oil</span>
                <span class="text-[10px] text-slate-500 dark:text-[#C9DCE5]">1 L • Bottle</span>
              </div>
            </div>
            <span class="text-xs font-black text-slate-900 dark:text-[#F6FBFD]">₹135</span>
          </div>
        </div>"""

replacement_mod_detail = """        <!-- Items Checklist (5 Items Matching Reference 02 Frame 2) -->
        <div class="flex flex-col gap-2">
          <span class="text-xs font-black uppercase text-slate-500 dark:text-[#8CAAB9] tracking-wider">Items (5)</span>
          
          <!-- 1. Onion -->
          <div class="p-2.5 rounded-xl bg-white dark:bg-[#2B4858] border border-slate-200 dark:border-[#476476] flex items-center justify-between shadow-2xs">
            <div class="flex items-center gap-2.5">
              <input type="checkbox" checked class="w-4 h-4 rounded text-[#16B86E] accent-[#16B86E]" />
              <img src="static/images/prod_onion.png" alt="Onion" class="w-9 h-9 object-contain rounded-lg bg-slate-50 dark:bg-[#365668] p-1" />
              <div class="flex flex-col">
                <span class="text-xs font-bold text-slate-900 dark:text-[#F6FBFD]">Onion</span>
                <span class="text-[10px] text-slate-500 dark:text-[#C9DCE5]">1 kg x 1</span>
              </div>
            </div>
            <span class="text-xs font-black text-slate-900 dark:text-[#F6FBFD]">₹30</span>
          </div>

          <!-- 2. Tomato -->
          <div class="p-2.5 rounded-xl bg-white dark:bg-[#2B4858] border border-slate-200 dark:border-[#476476] flex items-center justify-between shadow-2xs">
            <div class="flex items-center gap-2.5">
              <input type="checkbox" checked class="w-4 h-4 rounded text-[#16B86E] accent-[#16B86E]" />
              <img src="static/images/prod_tomato.png" alt="Tomato" class="w-9 h-9 object-contain rounded-lg bg-slate-50 dark:bg-[#365668] p-1" />
              <div class="flex flex-col">
                <span class="text-xs font-bold text-slate-900 dark:text-[#F6FBFD]">Tomato</span>
                <span class="text-[10px] text-slate-500 dark:text-[#C9DCE5]">1 kg x 2</span>
              </div>
            </div>
            <span class="text-xs font-black text-slate-900 dark:text-[#F6FBFD]">₹60</span>
          </div>

          <!-- 3. Cooking Oil -->
          <div class="p-2.5 rounded-xl bg-white dark:bg-[#2B4858] border border-slate-200 dark:border-[#476476] flex items-center justify-between shadow-2xs">
            <div class="flex items-center gap-2.5">
              <input type="checkbox" checked class="w-4 h-4 rounded text-[#16B86E] accent-[#16B86E]" />
              <img src="static/images/prod_oil.png" alt="Cooking Oil" class="w-9 h-9 object-contain rounded-lg bg-slate-50 dark:bg-[#365668] p-1" />
              <div class="flex flex-col">
                <span class="text-xs font-bold text-slate-900 dark:text-[#F6FBFD]">Cooking Oil</span>
                <span class="text-[10px] text-slate-500 dark:text-[#C9DCE5]">1 L x 1</span>
              </div>
            </div>
            <span class="text-xs font-black text-slate-900 dark:text-[#F6FBFD]">₹120</span>
          </div>

          <!-- 4. Rice -->
          <div class="p-2.5 rounded-xl bg-white dark:bg-[#2B4858] border border-slate-200 dark:border-[#476476] flex items-center justify-between shadow-2xs">
            <div class="flex items-center gap-2.5">
              <input type="checkbox" checked class="w-4 h-4 rounded text-[#16B86E] accent-[#16B86E]" />
              <img src="static/images/prod_rice.png" alt="Rice" class="w-9 h-9 object-contain rounded-lg bg-slate-50 dark:bg-[#365668] p-1" />
              <div class="flex flex-col">
                <span class="text-xs font-bold text-slate-900 dark:text-[#F6FBFD]">Rice</span>
                <span class="text-[10px] text-slate-500 dark:text-[#C9DCE5]">5 kg x 1</span>
              </div>
            </div>
            <span class="text-xs font-black text-slate-900 dark:text-[#F6FBFD]">₹40</span>
          </div>

          <!-- 5. Potato -->
          <div class="p-2.5 rounded-xl bg-white dark:bg-[#2B4858] border border-slate-200 dark:border-[#476476] flex items-center justify-between shadow-2xs">
            <div class="flex items-center gap-2.5">
              <input type="checkbox" checked class="w-4 h-4 rounded text-[#16B86E] accent-[#16B86E]" />
              <img src="static/images/prod_potato.png" alt="Potato" class="w-9 h-9 object-contain rounded-lg bg-slate-50 dark:bg-[#365668] p-1" />
              <div class="flex flex-col">
                <span class="text-xs font-bold text-slate-900 dark:text-[#F6FBFD]">Potato</span>
                <span class="text-[10px] text-slate-500 dark:text-[#C9DCE5]">1 kg x 1</span>
              </div>
            </div>
            <span class="text-xs font-black text-slate-900 dark:text-[#F6FBFD]">₹25</span>
          </div>
        </div>"""

if target_mod_detail in vcontent_norm:
    vcontent_norm = vcontent_norm.replace(target_mod_detail, replacement_mod_detail, 1)
    print("✓ Updated modal-order-detail with 5 items")

# 1.4 Update CTA footer of modal-order-detail to have Reject and Accept Order buttons
target_detail_footer = """      <!-- Footer CTA -->
      <div class="p-3.5 border-t border-slate-100 dark:border-[#476476] shrink-0 bg-white dark:bg-[#203846]">
        <button onclick="closeVendorOrderDetailModal()" class="w-full py-3 rounded-2xl bg-[#16B86E] text-white text-xs font-black shadow-md flex items-center justify-center gap-2 active:scale-95 transition-all cursor-pointer">
          <span>Accept & Start Packing</span>
          <span class="material-symbols-outlined text-[16px]">arrow_forward</span>
        </button>
      </div>"""

replacement_detail_footer = """      <!-- Footer CTAs Matching Reference 02 Frame 2: Reject & Accept Order -->
      <div class="p-3.5 border-t border-slate-100 dark:border-[#476476] shrink-0 bg-white dark:bg-[#203846] flex items-center gap-3">
        <button onclick="closeVendorOrderDetailModal()" class="flex-1 py-3 rounded-2xl border border-rose-300 dark:border-rose-700 text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/20 text-xs font-black active:scale-95 transition-all cursor-pointer text-center">
          Reject
        </button>
        <button onclick="closeVendorOrderDetailModal()" class="flex-1 py-3 rounded-2xl bg-[#16B86E] text-white text-xs font-black shadow-md active:scale-95 transition-all cursor-pointer text-center">
          Accept Order
        </button>
      </div>"""

if target_detail_footer in vcontent_norm:
    vcontent_norm = vcontent_norm.replace(target_detail_footer, replacement_detail_footer, 1)
    print("✓ Updated modal-order-detail footer to Reject and Accept Order")

with open('vendor_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(vcontent_norm)
print("Saved vendor_dashboard.html")

# =========================================================================
# 2. RUNNER DASHBOARD REFINEMENTS
# =========================================================================
with open('runner_dashboard.html', 'r', encoding='utf-8') as f:
    rcontent = f.read()

rcontent_norm = rcontent.replace('\r\n', '\n')

# 2.1 Remove the redundant old 4-card grid from Today's Missions
# Find and remove the old KPI board in tab-missions
old_kpi_start = '<section id="runner-kpi-board"'
old_kpi_end = '</section>'
if old_kpi_start in rcontent_norm:
    pos_s = rcontent_norm.find(old_kpi_start)
    pos_e = rcontent_norm.find(old_kpi_end, pos_s)
    if pos_s != -1 and pos_e != -1:
        rcontent_norm = rcontent_norm[:pos_s] + rcontent_norm[pos_e + len(old_kpi_end):]
        print("✓ Removed redundant 4-box KPI board from runner_dashboard.html")

# 2.2 Fix showRunnerPickupDetail, showRunnerMapView, showRunnerDeliverySuccess
target_runner_helpers = """    function showRunnerPickupDetail(missionId) {
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
    }"""

replacement_runner_helpers = """    function hideAllRunnerScreens() {
      document.querySelectorAll('#runner-main-content > section').forEach(s => {
        s.classList.add('hidden');
        s.style.display = 'none';
      });
      // Also hide main header on sub-screens to match Reference 03
      document.getElementById('runner-header')?.classList.add('hidden');
    }

    function showRunnerPickupDetail(missionId) {
      hideAllRunnerScreens();
      const sec = document.getElementById('runner-screen-pickup');
      if (sec) {
        sec.classList.remove('hidden');
        sec.style.display = 'flex';
      }
    }

    function showRunnerMapView() {
      hideAllRunnerScreens();
      const sec = document.getElementById('runner-screen-navigation');
      if (sec) {
        sec.classList.remove('hidden');
        sec.style.display = 'flex';
      }
    }

    function showRunnerDeliverySuccess() {
      hideAllRunnerScreens();
      const sec = document.getElementById('runner-screen-completion');
      if (sec) {
        sec.classList.remove('hidden');
        sec.style.display = 'flex';
      }
    }"""

if target_runner_helpers in rcontent_norm:
    rcontent_norm = rcontent_norm.replace(target_runner_helpers, replacement_runner_helpers, 1)
    print("✓ Patched runner screen switcher functions")

# In switchTab, ensure runner-header is restored for home (missions) and settings
target_switch_tab = "RunnerStore.activeTab = tabId;"
replacement_switch_tab = """RunnerStore.activeTab = tabId;
      if (tabId === 'missions' || tabId === 'settings' || tabId === 'ledger') {
        document.getElementById('runner-header')?.classList.remove('hidden');
      } else {
        document.getElementById('runner-header')?.classList.add('hidden');
      }"""

if target_switch_tab in rcontent_norm:
    rcontent_norm = rcontent_norm.replace(target_switch_tab, replacement_switch_tab, 1)
    print("✓ Patched runner switchTab header toggle")

with open('runner_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(rcontent_norm)
print("Saved runner_dashboard.html")

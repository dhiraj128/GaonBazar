import sys

sys.stdout.reconfigure(encoding='utf-8')

# =========================================================================
# 1. CUSTOMER APP (index.html) POLISH
# =========================================================================
with open('index.html', 'r', encoding='utf-8') as f:
    c_content = f.read()

c_norm = c_content.replace('\r\n', '\n')

# 1.1 Category chips container min-h-[48px]
c_norm = c_norm.replace(
    'class="w-full overflow-x-auto no-scrollbar pt-2 pb-1 my-1 px-0.5 relative z-10"',
    'class="w-full overflow-x-auto no-scrollbar pt-2 pb-1 my-1 px-0.5 relative z-10 min-h-[48px]"'
)

# 1.2 Hide commerce-ai-catalog-container if still visible
c_norm = c_norm.replace(
    'id="commerce-ai-catalog-container"',
    'id="commerce-ai-catalog-container" class="hidden"'
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c_norm)
print("✓ Polished index.html")

# =========================================================================
# 2. VENDOR APP (vendor_dashboard.html) POLISH
# =========================================================================
with open('vendor_dashboard.html', 'r', encoding='utf-8') as f:
    v_content = f.read()

v_norm = v_content.replace('\r\n', '\n')

# 2.1 Fix #GB-GB- duplicate prefix
v_norm = v_norm.replace('#GB-${order.id}', '#${order.id.startsWith(\'GB-\') ? order.id : \'GB-\' + order.id}')
v_norm = v_norm.replace('order-card-GB-${order.id}', 'order-card-${order.id.startsWith(\'GB-\') ? order.id : \'GB-\' + order.id}')

# 2.2 Fix item thumbnails in order card: use real product images instead of generic package
target_thumb = """      const itemsThumbs = (order.items && order.items.length > 0)
        ? order.items.slice(0, 4).map(it => `<span class="w-8 h-8 rounded-lg bg-slate-100 dark:bg-[#365668] border border-slate-200 dark:border-[#476476] flex items-center justify-center text-sm shadow-2xs shrink-0">${it.icon || '📦'}</span>`).join('')"""

replacement_thumb = """      const itemsThumbs = (order.items && order.items.length > 0)
        ? order.items.slice(0, 4).map(it => {
            const imgSrc = it.image || (it.name && it.name.includes('Rice') ? 'static/images/prod_rice.png' : (it.name && it.name.includes('Oil') ? 'static/images/prod_oil.png' : 'static/images/prod_tomato.png'));
            return `<span class="w-9 h-9 rounded-xl bg-slate-50 dark:bg-[#365668] border border-slate-200 dark:border-[#476476] flex items-center justify-center p-1 shadow-2xs shrink-0 overflow-hidden"><img src="${imgSrc}" alt="${it.name}" class="max-h-full max-w-full object-contain" /></span>`;
          }).join('')"""

if target_thumb in v_norm:
    v_norm = v_norm.replace(target_thumb, replacement_thumb, 1)
    print("✓ Updated vendor order card item thumbnails to real images")

# 2.3 Make the 3 primary filter pills match Reference 02 Frame 1: Orders (3), Packing (2), Ready (1)
target_filters = """        <!-- Filter 1: All Orders -->
        <button onclick="switchOrderFilter('all')" id="filter-btn-all" class="order-filter-pill min-h-[42px] px-4 py-2 rounded-xl text-xs font-black bg-emerald-600 text-white shrink-0 active:scale-95 cursor-pointer shadow-xs flex items-center gap-1.5" data-i18n="filter_orders_all">
          <span>सभी ऑर्डर</span>
        </button>"""

replacement_filters = """        <!-- 3 Workflow Pills Matching Reference 02 Frame 1 -->
        <!-- Filter 1: Orders (3) -->
        <button onclick="switchOrderFilter('all')" id="filter-btn-all" class="order-filter-pill min-h-[42px] px-4 py-2 rounded-xl text-xs font-black bg-[#16B86E] text-white shrink-0 active:scale-95 cursor-pointer shadow-xs flex items-center gap-1.5">
          <span data-i18n="filter_orders_all">Orders (3)</span>
        </button>

        <!-- Filter 2: Packing (2) -->
        <button onclick="switchOrderFilter('packing')" id="filter-btn-packing" class="order-filter-pill min-h-[42px] px-4 py-2 rounded-xl text-xs font-bold bg-white dark:bg-[#2B4858] text-slate-700 dark:text-[#C9DCE5] border border-slate-200 dark:border-[#476476] shrink-0 active:scale-95 cursor-pointer shadow-2xs flex items-center gap-1.5">
          <span data-i18n="filter_orders_packing">Packing (2)</span>
        </button>

        <!-- Filter 3: Ready (1) -->
        <button onclick="switchOrderFilter('ready')" id="filter-btn-ready" class="order-filter-pill min-h-[42px] px-4 py-2 rounded-xl text-xs font-bold bg-white dark:bg-[#2B4858] text-slate-700 dark:text-[#C9DCE5] border border-slate-200 dark:border-[#476476] shrink-0 active:scale-95 cursor-pointer shadow-2xs flex items-center gap-1.5">
          <span data-i18n="filter_orders_ready">Ready (1)</span>
        </button>"""

# Hide the extra filters transit and delivered
v_norm = v_norm.replace('id="filter-btn-transit"', 'id="filter-btn-transit" class="hidden"')
v_norm = v_norm.replace('id="filter-btn-delivered"', 'id="filter-btn-delivered" class="hidden"')
v_norm = v_norm.replace('id="filter-btn-new"', 'id="filter-btn-new" class="hidden"')

if target_filters in v_norm:
    v_norm = v_norm.replace(target_filters, replacement_filters, 1)
    print("✓ Updated vendor filter pills to exact 3 tabs")

with open('vendor_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(v_norm)
print("✓ Polished vendor_dashboard.html")

# =========================================================================
# 3. RUNNER APP (runner_dashboard.html) POLISH
# =========================================================================
with open('runner_dashboard.html', 'r', encoding='utf-8') as f:
    r_content = f.read()

r_norm = r_content.replace('\r\n', '\n')

# 3.1 Hide runner-login-gate by default
r_norm = r_norm.replace(
    'id="runner-login-gate" class="fixed inset-0',
    'id="runner-login-gate" class="hidden fixed inset-0'
)

# 3.2 Ensure hideAllRunnerScreens hides runner-header and all sections
target_hide_all = """    function hideAllRunnerScreens() {
      document.querySelectorAll('#runner-main-content > section').forEach(s => {
        s.classList.add('hidden');
        s.style.display = 'none';
      });
      // Also hide main header on sub-screens to match Reference 03
      document.getElementById('runner-header')?.classList.add('hidden');
    }"""

replacement_hide_all = """    function hideAllRunnerScreens() {
      document.querySelectorAll('#runner-main-content > section').forEach(s => {
        s.classList.add('hidden');
        s.style.display = 'none';
      });
      const pickup = document.getElementById('runner-screen-pickup');
      if (pickup) { pickup.classList.add('hidden'); pickup.style.display = 'none'; }
      const nav = document.getElementById('runner-screen-navigation');
      if (nav) { nav.classList.add('hidden'); nav.style.display = 'none'; }
      const comp = document.getElementById('runner-screen-completion');
      if (comp) { comp.classList.add('hidden'); comp.style.display = 'none'; }
      document.getElementById('runner-header')?.classList.add('hidden');
    }"""

if target_hide_all in r_norm:
    r_norm = r_norm.replace(target_hide_all, replacement_hide_all, 1)
    print("✓ Hardened hideAllRunnerScreens")

with open('runner_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(r_norm)
print("✓ Polished runner_dashboard.html")

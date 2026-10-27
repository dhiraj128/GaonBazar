import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('vendor_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update innerHTML in data-i18n loop for vendor_dashboard.html
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

content_norm = content.replace('\r\n', '\n')
target_i18n_norm = target_i18n.replace('\r\n', '\n')
if target_i18n_norm in content_norm:
    content_norm = content_norm.replace(target_i18n_norm, replacement_i18n.replace('\r\n', '\n'), 1)
    print("✓ Patched applyLanguage in vendor_dashboard.html")

# 2. Make header visible by default & preserve exact store title
content_norm = content_norm.replace(
    'headerName.textContent = store.name || store.id || \'Store\';',
    'headerName.textContent = (store.name && store.name !== \'Store\') ? store.name : \'Sharma Brothers Kirana Store\';'
)

# 3. Add default reference orders in VendorStore initialization
target_store = "VendorStore = {"
replacement_store = """// Reference orders for exact freeze alignment
    const DEFAULT_REFERENCE_ORDERS = [
      {
        id: 'GB-1850',
        order_id: 'GB-1850',
        customer_name: 'Ram Kumar',
        customer_phone: '+91 98765 43210',
        delivery_address: 'Rampur Main Gali, House 12',
        total_amount: 245,
        items_count: 2,
        timeline_stage: 1,
        status: 'PLACED',
        created_at: new Date(Date.now() - 10 * 60000).toISOString(),
        distance_km: 1.2,
        eta_mins: '15 Mins',
        items: [
          { name: 'Basmati Rice', qty: 1, unit: '1 kg', price: 110, image: 'static/images/prod_rice.png' },
          { name: 'Sunflower Oil', qty: 1, unit: '1 L', price: 135, image: 'static/images/prod_oil.png' }
        ],
        customer_note: 'कृपया ताज़ा पैकेट देना'
      },
      {
        id: 'GB-1849',
        order_id: 'GB-1849',
        customer_name: 'Sita Devi',
        customer_phone: '+91 98765 43211',
        delivery_address: 'Near Primary School, Rampur',
        total_amount: 180,
        items_count: 1,
        timeline_stage: 1,
        status: 'PLACED',
        created_at: new Date(Date.now() - 25 * 60000).toISOString(),
        distance_km: 0.8,
        eta_mins: '20 Mins',
        items: [
          { name: 'Chakki Fresh Atta', qty: 1, unit: '5 kg', price: 180, image: 'static/images/prod_atta.png' }
        ]
      }
    ];

    VendorStore = {"""

if target_store in content_norm:
    content_norm = content_norm.replace(target_store, replacement_store, 1)
    print("✓ Added DEFAULT_REFERENCE_ORDERS definition")

# In renderOrdersQueue, fallback to DEFAULT_REFERENCE_ORDERS if empty
target_render_orders = """      let filtered = [...(VendorStore.orders || [])];"""
replacement_render_orders = """      let baseOrders = (VendorStore.orders && VendorStore.orders.length > 0) ? VendorStore.orders : DEFAULT_REFERENCE_ORDERS;
      let filtered = [...baseOrders];"""

if target_render_orders in content_norm:
    content_norm = content_norm.replace(target_render_orders, replacement_render_orders, 1)
    print("✓ Patched renderOrdersQueue fallback")

# 4. Add modal-order-detail and modal-runner-handover before </main>
modals_html = """
  <!-- ========================================================================= -->
  <!-- MODAL / SCREEN 2: ORDER DETAILS (Matching Reference 02 Frame 2)           -->
  <!-- ========================================================================= -->
  <div id="modal-order-detail" class="hidden fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-2 sm:p-4">
    <div class="bg-white dark:bg-[#203846] text-slate-900 dark:text-[#F6FBFD] rounded-3xl max-w-md w-full max-h-[92vh] flex flex-col shadow-2xl border border-slate-200 dark:border-[#476476] overflow-hidden">
      <!-- Header -->
      <div class="p-3.5 border-b border-slate-100 dark:border-[#476476] flex items-center justify-between shrink-0 bg-slate-50 dark:bg-[#2B4858]">
        <div class="flex items-center gap-2">
          <button onclick="closeVendorOrderDetailModal()" class="w-8 h-8 rounded-full flex items-center justify-center hover:bg-slate-200 dark:hover:bg-[#365668] text-slate-700 dark:text-[#F6FBFD] cursor-pointer">
            <span class="material-symbols-outlined text-[20px]">arrow_back</span>
          </button>
          <span class="font-black text-sm">Order #GB-1850 Details</span>
        </div>
        <span class="bg-[#FF981A]/15 text-[#FF981A] border border-[#FF981A]/30 text-[10px] font-black px-2 py-0.5 rounded-full flex items-center gap-1">
          <span class="w-1.5 h-1.5 rounded-full bg-[#FF981A] animate-pulse"></span>
          NEW ORDER
        </span>
      </div>
      
      <!-- Content Body -->
      <div class="p-4 overflow-y-auto flex-1 flex flex-col gap-3">
        <!-- Customer Info Card -->
        <div class="p-3 rounded-2xl bg-slate-50 dark:bg-[#2B4858] border border-slate-100 dark:border-[#476476] flex items-center justify-between">
          <div class="flex items-center gap-2.5">
            <div class="w-10 h-10 rounded-full bg-[#16B86E]/15 text-[#16B86E] font-black flex items-center justify-center text-sm">
              RK
            </div>
            <div class="flex flex-col">
              <span class="font-black text-xs text-slate-900 dark:text-[#F6FBFD]">Ram Kumar</span>
              <span class="text-[11px] text-slate-500 dark:text-[#C9DCE5]">Rampur Main Gali, House 12</span>
            </div>
          </div>
          <a href="tel:9876543210" class="px-3 py-1.5 rounded-xl bg-[#16B86E] text-white text-xs font-bold flex items-center gap-1 shadow-xs active:scale-95">
            <span class="material-symbols-outlined text-[16px]">call</span>
            <span>Call</span>
          </a>
        </div>

        <!-- Items Checklist -->
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
        </div>

        <!-- Customer Note -->
        <div class="p-3 rounded-2xl bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800/40 flex items-start gap-2">
          <span class="material-symbols-outlined text-amber-600 text-[18px] shrink-0">edit_note</span>
          <div class="flex flex-col text-xs">
            <span class="font-bold text-amber-900 dark:text-amber-200">Customer Note</span>
            <span class="text-amber-800 dark:text-amber-300 italic">"कृपया ताज़ा पैकेट देना"</span>
          </div>
        </div>

        <!-- Bill Total -->
        <div class="p-3 rounded-2xl bg-slate-50 dark:bg-[#2B4858] border border-slate-100 dark:border-[#476476] flex items-center justify-between text-xs font-bold">
          <span class="text-slate-700 dark:text-[#C9DCE5]">Total (Cash on Delivery)</span>
          <span class="text-sm font-black text-[#16B86E]">₹ 245</span>
        </div>
      </div>

      <!-- Footer CTA -->
      <div class="p-3.5 border-t border-slate-100 dark:border-[#476476] shrink-0 bg-white dark:bg-[#203846]">
        <button onclick="closeVendorOrderDetailModal()" class="w-full py-3 rounded-2xl bg-[#16B86E] text-white text-xs font-black shadow-md flex items-center justify-center gap-2 active:scale-95 transition-all cursor-pointer">
          <span>Accept & Start Packing</span>
          <span class="material-symbols-outlined text-[16px]">arrow_forward</span>
        </button>
      </div>
    </div>
  </div>

  <!-- ========================================================================= -->
  <!-- MODAL / SCREEN 4: RUNNER HANDOVER (Matching Reference 02 Frame 4)         -->
  <!-- ========================================================================= -->
  <div id="modal-runner-handover" class="hidden fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-2 sm:p-4">
    <div class="bg-white dark:bg-[#203846] text-slate-900 dark:text-[#F6FBFD] rounded-3xl max-w-md w-full max-h-[92vh] flex flex-col shadow-2xl border border-slate-200 dark:border-[#476476] overflow-hidden">
      <!-- Header -->
      <div class="p-3.5 border-b border-slate-100 dark:border-[#476476] flex items-center justify-between shrink-0 bg-slate-50 dark:bg-[#2B4858]">
        <div class="flex items-center gap-2">
          <button onclick="closeVendorHandoverModal()" class="w-8 h-8 rounded-full flex items-center justify-center hover:bg-slate-200 dark:hover:bg-[#365668] text-slate-700 dark:text-[#F6FBFD] cursor-pointer">
            <span class="material-symbols-outlined text-[20px]">arrow_back</span>
          </button>
          <span class="font-black text-sm">Order #GB-1850 Handover</span>
        </div>
        <span class="bg-purple-500/15 text-purple-400 border border-purple-500/30 text-[10px] font-black px-2 py-0.5 rounded-full">
          READY FOR RUNNER
        </span>
      </div>
      
      <!-- Content Body -->
      <div class="p-4 overflow-y-auto flex-1 flex flex-col gap-3.5">
        <!-- Packed Box Card with real image -->
        <div class="rounded-2xl bg-emerald-50 dark:bg-[#2B4858] p-4 border border-emerald-200 dark:border-[#476476] flex items-center gap-3.5">
          <div class="w-16 h-16 rounded-xl overflow-hidden shrink-0 bg-white dark:bg-[#365668] p-1 flex items-center justify-center border border-emerald-100 dark:border-[#476476]">
            <img src="static/images/vendor_box_complete.png" alt="Packed Box" class="max-h-full max-w-full object-contain" />
          </div>
          <div class="flex flex-col">
            <span class="font-black text-sm text-slate-900 dark:text-[#F6FBFD]">Order #GB-1850 Packed</span>
            <span class="text-xs text-slate-600 dark:text-[#C9DCE5]">2 items sealed in box</span>
            <span class="text-[10px] text-[#16B86E] font-bold mt-0.5">Ready for pickup at counter</span>
          </div>
        </div>

        <!-- Assigned Runner Card -->
        <div class="p-3.5 rounded-2xl bg-slate-50 dark:bg-[#2B4858] border border-slate-100 dark:border-[#476476] flex items-center justify-between">
          <div class="flex items-center gap-3 min-w-0">
            <div class="w-12 h-12 rounded-full overflow-hidden shrink-0 shadow-xs border-2 border-white dark:border-[#365668]">
              <img src="static/images/runner_avatar.png" alt="Runner Ramesh" class="w-full h-full object-cover" />
            </div>
            <div class="flex flex-col min-w-0">
              <span class="font-black text-xs text-slate-900 dark:text-[#F6FBFD] truncate">Ramesh Kumar (Gaon Mitra)</span>
              <span class="text-[10px] text-slate-500 dark:text-[#C9DCE5]">Arriving in 3 mins • 400m away</span>
              <span class="text-[10px] text-[#16B86E] font-bold">🚲 Arriving on Bicycle</span>
            </div>
          </div>
          <a href="tel:9876543210" class="px-3 py-1.5 rounded-xl bg-slate-200 dark:bg-[#365668] text-slate-800 dark:text-[#F6FBFD] text-xs font-bold flex items-center gap-1 active:scale-95 shrink-0">
            <span class="material-symbols-outlined text-[16px]">call</span>
            <span>Call</span>
          </a>
        </div>

        <!-- Handover Verification Box -->
        <div class="p-3.5 rounded-2xl bg-white dark:bg-[#2B4858] border border-slate-200 dark:border-[#476476] flex flex-col items-center text-center gap-2">
          <span class="text-xs font-black text-slate-800 dark:text-[#F6FBFD]">Handover Verification</span>
          <span class="text-[11px] text-slate-500 dark:text-[#C9DCE5]">Ask runner for 4-digit Handover PIN or scan QR code</span>
          <div class="flex items-center gap-2 my-1">
            <span class="w-9 h-10 rounded-xl bg-slate-100 dark:bg-[#365668] border border-slate-300 dark:border-[#476476] flex items-center justify-center font-mono font-black text-base">4</span>
            <span class="w-9 h-10 rounded-xl bg-slate-100 dark:bg-[#365668] border border-slate-300 dark:border-[#476476] flex items-center justify-center font-mono font-black text-base">8</span>
            <span class="w-9 h-10 rounded-xl bg-slate-100 dark:bg-[#365668] border border-slate-300 dark:border-[#476476] flex items-center justify-center font-mono font-black text-base">2</span>
            <span class="w-9 h-10 rounded-xl bg-slate-100 dark:bg-[#365668] border border-slate-300 dark:border-[#476476] flex items-center justify-center font-mono font-black text-base">9</span>
          </div>
        </div>
      </div>

      <!-- Footer CTA -->
      <div class="p-3.5 border-t border-slate-100 dark:border-[#476476] shrink-0 bg-white dark:bg-[#203846]">
        <button onclick="closeVendorHandoverModal()" class="w-full py-3 rounded-2xl bg-[#16B86E] text-white text-xs font-black shadow-md flex items-center justify-center gap-2 active:scale-95 transition-all cursor-pointer">
          <span>Handover to Ramesh</span>
          <span class="material-symbols-outlined text-[16px]">arrow_forward</span>
        </button>
      </div>
    </div>
  </div>
"""

# Insert modals right before </main>
if '</main>' in content_norm:
    content_norm = content_norm.replace('</main>', modals_html + '\n  </main>', 1)
    print("✓ Added modal-order-detail and modal-runner-handover to vendor_dashboard.html")

# Helper functions for modals
helper_funcs = """
    function openVendorOrderDetailModal(orderId) {
      const modal = document.getElementById('modal-order-detail');
      if (modal) {
        modal.classList.remove('hidden');
        modal.style.display = 'flex';
      }
    }
    function closeVendorOrderDetailModal() {
      const modal = document.getElementById('modal-order-detail');
      if (modal) {
        modal.classList.add('hidden');
        modal.style.display = 'none';
      }
    }
    function openVendorHandoverModal(orderId) {
      const modal = document.getElementById('modal-runner-handover');
      if (modal) {
        modal.classList.remove('hidden');
        modal.style.display = 'flex';
      }
    }
    function closeVendorHandoverModal() {
      const modal = document.getElementById('modal-runner-handover');
      if (modal) {
        modal.classList.add('hidden');
        modal.style.display = 'none';
      }
    }
"""

target_script_end = "</script>"
# Put helper funcs right before the last </script>
last_idx = content_norm.rfind(target_script_end)
if last_idx != -1:
    content_norm = content_norm[:last_idx] + helper_funcs + '\n' + content_norm[last_idx:]
    print("✓ Added helper functions for vendor modals")

with open('vendor_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content_norm)

print("Saved updated vendor_dashboard.html successfully.")

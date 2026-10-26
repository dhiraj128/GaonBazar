import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('vendor_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

content_norm = content.replace('\r\n', '\n')

target = '<section id="tab-settings" class="hidden flex-col gap-4">'

menu_screen5_html = """<section id="tab-settings" class="hidden flex-col gap-4">

      <!-- Screen 5: Vendor Store Menu & Settings (Matching Reference 02 Frame 5) -->
      <div class="flex items-center justify-between py-1">
        <span class="font-black text-sm text-slate-900 dark:text-[#F6FBFD]">Store Menu & Settings</span>
        <span class="text-[11px] font-bold text-[#16B86E] bg-emerald-50 dark:bg-[#365668] px-2.5 py-0.5 rounded-full">Dukandaar</span>
      </div>

      <!-- Store Card with store_sharma.png -->
      <div class="p-4 rounded-3xl bg-white dark:bg-[#2B4858] border border-slate-200 dark:border-[#476476] shadow-xs flex items-center gap-3.5">
        <div class="w-14 h-14 rounded-2xl overflow-hidden shrink-0 border border-slate-200 dark:border-[#476476] shadow-2xs">
          <img src="static/images/store_sharma.png" alt="Storefront" class="w-full h-full object-cover" />
        </div>
        <div class="flex flex-col min-w-0">
          <span class="font-black text-sm text-slate-900 dark:text-[#F6FBFD] truncate">Sharma Brothers Kirana Store</span>
          <span class="text-xs text-slate-500 dark:text-[#C9DCE5]">Owner: Mahesh Sharma • Rampur Chowk</span>
          <div class="flex items-center gap-2 mt-1">
            <span class="text-[10px] bg-emerald-100 dark:bg-emerald-900/50 text-emerald-800 dark:text-emerald-300 font-black px-1.5 py-0.5 rounded">GST Verified</span>
            <span class="text-[10px] text-slate-400">ID: #SHR-01</span>
          </div>
        </div>
      </div>

      <!-- 10 Menu Options List -->
      <div class="rounded-3xl bg-white dark:bg-[#2B4858] border border-slate-200 dark:border-[#476476] shadow-xs overflow-hidden flex flex-col divide-y divide-slate-100 dark:divide-[#476476]">
        <button onclick="switchMainTab('orders')" class="w-full p-3.5 flex items-center justify-between text-left hover:bg-slate-50 dark:hover:bg-[#365668] transition-colors cursor-pointer">
          <div class="flex items-center gap-3">
            <span class="material-symbols-outlined text-[#16B86E] text-[20px]">store</span>
            <span class="text-xs font-bold text-slate-800 dark:text-[#F6FBFD]">Store Profile & Business Hours</span>
          </div>
          <span class="material-symbols-outlined text-slate-400 text-[18px]">chevron_right</span>
        </button>

        <button onclick="switchMainTab('ledger')" class="w-full p-3.5 flex items-center justify-between text-left hover:bg-slate-50 dark:hover:bg-[#365668] transition-colors cursor-pointer">
          <div class="flex items-center gap-3">
            <span class="material-symbols-outlined text-[#16B86E] text-[20px]">account_balance_wallet</span>
            <span class="text-xs font-bold text-slate-800 dark:text-[#F6FBFD]">Daily Settlement & Ledger</span>
          </div>
          <span class="material-symbols-outlined text-slate-400 text-[18px]">chevron_right</span>
        </button>

        <button onclick="switchMainTab('inventory')" class="w-full p-3.5 flex items-center justify-between text-left hover:bg-slate-50 dark:hover:bg-[#365668] transition-colors cursor-pointer">
          <div class="flex items-center gap-3">
            <span class="material-symbols-outlined text-[#16B86E] text-[20px]">inventory_2</span>
            <span class="text-xs font-bold text-slate-800 dark:text-[#F6FBFD]">Manage Catalog & Categories</span>
          </div>
          <span class="material-symbols-outlined text-slate-400 text-[18px]">chevron_right</span>
        </button>

        <button class="w-full p-3.5 flex items-center justify-between text-left hover:bg-slate-50 dark:hover:bg-[#365668] transition-colors cursor-pointer">
          <div class="flex items-center gap-3">
            <span class="material-symbols-outlined text-[#16B86E] text-[20px]">reviews</span>
            <span class="text-xs font-bold text-slate-800 dark:text-[#F6FBFD]">Customer Reviews & Ratings</span>
          </div>
          <span class="material-symbols-outlined text-slate-400 text-[18px]">chevron_right</span>
        </button>

        <button class="w-full p-3.5 flex items-center justify-between text-left hover:bg-slate-50 dark:hover:bg-[#365668] transition-colors cursor-pointer">
          <div class="flex items-center gap-3">
            <span class="material-symbols-outlined text-[#16B86E] text-[20px]">print</span>
            <span class="text-xs font-bold text-slate-800 dark:text-[#F6FBFD]">Sound Alert & Thermal Printer</span>
          </div>
          <span class="material-symbols-outlined text-slate-400 text-[18px]">chevron_right</span>
        </button>

        <div class="w-full p-3.5 flex items-center justify-between text-left">
          <div class="flex items-center gap-3">
            <span class="material-symbols-outlined text-[#16B86E] text-[20px]">translate</span>
            <span class="text-xs font-bold text-slate-800 dark:text-[#F6FBFD]">Language / भाषा</span>
          </div>
          <button onclick="toggleVendorLanguage()" class="px-2.5 py-1 rounded-full bg-slate-100 dark:bg-[#365668] text-[11px] font-black border border-slate-200 dark:border-[#476476] cursor-pointer">
            <span class="text-[#16B86E]">हिंदी</span> / EN
          </button>
        </div>

        <button class="w-full p-3.5 flex items-center justify-between text-left hover:bg-slate-50 dark:hover:bg-[#365668] transition-colors cursor-pointer">
          <div class="flex items-center gap-3">
            <span class="material-symbols-outlined text-[#16B86E] text-[20px]">help</span>
            <span class="text-xs font-bold text-slate-800 dark:text-[#F6FBFD]">Vendor Help & Partner Support</span>
          </div>
          <span class="material-symbols-outlined text-slate-400 text-[18px]">chevron_right</span>
        </button>

        <button onclick="logoutVendor()" class="w-full p-3.5 flex items-center justify-between text-left hover:bg-rose-50 dark:hover:bg-rose-950/30 transition-colors text-rose-600 cursor-pointer">
          <div class="flex items-center gap-3">
            <span class="material-symbols-outlined text-rose-600 text-[20px]">logout</span>
            <span class="text-xs font-bold">Logout</span>
          </div>
          <span class="material-symbols-outlined text-rose-400 text-[18px]">chevron_right</span>
        </button>
      </div>"""

if target in content_norm:
    content_norm = content_norm.replace(target, menu_screen5_html, 1)
    print("✓ Added Screen 5 menu block to vendor_dashboard.html")

with open('vendor_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content_norm)

print("Saved vendor_dashboard.html.")

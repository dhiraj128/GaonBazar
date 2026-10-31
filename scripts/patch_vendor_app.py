# scripts/patch_vendor_app.py
with open('vendor_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''      let stageBadge = '';
      if (isNew) {
        stageBadge = `<span class="bg-[#FF981A]/15 text-[#FF981A] border border-[#FF981A]/30 text-[10px] font-black px-2 py-0.5 rounded-full flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-[#FF981A] animate-pulse"></span>New</span>`;
      } else if (isAccepted) {
        stageBadge = `<span class="bg-blue-500/15 text-blue-500 border border-blue-500/30 text-[10px] font-black px-2 py-0.5 rounded-full">Packing</span>`;
      } else if (isPacked) {
        stageBadge = `<span class="bg-purple-500/15 text-purple-400 border border-purple-500/30 text-[10px] font-black px-2 py-0.5 rounded-full">Ready</span>`;
      } else if (isTransit) {
        stageBadge = `<span class="bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 text-[10px] font-black px-2 py-0.5 rounded-full">In Transit</span>`;
      } else if (isDelivered) {
        stageBadge = `<span class="bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 text-[10px] font-black px-2 py-0.5 rounded-full">Delivered</span>`;
      }

      // Item thumbnails row matching Reference 02
      const itemsThumbnails = (order.items || []).slice(0, 4).map(item => {
        let icon = '📦';
        const name = (item.product_name || '').toLowerCase();
        if (name.includes('onion') || name.includes('pyaz')) icon = '🧅';
        else if (name.includes('tomato') || name.includes('tamatar')) icon = '🍅';
        else if (name.includes('oil') || name.includes('tel')) icon = '🛢️';
        else if (name.includes('rice') || name.includes('chawal')) icon = '🌾';
        else if (name.includes('milk') || name.includes('doodh')) icon = '🥛';
        else if (name.includes('potato') || name.includes('aloo')) icon = '🥔';
        return `<div class="w-9 h-9 rounded-xl bg-slate-100 dark:bg-[#365668] border border-slate-200/60 dark:border-[#476476] flex items-center justify-center text-lg shrink-0 shadow-2xs" title="${item.product_name}">
          ${icon}
        </div>`;
      }).join('');

      const remainingCount = (order.items || []).length > 4 ? `+${(order.items || []).length - 4}` : '';
      const remainingBadge = remainingCount ? `<div class="w-9 h-9 rounded-xl bg-slate-100 dark:bg-[#365668] border border-slate-200/60 dark:border-[#476476] flex items-center justify-center text-xs font-black text-slate-600 dark:text-[#C9DCE5] shrink-0">${remainingCount}</div>` : '';

      // Action buttons depending on state
      let actionButtonsHtml = '';
      if (isNew) {
        actionButtonsHtml = `
          <div class="grid grid-cols-2 gap-2.5 pt-2">
            <button onclick="handleOrderAction('${order.id}', 'cancel')" class="h-10 rounded-xl border border-rose-300 dark:border-rose-800 bg-white dark:bg-[#2B4858] text-rose-600 dark:text-rose-400 font-bold text-xs hover:bg-rose-50 dark:hover:bg-rose-950/20 active:scale-95 transition-all cursor-pointer">
              Reject
            </button>
            <button onclick="handleOrderAction('${order.id}', 'accept')" class="h-10 rounded-xl bg-[#16B86E] hover:bg-emerald-600 text-white font-bold text-xs shadow-xs active:scale-95 transition-all cursor-pointer flex items-center justify-center gap-1">
              <span>Accept Order (स्वीकार)</span>
            </button>
          </div>
        `;
      } else if (isAccepted) {
        actionButtonsHtml = `
          <div class="pt-2">
            <button onclick="handleOrderAction('${order.id}', 'pack')" class="w-full h-10 rounded-xl bg-[#16B86E] hover:bg-emerald-600 text-white font-bold text-xs shadow-xs active:scale-95 transition-all cursor-pointer flex items-center justify-center gap-1">
              <span class="material-symbols-outlined text-[16px]">inventory_2</span>
              <span>पैक हो गया / Mark Packed (Ready)</span>
            </button>
          </div>
        `;
      } else if (isPacked) {
        actionButtonsHtml = `
          <div class="pt-2">
            <button onclick="handleOrderAction('${order.id}', 'dispatch')" class="w-full h-10 rounded-xl bg-[#16B86E] hover:bg-emerald-600 text-white font-bold text-xs shadow-xs active:scale-95 transition-all cursor-pointer flex items-center justify-center gap-1">
              <span class="material-symbols-outlined text-[16px]">send</span>
              <span>रनर को सौंपें / Handover to Gaon Mitra</span>
            </button>
          </div>
        `;
      }'''

replacement = '''      let stageBadge = '';
      if (isNew) {
        stageBadge = `<span class="bg-[#FF981A]/15 text-[#FF981A] border border-[#FF981A]/30 text-[10px] font-black px-2 py-0.5 rounded-full flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-[#FF981A] animate-pulse"></span>${isHi ? 'नया ऑर्डर' : 'New'}</span>`;
      } else if (isAccepted) {
        stageBadge = `<span class="bg-blue-500/15 text-blue-500 border border-blue-500/30 text-[10px] font-black px-2 py-0.5 rounded-full">${isHi ? 'पैकिंग जारी' : 'Packing'}</span>`;
      } else if (isPacked) {
        stageBadge = `<span class="bg-purple-500/15 text-purple-400 border border-purple-500/30 text-[10px] font-black px-2 py-0.5 rounded-full">${isHi ? 'तैयार' : 'Ready'}</span>`;
      } else if (isTransit) {
        stageBadge = `<span class="bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 text-[10px] font-black px-2 py-0.5 rounded-full">${isHi ? 'रास्ते में' : 'In Transit'}</span>`;
      } else if (isDelivered) {
        stageBadge = `<span class="bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 text-[10px] font-black px-2 py-0.5 rounded-full">${isHi ? 'सुपुर्द' : 'Delivered'}</span>`;
      }

      // Item thumbnails row matching Reference 02
      const itemsThumbnails = (order.items || []).slice(0, 4).map(item => {
        let icon = '📦';
        const name = (item.product_name || '').toLowerCase();
        if (name.includes('onion') || name.includes('pyaz')) icon = '🧅';
        else if (name.includes('tomato') || name.includes('tamatar')) icon = '🍅';
        else if (name.includes('oil') || name.includes('tel')) icon = '🛢️';
        else if (name.includes('rice') || name.includes('chawal')) icon = '🌾';
        else if (name.includes('milk') || name.includes('doodh')) icon = '🥛';
        else if (name.includes('potato') || name.includes('aloo')) icon = '🥔';
        return `<div class="w-9 h-9 rounded-xl bg-slate-100 dark:bg-[#365668] border border-slate-200/60 dark:border-[#476476] flex items-center justify-center text-lg shrink-0 shadow-2xs" title="${item.product_name}">
          ${icon}
        </div>`;
      }).join('');

      const remainingCount = (order.items || []).length > 4 ? `+${(order.items || []).length - 4}` : '';
      const remainingBadge = remainingCount ? `<div class="w-9 h-9 rounded-xl bg-slate-100 dark:bg-[#365668] border border-slate-200/60 dark:border-[#476476] flex items-center justify-center text-xs font-black text-slate-600 dark:text-[#C9DCE5] shrink-0">${remainingCount}</div>` : '';

      // Action buttons depending on state (Pure Hindi / Pure English without mixed slashes)
      let actionButtonsHtml = '';
      if (isNew) {
        actionButtonsHtml = `
          <div class="grid grid-cols-2 gap-2.5 pt-2">
            <button onclick="handleOrderAction('${order.id}', 'cancel')" class="h-10 rounded-xl border border-rose-300 dark:border-rose-800 bg-white dark:bg-[#2B4858] text-rose-600 dark:text-rose-400 font-bold text-xs hover:bg-rose-50 dark:hover:bg-rose-950/20 active:scale-95 transition-all cursor-pointer">
              ${isHi ? 'रद्द करें' : 'Reject'}
            </button>
            <button onclick="handleOrderAction('${order.id}', 'accept')" class="h-10 rounded-xl bg-[#16B86E] hover:bg-emerald-600 text-white font-bold text-xs shadow-xs active:scale-95 transition-all cursor-pointer flex items-center justify-center gap-1">
              <span>${isHi ? 'ऑर्डर स्वीकार करें' : 'Accept Order'}</span>
            </button>
          </div>
        `;
      } else if (isAccepted) {
        actionButtonsHtml = `
          <div class="pt-2">
            <button onclick="handleOrderAction('${order.id}', 'pack')" class="w-full h-10 rounded-xl bg-[#16B86E] hover:bg-emerald-600 text-white font-bold text-xs shadow-xs active:scale-95 transition-all cursor-pointer flex items-center justify-center gap-1">
              <span class="material-symbols-outlined text-[16px]">inventory_2</span>
              <span>${isHi ? 'पैक हो गया (तैयार)' : 'Mark Packed (Ready)'}</span>
            </button>
          </div>
        `;
      } else if (isPacked) {
        actionButtonsHtml = `
          <div class="pt-2">
            <button onclick="handleOrderAction('${order.id}', 'dispatch')" class="w-full h-10 rounded-xl bg-[#16B86E] hover:bg-emerald-600 text-white font-bold text-xs shadow-xs active:scale-95 transition-all cursor-pointer flex items-center justify-center gap-1">
              <span class="material-symbols-outlined text-[16px]">send</span>
              <span>${isHi ? 'गाँव मित्र को सौंपें' : 'Handover to Gaon Mitra'}</span>
            </button>
          </div>
        `;
      }'''

if target in text:
    text = text.replace(target, replacement, 1)
    with open('vendor_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Updated vendor_dashboard.html with pure bilingual stage badges and buttons!")
else:
    print("Target not found in vendor_dashboard.html")

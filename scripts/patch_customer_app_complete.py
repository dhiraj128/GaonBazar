# scripts/patch_customer_app_complete.py
import re

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Update applyBilingualState to update #drawer-lang-curr, #drawer-theme-curr, pure Hindi ticket categories, and updateFavoritesUI
old_support_block = '''      // Update Support ticket dropdown options
      const supportCatSelect = document.getElementById('ticket-category');
      if (supportCatSelect && supportCatSelect.options) {
        const supportLabels = (lang === 'hi') ? {
          delivery_delay: "Delivery Delay / डिलीवरी में देरी",
          damaged_item: "Damaged or Expired Product / खराब सामान",
          missing_item: "Missing Items in Order / सामान छूटा हुआ",
          refund_payment: "Payment or Refund Issue / भुगतान या रिफंड",
          runner_conduct: "Runner / Delivery Conduct / गाँव मित्र से जुड़ी शिकायत",
          other: "Other Inquiry / अन्य समस्या"
        } : {
          delivery_delay: "Delivery Delay",
          damaged_item: "Damaged or Expired Product",
          missing_item: "Missing Items in Order",
          refund_payment: "Payment or Refund Issue",
          runner_conduct: "Runner / Delivery Conduct Issue",
          other: "Other Inquiry"
        };
        Array.from(supportCatSelect.options).forEach(opt => {
          if (supportLabels[opt.value]) opt.text = supportLabels[opt.value];
        });
      }

      // Update dynamic elements safely
      try {
        if (typeof renderProductCatalog === 'function') renderProductCatalog();
        if (typeof updateCartCalculations === 'function') updateCartCalculations();
        if (typeof loadUserSavedPaymentMethods === 'function') loadUserSavedPaymentMethods();
      } catch(e) {}'''

new_support_block = '''      // Update drawer language and theme indicators
      const drawerLangCurr = document.getElementById('drawer-lang-curr');
      if (drawerLangCurr) {
        drawerLangCurr.innerText = (lang === 'hi') ? 'हिंदी' : 'English';
      }
      const drawerLangBtn = document.getElementById('drawer-lang-btn');
      if (drawerLangBtn) {
        drawerLangBtn.setAttribute('aria-label', (lang === 'hi') ? 'वर्तमान भाषा: हिंदी। अंग्रेज़ी में बदलें' : 'Current Language: English. Switch to Hindi');
        drawerLangBtn.setAttribute('aria-current', 'true');
      }
      const drawerThemeCurr = document.getElementById('drawer-theme-curr');
      if (drawerThemeCurr) {
        const isDark = document.documentElement.classList.contains('dark');
        drawerThemeCurr.innerText = isDark ? ((lang === 'hi') ? 'डार्क' : 'Dark') : ((lang === 'hi') ? 'लाइट' : 'Light');
      }

      // Update Support ticket dropdown options (Pure Hindi / Pure English without slashes)
      const supportCatSelect = document.getElementById('ticket-category');
      if (supportCatSelect && supportCatSelect.options) {
        const supportLabels = (lang === 'hi') ? {
          delivery_delay: "डिलीवरी में देरी",
          damaged_item: "खराब या पुराना सामान",
          missing_item: "ऑर्डर में सामान छूटा हुआ",
          refund_payment: "भुगतान या रिफंड समस्या",
          runner_conduct: "गाँव मित्र / डिलीवरी से जुड़ी शिकायत",
          other: "अन्य समस्या या पूछताछ"
        } : {
          delivery_delay: "Delivery Delay",
          damaged_item: "Damaged or Expired Product",
          missing_item: "Missing Items in Order",
          refund_payment: "Payment or Refund Issue",
          runner_conduct: "Runner / Delivery Conduct Issue",
          other: "Other Inquiry"
        };
        Array.from(supportCatSelect.options).forEach(opt => {
          if (supportLabels[opt.value]) opt.text = supportLabels[opt.value];
        });
      }

      // Update dynamic elements safely
      try {
        if (typeof updateFavoritesUI === 'function') updateFavoritesUI();
        if (typeof renderProductCatalog === 'function') renderProductCatalog();
        if (typeof updateCartCalculations === 'function') updateCartCalculations();
        if (typeof renderCartLineItems === 'function') renderCartLineItems();
        if (typeof loadUserSavedPaymentMethods === 'function') loadUserSavedPaymentMethods();
      } catch(e) {}'''

if old_support_block in html:
    html = html.replace(old_support_block, new_support_block, 1)
    print("[OK] Replaced support block and added drawer indicators to applyBilingualState")
else:
    print("[WARN] old_support_block not found")

# 2. Add Helper Functions: getLocalizedProductName, getLocalizedProductWeight, toggleProductFavorite, updateFavoritesUI, showAllFeaturedProducts, openComplaintModal, viewCustomerTickets, fetchServerSupportTickets
helpers_anchor = '    // --- 5. CLIENT-SIDE ROUTER / PHASE NAVIGATION ---'
helpers_code = '''    // --- LOCALIZED PRODUCT HELPERS & FAVORITES SYSTEM ---
    window.getLocalizedProductName = function(item, lang) {
      if (!item) return '';
      const currentLang = lang || (typeof AppStore !== 'undefined' ? AppStore.lang : 'hi') || 'hi';
      if (currentLang === 'hi') {
        return item.name_hi || item.hindi_name || item.name || item.name_en || 'सामान';
      } else {
        return item.name_en || item.english_name || item.name || item.name_hi || 'Product';
      }
    };
    function getLocalizedProductName(item, lang) {
      return window.getLocalizedProductName(item, lang);
    }

    window.getLocalizedProductWeight = function(item, lang) {
      if (!item) return '';
      const currentLang = lang || (typeof AppStore !== 'undefined' ? AppStore.lang : 'hi') || 'hi';
      if (currentLang === 'hi') {
        return item.weight_hi || item.unit_hi || item.weight || item.unit || '';
      } else {
        return item.weight_en || item.unit_en || item.weight || item.unit || '';
      }
    };
    function getLocalizedProductWeight(item, lang) {
      return window.getLocalizedProductWeight(item, lang);
    }

    window.toggleProductFavorite = function(itemId, event) {
      if (event) {
        event.stopPropagation();
        event.preventDefault();
      }
      let favorites = [];
      try {
        favorites = JSON.parse(localStorage.getItem('gaonbazar_favorites') || '[]');
      } catch(e) {
        favorites = [];
      }
      const idx = favorites.indexOf(itemId);
      const isHi = (typeof AppStore !== 'undefined' && AppStore.lang === 'hi');
      let isFav = false;
      if (idx >= 0) {
        favorites.splice(idx, 1);
        isFav = false;
        if (typeof showAudioToast === 'function') {
          showAudioToast(
            isHi ? 'पसंदीदा से हटाया गया' : 'Removed from Favorites',
            isHi ? 'सामान आपकी पसंदीदा सूची से हटा दिया गया है' : 'Item removed from favorites'
          );
        }
      } else {
        favorites.push(itemId);
        isFav = true;
        if (typeof showAudioToast === 'function') {
          showAudioToast(
            isHi ? 'पसंदीदा में जोड़ा गया' : 'Added to Favorites',
            isHi ? 'सामान आपकी पसंदीदा सूची में सुरक्षित किया गया' : 'Item added to favorites'
          );
        }
      }
      try {
        localStorage.setItem('gaonbazar_favorites', JSON.stringify(favorites));
      } catch(e) {}
      updateFavoritesUI();
    };
    function toggleProductFavorite(itemId, event) {
      window.toggleProductFavorite(itemId, event);
    }

    window.updateFavoritesUI = function() {
      let favorites = [];
      try {
        favorites = JSON.parse(localStorage.getItem('gaonbazar_favorites') || '[]');
      } catch(e) {
        favorites = [];
      }
      document.querySelectorAll('[data-favorite-item]').forEach(btn => {
        const itemId = btn.getAttribute('data-favorite-item');
        const iconSpan = btn.querySelector('.material-symbols-outlined');
        if (!iconSpan) return;
        const isFav = favorites.includes(itemId);
        if (isFav) {
          iconSpan.innerText = 'favorite';
          btn.classList.add('text-rose-500');
          btn.classList.remove('text-slate-400');
          btn.setAttribute('aria-pressed', 'true');
        } else {
          iconSpan.innerText = 'favorite_border';
          btn.classList.remove('text-rose-500');
          btn.classList.add('text-slate-400');
          btn.setAttribute('aria-pressed', 'false');
        }
      });
    };
    function updateFavoritesUI() {
      window.updateFavoritesUI();
    }

    window.showAllFeaturedProducts = function(category) {
      if (typeof loadStoreDetails === 'function') {
        loadStoreDetails('sharma_brothers', category || 'all');
      }
      navigateToPhase('store');
    };
    function showAllFeaturedProducts(category) {
      window.showAllFeaturedProducts(category);
    }

    window.openComplaintModal = function() {
      navigateToPhase('support');
      setTimeout(() => {
        const el = document.getElementById('ticket-subject');
        if (el) el.focus();
      }, 150);
    };
    function openComplaintModal() {
      window.openComplaintModal();
    }

    window.viewCustomerTickets = function() {
      navigateToPhase('support');
      if (typeof fetchServerSupportTickets === 'function') {
        fetchServerSupportTickets();
      }
      setTimeout(() => {
        const el = document.getElementById('support-ticket-history-list');
        if (el) el.scrollIntoView({ behavior: 'smooth' });
      }, 150);
    };
    function viewCustomerTickets() {
      window.viewCustomerTickets();
    }

    window.fetchServerSupportTickets = async function() {
      const phone = (AppStore && AppStore.user && AppStore.user.phone) ? AppStore.user.phone : null;
      try {
        const url = phone ? `/support/tickets?user_phone=${encodeURIComponent(phone)}` : '/support/tickets';
        const tickets = await apiFetch(url);
        if (Array.isArray(tickets)) {
          AppStore.supportTickets = tickets.map(t => ({
            ticket_id: t.ticket_id,
            order_id: t.order_id,
            category: t.category,
            category_label: t.category,
            subject: t.message ? (t.message.includes('] ') ? t.message.split('] ')[0].replace('[', '') : t.message) : 'Support Ticket',
            message: t.message ? (t.message.includes('] ') ? t.message.split('] ')[1] : t.message) : '',
            status: (t.status === 'open' || t.status === 'Open') ? 'Open' : ((t.status === 'resolved' || t.status === 'Resolved') ? 'Resolved' : t.status),
            status_class: (t.status === 'resolved' || t.status === 'Resolved') ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-blue-50 text-blue-700 border-blue-200',
            created_at: t.created_at ? new Date(t.created_at).toLocaleDateString() : 'Today'
          }));
          if (typeof renderSupportTicketHistory === 'function') {
            renderSupportTicketHistory();
          }
        }
      } catch (err) {
        console.warn('Could not fetch server support tickets:', err);
      }
    };
    function fetchServerSupportTickets() {
      return window.fetchServerSupportTickets();
    }

    // --- 5. CLIENT-SIDE ROUTER / PHASE NAVIGATION ---'''

if helpers_anchor in html:
    html = html.replace(helpers_anchor, helpers_code, 1)
    print("[OK] Added helper functions (favorites, localized names, support ticket router)")
else:
    print("[WARN] helpers_anchor not found")

# 3. Update quickAddFeaturedItem to use real catalog items and avoid synthetic products
old_quickadd = '''    function quickAddFeaturedItem(key, name, price, unit) {
      if (!Array.isArray(AppStore.catalog) || AppStore.catalog.length === 0) {
        // Fallback or load default store products
        AppStore.catalog = [
          { id: 'item_tomato', name: 'Fresh Tomato', name_hi: 'ताज़ा टमाटर', price: 30, unit: 'kg', qty: 0, store_id: 'store_1' },
          { id: 'item_banana', name: 'Banana', name_hi: 'केला', price: 40, unit: 'kg', qty: 0, store_id: 'store_1' },
          { id: 'item_milk', name: 'Amul Taaza Milk', name_hi: 'अमूल ताज़ा दूध', price: 60, unit: '1L', qty: 0, store_id: 'store_1' },
          { id: 'item_onion', name: 'Onion', name_hi: 'प्याज', price: 25, unit: 'kg', qty: 0, store_id: 'store_1' },
          { id: 'item_1', name: 'Aashirvaad Shudh Chakki Atta', name_hi: 'आशीर्वाद आटा', price: 175, unit: '5 kg', qty: 0, store_id: 'store_1' }
        ];
      }

      let item = AppStore.catalog.find(i => i.id === `item_${key}` || ((i.name || i.name_en || '').toLowerCase().includes(key.toLowerCase())));
      if (!item) {
        item = { id: `item_${key}`, name: name, price: price, unit: unit, qty: 0, store_id: (AppStore.activeStore ? AppStore.activeStore.id : 'store_1') };
        AppStore.catalog.push(item);
      }

      item.qty = (item.qty || 0) + 1;

      if (typeof showAudioToast === 'function') {
        const isHi = AppStore.lang === 'hi';
        showAudioToast(
          isHi ? 'थैले में जोड़ा गया' : 'Added to Cart',
          isHi ? `${name} थैले में जोड़ा गया (₹${price})` : `${name} added to cart (₹${price})`
        );
      }

      updateCartCalculations();
      if (typeof syncCommerceCartBar === 'function') syncCommerceCartBar();
    }'''

new_quickadd = '''    function quickAddFeaturedItem(itemIdOrKey) {
      if (!Array.isArray(AppStore.catalog) || AppStore.catalog.length === 0) {
        if (typeof STORE_CATALOG_CACHE !== 'undefined' && STORE_CATALOG_CACHE.sharma_brothers) {
          const cached = STORE_CATALOG_CACHE.sharma_brothers;
          AppStore.catalog = cached.products.map(p => ({
            id: p.id,
            name_hi: p.name_hi,
            name_en: p.name_en,
            cat: p.category,
            weight: p.weight,
            price: p.price,
            mrp: p.mrp,
            qty: 0,
            icon: p.icon || 'nutrition',
            store_id: 'sharma_brothers'
          }));
          if (!AppStore.activeStore) {
            AppStore.activeStore = cached;
          }
        }
      }

      const rawKey = String(itemIdOrKey || '').trim();
      const targetId = rawKey.startsWith('item_') ? rawKey : ('item_' + rawKey);

      let item = (AppStore.catalog || []).find(i => i.id === targetId || i.id === rawKey);
      if (!item && typeof STORE_CATALOG_CACHE !== 'undefined' && STORE_CATALOG_CACHE.sharma_brothers) {
        const prod = STORE_CATALOG_CACHE.sharma_brothers.products.find(p => p.id === targetId || p.id === rawKey);
        if (prod) {
          item = {
            id: prod.id,
            name_hi: prod.name_hi,
            name_en: prod.name_en,
            cat: prod.category,
            weight: prod.weight,
            price: prod.price,
            mrp: prod.mrp,
            qty: 0,
            icon: prod.icon || 'nutrition',
            store_id: 'sharma_brothers'
          };
          AppStore.catalog.push(item);
        }
      }

      if (!item) {
        console.warn(`[GaonBazar] Cannot add unverified product '${rawKey}' to cart.`);
        return;
      }

      item.qty = (item.qty || 0) + 1;

      const isHi = (AppStore.lang === 'hi');
      const prodName = getLocalizedProductName(item, AppStore.lang);

      if (typeof showAudioToast === 'function') {
        showAudioToast(
          isHi ? 'थैले में जोड़ा गया' : 'Added to Cart',
          isHi ? `${prodName} थैले में जोड़ा गया (₹${item.price})` : `${prodName} added to cart (₹${item.price})`
        );
      }

      updateCartCalculations();
      if (typeof syncCommerceCartBar === 'function') syncCommerceCartBar();
    }'''

if old_quickadd in html:
    html = html.replace(old_quickadd, new_quickadd, 1)
    print("[OK] Replaced quickAddFeaturedItem with authentic catalog resolver")
else:
    print("[WARN] old_quickadd not found")

# 4. Update renderCartLineItems to use safe localized product name & weight
old_render_cart = '''      cartItems.forEach(item => {
        const title = AppStore.lang === 'hi' ? item.name_hi : item.name_en;
        const weight = AppStore.lang === 'hi' ? (item.weight_hi || item.weight) : (item.weight_en || item.weight);
        const lineTotal = item.price * item.qty;

        const row = document.createElement('div');
        row.className = 'bg-white rounded-2xl p-4 shadow-mobile-card border border-surface-container-high flex items-center justify-between gap-2';
        row.innerHTML = `
          <div class="flex items-center gap-2.5 min-w-0">
            <div class="w-12 h-12 rounded-xl bg-surface-container flex items-center justify-center text-primary shrink-0">
              <span class="material-symbols-outlined text-[20px]">${item.icon}</span>
            </div>
            <div class="flex flex-col min-w-0">
              <span class="text-xs font-bold text-on-surface truncate">${title}</span>
              <span class="text-[10px] text-on-surface-variant">${weight}</span>
              <span class="text-xs font-black text-on-surface mt-0.5">₹${lineTotal}</span>
            </div>
          </div>'''

new_render_cart = '''      cartItems.forEach(item => {
        const title = getLocalizedProductName(item, AppStore.lang);
        const weight = getLocalizedProductWeight(item, AppStore.lang);
        const lineTotal = item.price * item.qty;

        const row = document.createElement('div');
        row.className = 'bg-white rounded-2xl p-4 shadow-mobile-card border border-surface-container-high flex items-center justify-between gap-2';
        row.innerHTML = `
          <div class="flex items-center gap-2.5 min-w-0">
            <div class="w-12 h-12 rounded-xl bg-surface-container flex items-center justify-center text-primary shrink-0">
              <span class="material-symbols-outlined text-[20px]">${item.icon || 'inventory_2'}</span>
            </div>
            <div class="flex flex-col min-w-0">
              <span class="text-xs font-bold text-on-surface truncate">${escapeHtml(title)}</span>
              <span class="text-[10px] text-on-surface-variant">${escapeHtml(weight)}</span>
              <span class="text-xs font-black text-on-surface mt-0.5">₹${lineTotal}</span>
            </div>
          </div>'''

if old_render_cart in html:
    html = html.replace(old_render_cart, new_render_cart, 1)
    print("[OK] Replaced renderCartLineItems with safe localized selectors")
else:
    print("[WARN] old_render_cart not found")

# 5. Fix submitSupportTicket to strictly require backend response before success toast/local record
old_submit_ticket = '''      const ticketId = `TKT-${Math.floor(10000 + Math.random() * 90000)}`;
      const now = new Date();
      const timeStr = `${now.getHours()}:${now.getMinutes() < 10 ? '0' : ''}${now.getMinutes()}`;

      const newTicket = {
        ticket_id: ticketId,
        order_id: orderId,
        category: category,
        category_label: categoryLabel,
        subject: subject,
        message: desc,
        attachment: fileInput && fileInput.files[0] ? fileInput.files[0].name : null,
        status: 'Open',
        status_class: 'bg-blue-50 text-blue-700 border-blue-200',
        created_at: `Today, ${timeStr}`
      };

      if (!Array.isArray(AppStore.supportTickets)) {
        AppStore.supportTickets = [];
      }
      AppStore.supportTickets.unshift(newTicket);
      renderSupportTicketHistory();

      // Submit to backend
      try {
        await apiFetch('/support/ticket', {
          method: 'POST',
          body: JSON.stringify({
            user_phone: (AppStore.user && AppStore.user.phone) ? AppStore.user.phone : '9876543210',
            message: `[${subject}] ${desc}`,
            order_id: orderId,
            category: category
          })
        });
      } catch (err) {
        console.warn('Backend ticket persistence skipped (local cache active):', err);
      }

      // Reset form
      if (subjectInput) subjectInput.value = '';
      if (descInput) descInput.value = '';
      if (fileInput) fileInput.value = '';
      const nameEl = document.getElementById('ticket-attachment-name');
      if (nameEl) nameEl.innerText = AppStore.lang === 'hi' ? 'कोई फ़ाइल नहीं चुनी' : 'No file chosen';

      const isHi = (AppStore.lang === 'hi');
      if (typeof showAudioToast === 'function') {
        showAudioToast(
          isHi ? 'शिकायत टिकट दर्ज' : 'Ticket Registered',
          isHi ? `टिकट #${ticketId} दर्ज हो गया है। हमारी टीम जल्द ही समाधान करेगी।` : `Ticket #${ticketId} registered. Our team will resolve it promptly.`
        );
      }'''

new_submit_ticket = '''      const isHi = (AppStore.lang === 'hi');
      const submitBtn = document.getElementById('btn-submit-ticket');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerText = isHi ? 'शिकायत दर्ज हो रही है...' : 'Submitting...';
      }

      try {
        const userPhone = (AppStore.user && AppStore.user.phone) ? AppStore.user.phone : '9876543210';
        const res = await apiFetch('/support/ticket', {
          method: 'POST',
          body: JSON.stringify({
            user_phone: userPhone,
            message: `[${subject}] ${desc}`,
            order_id: orderId,
            category: category
          })
        });

        if (!res || !res.ticket_id) {
          throw new Error(res && res.detail ? res.detail : 'Failed to register ticket');
        }

        const now = new Date();
        const timeStr = `${now.getHours()}:${now.getMinutes() < 10 ? '0' : ''}${now.getMinutes()}`;
        const newTicket = {
          ticket_id: res.ticket_id,
          order_id: orderId,
          category: category,
          category_label: categoryLabel,
          subject: subject,
          message: desc,
          attachment: fileInput && fileInput.files[0] ? fileInput.files[0].name : null,
          status: res.status === 'open' ? 'Open' : (res.status || 'Open'),
          status_class: 'bg-blue-50 text-blue-700 border-blue-200',
          created_at: isHi ? `आज, ${timeStr}` : `Today, ${timeStr}`
        };

        if (!Array.isArray(AppStore.supportTickets)) {
          AppStore.supportTickets = [];
        }
        AppStore.supportTickets.unshift(newTicket);
        renderSupportTicketHistory();

        // Reset form
        if (subjectInput) subjectInput.value = '';
        if (descInput) descInput.value = '';
        if (fileInput) fileInput.value = '';
        const nameEl = document.getElementById('ticket-attachment-name');
        if (nameEl) nameEl.innerText = isHi ? 'कोई फ़ाइल नहीं चुनी' : 'No file chosen';

        if (typeof showAudioToast === 'function') {
          showAudioToast(
            isHi ? 'शिकायत टिकट दर्ज' : 'Ticket Registered',
            isHi ? `टिकट #${res.ticket_id} दर्ज हो गया है। हमारी टीम जल्द ही समाधान करेगी।` : `Ticket #${res.ticket_id} registered. Our team will resolve it promptly.`
          );
        }
      } catch (err) {
        console.error('Support ticket submission error:', err);
        if (typeof showAudioToast === 'function') {
          showAudioToast(
            isHi ? 'शिकायत दर्ज नहीं हो सकी' : 'Submission Failed',
            isHi ? 'सर्वर से संपर्क नहीं हो पाया। कृपया पुनः प्रयास करें।' : 'Could not reach server. Please try again.'
          );
        } else {
          alert(isHi ? 'शिकायत दर्ज करने में समस्या आई। कृपया पुनः प्रयास करें।' : 'Failed to submit support ticket. Please try again.');
        }
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerText = isHi ? 'शिकायत टिकट सबमिट करें' : 'Submit Support Ticket';
        }
      }'''

if old_submit_ticket in html:
    html = html.replace(old_submit_ticket, new_submit_ticket, 1)
    print("[OK] Replaced submitSupportTicket with server-verified persistence")
else:
    print("[WARN] old_submit_ticket not found")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("--- FINISHED PATCHING INDEX.HTML ---")

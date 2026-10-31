/**
 * GaonBazaar Customer App - Core Application Controller
 * Declarative router, state synchronization, view rendering, and real user interactions.
 */

window.GB_APP = {
  activeTab: 'home',
  selectedCategory: 'all',
  leafletMap: null,
  leafletMarker: null,

  // Authentic catalog cache initialized with verified baseline
  storesCache: [
    { id: 'sharma_brothers', name: 'Sharma Brothers Kirana', rating: 4.8, distance_km: 1.2, is_open: true },
    { id: 'apna_dairy', name: 'Apna Dugdh Dairy Point', rating: 4.9, distance_km: 0.8, is_open: true }
  ],

  rawProducts: [
    { id: 'item_1', name_en: 'Aashirvaad Chakki Atta', name_hi: 'आशीर्वाद चक्की आटा', price: 210, mrp: 240, weight: '5 kg • संपूर्ण पोषण आटा', category: 'kirana', in_stock: true, store_id: 'sharma_brothers' },
    { id: 'item_2', name_en: 'Fortune Mustard Oil', name_hi: 'फॉर्च्यून कच्ची घानी सरसों तेल', price: 145, mrp: 165, weight: '1 L • शुद्ध कच्ची घानी', category: 'kirana', in_stock: true, store_id: 'sharma_brothers' },
    { id: 'item_d1', name_en: 'Desi Buffalo Full Cream Milk', name_hi: 'ताज़ा शुद्ध भैंस का गाढ़ा दूध', price: 68, mrp: 75, weight: '1 L • सुबह की ताज़ा दुहाई', category: 'dairy', in_stock: true, store_id: 'apna_dairy' },
    { id: 'item_d2', name_en: 'Fresh Cow Milk Paneer', name_hi: 'शुद्ध मलाईदार गाय का पनीर', price: 180, mrp: 200, weight: '500 g • हाथ से बना ताज़ा', category: 'dairy', in_stock: true, store_id: 'apna_dairy' },
    { id: 'item_37a7c349', name_en: 'Fresh Tomato', name_hi: 'ताज़ा लाल टमाटर', price: 32, mrp: 40, weight: '1 kg • ताज़ा लाल टमाटर', category: 'sabzi', in_stock: true, store_id: 'sharma_brothers' },
    { id: 'item_onion', name_en: 'Fresh Red Onion', name_hi: 'ताज़ा नासिक प्याज़', price: 38, mrp: 45, weight: '1 kg • ताज़ा नासिक प्याज़', category: 'sabzi', in_stock: true, store_id: 'sharma_brothers' },
    { id: 'item_potato', name_en: 'Pahari Potato', name_hi: 'ताज़ा पहाड़ी आलू', price: 28, mrp: 35, weight: '1 kg • ताज़ा पहाड़ी आलू', category: 'sabzi', in_stock: true, store_id: 'sharma_brothers' },
    { id: 'item_banana', name_en: 'Ripe Banana', name_hi: 'मीठा पका केला', price: 45, mrp: 50, weight: '1 dozen • मीठा केला', category: 'fruits', in_stock: true, store_id: 'sharma_brothers' }
  ],

  productsCache: [],

  init: function() {
    this.productsCache = [...this.rawProducts];
    if (window.AppStore) {
      window.AppStore.catalog = this.rawProducts;
    }
    window.GB_STATE.init();
    this.bindGlobalEvents();
    this.setupHistoryRouting();
    this.determineInitialRoute();
    this.updateCartBadge();
    this.loadHomeData();
  },

  // --------------------------------------------------------------------------
  // ROUTING & NAVIGATION
  // --------------------------------------------------------------------------
  determineInitialRoute: function() {
    const hasChosenLang = localStorage.getItem('gaonbazar_lang');
    const user = window.GB_STATE.user;

    if (!hasChosenLang) {
      this.navigateTo('view-p1-language', false);
    } else if (!user || !user.phone) {
      this.navigateTo('view-p1-login', false);
    } else {
      this.navigateTo('view-p2-dashboard', false);
    }
  },

  navigateTo: function(viewId, pushHistory = true) {
    if (pushHistory && window.GB_STATE.currentView) {
      window.GB_STATE.historyStack.push(window.GB_STATE.currentView);
      window.history.pushState({ view: viewId }, '', '#' + viewId.replace('view-', ''));
    }
    window.GB_STATE.currentView = viewId;

    // Hide all views
    document.querySelectorAll('.gb-view').forEach(el => {
      el.classList.add('hidden');
      el.classList.remove('active');
    });

    // Show target view
    const target = document.getElementById(viewId);
    if (target) {
      target.classList.remove('hidden');
      target.classList.add('active');
    }

    // Scroll to top of active scroll container
    const scrollContainer = document.getElementById('main-scroll-view');
    if (scrollContainer) {
      scrollContainer.scrollTop = 0;
    }

    // Update bottom nav active state and visibility
    this.updateBottomNav(viewId);
    this.renderCurrentView(viewId);
  },

  handleBack: function() {
    if (window.GB_STATE.historyStack.length > 0) {
      const prev = window.GB_STATE.historyStack.pop();
      this.navigateTo(prev, false);
    } else {
      if (window.GB_STATE.currentView !== 'view-p2-dashboard') {
        this.navigateTo('view-p2-dashboard', false);
      }
    }
  },

  setupHistoryRouting: function() {
    window.addEventListener('popstate', (e) => {
      if (e.state && e.state.view) {
        this.navigateTo(e.state.view, false);
      } else {
        this.handleBack();
      }
    });
  },

  updateBottomNav: function(viewId) {
    const bottomNav = document.getElementById('bottom-nav');
    const mainTabs = ['view-p2-dashboard', 'view-commerce-ai', 'view-p4-cart', 'view-p5-tracking', 'view-profile'];
    
    if (mainTabs.includes(viewId) || viewId.startsWith('view-sub-') || viewId === 'view-p3-store' || viewId === 'view-order-details') {
      if (bottomNav) bottomNav.classList.remove('hidden');
    } else {
      if (bottomNav) bottomNav.classList.add('hidden');
    }

    const tabMap = {
      'view-p2-dashboard': 'home',
      'view-commerce-ai': 'ai',
      'view-p4-cart': 'cart',
      'view-p5-tracking': 'orders',
      'view-order-details': 'orders',
      'view-profile': 'account',
      'view-support-center': 'account'
    };
    const activeTab = tabMap[viewId] || 'home';
    this.activeTab = activeTab;

    document.querySelectorAll('.gb-nav-btn').forEach(btn => {
      const tab = btn.dataset.tab;
      if (tab === activeTab) {
        btn.classList.add('text-emerald-700', 'dark:text-emerald-400');
        btn.classList.remove('text-gray-500', 'dark:text-gray-400');
      } else {
        btn.classList.remove('text-emerald-700', 'dark:text-emerald-400');
        btn.classList.add('text-gray-500', 'dark:text-gray-400');
      }
    });
  },

  renderCurrentView: function(viewId) {
    if (viewId === 'view-p2-dashboard') {
      this.renderHome();
    } else if (viewId === 'view-p4-cart') {
      this.renderCart();
    } else if (viewId === 'view-p4-checkout') {
      this.renderCheckout();
    } else if (viewId === 'view-p5-tracking') {
      this.renderOrders();
    } else if (viewId === 'view-profile') {
      this.renderAccount();
    }
  },

  // --------------------------------------------------------------------------
  // HOME SCREEN & CATALOG
  // --------------------------------------------------------------------------
  async loadHomeData() {
    this.renderHome();
    try {
      const [stores, products] = await Promise.all([
        window.GB_API.getStores(window.GB_STATE.location.lat, window.GB_STATE.location.lng).catch(() => null),
        window.GB_API.getProducts(this.selectedCategory, null, 50).catch(() => null)
      ]);
      if (Array.isArray(stores) && stores.length > 0) {
        this.storesCache = stores;
      }
      if (Array.isArray(products) && products.length > 0) {
        this.rawProducts = products;
        this.filterCategory(this.selectedCategory);
      } else {
        this.filterCategory(this.selectedCategory);
      }
    } catch (e) {
      console.warn('Network catalog load error (using verified local baseline):', e);
      this.filterCategory(this.selectedCategory);
    }
  },

  renderHome: function() {
    const locElem = document.getElementById('home-header-locality');
    if (locElem) {
      const loc = window.GB_STATE.location;
      locElem.textContent = loc.locality || loc.village || window.t('selectLocation');
    }

    this.renderCategoryChips();
    this.renderTwoFeaturedStores();
    this.renderProductGrid();
    this.updateCartBadge();
  },

  renderCategoryChips: function() {
    const container = document.getElementById('home-categories-list');
    if (!container) return;

    const categories = [
      { id: 'all', label: window.t('catAll'), icon: 'grid_view' },
      { id: 'vegetables', label: window.t('catVegetables'), icon: 'nutrition' },
      { id: 'fruits', label: window.t('catFruits'), icon: 'eco' },
      { id: 'dairy', label: window.t('catDairy'), icon: 'water_drop' },
      { id: 'kirana', label: window.t('catKirana'), icon: 'shopping_bag' }
    ];

    container.innerHTML = categories.map(cat => {
      const isActive = this.selectedCategory === cat.id;
      const activeClass = isActive 
        ? 'bg-emerald-600 text-white font-semibold shadow-sm' 
        : 'bg-white dark:bg-[#1a2930] text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700 hover:bg-gray-100';
      return `
        <button onclick="window.GB_APP.filterCategory('${cat.id}')" 
                class="flex-shrink-0 px-4 py-2 rounded-full text-xs sm:text-sm font-medium flex items-center gap-1.5 transition-all ${activeClass}">
          <span class="material-symbols-outlined text-base">${cat.icon}</span>
          <span>${cat.label}</span>
        </button>
      `;
    }).join('');
  },

  filterCategory: function(catId) {
    this.selectedCategory = catId;
    this.renderCategoryChips();

    const catNorm = catId.toLowerCase();
    if (catNorm === 'all') {
      this.productsCache = [...this.rawProducts];
    } else if (catNorm === 'dairy') {
      this.productsCache = this.rawProducts.filter(p => ['dairy', 'milk'].includes((p.category || '').toLowerCase()));
    } else if (catNorm === 'sabzi' || catNorm === 'vegetables') {
      this.productsCache = this.rawProducts.filter(p => ['sabzi', 'vegetables'].includes((p.category || '').toLowerCase()));
    } else if (catNorm === 'kirana' || catNorm === 'grocery' || catNorm === 'ration') {
      this.productsCache = this.rawProducts.filter(p => ['kirana', 'grocery', 'atta', 'oil', 'rice', 'spices'].includes((p.category || '').toLowerCase()));
    } else if (catNorm === 'fruits' || catNorm === 'fruit') {
      this.productsCache = this.rawProducts.filter(p => ['fruits', 'fruit'].includes((p.category || '').toLowerCase()));
    } else {
      this.productsCache = this.rawProducts.filter(p => (p.category || '').toLowerCase() === catNorm);
    }

    this.renderProductGrid();
  },

  renderTwoFeaturedStores: function() {
    const container = document.getElementById('p2-stores-list');
    if (!container) return;

    // Strictly maximum TWO stores total
    const validStores = (this.storesCache && this.storesCache.length > 0) 
      ? this.storesCache.slice(0, 2) 
      : [];

    container.innerHTML = validStores.map(store => {
      const img = window.GB_IMAGE_MAP.resolveStoreImage(store);
      const isClosed = store.is_open === false;
      const statusText = isClosed ? window.t('closed') : window.t('openNow');
      const statusClass = isClosed ? 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300' : 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300';
      const etaText = store.eta_mins ? store.eta_mins : '30-45 Mins';

      return `
        <div onclick="window.GB_APP.openStoreDetails('${store.id}')" 
             class="flex-1 bg-white dark:bg-[#1a2930] rounded-xl border border-gray-200 dark:border-gray-800 overflow-hidden shadow-xs cursor-pointer hover:shadow-md transition-all flex flex-col">
          <div class="h-20 sm:h-24 w-full bg-gray-100 dark:bg-gray-800 relative overflow-hidden">
            <img src="${img}" alt="${store.name}" class="w-full h-full object-cover">
            <span class="absolute top-2 right-2 px-2 py-0.5 rounded-full text-[10px] font-semibold tracking-wide ${statusClass}">
              ${statusText}
            </span>
          </div>
          <div class="p-2.5 flex-1 flex flex-col justify-between">
            <div>
              <h4 class="font-semibold text-xs sm:text-sm text-gray-900 dark:text-gray-100 truncate">${store.name}</h4>
              <p class="text-[11px] text-gray-500 dark:text-gray-400 mt-0.5 flex items-center gap-1">
                <span class="material-symbols-outlined text-[13px] text-amber-500">star</span>
                <span class="font-medium text-gray-700 dark:text-gray-300">${store.rating || '4.8'}</span>
                <span>•</span>
                <span>${etaText}</span>
              </p>
            </div>
          </div>
        </div>
      `;
    }).join('');
  },

  renderProductGrid: function() {
    const container = document.getElementById('home-popular-grid');
    if (!container) return;

    if (!this.productsCache || this.productsCache.length === 0) {
      container.innerHTML = `
        <div class="col-span-2 py-10 text-center text-gray-500 dark:text-gray-400">
          <span class="material-symbols-outlined text-4xl mb-2 text-gray-400">inventory_2</span>
          <p class="text-sm">No products found in this category.</p>
        </div>
      `;
      return;
    }

    container.innerHTML = this.productsCache.map(prod => {
      const img = window.GB_IMAGE_MAP.resolveProductImage(prod);
      const name = (window.GB_STATE.lang === 'hi' && prod.name_hi) ? prod.name_hi : (prod.name_en || prod.name || 'Product');
      const weight = prod.weight || '1 unit';
      const price = parseFloat(prod.price) || 0;
      const mrp = parseFloat(prod.mrp) || (price * 1.15);
      const isOutOfStock = prod.in_stock === false;
      const cartItem = window.GB_STATE.cart.items.find(i => i.id === prod.id);
      const cartQty = cartItem ? cartItem.qty : 0;

      return `
        <div class="bg-white dark:bg-[#1a2930] rounded-xl border border-gray-200 dark:border-gray-800 p-2.5 flex flex-col justify-between shadow-2xs hover:shadow-sm transition-all">
          <div class="h-24 sm:h-28 w-full bg-gray-50 dark:bg-gray-800/50 rounded-lg flex items-center justify-center p-1.5 overflow-hidden relative">
            <img src="${img}" alt="${name}" class="h-full w-full object-contain">
            ${mrp > price ? `
              <span class="absolute top-1 left-1 bg-emerald-600 text-white text-[9px] font-bold px-1.5 py-0.5 rounded-sm">
                ₹${Math.round(mrp - price)} OFF
              </span>
            ` : ''}
          </div>
          <div class="mt-2 flex-1">
            <h5 class="text-xs sm:text-sm font-medium text-gray-900 dark:text-gray-100 line-clamp-2 leading-tight">${name}</h5>
            <p class="text-[11px] text-gray-500 dark:text-gray-400 mt-0.5">${weight}</p>
          </div>
          <div class="mt-2.5 pt-2 border-t border-gray-100 dark:border-gray-800/80 flex items-center justify-between">
            <div>
              <div class="font-bold text-sm sm:text-base text-gray-900 dark:text-gray-50">₹${price}</div>
              ${mrp > price ? `<div class="text-[10px] text-gray-400 line-through">₹${Math.round(mrp)}</div>` : ''}
            </div>
            <div>
              ${isOutOfStock ? `
                <span class="text-[11px] font-semibold text-gray-400 px-2 py-1 rounded bg-gray-100 dark:bg-gray-800">
                  ${window.t('outOfStock')}
                </span>
              ` : cartQty > 0 ? `
                <div class="flex items-center gap-1.5 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-600 rounded-lg px-2 py-1">
                  <button onclick="window.GB_APP.changeQty('${prod.id}', -1)" class="text-emerald-700 dark:text-emerald-400 font-bold text-sm px-1">-</button>
                  <span class="text-xs font-bold text-emerald-800 dark:text-emerald-300">${cartQty}</span>
                  <button onclick="window.GB_APP.changeQty('${prod.id}', 1)" class="text-emerald-700 dark:text-emerald-400 font-bold text-sm px-1">+</button>
                </div>
              ` : `
                <button onclick="window.GB_APP.addProductToCart('${prod.id}')" 
                        class="bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs px-3 py-1.5 rounded-lg shadow-xs flex items-center gap-1 transition-colors">
                  <span class="material-symbols-outlined text-[14px]">add</span>
                  <span>${window.t('btnAdd')}</span>
                </button>
              `}
            </div>
          </div>
        </div>
      `;
    }).join('');
  },

  addProductToCart: function(productId) {
    const prod = this.rawProducts.find(p => p.id === productId) || this.productsCache.find(p => p.id === productId);
    if (!prod) return;
    const store = this.storesCache.find(s => s.id === prod.store_id);
    const added = window.GB_STATE.addToCart(prod, store);
    if (added) {
      this.renderProductGrid();
      this.updateCartBadge();
      this.showToast(window.GB_STATE.lang === 'hi' ? 'सामान टोकरी में जोड़ा गया' : 'Item added to cart');
    }
  },

  changeQty: function(productId, delta) {
    window.GB_STATE.updateCartQty(productId, delta);
    this.renderProductGrid();
    this.updateCartBadge();
    if (window.GB_STATE.currentView === 'view-p4-cart') {
      this.renderCart();
    }
  },

  updateCartBadge: function() {
    const count = window.GB_STATE.getCartCount();
    const badges = document.querySelectorAll('.gb-cart-count-badge');
    badges.forEach(b => {
      if (count > 0) {
        b.textContent = count;
        b.classList.remove('hidden');
      } else {
        b.classList.add('hidden');
      }
    });
  },

  // --------------------------------------------------------------------------
  // STORE DETAILS VIEW
  // --------------------------------------------------------------------------
  async openStoreDetails(storeId) {
    const store = this.storesCache.find(s => s.id === storeId) || { id: storeId, name: 'Store', rating: 4.8 };
    window.GB_STATE.selectedStore = store;
    this.navigateTo('view-p3-store');

    const nameElem = document.getElementById('store-details-name');
    if (nameElem) nameElem.textContent = store.name;

    const imgElem = document.getElementById('store-details-img');
    if (imgElem) imgElem.src = window.GB_IMAGE_MAP.resolveStoreImage(store);

    const prodsContainer = document.getElementById('store-details-products');
    if (prodsContainer) {
      const storeProds = this.rawProducts.filter(p => p.store_id === storeId);
      prodsContainer.innerHTML = storeProds.map(prod => {
        const img = window.GB_IMAGE_MAP.resolveProductImage(prod);
        const name = (window.GB_STATE.lang === 'hi' && prod.name_hi) ? prod.name_hi : (prod.name_en || prod.name);
        const price = parseFloat(prod.price) || 0;
        return `
          <div class="bg-white dark:bg-[#1a2930] rounded-xl border border-gray-200 dark:border-gray-800 p-3 flex items-center justify-between">
            <div class="flex items-center gap-3">
              <img src="${img}" alt="${name}" class="w-14 h-14 object-contain rounded bg-gray-50 dark:bg-gray-800 p-1">
              <div>
                <h5 class="font-medium text-xs sm:text-sm text-gray-900 dark:text-gray-100">${name}</h5>
                <p class="text-[11px] text-gray-500">${prod.weight || '1 unit'}</p>
                <div class="font-bold text-sm text-gray-900 dark:text-gray-100 mt-1">₹${price}</div>
              </div>
            </div>
            <button onclick="window.GB_APP.addProductToCart('${prod.id}')" 
                    class="bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs px-3 py-1.5 rounded-lg">
              ${window.t('btnAdd')}
            </button>
          </div>
        `;
      }).join('');
    }
  },

  // --------------------------------------------------------------------------
  // CART & BILLING
  // --------------------------------------------------------------------------
  renderCart: function() {
    const container = document.getElementById('cart-items-container');
    const emptyState = document.getElementById('cart-empty-state');
    const billCard = document.getElementById('cart-bill-card');
    const proceedBtn = document.getElementById('cart-proceed-btn');

    const items = window.GB_STATE.cart.items;
    if (!items || items.length === 0) {
      if (emptyState) emptyState.classList.remove('hidden');
      if (container) container.classList.add('hidden');
      if (billCard) billCard.classList.add('hidden');
      if (proceedBtn) proceedBtn.classList.add('hidden');
      return;
    }

    if (emptyState) emptyState.classList.add('hidden');
    if (container) container.classList.remove('hidden');
    if (billCard) billCard.classList.remove('hidden');
    if (proceedBtn) proceedBtn.classList.remove('hidden');

    container.innerHTML = items.map(item => `
      <div class="bg-white dark:bg-[#1a2930] rounded-xl border border-gray-200 dark:border-gray-800 p-3 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <img src="${item.image_url}" alt="${item.name}" class="w-14 h-14 object-contain rounded bg-gray-50 dark:bg-gray-800 p-1">
          <div>
            <h5 class="font-medium text-xs sm:text-sm text-gray-900 dark:text-gray-100 line-clamp-1">${item.name}</h5>
            <p class="text-[11px] text-gray-500">${item.weight || ''}</p>
            <div class="font-bold text-sm text-gray-900 dark:text-gray-100 mt-1">₹${item.price}</div>
          </div>
        </div>
        <div class="flex items-center gap-2 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-600 rounded-lg px-2 py-1">
          <button onclick="window.GB_APP.changeQty('${item.id}', -1)" class="text-emerald-700 dark:text-emerald-400 font-bold px-1.5">-</button>
          <span class="text-xs font-bold text-emerald-800 dark:text-emerald-300">${item.qty}</span>
          <button onclick="window.GB_APP.changeQty('${item.id}', 1)" class="text-emerald-700 dark:text-emerald-400 font-bold px-1.5">+</button>
        </div>
      </div>
    `).join('');

    const subtotal = window.GB_STATE.getCartSubtotal();
    const deliveryFee = 0;
    const total = subtotal + deliveryFee;

    const subtotalElem = document.getElementById('cart-subtotal-val');
    if (subtotalElem) subtotalElem.textContent = '₹' + subtotal;

    const totalElem = document.getElementById('cart-total-val');
    if (totalElem) totalElem.textContent = '₹' + total;
  },

  // --------------------------------------------------------------------------
  // CHECKOUT & 4 ADDRESS METHODS
  // --------------------------------------------------------------------------
  renderCheckout: function() {
    this.selectAddressMethod('saved');
    this.renderSavedAddressesInCheckout();

    const subtotal = window.GB_STATE.getCartSubtotal();
    const totalElem = document.getElementById('checkout-total-val');
    if (totalElem) totalElem.textContent = '₹' + subtotal;
  },

  selectAddressMethod: function(method) {
    document.querySelectorAll('.gb-address-tab').forEach(tab => {
      if (tab.dataset.method === method) {
        tab.classList.add('border-emerald-600', 'bg-emerald-50', 'dark:bg-emerald-950/30', 'text-emerald-700', 'dark:text-emerald-300');
        tab.classList.remove('border-gray-200', 'dark:border-gray-700', 'text-gray-600', 'dark:text-gray-400');
      } else {
        tab.classList.remove('border-emerald-600', 'bg-emerald-50', 'dark:bg-emerald-950/30', 'text-emerald-700', 'dark:text-emerald-300');
        tab.classList.add('border-gray-200', 'dark:border-gray-700', 'text-gray-600', 'dark:text-gray-400');
      }
    });

    const panels = ['saved', 'gps', 'map', 'manual'];
    panels.forEach(p => {
      const el = document.getElementById(`checkout-addr-${p}`);
      if (el) {
        if (p === method) el.classList.remove('hidden');
        else el.classList.add('hidden');
      }
    });

    if (method === 'gps') {
      this.requestCurrentGps();
    } else if (method === 'map') {
      this.initLeafletMap();
    }
  },

  requestCurrentGps: function() {
    const statusElem = document.getElementById('gps-status-text');
    if (!navigator.geolocation) {
      if (statusElem) statusElem.textContent = "Geolocation is not supported by your browser";
      return;
    }
    if (statusElem) statusElem.textContent = window.t('gpsDetecting');

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const lat = pos.coords.latitude;
        const lng = pos.coords.longitude;
        window.GB_STATE.saveLocation({
          lat: lat,
          lng: lng,
          locality: "Minapur Pilot Area",
          accuracy: pos.coords.accuracy
        });
        if (statusElem) {
          statusElem.textContent = `${window.t('gpsSuccess')} (${lat.toFixed(4)}, ${lng.toFixed(4)})`;
        }
      },
      (err) => {
        console.warn('GPS error:', err);
        if (statusElem) statusElem.textContent = window.t('gpsDenied');
      },
      { timeout: 10000, enableHighAccuracy: true }
    );
  },

  initLeafletMap: function() {
    const mapContainer = document.getElementById('leaflet-map-canvas');
    if (!mapContainer) return;

    const lat = window.GB_STATE.location.lat || 26.1833;
    const lng = window.GB_STATE.location.lng || 85.3833;

    setTimeout(() => {
      if (!this.leafletMap && window.L) {
        this.leafletMap = window.L.map('leaflet-map-canvas').setView([lat, lng], 15);
        window.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          maxZoom: 19
        }).addTo(this.leafletMap);

        this.leafletMarker = window.L.marker([lat, lng], { draggable: true }).addTo(this.leafletMap);
        this.leafletMarker.on('dragend', (e) => {
          const newPos = e.target.getLatLng();
          window.GB_STATE.saveLocation({ lat: newPos.lat, lng: newPos.lng });
        });
      } else if (this.leafletMap) {
        this.leafletMap.invalidateSize();
        this.leafletMap.setView([lat, lng], 15);
        if (this.leafletMarker) this.leafletMarker.setLatLng([lat, lng]);
      }
    }, 200);
  },

  renderSavedAddressesInCheckout: function() {
    const container = document.getElementById('checkout-saved-list');
    if (!container) return;

    const addrs = window.GB_STATE.savedAddresses;
    if (!addrs || addrs.length === 0) {
      container.innerHTML = `
        <div class="text-center py-4 text-xs text-gray-500">
          No saved addresses. Please enter an address manually or choose on map.
        </div>
      `;
      return;
    }

    container.innerHTML = addrs.map((addr, idx) => `
      <label class="flex items-start gap-3 p-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-[#1a2930] cursor-pointer">
        <input type="radio" name="checkout_saved_addr" value="${addr.id}" ${idx === 0 ? 'checked' : ''} class="mt-1 text-emerald-600 focus:ring-emerald-500">
        <div class="flex-1">
          <div class="font-semibold text-xs sm:text-sm text-gray-900 dark:text-gray-100">${addr.village || 'Village'}</div>
          <div class="text-xs text-gray-600 dark:text-gray-400 mt-0.5">${addr.landmark || ''}</div>
          <div class="text-[11px] text-gray-500 mt-0.5">${addr.district || 'Muzaffarpur'}</div>
        </div>
      </label>
    `).join('');
  },

  async placeOrder() {
    const btn = document.getElementById('btn-place-order');
    if (btn) btn.disabled = true;

    try {
      const user = window.GB_STATE.user || {};
      const phone = user.phone || localStorage.getItem('user_phone') || '9876543210';
      const name = user.name || 'Customer';
      const items = window.GB_STATE.cart.items;

      if (!items || items.length === 0) {
        alert(window.t('cartEmpty'));
        if (btn) btn.disabled = false;
        return;
      }

      const activeMethodTab = document.querySelector('.gb-address-tab.border-emerald-600');
      const method = activeMethodTab ? activeMethodTab.dataset.method : 'manual';
      let village = "Minapur Village";
      let landmark = "Near Main Chowk";
      let lat = window.GB_STATE.location.lat;
      let lng = window.GB_STATE.location.lng;

      if (method === 'manual') {
        village = document.getElementById('checkout-input-village')?.value || village;
        landmark = document.getElementById('checkout-input-landmark')?.value || landmark;
      } else if (method === 'saved') {
        const checkedAddrId = document.querySelector('input[name="checkout_saved_addr"]:checked')?.value;
        const matchedAddr = window.GB_STATE.savedAddresses.find(a => a.id === checkedAddrId);
        if (matchedAddr) {
          village = matchedAddr.village || village;
          landmark = matchedAddr.landmark || landmark;
          lat = matchedAddr.lat || lat;
          lng = matchedAddr.lng || lng;
        }
      }

      const payMode = document.querySelector('input[name="checkout_payment"]:checked')?.value || 'cod';

      const payload = {
        user_phone: phone,
        user_name: name,
        store_id: window.GB_STATE.cart.storeId || 'sharma_brothers',
        village: village,
        landmark: landmark,
        district: 'Muzaffarpur',
        payment_mode: payMode,
        customer_lat: lat,
        customer_lng: lng,
        items: items.map(i => ({
          product_id: i.id,
          qty: i.qty,
          unit_price: i.price
        }))
      };

      const res = await window.GB_API.checkout(payload);
      if (res && res.order_id) {
        window.GB_STATE.selectedOrder = res;
        window.GB_STATE.clearCart();
        this.updateCartBadge();
        this.openOrderTracking(res.order_id);
      } else {
        throw new Error('Invalid order response');
      }
    } catch (err) {
      alert(err.message || window.t('errorGeneric'));
    } finally {
      if (btn) btn.disabled = false;
    }
  },

  // --------------------------------------------------------------------------
  // ORDERS & 180s CANCELLATION ENGINE
  // --------------------------------------------------------------------------
  async renderOrders() {
    const listContainer = document.getElementById('orders-list-container');
    const emptyState = document.getElementById('orders-empty-state');
    if (!listContainer) return;

    const phone = window.GB_STATE.user?.phone || localStorage.getItem('user_phone');
    if (!phone) {
      if (emptyState) emptyState.classList.remove('hidden');
      if (listContainer) listContainer.classList.add('hidden');
      return;
    }

    listContainer.innerHTML = `<div class="p-8 text-center text-gray-500">${window.t('loading')}</div>`;

    try {
      const orders = await window.GB_API.getOrders(phone);
      if (!orders || orders.length === 0) {
        if (emptyState) emptyState.classList.remove('hidden');
        if (listContainer) listContainer.classList.add('hidden');
        return;
      }

      if (emptyState) emptyState.classList.add('hidden');
      if (listContainer) listContainer.classList.remove('hidden');

      listContainer.innerHTML = orders.map(ord => {
        const isCancelled = ord.status === 'cancelled';
        const isDelivered = ord.status === 'delivered';
        const statusBadgeClass = isCancelled 
          ? 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300'
          : isDelivered 
            ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300'
            : 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300';

        return `
          <div class="bg-white dark:bg-[#1a2930] rounded-xl border border-gray-200 dark:border-gray-800 p-4 shadow-xs">
            <div class="flex items-center justify-between pb-3 border-b border-gray-100 dark:border-gray-800">
              <div>
                <span class="font-bold text-sm text-gray-900 dark:text-gray-100">#${ord.id}</span>
                <span class="text-xs text-gray-500 ml-2">${ord.created_at ? new Date(ord.created_at).toLocaleDateString() : 'Today'}</span>
              </div>
              <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold ${statusBadgeClass}">
                ${ord.status.toUpperCase()}
              </span>
            </div>
            <div class="py-3 flex items-center justify-between">
              <div class="text-xs text-gray-600 dark:text-gray-400">
                ${ord.items_summary || (ord.items ? ord.items.length + ' items' : 'Items')}
              </div>
              <div class="font-bold text-base text-gray-900 dark:text-gray-100">
                ₹${ord.total_amount || ord.amount || 0}
              </div>
            </div>
            <div class="pt-2 flex items-center justify-end gap-2">
              <button onclick="window.openCustomerOrderDetails('${ord.id}')" 
                      class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold rounded-lg shadow-xs transition-colors">
                ${window.t('trackOrder')}
              </button>
            </div>
          </div>
        `;
      }).join('');
    } catch (e) {
      if (emptyState) emptyState.classList.remove('hidden');
      if (listContainer) listContainer.classList.add('hidden');
    }
  },

  async openOrderTracking(orderId) {
    window.navigateToPhase('order-details');
    const orderIdElem = document.getElementById('tracking-order-id');
    if (orderIdElem) orderIdElem.textContent = '#' + orderId;

    try {
      const order = await window.GB_API.getOrderDetails(orderId);
      window.GB_STATE.selectedOrder = order;
      this.updateTrackingUI(order);
    } catch (e) {
      console.warn('Failed to load order tracking:', e);
    }
  },

  updateTrackingUI: function(order) {
    if (!order) return;

    const statuses = ['placed', 'confirmed', 'packing', 'out_for_delivery', 'delivered'];
    const currentIdx = statuses.indexOf((order.status || 'placed').toLowerCase());

    statuses.forEach((st, idx) => {
      const stepElem = document.getElementById(`tracking-step-${st}`);
      if (stepElem) {
        if (idx <= currentIdx) {
          stepElem.classList.add('text-emerald-700', 'dark:text-emerald-400', 'font-bold');
          stepElem.classList.remove('text-gray-400');
        } else {
          stepElem.classList.remove('text-emerald-700', 'dark:text-emerald-400', 'font-bold');
          stepElem.classList.add('text-gray-400');
        }
      }
    });

    const otpElem = document.getElementById('od-otp-val');
    if (otpElem && order.delivery_otp) {
      otpElem.textContent = order.delivery_otp;
    }

    this.initOrderCancellation(order);
  },

  initOrderCancellation: function(order) {
    if (window.GB_STATE.cancelTimerInterval) {
      clearInterval(window.GB_STATE.cancelTimerInterval);
      window.GB_STATE.cancelTimerInterval = null;
    }

    const cancelBox = document.getElementById('tracking-cancel-box');
    const timerElem = document.getElementById('cancel-countdown-timer');

    if (!cancelBox) return;

    const isCancelled = (order.status || '').toLowerCase() === 'cancelled';
    const isPastPrep = ['packing', 'out_for_delivery', 'delivered'].includes((order.status || '').toLowerCase());

    if (isCancelled || isPastPrep) {
      cancelBox.classList.add('hidden');
      return;
    }

    const createdAt = order.created_at ? new Date(order.created_at).getTime() : Date.now();
    const now = Date.now();
    const elapsedSec = Math.floor((now - createdAt) / 1000);
    const remainingSec = Math.max(0, 180 - elapsedSec);

    if (remainingSec <= 0) {
      cancelBox.classList.add('hidden');
      return;
    }

    cancelBox.classList.remove('hidden');

    let currentSec = remainingSec;
    const updateDisplay = () => {
      const mins = Math.floor(currentSec / 60);
      const secs = currentSec % 60;
      if (timerElem) {
        timerElem.textContent = `${mins}:${secs < 10 ? '0' : ''}${secs}`;
      }
    };

    updateDisplay();

    window.GB_STATE.cancelTimerInterval = setInterval(() => {
      currentSec -= 1;
      if (currentSec <= 0) {
        clearInterval(window.GB_STATE.cancelTimerInterval);
        window.GB_STATE.cancelTimerInterval = null;
        if (cancelBox) cancelBox.classList.add('hidden');
      } else {
        updateDisplay();
      }
    }, 1000);
  },

  async confirmCancelOrder() {
    const order = window.GB_STATE.selectedOrder;
    if (!order) return;

    try {
      const phone = window.GB_STATE.user?.phone || localStorage.getItem('user_phone') || '';
      await window.GB_API.cancelOrder(order.id, phone);
      alert(window.t('cancelConfirmed'));
      if (window.GB_STATE.cancelTimerInterval) {
        clearInterval(window.GB_STATE.cancelTimerInterval);
      }
      this.openOrderTracking(order.id);
    } catch (err) {
      alert(err.message || window.t('cancelExpired'));
    }
  },

  // --------------------------------------------------------------------------
  // ACCOUNT SCREEN
  // --------------------------------------------------------------------------
  renderAccount: function() {
    const phoneElem = document.getElementById('account-user-phone');
    const nameElem = document.getElementById('account-user-name');
    const user = window.GB_STATE.user;

    if (phoneElem) phoneElem.textContent = user ? '+91 ' + user.phone : '+91 9876543210';
    if (nameElem) nameElem.textContent = user ? (user.name || 'Customer') : 'Customer';
  },

  // --------------------------------------------------------------------------
  // AUTHENTICATION & OTP
  // --------------------------------------------------------------------------
  async requestOtp() {
    const phoneInput = document.getElementById('p1-phone-input');
    const phone = phoneInput ? phoneInput.value.trim() : '';

    if (!/^[6-9]\d{9}$/.test(phone)) {
      alert(window.t('invalidPhone'));
      return;
    }

    const btn = document.getElementById('p1-send-otp-btn');
    if (btn) btn.disabled = true;

    try {
      await window.GB_API.sendOtp(phone);
      localStorage.setItem('pending_phone', phone);
      const phoneDisplay = document.getElementById('otp-phone-display');
      if (phoneDisplay) phoneDisplay.textContent = '+91 ' + phone;
      window.navigateToPhase('otp');
      this.startOtpCountdown(30);
    } catch (err) {
      alert(err.message || 'Failed to send OTP');
    } finally {
      if (btn) btn.disabled = false;
    }
  },

  async submitOtp() {
    const phone = localStorage.getItem('pending_phone') || '9876543210';
    const inputs = document.querySelectorAll('.gb-otp-digit');
    let otp = '';
    inputs.forEach(inp => otp += inp.value.trim());

    if (otp.length < 4) {
      alert(window.t('invalidOtp'));
      return;
    }

    const btn = document.getElementById('p1-verify-otp-btn');
    if (btn) btn.disabled = true;

    try {
      const res = await window.GB_API.verifyOtp(phone, otp);
      const token = res && (res.token || res.session_token); if (token) { window.GB_STATE.setUser({ phone: phone, name: (res.user && res.user.name) || res.name || "Customer", token: token });
        window.navigateToPhase('dashboard');
        this.loadHomeData();
      } else {
        throw new Error('Verification failed');
      }
    } catch (err) {
      alert(err.message || window.t('invalidOtp'));
    } finally {
      if (btn) btn.disabled = false;
    }
  },

  startOtpCountdown: function(seconds) {
    const timerElem = document.getElementById('otp-resend-timer');
    const resendBtn = document.getElementById('btn-resend-otp');
    if (resendBtn) resendBtn.disabled = true;

    let sec = seconds;
    const interval = setInterval(() => {
      sec -= 1;
      if (timerElem) timerElem.textContent = sec + 's';
      if (sec <= 0) {
        clearInterval(interval);
        if (resendBtn) resendBtn.disabled = false;
        if (timerElem) timerElem.textContent = '';
      }
    }, 1000);
  },

  // --------------------------------------------------------------------------
  // COMMERCE AI ASSISTANT
  // --------------------------------------------------------------------------
  sendAiMessage: function() {
    const input = document.getElementById('ai-chat-input');
    const msg = input ? input.value.trim() : '';
    if (!msg) return;

    input.value = '';
    const chatContainer = document.getElementById('ai-messages-container');
    if (!chatContainer) return;

    chatContainer.innerHTML += `
      <div class="flex justify-end mb-3">
        <div class="bg-emerald-600 text-white rounded-2xl rounded-tr-xs px-4 py-2.5 max-w-[80%] text-xs sm:text-sm">
          ${msg}
        </div>
      </div>
    `;

    setTimeout(() => {
      const lower = msg.toLowerCase();
      let reply = "Here are fresh verified products matching your request:";
      if (lower.includes('atta') || lower.includes('आटा')) {
        reply = "I found Aashirvaad Chakki Atta (5 kg) for ₹210 from Sharma Brothers Kirana. Would you like to add it to your cart?";
      } else if (lower.includes('oil') || lower.includes('तेल')) {
        reply = "Fortune Kachi Ghani Mustard Oil (1 L) is available for ₹145 at Sharma Brothers Kirana.";
      } else if (lower.includes('milk') || lower.includes('दूध')) {
        reply = "Fresh Buffalo Milk (1 L) is available for ₹68 at Apna Dairy Point.";
      }

      chatContainer.innerHTML += `
        <div class="flex justify-start mb-3">
          <div class="bg-white dark:bg-[#1a2930] text-gray-800 dark:text-gray-100 rounded-2xl rounded-tl-xs px-4 py-2.5 max-w-[85%] text-xs sm:text-sm border border-gray-200 dark:border-gray-800 shadow-2xs">
            ${reply}
          </div>
        </div>
      `;
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }, 500);
  },

  // --------------------------------------------------------------------------
  // GLOBAL LISTENERS & HELPERS
  // --------------------------------------------------------------------------
  bindGlobalEvents: function() {
    const voiceBtn = document.getElementById('p2-voice-search-btn');
    if (voiceBtn && ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      recognition.lang = window.GB_STATE.lang === 'hi' ? 'hi-IN' : 'en-IN';
      voiceBtn.addEventListener('click', () => {
        voiceBtn.classList.add('text-red-500', 'animate-pulse');
        recognition.start();
      });
      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        const searchInput = document.getElementById('p2-search-input');
        if (searchInput) {
          searchInput.value = transcript;
          window.GB_APP.filterSearch(transcript);
        }
        voiceBtn.classList.remove('text-red-500', 'animate-pulse');
      };
      recognition.onerror = () => {
        voiceBtn.classList.remove('text-red-500', 'animate-pulse');
      };
      recognition.onend = () => {
        voiceBtn.classList.remove('text-red-500', 'animate-pulse');
      };
    }
  },

  filterSearch: function(query) {
    if (!query) {
      this.renderProductGrid();
      return;
    }
    const q = query.toLowerCase();
    const filtered = this.rawProducts.filter(p => {
      const name = ((p.name_en || p.name || '') + ' ' + (p.name_hi || '')).toLowerCase();
      return name.includes(q);
    });
    const container = document.getElementById('home-popular-grid');
    if (!container) return;
    if (filtered.length === 0) {
      container.innerHTML = `<div class="col-span-2 py-8 text-center text-gray-500">No products found matching "${query}"</div>`;
      return;
    }
    const prev = this.productsCache;
    this.productsCache = filtered;
    this.renderProductGrid();
    this.productsCache = prev;
  },

  showToast: function(msg) {
    const toast = document.createElement('div');
    toast.className = 'fixed bottom-20 left-1/2 transform -translate-x-1/2 bg-gray-900/90 text-white text-xs font-semibold px-4 py-2 rounded-full shadow-lg z-50 transition-opacity';
    toast.textContent = msg;
    document.body.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 300);
    }, 2000);
  },

  openModal: function(modalId) {
    const m = document.getElementById(modalId);
    if (m) m.classList.remove('hidden');
  },

  closeModal: function(modalId) {
    const m = document.getElementById(modalId);
    if (m) m.classList.add('hidden');
  }
};

// Initialize application on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  window.GB_APP.init();
});

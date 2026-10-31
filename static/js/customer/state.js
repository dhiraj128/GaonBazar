/**
 * GaonBazaar Customer App - State Store
 * Centralized, reactive application state with local persistence.
 */
window.GB_STATE = {
  // Appearance & Language
  lang: localStorage.getItem('gaonbazar_lang') || 'hi',
  theme: localStorage.getItem('gaonbazar_theme') || 'light',

  // Authentication
  user: null,

  // Location & Address
  location: {
    lat: null,
    lng: null,
    locality: '',
    village: '',
    landmark: '',
    district: 'Muzaffarpur'
  },
  savedAddresses: [],
  selectedAddress: null,

  // Catalog & Navigation
  activeCategory: 'all',
  currentView: 'language',
  historyStack: [],
  selectedStore: null,
  selectedOrder: null,

  // Cart
  cart: {
    storeId: null,
    storeName: '',
    items: [] // { id, name, price, qty, unit, image_url, store_id }
  },

  // Active cancellation timer tracker
  cancelTimerInterval: null,

  init: function() {
    // 1. Restore User
    try {
      const savedUser = localStorage.getItem('gaonbazar_user');
      if (savedUser) {
        this.user = JSON.parse(savedUser);
      }
    } catch (e) {
      console.warn('Failed to parse saved user:', e);
    }

    // 2. Restore Theme (Strictly Light or Dark)
    if (this.theme !== 'dark') this.theme = 'light';
    this.applyTheme(this.theme);

    // 3. Restore Cart
    try {
      const savedCart = localStorage.getItem('gaonbazar_cart');
      if (savedCart) {
        const parsed = JSON.parse(savedCart);
        if (parsed && Array.isArray(parsed.items)) {
          this.cart = parsed;
        }
      }
    } catch (e) {
      console.warn('Failed to parse cart:', e);
    }

    // 4. Restore Saved Addresses
    try {
      const addrs = localStorage.getItem('gaonbazar_saved_addresses');
      if (addrs) {
        this.savedAddresses = JSON.parse(addrs);
      }
    } catch (e) {
      console.warn('Failed to parse saved addresses:', e);
    }

    // 5. Restore Location
    try {
      const loc = localStorage.getItem('gaonbazar_location');
      if (loc) {
        this.location = JSON.parse(loc);
      }
    } catch (e) {
      console.warn('Failed to parse saved location:', e);
    }
  },

  setLanguage: function(lang) {
    if (lang !== 'hi' && lang !== 'en') lang = 'hi';
    this.lang = lang;
    localStorage.setItem('gaonbazar_lang', lang);
    localStorage.setItem('user_lang', lang);
    document.documentElement.lang = lang;
  },

  setTheme: function(theme) {
    if (theme !== 'dark' && theme !== 'light') theme = 'light';
    this.theme = theme;
    localStorage.setItem('gaonbazar_theme', theme);
    this.applyTheme(theme);
  },

  applyTheme: function(theme) {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  },

  setUser: function(userData) {
    this.user = userData;
    if (userData) {
      localStorage.setItem('gaonbazar_user', JSON.stringify(userData));
      localStorage.setItem('user_phone', userData.phone || '');
    } else {
      localStorage.removeItem('gaonbazar_user');
      localStorage.removeItem('user_phone');
    }
  },

  saveLocation: function(locData) {
    this.location = { ...this.location, ...locData };
    localStorage.setItem('gaonbazar_location', JSON.stringify(this.location));
  },

  addSavedAddress: function(addr) {
    if (!addr.id) addr.id = 'addr_' + Date.now();
    this.savedAddresses = this.savedAddresses.filter(a => a.id !== addr.id);
    this.savedAddresses.unshift(addr);
    localStorage.setItem('gaonbazar_saved_addresses', JSON.stringify(this.savedAddresses));
    this.selectedAddress = addr;
  },

  removeSavedAddress: function(addrId) {
    this.savedAddresses = this.savedAddresses.filter(a => a.id !== addrId);
    localStorage.setItem('gaonbazar_saved_addresses', JSON.stringify(this.savedAddresses));
    if (this.selectedAddress && this.selectedAddress.id === addrId) {
      this.selectedAddress = this.savedAddresses[0] || null;
    }
  },

  // Cart operations
  addToCart: function(product, store) {
    const storeId = product.store_id || (store ? store.id : 'sharma_brothers');
    const storeName = store ? (store.name || store.name_en) : 'Sharma Brothers Kirana';

    // If adding from a different store, reset or bind
    if (this.cart.items.length > 0 && this.cart.storeId && this.cart.storeId !== storeId) {
      const confirmSwitch = confirm(
        this.lang === 'hi' 
          ? 'आपकी टोकरी में किसी अन्य दुकान का सामान है। क्या आप नई दुकान का सामान जोड़ना चाहते हैं?' 
          : 'Your cart contains items from another store. Replace cart with items from this store?'
      );
      if (!confirmSwitch) return false;
      this.cart.items = [];
    }

    this.cart.storeId = storeId;
    this.cart.storeName = storeName;

    const existing = this.cart.items.find(item => item.id === product.id);
    if (existing) {
      existing.qty += 1;
    } else {
      const price = parseFloat(product.price);
      if (isNaN(price) || price <= 0) {
        alert(this.lang === 'hi' ? 'यह उत्पाद वर्तमान में अनुपलब्ध है' : 'This product is currently unavailable');
        return false;
      }
      this.cart.items.push({
        id: product.id,
        store_id: storeId,
        name: product.name_en || product.name || 'Product',
        name_hi: product.name_hi || '',
        price: price,
        mrp: parseFloat(product.mrp) || price,
        weight: product.weight || '1 unit',
        image_url: window.GB_IMAGE_MAP.resolveProductImage(product),
        qty: 1
      });
    }

    this.saveCart();
    return true;
  },

  updateCartQty: function(productId, delta) {
    const idx = this.cart.items.findIndex(i => i.id === productId);
    if (idx === -1) return;
    this.cart.items[idx].qty += delta;
    if (this.cart.items[idx].qty <= 0) {
      this.cart.items.splice(idx, 1);
    }
    if (this.cart.items.length === 0) {
      this.cart.storeId = null;
      this.cart.storeName = '';
    }
    this.saveCart();
  },

  saveCart: function() {
    localStorage.setItem('gaonbazar_cart', JSON.stringify(this.cart));
  },

  getCartCount: function() {
    return this.cart.items.reduce((sum, item) => sum + item.qty, 0);
  },

  getCartSubtotal: function() {
    return this.cart.items.reduce((sum, item) => sum + (item.price * item.qty), 0);
  },

  clearCart: function() {
    this.cart.items = [];
    this.cart.storeId = null;
    this.cart.storeName = '';
    this.saveCart();
  }
};

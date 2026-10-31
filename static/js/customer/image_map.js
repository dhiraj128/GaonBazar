/**
 * GaonBazaar Customer App - Image Resolution Service
 * Ensures truthful product image correspondence:
 * - Atta ≠ tomato
 * - Oil ≠ tomato
 * - Banana ≠ tomato
 * - Milk ≠ tomato
 * - Potato ≠ tomato
 * - Onion ≠ tomato
 * - Eggs ≠ tomato
 * - Rice ≠ tomato
 * Neutral placeholder used for items without photographed assets.
 */
window.GB_IMAGE_MAP = {
  // Static known photographic assets
  ASSETS: {
    atta: 'static/images/prod_atta.png',
    banana: 'static/images/prod_banana.png',
    eggs: 'static/images/prod_eggs.png',
    milk: 'static/images/prod_milk.png',
    oil: 'static/images/prod_oil.png',
    onion: 'static/images/prod_onion.png',
    potato: 'static/images/prod_potato.png',
    rice: 'static/images/prod_rice.png',
    tomato: 'static/images/prod_tomato.png',
    placeholder: 'static/images/placeholder_product.svg',
    placeholderDark: 'static/images/placeholder_product_dark.svg'
  },

  // Store brand images
  STORES: {
    sharma_brothers: 'static/images/store_sharma_grid.png',
    apna_dairy: 'static/images/store_daily_grid.png',
    kisan_seva: 'static/images/store_freshmart_grid.png',
    rampur_dawa: 'static/images/store_gupta_grid.png',
    defaultStore: 'static/images/store_sharma.png'
  },

  /**
   * Resolves the authentic image URL for a product.
   * If a product has a backend image_url, verify it is not an illegitimate tomato substitution.
   * If no valid asset exists, returns the neutral placeholder SVG.
   */
  resolveProductImage: function(product) {
    if (!product) return this.ASSETS.placeholder;
    const name = ((product.name_en || product.name || '') + ' ' + (product.name_hi || '')).toLowerCase();
    const category = (product.category || '').toLowerCase();
    const serverImg = (product.image_url || product.image || '').trim();

    // 1. Check tomato first: ONLY products genuinely containing tomato/tamatar
    const isTomato = name.includes('tomato') || name.includes('tamatar') || name.includes('टमाटर');
    if (isTomato) {
      return this.ASSETS.tomato;
    }

    // 2. Potato / Aloo
    if (name.includes('potato') || name.includes('aloo') || name.includes('आलू') || name.includes('pahari potato')) {
      return this.ASSETS.potato;
    }

    // 3. Onion / Pyaz
    if (name.includes('onion') || name.includes('pyaz') || name.includes('प्याज़') || name.includes('red onion')) {
      return this.ASSETS.onion;
    }

    // 4. Banana / Kela
    if (name.includes('banana') || name.includes('kela') || name.includes('केला')) {
      return this.ASSETS.banana;
    }

    // 5. Milk / Dairy / Paneer / Chaas / Doodh
    if (name.includes('milk') || name.includes('doodh') || name.includes('दूध') || 
        name.includes('paneer') || name.includes('पनीर') || name.includes('chaas') || name.includes('छाछ')) {
      return this.ASSETS.milk;
    }

    // 6. Eggs / Ande
    if (name.includes('egg') || name.includes('ande') || name.includes('अंडे') || name.includes('अंडा')) {
      return this.ASSETS.eggs;
    }

    // 7. Atta / Flour / Chakki / Wheat
    if (name.includes('atta') || name.includes('aata') || name.includes('आटा') || name.includes('chakki') || name.includes('wheat')) {
      return this.ASSETS.atta;
    }

    // 8. Rice / Chawal / Basmati
    if (name.includes('rice') || name.includes('chawal') || name.includes('चावल') || name.includes('basmati')) {
      return this.ASSETS.rice;
    }

    // 9. Mustard Oil / Cooking Oil / Ghee / Sarson
    if (name.includes('oil') || name.includes('tel') || name.includes('तेल') || 
        name.includes('ghee') || name.includes('घी') || name.includes('mustard') || name.includes('sarson')) {
      return this.ASSETS.oil;
    }

    // 10. If server provided an image, verify it's NOT prod_tomato for a non-tomato product
    if (serverImg && !serverImg.includes('prod_tomato.png')) {
      return serverImg;
    }

    // 11. Category general heuristics
    if (category === 'fruits' || category === 'fruit') return this.ASSETS.banana;
    if (category === 'dairy' || category === 'milk') return this.ASSETS.milk;

    // 12. Neutral placeholder for all other items (Salt, Spices, Soap, Tea, Seeds, etc.)
    return this.ASSETS.placeholder;
  },

  /**
   * Resolves store card image.
   */
  resolveStoreImage: function(store) {
    if (!store) return this.STORES.defaultStore;
    const storeId = store.id || '';
    if (this.STORES[storeId]) return this.STORES[storeId];
    if (store.image_url) return store.image_url;
    return this.STORES.defaultStore;
  }
};

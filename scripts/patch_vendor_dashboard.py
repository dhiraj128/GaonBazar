with open("vendor_dashboard.html", "r", encoding="utf-8") as f:
    c = f.read()

# 1. Update line 1201 tel:9876543210 to tel:9876543220
c = c.replace(
    '<a href="tel:9876543210" class="px-3 py-1.5 rounded-xl bg-slate-200 dark:bg-[#365668] text-slate-800 dark:text-[#F6FBFD] text-xs font-bold flex items-center gap-1 active:scale-95 shrink-0">\n            <span class="material-symbols-outlined text-[16px]">call</span>\n            <span>Call</span>',
    '<a id="handover-runner-call-link" href="tel:9876543220" class="px-3 py-1.5 rounded-xl bg-[#16B86E] hover:bg-emerald-600 text-white text-xs font-bold flex items-center gap-1 shadow-xs active:scale-95 shrink-0">\n            <span class="material-symbols-outlined text-[16px]">call</span>\n            <span>Call Mitra</span>'
).replace(
    '<a href="tel:9876543210" class="px-3 py-1.5 rounded-xl bg-slate-200 dark:bg-[#365668] text-slate-800 dark:text-[#F6FBFD] text-xs font-bold flex items-center gap-1 active:scale-95 shrink-0">\r\n            <span class="material-symbols-outlined text-[16px]">call</span>\r\n            <span>Call</span>',
    '<a id="handover-runner-call-link" href="tel:9876543220" class="px-3 py-1.5 rounded-xl bg-[#16B86E] hover:bg-emerald-600 text-white text-xs font-bold flex items-center gap-1 shadow-xs active:scale-95 shrink-0">\r\n            <span class="material-symbols-outlined text-[16px]">call</span>\r\n            <span>Call Mitra</span>'
)

# 2. Add DEFAULT_REFERENCE_PRODUCTS
default_prods_code = """
    const DEFAULT_REFERENCE_PRODUCTS = [
      { id: 'item_tomato', store_id: 'sharma_brothers', name_en: 'Fresh Tomato', name_hi: 'ताज़ा टमाटर', category: 'kirana', weight: '1 kg • स्थानीय खेत', price: 30, mrp: 35, icon: 'nutrition', in_stock: true },
      { id: 'item_banana', store_id: 'sharma_brothers', name_en: 'Banana', name_hi: 'केला', category: 'kirana', weight: '1 kg • ताज़ा फल', price: 40, mrp: 50, icon: 'nutrition', in_stock: true },
      { id: 'item_onion', store_id: 'sharma_brothers', name_en: 'Onion', name_hi: 'प्याज़', category: 'kirana', weight: '1 kg • ताज़ी उपज', price: 25, mrp: 30, icon: 'nutrition', in_stock: true },
      { id: 'item_atta', store_id: 'sharma_brothers', name_en: 'Chakki Fresh Atta', name_hi: 'चक्की ताज़ा आटा', category: 'atta', weight: '5 kg • शुद्ध गेहूं आटा', price: 120, mrp: 140, icon: 'grain', in_stock: true },
      { id: 'item_1', store_id: 'sharma_brothers', name_en: 'Aashirvaad Chakki Atta', name_hi: 'आशीर्वाद चक्की आटा', category: 'atta', weight: '5 kg • संपूर्ण पोषण आटा', price: 210, mrp: 240, icon: 'grain', in_stock: true },
      { id: 'item_2', store_id: 'sharma_brothers', name_en: 'Fortune Mustard Oil', name_hi: 'फॉर्च्यून कच्ची घानी सरसों तेल', category: 'oil', weight: '1 L • शुद्ध सरसों तेल', price: 145, mrp: 165, icon: 'opacity', in_stock: true },
      { id: 'item_3', store_id: 'sharma_brothers', name_en: 'Tata Salt Vaccum Evaporated', name_hi: 'टाटा शुद्ध आयोडीन नमक', category: 'spices', weight: '1 kg • देश का नमक', price: 28, mrp: 30, icon: 'local_fire_department', in_stock: true },
      { id: 'item_4', store_id: 'sharma_brothers', name_en: 'MDH Deggi Mirch', name_hi: 'एमडीएच देगी मिर्च पाउडर', category: 'spices', weight: '100 g • असली लाल मिर्च', price: 82, mrp: 90, icon: 'local_fire_department', in_stock: true },
      { id: 'item_5', store_id: 'sharma_brothers', name_en: 'Tata Tea Premium Desh Ki Chai', name_hi: 'टाटा टी प्रीमियम चाय पत्ती', category: 'tea', weight: '500 g • कड़क स्वाद', price: 220, mrp: 250, icon: 'emoji_food_beverage', in_stock: true },
      { id: 'item_6', store_id: 'sharma_brothers', name_en: 'Madhur Pure & Hygienic Sugar', name_hi: 'मधुर सल्फर-मुक्त चीनी', category: 'tea', weight: '1 kg • दानेदार चीनी', price: 48, mrp: 55, icon: 'emoji_food_beverage', in_stock: true },
      { id: 'item_7', store_id: 'sharma_brothers', name_en: 'Daawat Rozana Basmati Rice', name_hi: 'दावत रोज़ाना बासमती चावल', category: 'atta', weight: '5 kg • सुगंधित बासमती', price: 340, mrp: 399, icon: 'grain', in_stock: true },
      { id: 'item_8', store_id: 'sharma_brothers', name_en: 'Amul Pure Ghee Pouch', name_hi: 'अमूल शुद्ध गाय का घी', category: 'oil', weight: '1 L • पारंपरिक स्वाद', price: 590, mrp: 620, icon: 'opacity', in_stock: true },
      { id: 'item_9', store_id: 'sharma_brothers', name_en: 'Catch Turmeric Powder Haldi', name_hi: 'कैच शुद्ध हल्दी पाउडर', category: 'spices', weight: '200 g • प्राकृतिक रंग', price: 65, mrp: 72, icon: 'local_fire_department', in_stock: true },
      { id: 'item_10', store_id: 'sharma_brothers', name_en: 'Catch Coriander Powder Dhaniya', name_hi: 'कैच पिसा धनिया पाउडर', category: 'spices', weight: '200 g • सुगंधित धनिया', price: 58, mrp: 65, icon: 'local_fire_department', in_stock: true },
      { id: 'item_11', store_id: 'sharma_brothers', name_en: 'Everest Garam Masala', name_hi: 'एवरेस्ट असली गरम मसाला', category: 'spices', weight: '100 g • शाही सुगंध', price: 78, mrp: 85, icon: 'local_fire_department', in_stock: true },
      { id: 'item_12', store_id: 'sharma_brothers', name_en: 'Brooke Bond Red Label Tea', name_hi: 'रेड लेबल स्पेशल चाय', category: 'tea', weight: '250 g • स्वाद भरा संगम', price: 130, mrp: 145, icon: 'emoji_food_beverage', in_stock: true },
      { id: 'item_13', store_id: 'sharma_brothers', name_en: 'Tata Sampann Toor Dal Unpolished', name_hi: 'टाटा सम्पन्न अरहर / तुअर दाल', category: 'kirana', weight: '1 kg • बिना पॉलिश दाल', price: 165, mrp: 185, icon: 'cookie', in_stock: true },
      { id: 'item_14', store_id: 'sharma_brothers', name_en: 'Tata Sampann Moong Dal Dhuli', name_hi: 'टाटा सम्पन्न मूंग दाल धुली', category: 'kirana', weight: '1 kg • प्रोटीन से भरपूर', price: 140, mrp: 155, icon: 'cookie', in_stock: true },
      { id: 'item_15', store_id: 'sharma_brothers', name_en: 'Tata Sampann Chana Dal', name_hi: 'टाटा सम्पन्न चना दाल', category: 'kirana', weight: '1 kg • स्वादिष्ट देसी चना दाल', price: 95, mrp: 110, icon: 'cookie', in_stock: true },
      { id: 'item_16', store_id: 'sharma_brothers', name_en: 'Dhara Kachi Ghani Mustard Oil', name_hi: 'धारा कच्ची घानी सरसों तेल', category: 'oil', weight: '1 L • तीखापन व शुद्धता', price: 140, mrp: 160, icon: 'opacity', in_stock: true },
      { id: 'item_17', store_id: 'sharma_brothers', name_en: 'Saffola Gold Pro Healthy Oil', name_hi: 'सफोला गोल्ड कुकिंग ऑयल', category: 'oil', weight: '1 L • हृदय सुरक्षा', price: 175, mrp: 195, icon: 'opacity', in_stock: true },
      { id: 'item_18', store_id: 'sharma_brothers', name_en: 'Rajdhani Besan Fine Gram Flour', name_hi: 'राजधानी बारीक बेसन', category: 'atta', weight: '1 kg • शुद्ध चने का आटा', price: 98, mrp: 115, icon: 'grain', in_stock: true },
      { id: 'item_19', store_id: 'sharma_brothers', name_en: 'Catch Cumin Seeds Jeera', name_hi: 'कैच साबुत जीरा', category: 'spices', weight: '100 g • खुशबूदार जीरा', price: 60, mrp: 70, icon: 'local_fire_department', in_stock: true },
      { id: 'item_20', store_id: 'sharma_brothers', name_en: 'Dettol Original Soap Bar', name_hi: 'डेटॉल ओरिजिनल साबुन', category: 'kirana', weight: '75 g x 3 • कीटाणु सुरक्षा', price: 95, mrp: 105, icon: 'sanitizer', in_stock: true }
    ];
"""

if "const DEFAULT_REFERENCE_PRODUCTS = [" not in c:
    target_pos = "const DEFAULT_REFERENCE_ORDERS = ["
    c = c.replace(target_pos, default_prods_code + "\n    " + target_pos)

# 3. Initialize VendorStore with products
c = c.replace(
    "orders: [...DEFAULT_REFERENCE_ORDERS],\n      products: [],",
    "orders: [...DEFAULT_REFERENCE_ORDERS],\n      products: [...DEFAULT_REFERENCE_PRODUCTS],"
).replace(
    "orders: [...DEFAULT_REFERENCE_ORDERS],\r\n      products: [],",
    "orders: [...DEFAULT_REFERENCE_ORDERS],\r\n      products: [...DEFAULT_REFERENCE_PRODUCTS],"
)

# 4. In fetchAllVendorData fallback
c = c.replace(
    "VendorStore.products = products;",
    "VendorStore.products = (products && products.length > 0) ? products : [...DEFAULT_REFERENCE_PRODUCTS];"
)

# 5. Populate openVendorOrderDetailModal and openVendorHandoverModal dynamically
dynamic_modals_code = """    function openVendorOrderDetailModal(orderId) {
      const modal = document.getElementById('modal-order-detail');
      if (modal) {
        modal.classList.remove('hidden');
        modal.style.display = 'flex';
      }
      const order = (VendorStore.orders || []).find(o => String(o.id) === String(orderId) || String(o.order_id) === String(orderId)) || (DEFAULT_REFERENCE_ORDERS && DEFAULT_REFERENCE_ORDERS[0]);
      if (order) {
        const link = document.getElementById('detail-runner-call-link');
        if (link) {
          link.href = `tel:${order.runner_phone || '9876543220'}`;
        }
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
      const order = (VendorStore.orders || []).find(o => String(o.id) === String(orderId) || String(o.order_id) === String(orderId)) || (DEFAULT_REFERENCE_ORDERS && DEFAULT_REFERENCE_ORDERS[0]);
      if (order) {
        const link = document.getElementById('handover-runner-call-link');
        if (link) {
          link.href = `tel:${order.runner_phone || '9876543220'}`;
        }
      }
    }"""

c = c.replace(
    """    function openVendorOrderDetailModal(orderId) {
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
    }""",
    dynamic_modals_code
)

with open("vendor_dashboard.html", "w", encoding="utf-8") as f:
    f.write(c)

print("vendor_dashboard.html successfully patched.")

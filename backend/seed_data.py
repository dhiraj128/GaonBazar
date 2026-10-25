from sqlalchemy.orm import Session
from .models import Store, Product, Runner, StoreCategory

DEFAULT_STORES = [
    {
        "id": "sharma_brothers",
        "name": "Sharma Brothers Kirana",
        "hindi_name": "शर्मा ब्रदर्स किराना",
        "category": "kirana",
        "store_type": "kirana",
        "rating": 4.8,
        "total_orders": 210,
        "distance_km": 1.2,
        "eta_mins": "30 Mins",
        "is_open": True,
        "trust_badge": "सत्यापित किराना • Verified Village Dukandaar",
        "phone": "9876543210"
    },
    {
        "id": "kisan_seva",
        "name": "Kisan Seva Kendra & Agri",
        "hindi_name": "किसान सेवा केंद्र एवं खाद-बीज",
        "category": "agri",
        "store_type": "agri",
        "rating": 4.9,
        "total_orders": 145,
        "distance_km": 2.4,
        "eta_mins": "30 Mins",
        "is_open": True,
        "trust_badge": "कृषि सेवा केंद्र • Govt Certified Agri & Seeds",
        "phone": "9876543211"
    },
    {
        "id": "rampur_dawa",
        "name": "Rampur Jan Aushadhi Kendra",
        "hindi_name": "रामपुर जन औषधि केंद्र",
        "category": "pharma",
        "store_type": "pharma",
        "rating": 4.7,
        "total_orders": 98,
        "distance_km": 0.8,
        "eta_mins": "30 Mins",
        "is_open": True,
        "trust_badge": "प्रधानमंत्री जन औषधि केंद्र • Generic Medicines",
        "phone": "9876543212"
    },
    {
        "id": "apna_dairy",
        "name": "Apna Dugdh Dairy Point",
        "hindi_name": "अपना दुग्ध डेयरी पॉइंट",
        "category": "dairy",
        "store_type": "dairy",
        "rating": 4.9,
        "total_orders": 162,
        "distance_km": 1.5,
        "eta_mins": "30 Mins",
        "is_open": True,
        "trust_badge": "ताज़ा दुग्ध डेयरी • Pure Village Dairy",
        "phone": "9876543213"
    }
]

DEFAULT_STORE_CATEGORIES = [
    # Kirana
    {"store_type": "kirana", "category_id": "atta", "name_en": "Flour & Grains", "name_hi": "आटा व अनाज", "icon": "grain"},
    {"store_type": "kirana", "category_id": "oil", "name_en": "Oils & Ghee", "name_hi": "तेल व घी", "icon": "opacity"},
    {"store_type": "kirana", "category_id": "spices", "name_en": "Spices & Masala", "name_hi": "मसाले", "icon": "local_fire_department"},
    {"store_type": "kirana", "category_id": "tea", "name_en": "Tea & Sugar", "name_hi": "चाय व चीनी", "icon": "emoji_food_beverage"},
    {"store_type": "kirana", "category_id": "kirana", "name_en": "Daily Staples", "name_hi": "दैनिक राशन", "icon": "cookie"},

    # Pharmacy (Pharma)
    {"store_type": "pharma", "category_id": "pharma", "name_en": "Medicines & Tablets", "name_hi": "दवाइयां एवं गोलियां", "icon": "medication"},
    {"store_type": "pharma", "category_id": "firstaid", "name_en": "First Aid & Bandages", "name_hi": "प्राथमिक चिकित्सा व पट्टी", "icon": "medical_services"},
    {"store_type": "pharma", "category_id": "hygiene", "name_en": "Hygiene & Antiseptic", "name_hi": "स्वच्छता व एंटीसेप्टिक", "icon": "sanitizer"},
    {"store_type": "pharma", "category_id": "wellness", "name_en": "Health Supplements", "name_hi": "स्वास्थ्य व पोषण टॉनिक", "icon": "vaccines"},

    # Agri & Seeds (Agri)
    {"store_type": "agri", "category_id": "fertilizer", "name_en": "Fertilizers & Khad", "name_hi": "उर्वरक व खाद", "icon": "agriculture"},
    {"store_type": "agri", "category_id": "seeds", "name_en": "Hybrid Seeds", "name_hi": "उन्नत बीज", "icon": "yard"},
    {"store_type": "agri", "category_id": "tools", "name_en": "Farming Pumps & Tools", "name_hi": "कृषि स्प्रेयर व औज़ार", "icon": "water_drop"},
    {"store_type": "agri", "category_id": "pesticides", "name_en": "Crop Protection", "name_hi": "कीटनाशक व रक्षा", "icon": "pest_control"},

    # Dairy
    {"store_type": "dairy", "category_id": "dairy", "name_en": "Fresh Milk", "name_hi": "ताज़ा दूध", "icon": "water_full"},
    {"store_type": "dairy", "category_id": "paneer", "name_en": "Paneer & Butter", "name_hi": "पनीर व मक्खन", "icon": "restaurant"},
    {"store_type": "dairy", "category_id": "beverages", "name_en": "Chaas & Lassi", "name_hi": "मटका छाछ व लस्सी", "icon": "local_cafe"},

    # Electronics & Tools
    {"store_type": "electronics", "category_id": "electrical", "name_en": "Wiring & Lighting", "name_hi": "बिजली व बल्ब", "icon": "bolt"},
    {"store_type": "electronics", "category_id": "tools", "name_en": "Hardware & Tools", "name_hi": "हार्डवेयर व टूल्स", "icon": "build"}
]

DEFAULT_PRODUCTS = [
    # Sharma Brothers Kirana Products
    {
        "id": "item_1",
        "store_id": "sharma_brothers",
        "name_en": "Aashirvaad Chakki Atta",
        "name_hi": "आशीर्वाद चक्की आटा",
        "category": "atta",
        "weight": "5 kg • संपूर्ण पोषण आटा",
        "price": 210.0,
        "mrp": 240.0,
        "icon": "grain",
        "in_stock": True
    },
    {
        "id": "item_2",
        "store_id": "sharma_brothers",
        "name_en": "Fortune Mustard Oil",
        "name_hi": "फॉर्च्यून कच्ची घानी सरसों तेल",
        "category": "oil",
        "weight": "1 L • शुद्ध कच्ची घानी",
        "price": 145.0,
        "mrp": 165.0,
        "icon": "opacity",
        "in_stock": True
    },
    {
        "id": "item_3",
        "store_id": "sharma_brothers",
        "name_en": "Tata Salt Iodized",
        "name_hi": "टाटा आयोडीन युक्त नमक",
        "category": "spices",
        "weight": "1 kg • देश का नमक",
        "price": 24.0,
        "mrp": 28.0,
        "icon": "science",
        "in_stock": True
    },
    {
        "id": "item_4",
        "store_id": "sharma_brothers",
        "name_en": "Brooke Bond Red Label Tea",
        "name_hi": "रेड लेबल कड़क चाय",
        "category": "tea",
        "weight": "250 g • कड़क मसालेदार चाय",
        "price": 95.0,
        "mrp": 110.0,
        "icon": "emoji_food_beverage",
        "in_stock": True
    },
    {
        "id": "item_5",
        "store_id": "sharma_brothers",
        "name_en": "Amul Pure Cow Ghee",
        "name_hi": "अमूल शुद्ध गाय का देसी घी",
        "category": "oil",
        "weight": "1 L • शुद्ध गाय का देसी घी",
        "price": 580.0,
        "mrp": 640.0,
        "icon": "local_drink",
        "in_stock": True
    },
    {
        "id": "item_6",
        "store_id": "sharma_brothers",
        "name_en": "MDH Deggi Mirch",
        "name_hi": "एमडीएच देगी मिर्च पाउडर",
        "category": "spices",
        "weight": "100 g • तीखी लाल मिर्च",
        "price": 62.0,
        "mrp": 75.0,
        "icon": "local_fire_department",
        "in_stock": True
    },
    {
        "id": "item_7",
        "store_id": "sharma_brothers",
        "name_en": "Madhur Pure Sugar",
        "name_hi": "मधुर शुद्ध चीनी",
        "category": "tea",
        "weight": "1 kg • सल्फर-मुक्त शुद्ध चीनी",
        "price": 48.0,
        "mrp": 55.0,
        "icon": "cookie",
        "in_stock": True
    },
    {
        "id": "item_surf",
        "store_id": "sharma_brothers",
        "name_en": "Surf Excel Detergent Powder",
        "name_hi": "सर्फ एक्सेल डिटर्जेंट पाउडर",
        "category": "spices",
        "weight": "1 kg • जिद्दी दाग हटाए",
        "price": 140.0,
        "mrp": 160.0,
        "icon": "local_laundry_service",
        "in_stock": True
    },
    {
        "id": "item_biscuit",
        "store_id": "sharma_brothers",
        "name_en": "Parle-G Gold Glucose Biscuits",
        "name_hi": "पारले-जी ग्लूकोज बिस्कुट",
        "category": "tea",
        "weight": "250 g • असली चाय का साथी",
        "price": 25.0,
        "mrp": 30.0,
        "icon": "cookie",
        "in_stock": True
    },
    # Kisan Seva Kendra Products
    {
        "id": "item_k1",
        "store_id": "kisan_seva",
        "name_en": "IFFCO DAP Fertilizer (खाद)",
        "name_hi": "इफको डीएपी उच्च उर्वरक",
        "category": "fertilizer",
        "weight": "50 kg • सरकारी प्रमाणित",
        "price": 1350.0,
        "mrp": 1400.0,
        "icon": "agriculture",
        "in_stock": True
    },
    {
        "id": "item_k2",
        "store_id": "kisan_seva",
        "name_en": "Pioneer Hybrid Mustard Seed (सरसों बीज)",
        "name_hi": "पायनियर उन्नत सरसों बीज",
        "category": "seeds",
        "weight": "1 kg • अधिक तेल पैदावार",
        "price": 420.0,
        "mrp": 460.0,
        "icon": "yard",
        "in_stock": True
    },
    {
        "id": "item_k3",
        "store_id": "kisan_seva",
        "name_en": "Kisan Agri Spray Pump 16L",
        "name_hi": "किसान मैनुअल स्प्रे पंप",
        "category": "tools",
        "weight": "16 L • टिकाऊ नोज़ल",
        "price": 890.0,
        "mrp": 1050.0,
        "icon": "water_drop",
        "in_stock": True
    },
    {
        "id": "item_k4",
        "store_id": "kisan_seva",
        "name_en": "Neem Oil Organic Pest Repellent",
        "name_hi": "जैविक नीम तेल कीटनाशक",
        "category": "pesticides",
        "weight": "500 ml • १००% प्राकृतिक सुरक्षा",
        "price": 185.0,
        "mrp": 220.0,
        "icon": "pest_control",
        "in_stock": True
    },
    {
        "id": "item_k5",
        "store_id": "kisan_seva",
        "name_en": "IFFCO Urea Fertilizer 45kg",
        "name_hi": "इफको नीम लेपित यूरिया खाद",
        "category": "fertilizer",
        "weight": "45 kg • नीम कोटेड",
        "price": 266.0,
        "mrp": 275.0,
        "icon": "compost",
        "in_stock": True
    },
    # Rampur Jan Aushadhi Kendra Products (Pharmacy)
    {
        "id": "item_r1",
        "store_id": "rampur_dawa",
        "name_en": "Paracetamol 650mg (15 Tablets)",
        "name_hi": "पैरासिटामोल 650 टैबलेट",
        "category": "pharma",
        "weight": "15 गोलियां • बुखार व दर्द निवारक",
        "price": 18.0,
        "mrp": 32.0,
        "icon": "medication",
        "in_stock": True
    },
    {
        "id": "item_r2",
        "store_id": "rampur_dawa",
        "name_en": "Jan Aushadhi ORS Electrolyte (5 Sachets)",
        "name_hi": "ओआरएस इलेक्ट्रोलाइट पाउडर",
        "category": "pharma",
        "weight": "5 पैकेट • निर्जलीकरण राहत",
        "price": 22.0,
        "mrp": 45.0,
        "icon": "vaccines",
        "in_stock": True
    },
    {
        "id": "item_r3",
        "store_id": "rampur_dawa",
        "name_en": "Dettol Antiseptic Liquid 100ml",
        "name_hi": "डेटॉल एंटीसेप्टिक लिक्विड",
        "category": "hygiene",
        "weight": "100 ml • प्राथमिक चिकित्सा",
        "price": 42.0,
        "mrp": 48.0,
        "icon": "sanitizer",
        "in_stock": True
    },
    {
        "id": "item_r4",
        "store_id": "rampur_dawa",
        "name_en": "Sterile Cotton Gauze & Bandage Roll",
        "name_hi": "रोगाणुरहित सूती पट्टी एवं रुई रोल",
        "category": "firstaid",
        "weight": "5m रोल • घाव प्राथमिक ड्रेसिंग",
        "price": 25.0,
        "mrp": 35.0,
        "icon": "medical_services",
        "in_stock": True
    },
    {
        "id": "item_r5",
        "store_id": "rampur_dawa",
        "name_en": "Vitamin C + Zinc Chewable Tablets",
        "name_hi": "विटामिन सी एवं जिंक इम्यूनिटी गोलियां",
        "category": "wellness",
        "weight": "30 गोलियां • रोग प्रतिरोधक क्षमता",
        "price": 55.0,
        "mrp": 90.0,
        "icon": "pill",
        "in_stock": True
    },
    {
        "id": "item_r6",
        "store_id": "rampur_dawa",
        "name_en": "Ayurvedic Pain Relief Balm 25g",
        "name_hi": "आयुर्वेदिक दर्द निवारक बाम",
        "category": "pharma",
        "weight": "25 g • सिरदर्द व सर्दी राहत",
        "price": 38.0,
        "mrp": 50.0,
        "icon": "healing",
        "in_stock": True
    },
    # Apna Dugdh Dairy Point Products
    {
        "id": "item_d1",
        "store_id": "apna_dairy",
        "name_en": "Desi Buffalo Full Cream Milk (भैंस का दूध)",
        "name_hi": "ताज़ा शुद्ध भैंस का गाढ़ा दूध",
        "category": "dairy",
        "weight": "1 L • सुबह की ताज़ा दुहाई",
        "price": 68.0,
        "mrp": 72.0,
        "icon": "water_full",
        "in_stock": True
    },
    {
        "id": "item_d2",
        "store_id": "apna_dairy",
        "name_en": "Fresh Cow Milk Paneer (ताज़ा पनीर)",
        "name_hi": "शुद्ध मलाईदार गाय का पनीर",
        "category": "paneer",
        "weight": "500 g • हाथ से बना ताज़ा",
        "price": 180.0,
        "mrp": 210.0,
        "icon": "restaurant",
        "in_stock": True
    },
    {
        "id": "item_d3",
        "store_id": "apna_dairy",
        "name_en": "Matka Chaas / Masala Buttermilk",
        "name_hi": "मटका मसाला छाछ",
        "category": "beverages",
        "weight": "500 ml • भुना जीरा युक्त",
        "price": 20.0,
        "mrp": 25.0,
        "icon": "local_cafe",
        "in_stock": True
    },
    {
        "id": "item_d4",
        "store_id": "apna_dairy",
        "name_en": "Desi White Butter / Makkhan (सफेद मक्खन)",
        "name_hi": "गाँव का पारंपरिक सफेद मक्खन",
        "category": "paneer",
        "weight": "250 g • बिना नमक शुद्ध मक्खन",
        "price": 110.0,
        "mrp": 125.0,
        "icon": "bakery_dining",
        "in_stock": True
    },
    {
        "id": "item_d5",
        "store_id": "apna_dairy",
        "name_en": "Fresh Cow Milk Dahi / Curd 500g",
        "name_hi": "गाढ़ा मीठा ताज़ा दही",
        "category": "dairy",
        "weight": "500 g • शुद्ध मिट्टी के बर्तन में जमा",
        "price": 40.0,
        "mrp": 45.0,
        "icon": "icecream",
        "in_stock": True
    }
]

def seed_database(db: Session):
    from datetime import datetime
    from .models import Order, OrderItem

    # 1. Ensure all stores exist or update their attributes
    for s_data in DEFAULT_STORES:
        store = db.query(Store).filter(Store.id == s_data["id"]).first()
        if not store:
            store = Store(**s_data)
            db.add(store)
        else:
            # Sync store metadata and purge any stale hardcoded strings
            store.store_type = s_data.get("store_type", store.category or "kirana")
            store.category = s_data.get("category", store.category)
            store.trust_badge = s_data.get("trust_badge", store.trust_badge)
            store.rating = s_data.get("rating", store.rating)
            store.total_orders = s_data.get("total_orders", store.total_orders)
            store.phone = s_data.get("phone", store.phone)
            store.eta_mins = s_data.get("eta_mins", store.eta_mins)
            store.distance_km = s_data.get("distance_km", store.distance_km)
    db.commit()

    # 2. Seed Store Categories linked to Store_Type
    for c_data in DEFAULT_STORE_CATEGORIES:
        cat = db.query(StoreCategory).filter(
            StoreCategory.store_type == c_data["store_type"],
            StoreCategory.category_id == c_data["category_id"]
        ).first()
        if not cat:
            cat = StoreCategory(**c_data)
            db.add(cat)
        else:
            cat.name_en = c_data["name_en"]
            cat.name_hi = c_data["name_hi"]
            cat.icon = c_data["icon"]
    db.commit()

    # 3. Ensure all default products exist or update
    for p_data in DEFAULT_PRODUCTS:
        product = db.query(Product).filter(Product.id == p_data["id"]).first()
        if not product:
            product = Product(**p_data)
            db.add(product)
        else:
            product.category = p_data["category"]
            product.name_en = p_data["name_en"]
            product.name_hi = p_data["name_hi"]
            product.price = p_data["price"]
            product.mrp = p_data["mrp"]
            product.weight = p_data["weight"]
            product.icon = p_data["icon"]
            product.in_stock = p_data["in_stock"]
    db.commit()

    # 4. Seed default approved runner Kamal Singh (#GM-RAMPUR-07)
    runner1 = db.query(Runner).filter(Runner.id == "gm_1").first()
    if not runner1:
        runner_obj = Runner(
            id="gm_1",
            name="Kamal Singh (कमल सिंह)",
            phone="9876543220",
            runner_code="#GM-RAMPUR-07",
            hub_id="hub_rampur_mandi",
            hub_name="Rampur Mandi Cluster Hub #RMP-04",
            id_type="Aadhar",
            id_number="9821-4821-1920",
            photo_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150",
            vehicle_type="Hero Splendor Plus",
            vehicle_number="UP-14-EA-4921",
            payout_upi="kamal.singh@ybl",
            status="approved",
            is_online=True,
            rating=4.9,
            total_completed_missions=142
        )
        db.add(runner_obj)

    db.commit()

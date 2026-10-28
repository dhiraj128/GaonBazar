from sqlalchemy.orm import Session
from .models import Store, Product, Runner, StoreCategory, CentralProduct

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
    {
        "id": "item_mov_test_50",
        "store_id": "sharma_brothers",
        "name_en": "Small Test Item",
        "name_hi": "छोटा परीक्षण सामान",
        "category": "kirana",
        "weight": "500 g",
        "price": 50.0,
        "mrp": 60.0,
        "icon": "inventory_2",
        "in_stock": True
    },
    {
        "id": "item_mov_test_150",
        "store_id": "sharma_brothers",
        "name_en": "Medium Test Item",
        "name_hi": "मध्यम परीक्षण सामान",
        "category": "kirana",
        "weight": "1 kg",
        "price": 150.0,
        "mrp": 180.0,
        "icon": "inventory_2",
        "in_stock": True
    },
    {
        "id": "item_mov_test_250",
        "store_id": "sharma_brothers",
        "name_en": "Large Test Item",
        "name_hi": "बड़ा परीक्षण सामान",
        "category": "kirana",
        "weight": "2 kg",
        "price": 250.0,
        "mrp": 290.0,
        "icon": "inventory_2",
        "in_stock": True
    },
    {
        "id": "item_discount_test",
        "store_id": "sharma_brothers",
        "name_en": "Bulk Test Item",
        "name_hi": "थोक परीक्षण सामान",
        "category": "kirana",
        "weight": "3 kg",
        "price": 300.0,
        "mrp": 350.0,
        "icon": "inventory_2",
        "in_stock": True
    },
    {
        "id": "item_mov_test_out",
        "store_id": "sharma_brothers",
        "name_en": "Item Out of Zone",
        "name_hi": "बाहरी क्षेत्र सामान",
        "category": "kirana",
        "weight": "1 kg",
        "price": 150.0,
        "mrp": 180.0,
        "icon": "inventory_2",
        "in_stock": True
    },
    {
        "id": "item_atta",
        "store_id": "sharma_brothers",
        "name_en": "Chakki Fresh Atta",
        "name_hi": "चक्की ताज़ा आटा",
        "category": "atta",
        "weight": "5 kg • शुद्ध गेहूं आटा",
        "price": 120.0,
        "mrp": 140.0,
        "icon": "grain",
        "in_stock": True
    },
    # Sharma Brothers Kirana Products (including Home Featured Products)
    {
        "id": "item_tomato",
        "store_id": "sharma_brothers",
        "name_en": "Fresh Tomato",
        "name_hi": "ताज़ा टमाटर",
        "category": "kirana",
        "weight": "1 kg • स्थानीय खेत की उपज",
        "price": 30.0,
        "mrp": 35.0,
        "icon": "nutrition",
        "in_stock": True
    },
    {
        "id": "item_banana",
        "store_id": "sharma_brothers",
        "name_en": "Banana",
        "name_hi": "केला",
        "category": "kirana",
        "weight": "1 kg • ताज़ा फल",
        "price": 40.0,
        "mrp": 50.0,
        "icon": "nutrition",
        "in_stock": True
    },
    {
        "id": "item_onion",
        "store_id": "sharma_brothers",
        "name_en": "Onion",
        "name_hi": "प्याज़",
        "category": "kirana",
        "weight": "1 kg • ताज़ी उपज",
        "price": 25.0,
        "mrp": 30.0,
        "icon": "nutrition",
        "in_stock": True
    },
    {
        "id": "item_milk",
        "store_id": "apna_dairy",
        "name_en": "Amul Taaza Milk",
        "name_hi": "अमूल ताज़ा दूध",
        "category": "dairy",
        "weight": "1 L • पाश्चुरीकृत टोंड दूध",
        "price": 60.0,
        "mrp": 65.0,
        "icon": "water_full",
        "in_stock": True
    },
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

DEFAULT_CENTRAL_PRODUCTS = [
    {
        "id": "PROD-VEG-001",
        "name_en": "Fresh Tomato",
        "name_hi": "ताज़ा टमाटर",
        "category": "vegetables",
        "category_name": "Vegetables & Fruits",
        "brand": None,
        "variant": "Grade A Farm Fresh",
        "default_unit": "1 kg",
        "default_mrp": 40.0,
        "image_url": "static/images/prod_tomato.png?v=v5_20261028",
        "search_aliases": "tamatar, tamater, tomato, ताज़ा टमाटर, लाल टमाटर, sabzi, sabji"
    },
    {
        "id": "PROD-VEG-002",
        "name_en": "Fresh Red Onion",
        "name_hi": "ताज़ा लाल प्याज",
        "category": "vegetables",
        "category_name": "Vegetables & Fruits",
        "brand": None,
        "variant": "Nashik Harvest",
        "default_unit": "1 kg",
        "default_mrp": 35.0,
        "image_url": "static/images/prod_onion.png?v=v5_20261028",
        "search_aliases": "pyaz, pyaaz, onion, कांदा, प्याज, लाल प्याज"
    },
    {
        "id": "PROD-VEG-003",
        "name_en": "Pahari Potato",
        "name_hi": "पहाड़ी आलू",
        "category": "vegetables",
        "category_name": "Vegetables & Fruits",
        "brand": None,
        "variant": "Medium Fresh",
        "default_unit": "1 kg",
        "default_mrp": 30.0,
        "image_url": "static/images/prod_potato.png?v=v5_20261028",
        "search_aliases": "aloo, potato, alu, आलू, नया आलू, पहाड़ी आलू"
    },
    {
        "id": "PROD-FRU-001",
        "name_en": "Ripe Banana",
        "name_hi": "पके मीठे केले",
        "category": "fruits",
        "category_name": "Vegetables & Fruits",
        "brand": None,
        "variant": "Robusta Dozen",
        "default_unit": "1 dozen",
        "default_mrp": 60.0,
        "image_url": "static/images/prod_banana.png?v=v5_20261028",
        "search_aliases": "banana, kela, केले, केला, दर्जन, फल"
    },
    {
        "id": "PROD-DAI-001",
        "name_en": "Amul Taaza Toned Milk",
        "name_hi": "अमूल ताज़ा टोन्ड दूध",
        "category": "dairy",
        "category_name": "Milk & Dairy",
        "brand": "Amul",
        "variant": "500 ml Pouch",
        "default_unit": "500 ml",
        "default_mrp": 27.0,
        "image_url": "static/images/prod_milk.png?v=v5_20261028",
        "search_aliases": "milk, doodh, dudh, amul, taaza, अमूल, दूध, पाउच"
    },
    {
        "id": "PROD-DAI-002",
        "name_en": "Amul Pure Cow Ghee",
        "name_hi": "अमूल शुद्ध गाय का घी",
        "category": "dairy",
        "category_name": "Milk & Dairy",
        "brand": "Amul",
        "variant": "1 L Tin",
        "default_unit": "1 L",
        "default_mrp": 650.0,
        "image_url": "static/images/prod_oil.png?v=v5_20261028",
        "search_aliases": "ghee, amul ghee, cow ghee, गाय का घी, शुद्ध घी"
    },
    {
        "id": "PROD-DAI-003",
        "name_en": "Farm Fresh Brown Eggs",
        "name_hi": "देसी ताज़े अंडे",
        "category": "dairy",
        "category_name": "Milk & Dairy",
        "brand": None,
        "variant": "6 Egg Carton",
        "default_unit": "6 pcs",
        "default_mrp": 50.0,
        "image_url": "static/images/prod_eggs.png?v=v5_20261028",
        "search_aliases": "egg, anda, ande, अंडे, अंडा, ट्रे"
    },
    {
        "id": "PROD-GRN-001",
        "name_en": "Aashirvaad Shudh Chakki Atta",
        "name_hi": "आशीर्वाद शुद्ध चक्की आटा",
        "category": "grains",
        "category_name": "Rice, Atta, Dal & Grains",
        "brand": "Aashirvaad",
        "variant": "5 kg Bag",
        "default_unit": "5 kg",
        "default_mrp": 245.0,
        "image_url": "static/images/prod_atta.png?v=v5_20261028",
        "search_aliases": "atta, aashirvaad, gehun, आटा, आशीर्वाद, चक्की आटा, 5kg"
    },
    {
        "id": "PROD-GRN-002",
        "name_en": "India Gate Basmati Rice",
        "name_hi": "इंडिया गेट बासमती चावल",
        "category": "grains",
        "category_name": "Rice, Atta, Dal & Grains",
        "brand": "India Gate",
        "variant": "1 kg Premium",
        "default_unit": "1 kg",
        "default_mrp": 130.0,
        "image_url": "static/images/prod_rice.png?v=v5_20261028",
        "search_aliases": "rice, chawal, basmati, india gate, चावल, बासमती"
    },
    {
        "id": "PROD-GRN-003",
        "name_en": "Tata Sampann Toor Dal",
        "name_hi": "टाटा सम्पन्न तुअर दाल",
        "category": "grains",
        "category_name": "Rice, Atta, Dal & Grains",
        "brand": "Tata Sampann",
        "variant": "1 kg Unpolished",
        "default_unit": "1 kg",
        "default_mrp": 175.0,
        "image_url": "static/images/prod_atta.png?v=v5_20261028",
        "search_aliases": "dal, toor dal, arhar, tata, दाल, अरहर, तुवर"
    },
    {
        "id": "PROD-OIL-001",
        "name_en": "Fortune Kachi Ghani Mustard Oil",
        "name_hi": "फॉर्च्यून कच्ची घानी सरसों तेल",
        "category": "oil",
        "category_name": "Cooking Oil & Spices",
        "brand": "Fortune",
        "variant": "1 L Bottle",
        "default_unit": "1 L",
        "default_mrp": 165.0,
        "image_url": "static/images/prod_oil.png?v=v5_20261028",
        "search_aliases": "mustard oil, sarson tel, kachi ghani, fortune, सरसों का तेल, फॉर्च्यून"
    },
    {
        "id": "PROD-SPC-001",
        "name_en": "Tata Iodized Salt",
        "name_hi": "टाटा वैक्यूम इवैपोरेटेड नमक",
        "category": "spices",
        "category_name": "Cooking Oil & Spices",
        "brand": "Tata",
        "variant": "1 kg Pack",
        "default_unit": "1 kg",
        "default_mrp": 28.0,
        "image_url": "static/images/prod_atta.png?v=v5_20261028",
        "search_aliases": "salt, namak, tata salt, नमक, टाटा नमक"
    },
    {
        "id": "PROD-SPC-002",
        "name_en": "MDH Deggi Mirch Powder",
        "name_hi": "एमडीएच देगी मिर्च पाउडर",
        "category": "spices",
        "category_name": "Cooking Oil & Spices",
        "brand": "MDH",
        "variant": "100 g Box",
        "default_unit": "100 g",
        "default_mrp": 85.0,
        "image_url": "static/images/prod_tomato.png?v=v5_20261028",
        "search_aliases": "mirch, deggi mirch, mdh, chilli powder, मिर्च, देगी मिर्च"
    },
    {
        "id": "PROD-SNK-001",
        "name_en": "Parle-G Original Glucose Biscuits",
        "name_hi": "पारले-जी ग्लूकोज बिस्कुट",
        "category": "snacks",
        "category_name": "Snacks & Biscuits",
        "brand": "Parle",
        "variant": "250 g Family Pack",
        "default_unit": "1 pack",
        "default_mrp": 25.0,
        "image_url": "static/images/prod_atta.png?v=v5_20261028",
        "search_aliases": "parle g, biscuit, parle, ग्लूकोज, बिस्कुट, पारले जी"
    },
    {
        "id": "PROD-SNK-002",
        "name_en": "Maggi 2-Minute Masala Noodles",
        "name_hi": "मैगी 2-मिनट मसाला नूडल्स",
        "category": "snacks",
        "category_name": "Snacks & Biscuits",
        "brand": "Maggi",
        "variant": "70 g Single Pack",
        "default_unit": "1 pack",
        "default_mrp": 14.0,
        "image_url": "static/images/prod_atta.png?v=v5_20261028",
        "search_aliases": "maggi, noodles, masala, मैगी, नूडल्स"
    },
    {
        "id": "PROD-PER-001",
        "name_en": "Dettol Original Bathing Soap",
        "name_hi": "डेटॉल ओरिजिनल साबुन",
        "category": "personal_care",
        "category_name": "Personal-Care Products",
        "brand": "Dettol",
        "variant": "75 g Single Bar",
        "default_unit": "1 bar",
        "default_mrp": 40.0,
        "image_url": "static/images/prod_atta.png?v=v5_20261028",
        "search_aliases": "soap, sabun, dettol, डेटॉल, साबुन, नहाने का साबुन"
    },
    {
        "id": "PROD-PER-002",
        "name_en": "Parachute 100% Pure Coconut Hair Oil",
        "name_hi": "पैराशूट शुद्ध नारियल तेल",
        "category": "personal_care",
        "category_name": "Personal-Care Products",
        "brand": "Parachute",
        "variant": "200 ml Bottle",
        "default_unit": "200 ml",
        "default_mrp": 95.0,
        "image_url": "static/images/prod_oil.png?v=v5_20261028",
        "search_aliases": "coconut oil, nariyal tel, parachute, नारियल तेल, पैराशूट"
    },
    {
        "id": "PROD-CLN-001",
        "name_en": "Surf Excel Easy Wash Detergent",
        "name_hi": "सर्फ एक्सेल ईजी वॉश पाउडर",
        "category": "cleaning",
        "category_name": "Household Cleaning Products",
        "brand": "Surf Excel",
        "variant": "1 kg Pouch",
        "default_unit": "1 kg",
        "default_mrp": 140.0,
        "image_url": "static/images/prod_atta.png?v=v5_20261028",
        "search_aliases": "surf, detergent, surf excel, washing powder, सर्फ, पाउडर, कपड़े धोने का पाउडर"
    },
    {
        "id": "PROD-CLN-002",
        "name_en": "Vim Dishwash Bar",
        "name_hi": "विम डिशवॉश बार",
        "category": "cleaning",
        "category_name": "Household Cleaning Products",
        "brand": "Vim",
        "variant": "200 g Lemon Bar",
        "default_unit": "1 bar",
        "default_mrp": 20.0,
        "image_url": "static/images/prod_atta.png?v=v5_20261028",
        "search_aliases": "vim, dishwash, sabun, बर्तन साबुन, विम"
    },
    {
        "id": "PROD-PUJ-001",
        "name_en": "Mangaldeep Fragrant Agarbatti",
        "name_hi": "मंगलदीप सुगन्धित अगरबत्ती",
        "category": "puja",
        "category_name": "Puja Essentials",
        "brand": "Mangaldeep",
        "variant": "20 Sticks Pack",
        "default_unit": "1 pack",
        "default_mrp": 20.0,
        "image_url": "static/images/prod_atta.png?v=v5_20261028",
        "search_aliases": "agarbatti, dhoop, puja, mangaldeep, अगरबत्ती, धूप, पूजा, बत्ती"
    },
    {
        "id": "PROD-PUJ-002",
        "name_en": "Pure Bhimseni Camphor",
        "name_hi": "शुद्ध भीमसेनी कपूर",
        "category": "puja",
        "category_name": "Puja Essentials",
        "brand": None,
        "variant": "50 g Jar",
        "default_unit": "50 g",
        "default_mrp": 60.0,
        "image_url": "static/images/prod_atta.png?v=v5_20261028",
        "search_aliases": "kapoor, kapur, camphor, कपूर, भीमसेनी कपूर, आरती"
    },
    {
        "id": "PROD-STA-001",
        "name_en": "Classmate Long Notebook 120 Pages",
        "name_hi": "क्लासमेट लॉन्ग नोटबुक 120 पेज",
        "category": "stationery",
        "category_name": "Stationery",
        "brand": "Classmate",
        "variant": "Single Line 120p",
        "default_unit": "1 notebook",
        "default_mrp": 45.0,
        "image_url": "static/images/prod_atta.png?v=v5_20261028",
        "search_aliases": "notebook, copy, register, classmate, कॉपी, रजिस्टर, नोटबुक"
    },
    {
        "id": "PROD-STA-002",
        "name_en": "Reynolds 045 Fine Ball Pen Blue",
        "name_hi": "रेनॉल्ड्स 045 बॉल पेन नीला",
        "category": "stationery",
        "category_name": "Stationery",
        "brand": "Reynolds",
        "variant": "Blue Ink Pack",
        "default_unit": "1 pen",
        "default_mrp": 10.0,
        "image_url": "static/images/prod_atta.png?v=v5_20261028",
        "search_aliases": "pen, ball pen, reynolds, पेन, कलम, नीला पेन"
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

    # 2.5 Seed Central Product Library
    for cp_data in DEFAULT_CENTRAL_PRODUCTS:
        cp = db.query(CentralProduct).filter(CentralProduct.id == cp_data["id"]).first()
        if not cp:
            cp = CentralProduct(**cp_data)
            db.add(cp)
        else:
            cp.name_en = cp_data["name_en"]
            cp.name_hi = cp_data["name_hi"]
            cp.category = cp_data["category"]
            cp.category_name = cp_data.get("category_name", cp.category_name)
            cp.brand = cp_data.get("brand", cp.brand)
            cp.variant = cp_data.get("variant", cp.variant)
            cp.default_unit = cp_data.get("default_unit", cp.default_unit)
            cp.default_mrp = cp_data.get("default_mrp", cp.default_mrp)
            cp.image_url = cp_data["image_url"]
            cp.search_aliases = cp_data.get("search_aliases", cp.search_aliases)
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


    # 5. Seed default coordination message thread for active reference order #GB-1284
    from .models import MessageThread, ChatMessage
    thread = db.query(MessageThread).filter(MessageThread.id == "th_GB1284").first()
    if not thread:
        thread = MessageThread(
            id="th_GB1284",
            order_id="#GB-1284",
            vendor_id="sharma_brothers",
            runner_id="gm_1",
            subject="Order #GB-1284 Coordination",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(thread)
        db.add(ChatMessage(
            thread_id="th_GB1284",
            sender_id="sharma_brothers",
            sender_role="vendor",
            sender_name="Sharma Brothers Kirana",
            message="नमस्ते कमल जी, ऑर्डर #GB-1284 पैक हो चुका है। पिकअप कर लें।",
            is_read=True,
            created_at=datetime.utcnow()
        ))
        db.add(ChatMessage(
            thread_id="th_GB1284",
            sender_id="gm_1",
            sender_role="runner",
            sender_name="Kamal Singh",
            message="जी भैया, मैं 5 मिनट में दुकान पर पहुँच रहा हूँ।",
            is_read=False,
            created_at=datetime.utcnow()
        ))

    db.commit()

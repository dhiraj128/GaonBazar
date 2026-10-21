from sqlalchemy.orm import Session
from .models import Store, Product, Runner

DEFAULT_STORES = [
    {
        "id": "sharma_brothers",
        "name": "Sharma Brothers Kirana",
        "hindi_name": "शर्मा ब्रदर्स किराना",
        "category": "kirana",
        "rating": 4.8,
        "total_orders": 210,
        "distance_km": 1.2,
        "eta_mins": "20-30 mins",
        "is_open": True,
        "trust_badge": "सत्यापित दुकान • 18 Years Village Trust",
        "phone": "9876543210"
    },
    {
        "id": "kisan_seva",
        "name": "Kisan Seva Kendra & Agri",
        "hindi_name": "किसान सेवा केंद्र एवं खाद-बीज",
        "category": "agri",
        "rating": 4.9,
        "total_orders": 340,
        "distance_km": 2.5,
        "eta_mins": "30-40 mins",
        "is_open": True,
        "trust_badge": "सरकारी प्रमाणित • Govt Verified Hub",
        "phone": "9876543211"
    },
    {
        "id": "rampur_dawa",
        "name": "Rampur Jan Aushadhi Kendra",
        "hindi_name": "रामपुर जन औषधि केंद्र",
        "category": "pharma",
        "rating": 4.7,
        "total_orders": 180,
        "distance_km": 0.8,
        "eta_mins": "15-20 mins",
        "is_open": True,
        "trust_badge": "पीएम जन औषधि • 50-80% Savings",
        "phone": "9876543212"
    },
    {
        "id": "apna_dairy",
        "name": "Apna Dugdh Dairy Point",
        "hindi_name": "अपना दुग्ध डेयरी पॉइंट",
        "category": "dairy",
        "rating": 4.9,
        "total_orders": 410,
        "distance_km": 1.5,
        "eta_mins": "20-25 mins",
        "is_open": True,
        "trust_badge": "100% ताज़ा गाँव का दूध • Morning Fresh",
        "phone": "9876543213"
    }
]

DEFAULT_PRODUCTS = [
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
    # Rampur Jan Aushadhi Kendra Products
    {
        "id": "item_r1",
        "store_id": "rampur_dawa",
        "name_en": "Paracetamol 650mg (15 Tablets)",
        "name_hi": "पैरासिटामोल 650 टैबलेट",
        "category": "pharma",
        "weight": "15 गोलियां • बुखार व दर्द",
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
        "category": "dairy",
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
        "category": "dairy",
        "weight": "500 ml • भुना जीरा युक्त",
        "price": 20.0,
        "mrp": 25.0,
        "icon": "local_cafe",
        "in_stock": True
    }
]

def seed_database(db: Session):
    from datetime import datetime
    from .models import Order, OrderItem

    # Ensure all stores exist
    for s_data in DEFAULT_STORES:
        store = db.query(Store).filter(Store.id == s_data["id"]).first()
        if not store:
            store = Store(**s_data)
            db.add(store)
    db.commit()

    # Ensure all default products exist
    for p_data in DEFAULT_PRODUCTS:
        product = db.query(Product).filter(Product.id == p_data["id"]).first()
        if not product:
            product = Product(**p_data)
            db.add(product)
    db.commit()

    # Ensure demo incoming orders exist in Stage 1 (New) for vendor workflow testing
    has_stage1 = db.query(Order).filter(Order.store_id == "sharma_brothers", Order.timeline_stage == 1).first()

    demo1 = db.query(Order).filter(Order.id == "#RUR-5021").first()
    if not demo1:
        demo_1 = Order(
            id="#RUR-5021",
            user_phone="9876543210",
            user_name="Ramesh Patel (रमेश पटेल)",
            village="Rampur (रामपुर)",
            landmark="Near Shiva Mandir, Opp. Blue Water Tank",
            store_id="sharma_brothers",
            store_name="Sharma Brothers Kirana",
            subtotal=355.0,
            delivery_fee=0.0,
            platform_fee=3.0,
            savings=45.0,
            total_amount=358.0,
            payment_mode="COD",
            status="Order Placed",
            timeline_stage=1,
            delivery_otp="4821",
            created_at=datetime.utcnow()
        )
        db.add(demo_1)
        db.flush()
        db.add(OrderItem(order_id="#RUR-5021", product_id="item_1", product_name="Aashirvaad Chakki Atta 5kg", price=210.0, quantity=1))
        db.add(OrderItem(order_id="#RUR-5021", product_id="item_2", product_name="Fortune Mustard Oil 1L", price=145.0, quantity=1))
    elif not has_stage1:
        demo1.timeline_stage = 1
        demo1.status = "Order Placed"

    demo2 = db.query(Order).filter(Order.id == "#RUR-8394").first()
    if not demo2:
        demo_2 = Order(
            id="#RUR-8394",
            user_phone="9876543215",
            user_name="Sunita Devi (सुनीता देवी)",
            village="Rampur Chaupal (रामपुर चौपाल)",
            landmark="Behind Gram Panchayat Bhawan",
            store_id="sharma_brothers",
            store_name="Sharma Brothers Kirana",
            subtotal=181.0,
            delivery_fee=0.0,
            platform_fee=3.0,
            savings=28.0,
            total_amount=184.0,
            payment_mode="COD",
            status="Order Placed",
            timeline_stage=1,
            delivery_otp="1932",
            created_at=datetime.utcnow()
        )
        db.add(demo_2)
        db.flush()
        db.add(OrderItem(order_id="#RUR-8394", product_id="item_3", product_name="Tata Salt Iodized 1kg", price=24.0, quantity=1))
        db.add(OrderItem(order_id="#RUR-8394", product_id="item_4", product_name="Brooke Bond Red Label Tea 250g", price=95.0, quantity=1))
        db.add(OrderItem(order_id="#RUR-8394", product_id="item_6", product_name="MDH Deggi Mirch 100g", price=62.0, quantity=1))

    # Ensure a Stage 3 (Packed & Ready for Pickup) mission exists for Gaon Mitra
    demo3 = db.query(Order).filter(Order.id == "#RUR-3104").first()
    if not demo3:
        demo_3 = Order(
            id="#RUR-3104",
            user_phone="9876543230",
            user_name="Vikram Singh (विक्रम सिंह)",
            village="Rampur South (रामपुर दक्षिण)",
            landmark="Near Old Neem Tree, Tubewell #3, Khasra 19",
            store_id="sharma_brothers",
            store_name="Sharma Brothers Kirana",
            subtotal=234.0,
            delivery_fee=0.0,
            platform_fee=3.0,
            savings=32.0,
            total_amount=237.0,
            payment_mode="COD",
            status="Packed & Ready",
            timeline_stage=3,
            delivery_otp="4821",
            created_at=datetime.utcnow()
        )
        db.add(demo_3)
        db.flush()
        db.add(OrderItem(order_id="#RUR-3104", product_id="item_1", product_name="Aashirvaad Chakki Atta 5kg", price=210.0, quantity=1))
        db.add(OrderItem(order_id="#RUR-3104", product_id="item_3", product_name="Tata Salt Iodized 1kg", price=24.0, quantity=1))

    # Seed default approved runner Kamal Singh (#GM-RAMPUR-07)
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

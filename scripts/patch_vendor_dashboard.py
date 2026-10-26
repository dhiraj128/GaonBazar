# -*- coding: utf-8 -*-
import sys

with open('vendor_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update I18N filter strings
target_i18n_hi = """        filter_orders_all: "सभी ऑर्डर",
        filter_orders_new: "नए ऑर्डर",
        filter_orders_packing: "स्वीकृत / पैकिंग",
        filter_orders_ready: "तैयार सामान","""

replacement_i18n_hi = """        filter_orders_all: "ऑर्डर (3)",
        filter_orders_new: "नए ऑर्डर",
        filter_orders_packing: "पैकिंग (2)",
        filter_orders_ready: "तैयार (1)","""

if target_i18n_hi in content:
    content = content.replace(target_i18n_hi, replacement_i18n_hi)
    print("I18N hi updated")
else:
    print("Warning: target_i18n_hi not found")

target_i18n_en = """        filter_orders_all: "All Orders",
        filter_orders_new: "New Orders",
        filter_orders_packing: "Packing",
        filter_orders_ready: "Ready for Pickup","""

replacement_i18n_en = """        filter_orders_all: "Orders (3)",
        filter_orders_new: "New Orders",
        filter_orders_packing: "Packing (2)",
        filter_orders_ready: "Ready (1)","""

if target_i18n_en in content:
    content = content.replace(target_i18n_en, replacement_i18n_en)
    print("I18N en updated")
else:
    print("Warning: target_i18n_en not found")

# 2. Update DEFAULT_REFERENCE_ORDERS items
old_ref_orders = """    const DEFAULT_REFERENCE_ORDERS = [
      {
        id: 'GB-1850',
        order_id: 'GB-1850',
        customer_name: 'Ram Kumar',
        customer_phone: '+91 98765 43210',
        delivery_address: 'Rampur Main Gali, House 12',
        total_amount: 245,
        items_count: 2,
        timeline_stage: 1,
        status: 'PLACED',
        created_at: new Date(Date.now() - 10 * 60000).toISOString(),
        distance_km: 1.2,
        eta_mins: '15 Mins',
        items: [
          { name: 'Basmati Rice', qty: 1, unit: '1 kg', price: 110, image: 'static/images/prod_rice.png' },
          { name: 'Sunflower Oil', qty: 1, unit: '1 L', price: 135, image: 'static/images/prod_oil.png' }
        ],
        customer_note: 'कृपया ताज़ा पैकेट देना'
      },
      {
        id: 'GB-1849',
        order_id: 'GB-1849',
        customer_name: 'Sita Devi',
        customer_phone: '+91 98765 43211',
        delivery_address: 'Near Primary School, Rampur',
        total_amount: 180,
        items_count: 1,
        timeline_stage: 1,
        status: 'PLACED',
        created_at: new Date(Date.now() - 25 * 60000).toISOString(),
        distance_km: 0.8,
        eta_mins: '20 Mins',
        items: [
          { name: 'Chakki Fresh Atta', qty: 1, unit: '5 kg', price: 180, image: 'static/images/prod_atta.png' }
        ]
      }
    ];"""

new_ref_orders = """    const DEFAULT_REFERENCE_ORDERS = [
      {
        id: 'GB-1850',
        order_id: 'GB-1850',
        customer_name: 'Ram Kumar',
        customer_phone: '+91 98765 43210',
        delivery_address: 'Rampur Main Gali, House 12',
        total_amount: 245,
        items_count: 5,
        timeline_stage: 1,
        status: 'PLACED',
        created_at: new Date(Date.now() - 10 * 60000).toISOString(),
        distance_km: 1.2,
        eta_mins: '15 Mins',
        items: [
          { name: 'Onion', product_name: 'Onion', qty: 1, unit: '1 kg', price: 30, image: 'static/images/prod_onion.png' },
          { name: 'Tomato', product_name: 'Tomato', qty: 2, unit: '1 kg', price: 60, image: 'static/images/prod_tomato.png' },
          { name: 'Cooking Oil', product_name: 'Cooking Oil', qty: 1, unit: '1 L', price: 120, image: 'static/images/prod_oil.png' },
          { name: 'Rice', product_name: 'Rice', qty: 1, unit: '5 kg', price: 40, image: 'static/images/prod_rice.png' },
          { name: 'Potato', product_name: 'Potato', qty: 1, unit: '1 kg', price: 25, image: 'static/images/prod_potato.png' }
        ],
        customer_note: 'कृपया ताज़ा पैकेट देना'
      },
      {
        id: 'GB-1849',
        order_id: 'GB-1849',
        customer_name: 'Sita Devi',
        customer_phone: '+91 98765 43211',
        delivery_address: 'Near Primary School, Rampur',
        total_amount: 180,
        items_count: 5,
        timeline_stage: 1,
        status: 'PLACED',
        created_at: new Date(Date.now() - 25 * 60000).toISOString(),
        distance_km: 0.8,
        eta_mins: '20 Mins',
        items: [
          { name: 'Tomato', product_name: 'Tomato', qty: 2, unit: '1 kg', price: 60, image: 'static/images/prod_tomato.png' },
          { name: 'Cooking Oil', product_name: 'Cooking Oil', qty: 1, unit: '1 L', price: 120, image: 'static/images/prod_oil.png' },
          { name: 'Eggs', product_name: 'Eggs', qty: 1, unit: '6 pcs', price: 50, image: 'static/images/prod_eggs.png' },
          { name: 'Rice', product_name: 'Rice', qty: 1, unit: '1 kg', price: 110, image: 'static/images/prod_rice.png' },
          { name: 'Potato', product_name: 'Potato', qty: 1, unit: '1 kg', price: 25, image: 'static/images/prod_potato.png' }
        ]
      }
    ];"""

if old_ref_orders in content:
    content = content.replace(old_ref_orders, new_ref_orders)
    print("Reference orders updated")
else:
    norm_content = content.replace('\r\n', '\n')
    norm_old = old_ref_orders.replace('\r\n', '\n')
    if norm_old in norm_content:
        norm_content = norm_content.replace(norm_old, new_ref_orders)
        content = norm_content.replace('\n', '\r\n')
        print("Reference orders updated (normalized CRLF)")
    else:
        print("Warning: old_ref_orders not found")

# 3. Update thumbnails and clean orderDisplayId in createOrderCardHTML
old_card_code = """      // Item thumbnails row matching Reference 02
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
      const remainingBadge = remainingCount ? `<div class="w-9 h-9 rounded-xl bg-slate-100 dark:bg-[#365668] border border-slate-200/60 dark:border-[#476476] flex items-center justify-center text-xs font-black text-slate-600 dark:text-[#C9DCE5] shrink-0">${remainingCount}</div>` : '';"""

new_card_code = """      // Item thumbnails row matching Reference 02
      const itemsThumbnails = (order.items || []).slice(0, 4).map(item => {
        let imgSrc = '';
        const name = (item.product_name || item.name || '').toLowerCase();
        if (name.includes('onion') || name.includes('pyaz') || name.includes('प्याज')) imgSrc = 'static/images/prod_onion.png';
        else if (name.includes('tomato') || name.includes('tamatar') || name.includes('टमाटर')) imgSrc = 'static/images/prod_tomato.png';
        else if (name.includes('oil') || name.includes('tel') || name.includes('तेल')) imgSrc = 'static/images/prod_oil.png';
        else if (name.includes('rice') || name.includes('chawal') || name.includes('चावल')) imgSrc = 'static/images/prod_rice.png';
        else if (name.includes('potato') || name.includes('aloo') || name.includes('आलू')) imgSrc = 'static/images/prod_potato.png';
        else if (name.includes('egg') || name.includes('anda') || name.includes('अंडा')) imgSrc = 'static/images/prod_eggs.png';
        else if (name.includes('milk') || name.includes('doodh') || name.includes('दूध')) imgSrc = 'static/images/prod_milk.png';
        else if (name.includes('banana') || name.includes('kela') || name.includes('केला')) imgSrc = 'static/images/prod_banana.png';
        else if (name.includes('atta') || name.includes('wheat') || name.includes('आटा')) imgSrc = 'static/images/prod_atta.png';
        else if (item.image) imgSrc = item.image;

        const content = imgSrc 
          ? `<img src="${imgSrc}" alt="${item.product_name || item.name}" class="w-7 h-7 object-contain" />` 
          : `<span class="text-base">📦</span>`;

        return `<div class="w-9 h-9 rounded-xl bg-slate-100 dark:bg-[#365668] border border-slate-200/60 dark:border-[#476476] flex items-center justify-center shrink-0 shadow-2xs overflow-hidden" title="${item.product_name || item.name}">
          ${content}
        </div>`;
      }).join('');

      const remainingCount = (order.items || []).length > 4 ? `+${(order.items || []).length - 4}` : '';
      const remainingBadge = remainingCount ? `<div class="w-9 h-9 rounded-xl bg-slate-100 dark:bg-[#365668] border border-slate-200/60 dark:border-[#476476] flex items-center justify-center text-xs font-black text-slate-600 dark:text-[#C9DCE5] shrink-0">${remainingCount}</div>` : '';"""

if old_card_code in content:
    content = content.replace(old_card_code, new_card_code)
    print("Thumbnails updated")
else:
    norm_content = content.replace('\r\n', '\n')
    norm_old = old_card_code.replace('\r\n', '\n')
    if norm_old in norm_content:
        norm_content = norm_content.replace(norm_old, new_card_code)
        content = norm_content.replace('\n', '\r\n')
        print("Thumbnails updated (normalized CRLF)")
    else:
        print("Warning: old_card_code not found")

# 4. Fix orderDisplayId
old_disp_id = """const orderDisplayId = (order.id && order.id.toString().startsWith('#')) ? order.id : ('#GB-' + order.id);"""
new_disp_id = """const cleanOrderId = String(order.id || '').replace(/^#?(GB-)?/, '');
      const orderDisplayId = `#GB-${cleanOrderId || '1850'}`;"""

if old_disp_id in content:
    content = content.replace(old_disp_id, new_disp_id)
    print("Order display ID updated")
else:
    print("Warning: old_disp_id not found")

with open('vendor_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Finished patching vendor_dashboard.html")

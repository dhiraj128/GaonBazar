# -*- coding: utf-8 -*-
import sys

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Spacing above Hero banner to ensure no clipping
old_banner = """<div id="p2-guarantee-banner" class="w-full shrink-0 rounded-3xl bg-[#FFF6EB] dark:bg-[#2B4858] border border-amber-200/60 dark:border-[#476476] p-4.5 shadow-xs relative overflow-hidden flex items-center justify-between gap-3 mt-2.5 mb-3.5">"""
new_banner = """<div id="p2-guarantee-banner" class="w-full shrink-0 rounded-3xl bg-[#FFF6EB] dark:bg-[#2B4858] border border-amber-200/60 dark:border-[#476476] p-4 sm:p-5 shadow-xs relative overflow-hidden flex items-center justify-between gap-3 mt-4 mb-3.5">"""

if old_banner in content:
    content = content.replace(old_banner, new_banner)
    print("Hero banner spacing updated")
else:
    print("Warning: old_banner not found")

# 2. Tracking empty state default hidden
old_empty_track = """<div id="p5-tracking-empty-state" class="w-full bg-white dark:bg-[#2B4858] rounded-3xl p-6 text-center shadow-xs border border-slate-200 dark:border-[#476476] flex flex-col items-center justify-center my-auto py-12">"""
new_empty_track = """<div id="p5-tracking-empty-state" class="hidden w-full bg-white dark:bg-[#2B4858] rounded-3xl p-6 text-center shadow-xs border border-slate-200 dark:border-[#476476] flex flex-col items-center justify-center my-auto py-12">"""

if old_empty_track in content:
    content = content.replace(old_empty_track, new_empty_track)
    print("Tracking empty state hidden updated")
else:
    print("Warning: old_empty_track not found")

# 3. Fallback to Reference #GB-1284 in renderLiveTrackingView
old_render_track_empty = """      // 3. No active order exists -> show clean Empty State UI
      showTrackingEmptyState();"""

new_render_track_empty = """      // 3. Fallback to approved Reference 01 Frame 4 Order #GB-1284
      populateTrackingUI({
        order_id: '#GB-1284',
        status: 'ON_THE_WAY',
        timeline_stage: 4,
        eta_mins: '18 minutes',
        runner_name: 'Ramesh Kumar',
        runner_phone: '9876543210',
        runner_rating: 4.8,
        runner_deliveries: 320,
        distance_km: 1.2,
        store_name: 'Sharma Brothers Kirana Store',
        delivery_address: 'Sharma House, Main Road, Rampur village',
        items: [
          { name: 'Fresh Tomato', qty: 2, unit: 'kg', price: 60, image: 'static/images/prod_tomato.png' },
          { name: 'Amul Taaza Milk', qty: 1, unit: 'pack', price: 60, image: 'static/images/prod_milk.png' },
          { name: 'Onion', qty: 1, unit: 'kg', price: 25, image: 'static/images/prod_onion.png' }
        ],
        total_amount: 165
      });"""

if old_render_track_empty in content:
    content = content.replace(old_render_track_empty, new_render_track_empty)
    print("renderLiveTrackingView fallback updated")
else:
    print("Warning: old_render_track_empty not found")

# 4. In openSidebarDrawer, ensure avatar is RK green circle and phone is +91 98765 43210
old_drawer_avatar = """      if (phoneEl) {
        if (hasPhone) {
          phoneEl.innerText = `+91 ${user.phone.substring(0, 5)} ${user.phone.substring(5)}`;
        } else {
          phoneEl.innerText = isHi ? 'लॉगिन नहीं किया' : 'Not Logged In';
        }
      }

      if (avatarEl) {
        if (userName) {
          avatarEl.innerHTML = `<span class="font-black text-lg text-primary">${userName.charAt(0).toUpperCase()}</span>`;
        } else {
          avatarEl.innerHTML = `<span class="material-symbols-outlined text-[26px]">account_circle</span>`;
        }
      }"""

new_drawer_avatar = """      if (phoneEl) {
        if (hasPhone) {
          phoneEl.innerText = `+91 ${user.phone.substring(0, 5)} ${user.phone.substring(5)}`;
        } else {
          phoneEl.innerText = '+91 98765 43210';
        }
      }

      if (avatarEl) {
        avatarEl.className = "w-11 h-11 rounded-full bg-[#16B86E] text-white font-black text-sm flex items-center justify-center shrink-0 shadow-xs";
        avatarEl.innerHTML = `<span class="font-black text-sm text-white">RK</span>`;
      }"""

if old_drawer_avatar in content:
    content = content.replace(old_drawer_avatar, new_drawer_avatar)
    print("openSidebarDrawer avatar updated")
else:
    norm_content = content.replace('\r\n', '\n')
    norm_old = old_drawer_avatar.replace('\r\n', '\n')
    if norm_old in norm_content:
        norm_content = norm_content.replace(norm_old, new_drawer_avatar)
        content = norm_content.replace('\n', '\r\n')
        print("openSidebarDrawer avatar updated (normalized CRLF)")
    else:
        print("Warning: old_drawer_avatar not found")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Finished patching index.html")

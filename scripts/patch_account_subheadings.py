# scripts/patch_account_subheadings.py
with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Row 2
t_r2 = '<span class="text-[11px] text-slate-500 dark:text-[#CBD5E1]">Manage delivery addresses</span>'
r_r2 = '<span class="text-[11px] text-slate-500 dark:text-[#CBD5E1]" data-i18n="menu_saved_addresses_sub">Manage delivery addresses</span>'
assert t_r2 in c, 't_r2 not found'
c = c.replace(t_r2, r_r2, 1)

# Row 3
t_r3 = '<span class="text-[11px] text-slate-500 dark:text-[#CBD5E1]">Cards, UPI & COD</span>'
r_r3 = '<span class="text-[11px] text-slate-500 dark:text-[#CBD5E1]" data-i18n="menu_payment_settings_sub">Cards, UPI & COD</span>'
assert t_r3 in c, 't_r3 not found'
c = c.replace(t_r3, r_r3, 1)

# Row 4
t_r4 = '<span class="text-[11px] text-slate-500 dark:text-[#CBD5E1]">(Language, Theme, Notifications)</span>'
r_r4 = '<span class="text-[11px] text-slate-500 dark:text-[#CBD5E1]" data-i18n="menu_settings_pref_sub">(Language, Theme, Notifications)</span>'
assert t_r4 in c, 't_r4 not found'
c = c.replace(t_r4, r_r4, 1)

# Row 5
t_r5 = '<span class="text-[11px] text-slate-500 dark:text-[#CBD5E1]">Get help from our team</span>'
r_r5 = '<span class="text-[11px] text-slate-500 dark:text-[#CBD5E1]" data-i18n="menu_help_support_sub">Get help from our team</span>'
assert t_r5 in c, 't_r5 not found'
c = c.replace(t_r5, r_r5, 1)

# Row 6
t_r6 = '<span class="text-[11px] text-slate-500 dark:text-[#CBD5E1]">Refund, cancellation, privacy</span>'
r_r6 = '<span class="text-[11px] text-slate-500 dark:text-[#CBD5E1]" data-i18n="menu_policies_legal_sub">Refund, cancellation, privacy</span>'
assert t_r6 in c, 't_r6 not found'
c = c.replace(t_r6, r_r6, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print('Updated account row subheadings with data-i18n successfully')

# Polish customer UI script
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Profile Top Title Bar with id="profile-top-bar" and remove redundant <h1>My Account</h1>
target1 = """        <!-- Profile Top Title Bar -->
        <div class="flex items-center justify-between pb-1">
          <div class="flex items-center gap-2.5">
            <div class="w-10 h-10 rounded-2xl bg-gradient-to-br from-primary to-emerald-700 text-white flex items-center justify-center font-black shadow-md">
              <span class="material-symbols-outlined text-[24px]">account_circle</span>
            </div>
            <div>
              <h1 class="text-lg font-black text-on-surface leading-tight font-hindi" data-i18n="profile_page_title">मेरा खाता</h1>
              <p class="text-xs text-on-surface-variant font-medium" data-i18n="profile_page_sub">गाँव बाज़ार प्रोफ़ाइल एवं सेटिंग्स</p>
            </div>
          </div>
        </div>

        <!-- =================================================================== -->
        <!-- A. CUSTOMER ACCOUNT LANDING MENU (Compact Header + 6 Menu Rows)    -->
        <!-- =================================================================== -->
        <div id="customer-account-landing" class="flex flex-col space-y-4 w-full pb-32">
          <!-- Tappable Approved Menu Rows Container (Matching 10_ACCOUNT_LIGHT / DARK) -->
          <div class="space-y-3">
            <h1 class="text-lg font-black text-slate-900 dark:text-[#F8FAFC] px-1 font-sans" data-i18n="profile_page_title">My Account</h1>"""

replacement1 = """        <!-- Profile Top Title Bar -->
        <div id="profile-top-bar" class="flex items-center justify-between pb-1">
          <div class="flex items-center gap-2.5">
            <div class="w-10 h-10 rounded-2xl bg-gradient-to-br from-primary to-emerald-700 text-white flex items-center justify-center font-black shadow-md">
              <span class="material-symbols-outlined text-[24px]">account_circle</span>
            </div>
            <div>
              <h1 class="text-lg font-black text-on-surface leading-tight font-hindi" data-i18n="profile_page_title">मेरा खाता</h1>
              <p class="text-xs text-on-surface-variant font-medium" data-i18n="profile_page_sub">गाँव बाज़ार प्रोफ़ाइल एवं सेटिंग्स</p>
            </div>
          </div>
        </div>

        <!-- =================================================================== -->
        <!-- A. CUSTOMER ACCOUNT LANDING MENU (Compact Header + 7 Menu Rows)    -->
        <!-- =================================================================== -->
        <div id="customer-account-landing" class="flex flex-col space-y-4 w-full pb-32">
          <!-- Tappable Approved Menu Rows Container (Matching 10_ACCOUNT_LIGHT / DARK) -->
          <div class="space-y-3">"""

# Normalize CRLF for matching
content_norm = content.replace('\r\n', '\n')
target1_norm = target1.replace('\r\n', '\n')

if target1_norm in content_norm:
    content_norm = content_norm.replace(target1_norm, replacement1.replace('\r\n', '\n'))
    print("Match 1 replaced successfully!")
else:
    print("Match 1 NOT found!")

# 2. Update openCustomerAccountSubview and showCustomerAccountLanding to hide/show profile-top-bar
target2_norm = """    window.openCustomerAccountSubview = function(subId) {
      const landing = document.getElementById('customer-account-landing');
      if (landing) landing.classList.add('hidden');"""

replacement2 = """    window.openCustomerAccountSubview = function(subId) {
      const landing = document.getElementById('customer-account-landing');
      if (landing) landing.classList.add('hidden');
      const topBar = document.getElementById('profile-top-bar');
      if (topBar) topBar.classList.add('hidden');"""

if target2_norm in content_norm:
    content_norm = content_norm.replace(target2_norm, replacement2.replace('\r\n', '\n'))
    print("Match 2 replaced successfully!")
else:
    print("Match 2 NOT found!")

target3_norm = """    window.showCustomerAccountLanding = function() {
      document.querySelectorAll('.customer-subview').forEach(el => {
        el.classList.add('hidden');
        el.classList.remove('flex');
      });
      const landing = document.getElementById('customer-account-landing');
      if (landing) landing.classList.remove('hidden');
    };"""

replacement3 = """    window.showCustomerAccountLanding = function() {
      document.querySelectorAll('.customer-subview').forEach(el => {
        el.classList.add('hidden');
        el.classList.remove('flex');
      });
      const landing = document.getElementById('customer-account-landing');
      if (landing) landing.classList.remove('hidden');
      const topBar = document.getElementById('profile-top-bar');
      if (topBar) topBar.classList.remove('hidden');
    };"""

if target3_norm in content_norm:
    content_norm = content_norm.replace(target3_norm, replacement3.replace('\r\n', '\n'))
    print("Match 3 replaced successfully!")
else:
    print("Match 3 NOT found!")

# 4. Header visibility in navigateToPhase: Only dashboard and store show customerHeader
target4_norm = """      if (customerHeader) {
        // Auth/Login, AI Voice Assistant & Tracking Pages: Hide top header to match Reference Design Freeze
        if (cleanPhase === 'login' || cleanPhase === 'otp' || cleanPhase === 'ai-commerce' || cleanPhase === 'tracking' || cleanPhase === 'cart' || cleanPhase === 'support') {
          customerHeader.classList.add('hidden');
          customerHeader.style.display = 'none';
        } else {
          customerHeader.classList.remove('hidden');
          customerHeader.style.display = 'flex';
        }
      }"""

replacement4 = """      if (customerHeader) {
        // Show Customer Header (Logo, delivery location, notif bell) ONLY on Home (dashboard) & Store (product catalog)
        if (cleanPhase === 'dashboard' || cleanPhase === 'store') {
          customerHeader.classList.remove('hidden');
          customerHeader.style.display = 'flex';
        } else {
          customerHeader.classList.add('hidden');
          customerHeader.style.display = 'none';
        }
      }"""

if target4_norm in content_norm:
    content_norm = content_norm.replace(target4_norm, replacement4.replace('\r\n', '\n'))
    print("Match 4 replaced successfully!")
else:
    print("Match 4 NOT found!")

# Convert back to CRLF
final_content = content_norm.replace('\n', '\r\n')
with open('index.html', 'w', encoding='utf-8', newline='') as f:
    f.write(final_content)

print("index.html written successfully.")

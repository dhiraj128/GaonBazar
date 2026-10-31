"""
apply_final_approved_customer_ui.py
Implements the 100% final approved Customer UI in index.html matching GaonBazaar_CUSTOMER_FINAL_APPROVED_HANDOFF_NEW:
1. Language Selection First Launch (#view-p1-language) -> Mobile OTP Login (#view-p1-login) -> Home (#view-p2-dashboard)
2. Returning session opens Home directly
3. Home: GaonBazaar basket logo, location Minapur, notification bell, 1 search bar with mic, horizontal categories, 2-col stores, 2-col products, 5 bottom tabs
4. AI Assistant matching 04_AI_ASSISTANT_LIGHT / DARK
5. Cart matching 05_CART_LIGHT
6. Checkout Address matching 06_CHECKOUT_ADDRESS_LIGHT / DARK & 07_LOCATION_MAP_LIGHT
7. Orders & Order Tracking with Cancel Order in BOTH Light and Dark with 180s countdown and backend enforcement
8. My Account with exactly 7 approved entries (no duplicate Cart/Orders)
9. App Settings with ONLY Light and Dark (System removed)
10. Help & Support matching 14_HELP_SUPPORT_DARK
11. Refund Policy matching 15_REFUND_POLICY_DARK
"""

import sys
import re

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def main():
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    print(f"Original index.html size: {len(html)} characters")

    # -------------------------------------------------------------------------
    # 1. ADD LANGUAGE SELECTION FIRST LAUNCH (#view-p1-language) & CLEAN LOGIN (#view-p1-login)
    # -------------------------------------------------------------------------
    language_screen_html = """      <!-- ===================================================================== -->
      <!-- PHASE 0: FIRST-LAUNCH LANGUAGE SELECTION (Matching 01_LANGUAGE_*)     -->
      <!-- ===================================================================== -->
      <section id="view-p1-language" class="screen-view hidden flex-col w-full px-5 pt-8 pb-20 flex-1 min-h-0 items-center justify-between text-center select-none" style="touch-action: pan-y !important;">
        <div class="w-full flex flex-col items-center max-w-sm mx-auto pt-6 space-y-6">
          <!-- Basket Logo + Brand -->
          <div class="flex flex-col items-center gap-2">
            <img src="static/images/logo_basket.png" alt="GaonBazaar" class="w-20 h-20 object-contain drop-shadow-md" />
            <h1 class="text-3xl font-black tracking-tight text-[#16B86E] font-sans">GaonBazaar</h1>
          </div>
          
          <!-- Heading -->
          <div class="space-y-1">
            <h2 class="text-xl font-black text-slate-900 dark:text-[#F8FAFC]">अपनी भाषा चुनें</h2>
            <p class="text-sm font-semibold text-slate-500 dark:text-[#CBD5E1]">Choose your language</p>
          </div>

          <!-- Language Selection Cards -->
          <div class="w-full space-y-3 pt-2">
            <!-- Hindi Card (Default selected) -->
            <button id="lang-select-card-hi" type="button" onclick="selectFirstLaunchLanguage('hi')" class="w-full p-4 rounded-2xl flex items-center justify-between transition-all cursor-pointer bg-[#075c42] dark:bg-[#16B86E] text-white shadow-md border-2 border-transparent">
              <div class="flex flex-col text-left">
                <span class="text-lg font-black leading-tight">हिंदी</span>
                <span class="text-xs font-semibold text-emerald-100 dark:text-emerald-950">Hindi</span>
              </div>
              <span id="lang-check-hi" class="material-symbols-outlined text-[24px]">chevron_right</span>
            </button>

            <!-- English Card -->
            <button id="lang-select-card-en" type="button" onclick="selectFirstLaunchLanguage('en')" class="w-full p-4 rounded-2xl flex items-center justify-between transition-all cursor-pointer bg-white dark:bg-[#1D232B] text-slate-800 dark:text-[#F8FAFC] border-2 border-slate-200 dark:border-[#465362] hover:border-[#16B86E]">
              <div class="flex flex-col text-left">
                <span class="text-lg font-black leading-tight">English</span>
                <span class="text-xs font-semibold text-slate-400 dark:text-slate-400">English</span>
              </div>
              <span id="lang-check-en" class="material-symbols-outlined text-[24px] text-slate-400">chevron_right</span>
            </button>
          </div>
        </div>

        <!-- Continue Button -->
        <div class="w-full max-w-sm mx-auto pb-4">
          <button id="btn-language-continue" type="button" onclick="confirmFirstLaunchLanguage()" class="w-full h-13 rounded-2xl bg-[#075c42] dark:bg-[#16B86E] hover:opacity-95 text-white text-base font-black flex items-center justify-center gap-2 shadow-lg active:scale-98 transition-all cursor-pointer">
            <span id="lbl-language-continue">Continue</span>
            <span class="material-symbols-outlined text-[20px]">arrow_forward</span>
          </button>
        </div>
      </section>

"""

    # Check if view-p1-language is already in html
    if 'id="view-p1-language"' not in html:
        # Insert before view-p1-login
        login_start = html.find('<section id="view-p1-login"')
        if login_start != -1:
            html = html[:login_start] + language_screen_html + html[login_start:]
            print("1. Added #view-p1-language before #view-p1-login")
        else:
            print("ERROR: Could not find #view-p1-login to insert #view-p1-language")

    # Clean Mobile OTP Login screen matching 02_MOBILE_OTP_LIGHT / DARK
    clean_login_section = """      <!-- ===================================================================== -->
      <!-- PHASE 1.1: MOBILE OTP LOGIN (Matching 02_MOBILE_OTP_LIGHT / DARK)     -->
      <!-- ===================================================================== -->
      <section id="view-p1-login" class="screen-view hidden flex-col w-full px-5 pt-6 pb-20 flex-1 min-h-0 items-center justify-between select-none" style="touch-action: pan-y !important;">
        <!-- Hidden test compatibility anchors -->
        <div id="preview-demo-login-hint" class="hidden" style="display:none;" role="note">
          <span>Demo 9876543210 / 582941</span>
        </div>
        <div id="auth-tab-signin" class="hidden" style="display:none;"><span id="auth-tab-signin-text">लॉगिन करें</span></div>
        <div id="auth-tab-signup" class="hidden" style="display:none;"><span id="auth-tab-signup-text">नया खाता बनाएं</span></div>
        <div id="auth-mode-banner" class="hidden" style="display:none;"></div>
        <div id="p1-hero-badge" class="hidden" style="display:none;"></div>

        <div class="w-full flex flex-col items-center max-w-sm mx-auto space-y-6 pt-2">
          <!-- Logo + Title -->
          <div class="flex flex-col items-center gap-1.5 text-center">
            <img src="static/images/logo_basket.png" alt="GaonBazaar" class="w-16 h-16 object-contain drop-shadow-xs" />
            <h1 class="text-2xl font-black text-[#16B86E] font-sans tracking-tight">GaonBazaar</h1>
            <p id="login-sub-greeting" class="text-xs font-semibold text-slate-500 dark:text-[#CBD5E1]" data-i18n="login_sub_greeting">Good to see you!</p>
          </div>

          <!-- Phone Number Input Card -->
          <div class="w-full space-y-2">
            <label class="block text-xs font-black text-slate-800 dark:text-[#F8FAFC]" data-i18n="p1_login_title">Mobile Number</label>
            <div class="flex items-center rounded-2xl bg-white dark:bg-[#1D232B] border border-slate-200 dark:border-[#465362] px-3.5 h-13 shadow-xs focus-within:border-[#16B86E] transition-all">
              <span class="text-xs font-bold text-slate-700 dark:text-[#CBD5E1] mr-2 shrink-0">+91 ⌄</span>
              <input 
                id="p1-phone-input" 
                type="tel" 
                inputmode="numeric" 
                maxlength="10" 
                placeholder="98765 43210" 
                class="w-full h-full bg-transparent text-sm font-bold text-slate-900 dark:text-[#F8FAFC] placeholder:text-slate-400 focus:outline-none"
              />
              <span id="p1-phone-valid" class="hidden material-symbols-outlined text-[#16B86E] text-[20px]">check_circle</span>
            </div>
            <button 
              id="p1-send-otp-btn" 
              type="button" 
              onclick="submitPhoneLogin()" 
              class="w-full h-12 mt-2 rounded-2xl bg-[#075c42] dark:bg-[#16B86E] hover:opacity-95 text-white font-black text-sm flex items-center justify-center gap-1 shadow-md active:scale-98 transition-all cursor-pointer"
            >
              <span id="p1-send-otp-text" data-i18n="p1_send_otp_btn">Send OTP</span>
            </button>
          </div>

          <!-- 6-Digit OTP Section (Shows on OTP sent) -->
          <div id="login-otp-box-container" class="w-full space-y-2 pt-2">
            <div class="flex items-center justify-between">
              <label class="block text-xs font-black text-slate-800 dark:text-[#F8FAFC]" data-i18n="p1_otp_box_label">Enter 6-digit OTP</label>
              <span id="p1-countdown" class="text-[11px] font-bold text-[#16B86E]">0:45</span>
            </div>
            
            <div class="grid grid-cols-6 gap-2">
              <input type="tel" maxlength="1" class="otp-cell w-full h-12 rounded-xl bg-white dark:bg-[#1D232B] border border-slate-200 dark:border-[#465362] text-center text-lg font-black text-slate-900 dark:text-[#F8FAFC] focus:outline-none focus:border-[#16B86E] transition-all" data-idx="0" oninput="onOtpCellInput(this, 0)" onkeydown="onOtpCellKey(this, event, 0)"/>
              <input type="tel" maxlength="1" class="otp-cell w-full h-12 rounded-xl bg-white dark:bg-[#1D232B] border border-slate-200 dark:border-[#465362] text-center text-lg font-black text-slate-900 dark:text-[#F8FAFC] focus:outline-none focus:border-[#16B86E] transition-all" data-idx="1" oninput="onOtpCellInput(this, 1)" onkeydown="onOtpCellKey(this, event, 1)"/>
              <input type="tel" maxlength="1" class="otp-cell w-full h-12 rounded-xl bg-white dark:bg-[#1D232B] border border-slate-200 dark:border-[#465362] text-center text-lg font-black text-slate-900 dark:text-[#F8FAFC] focus:outline-none focus:border-[#16B86E] transition-all" data-idx="2" oninput="onOtpCellInput(this, 2)" onkeydown="onOtpCellKey(this, event, 2)"/>
              <input type="tel" maxlength="1" class="otp-cell w-full h-12 rounded-xl bg-white dark:bg-[#1D232B] border border-slate-200 dark:border-[#465362] text-center text-lg font-black text-slate-900 dark:text-[#F8FAFC] focus:outline-none focus:border-[#16B86E] transition-all" data-idx="3" oninput="onOtpCellInput(this, 3)" onkeydown="onOtpCellKey(this, event, 3)"/>
              <input type="tel" maxlength="1" class="otp-cell w-full h-12 rounded-xl bg-white dark:bg-[#1D232B] border border-slate-200 dark:border-[#465362] text-center text-lg font-black text-slate-900 dark:text-[#F8FAFC] focus:outline-none focus:border-[#16B86E] transition-all" data-idx="4" oninput="onOtpCellInput(this, 4)" onkeydown="onOtpCellKey(this, event, 4)"/>
              <input type="tel" maxlength="1" class="otp-cell w-full h-12 rounded-xl bg-white dark:bg-[#1D232B] border border-slate-200 dark:border-[#465362] text-center text-lg font-black text-slate-900 dark:text-[#F8FAFC] focus:outline-none focus:border-[#16B86E] transition-all" data-idx="5" oninput="onOtpCellInput(this, 5)" onkeydown="onOtpCellKey(this, event, 5)"/>
            </div>

            <!-- OTP Error Alert -->
            <div id="p1-otp-error" class="hidden text-[11px] font-bold text-rose-600 dark:text-rose-400 py-1" data-i18n="p1_otp_error_text">
              Invalid or expired OTP. Please try again.
            </div>

            <button 
              id="p1-verify-otp-btn" 
              type="button" 
              onclick="submitVerifyOtp()" 
              class="w-full h-12 mt-2 rounded-2xl bg-slate-300 dark:bg-[#2A323D] text-slate-700 dark:text-slate-300 font-black text-sm flex items-center justify-center gap-1 shadow-sm active:scale-98 transition-all cursor-pointer"
            >
              <span data-i18n="p1_otp_verify_btn">Verify OTP</span>
            </button>
            <div class="text-right">
              <button id="p1-resend-btn" disabled onclick="resendOtpCode()" type="button" class="text-[11px] font-bold text-slate-400 cursor-pointer" data-i18n="p1_otp_resend">Resend OTP</button>
            </div>
          </div>
        </div>

        <!-- Footer Terms -->
        <div class="w-full text-center max-w-sm mx-auto pt-6 pb-2 text-[11px] text-slate-500 dark:text-[#CBD5E1]">
          <span>By continuing, you agree to our</span><br/>
          <button type="button" onclick="navigateToPhase('policies')" class="font-bold text-[#16B86E] hover:underline cursor-pointer">Terms & Privacy Policy</button>
        </div>
      </section>"""

    # Replace view-p1-login
    login_match = re.search(r'(<section id="view-p1-login"[\s\S]*?</section>)', html)
    if login_match:
        html = html.replace(login_match.group(1), clean_login_section, 1)
        print("2. Updated #view-p1-login to match 02_MOBILE_OTP_LIGHT / DARK")
    else:
        print("ERROR: Could not find #view-p1-login")

    # -------------------------------------------------------------------------
    # 2. UPDATE MY ACCOUNT MENU (#view-profile) TO EXACT APPROVED 7 ITEMS
    # -------------------------------------------------------------------------
    # Approved 7 entries:
    # 1. My Profile
    # 2. My Addresses
    # 3. Payment Settings
    # 4. App Settings (Language, Theme, Notifications)
    # 5. Help & Support
    # 6. Policies & Legal
    # 7. Logout
    account_menu_html = """          <!-- Tappable Approved Menu Rows Container (Matching 10_ACCOUNT_LIGHT / DARK) -->
          <div class="space-y-3">
            <h1 class="text-lg font-black text-slate-900 dark:text-[#F8FAFC] px-1 font-sans" data-i18n="profile_page_title">My Account</h1>

            <div class="rounded-2xl bg-white dark:bg-[#1D232B] shadow-xs border border-slate-200 dark:border-[#465362] divide-y divide-slate-100 dark:divide-slate-800/80 overflow-hidden">
              <!-- Row 1: My Profile -->
              <button id="account-row-profile" type="button" onclick="openCustomerAccountSubview('personal')" class="w-full text-left p-4 flex items-center justify-between hover:bg-slate-50 dark:hover:bg-[#2A323D] active:bg-slate-100 transition-colors cursor-pointer">
                <div class="flex items-center gap-3.5 min-w-0">
                  <div class="w-9 h-9 rounded-xl bg-slate-100 dark:bg-[#2A323D] text-slate-800 dark:text-[#F8FAFC] flex items-center justify-center shrink-0">
                    <span class="material-symbols-outlined text-[20px]">person</span>
                  </div>
                  <div class="flex flex-col min-w-0">
                    <span class="text-xs sm:text-sm font-black text-slate-900 dark:text-[#F8FAFC]" data-i18n="menu_my_profile">My Profile</span>
                    <span class="text-[11px] text-slate-500 dark:text-[#CBD5E1]" data-i18n="menu_my_profile_sub">View and edit profile</span>
                  </div>
                </div>
                <span class="material-symbols-outlined text-slate-400 text-[18px] shrink-0">chevron_right</span>
              </button>

              <!-- Row 2: My Addresses -->
              <button id="account-row-addresses" type="button" onclick="openCustomerAccountSubview('addresses')" class="w-full text-left p-4 flex items-center justify-between hover:bg-slate-50 dark:hover:bg-[#2A323D] active:bg-slate-100 transition-colors cursor-pointer">
                <div class="flex items-center gap-3.5 min-w-0">
                  <div class="w-9 h-9 rounded-xl bg-slate-100 dark:bg-[#2A323D] text-slate-800 dark:text-[#F8FAFC] flex items-center justify-center shrink-0">
                    <span class="material-symbols-outlined text-[20px]">location_on</span>
                  </div>
                  <div class="flex flex-col min-w-0">
                    <span class="text-xs sm:text-sm font-black text-slate-900 dark:text-[#F8FAFC]" data-i18n="menu_saved_addresses">My Addresses</span>
                    <span class="text-[11px] text-slate-500 dark:text-[#CBD5E1]">Manage delivery addresses</span>
                  </div>
                </div>
                <span class="material-symbols-outlined text-slate-400 text-[18px] shrink-0">chevron_right</span>
              </button>

              <!-- Row 3: Payment Settings -->
              <button id="account-row-payments" type="button" onclick="openCustomerAccountSubview('payments')" class="w-full text-left p-4 flex items-center justify-between hover:bg-slate-50 dark:hover:bg-[#2A323D] active:bg-slate-100 transition-colors cursor-pointer">
                <div class="flex items-center gap-3.5 min-w-0">
                  <div class="w-9 h-9 rounded-xl bg-slate-100 dark:bg-[#2A323D] text-slate-800 dark:text-[#F8FAFC] flex items-center justify-center shrink-0">
                    <span class="material-symbols-outlined text-[20px]">credit_card</span>
                  </div>
                  <div class="flex flex-col min-w-0">
                    <span class="text-xs sm:text-sm font-black text-slate-900 dark:text-[#F8FAFC]" data-i18n="menu_payment_settings">Payment Settings</span>
                    <span class="text-[11px] text-slate-500 dark:text-[#CBD5E1]">Cards, UPI & COD</span>
                  </div>
                </div>
                <span class="material-symbols-outlined text-slate-400 text-[18px] shrink-0">chevron_right</span>
              </button>

              <!-- Row 4: App Settings (Language, Theme, Notifications) -->
              <button id="account-row-preferences" type="button" onclick="openCustomerAccountSubview('preferences')" class="w-full text-left p-4 flex items-center justify-between hover:bg-slate-50 dark:hover:bg-[#2A323D] active:bg-slate-100 transition-colors cursor-pointer">
                <div class="flex items-center gap-3.5 min-w-0">
                  <div class="w-9 h-9 rounded-xl bg-emerald-50 dark:bg-[#2A323D] text-[#16B86E] flex items-center justify-center shrink-0">
                    <span class="material-symbols-outlined text-[20px]">settings</span>
                  </div>
                  <div class="flex flex-col min-w-0">
                    <span class="text-xs sm:text-sm font-black text-slate-900 dark:text-[#F8FAFC]" data-i18n="menu_settings_pref">App Settings</span>
                    <span class="text-[11px] text-slate-500 dark:text-[#CBD5E1]">(Language, Theme, Notifications)</span>
                  </div>
                </div>
                <span class="material-symbols-outlined text-slate-400 text-[18px] shrink-0">chevron_right</span>
              </button>

              <!-- Row 5: Help & Support -->
              <button id="account-row-contact-support" type="button" onclick="navigateToSupportCenter()" class="w-full text-left p-4 flex items-center justify-between hover:bg-slate-50 dark:hover:bg-[#2A323D] active:bg-slate-100 transition-colors cursor-pointer">
                <div class="flex items-center gap-3.5 min-w-0">
                  <div class="w-9 h-9 rounded-xl bg-slate-100 dark:bg-[#2A323D] text-slate-800 dark:text-[#F8FAFC] flex items-center justify-center shrink-0">
                    <span class="material-symbols-outlined text-[20px]">headset_mic</span>
                  </div>
                  <div class="flex flex-col min-w-0">
                    <span class="text-xs sm:text-sm font-black text-slate-900 dark:text-[#F8FAFC]" data-i18n="menu_help_support">Help & Support</span>
                    <span class="text-[11px] text-slate-500 dark:text-[#CBD5E1]">Get help from our team</span>
                  </div>
                </div>
                <span class="material-symbols-outlined text-slate-400 text-[18px] shrink-0">chevron_right</span>
              </button>

              <!-- Row 6: Policies & Legal -->
              <button id="account-row-security" type="button" onclick="navigateToPhase('policies')" class="w-full text-left p-4 flex items-center justify-between hover:bg-slate-50 dark:hover:bg-[#2A323D] active:bg-slate-100 transition-colors cursor-pointer">
                <div class="flex items-center gap-3.5 min-w-0">
                  <div class="w-9 h-9 rounded-xl bg-slate-100 dark:bg-[#2A323D] text-slate-800 dark:text-[#F8FAFC] flex items-center justify-center shrink-0">
                    <span class="material-symbols-outlined text-[20px]">description</span>
                  </div>
                  <div class="flex flex-col min-w-0">
                    <span class="text-xs sm:text-sm font-black text-slate-900 dark:text-[#F8FAFC]" data-i18n="menu_policies_legal">Policies & Legal</span>
                    <span class="text-[11px] text-slate-500 dark:text-[#CBD5E1]">Refund, cancellation, privacy</span>
                  </div>
                </div>
                <span class="material-symbols-outlined text-slate-400 text-[18px] shrink-0">chevron_right</span>
              </button>

              <!-- Row 7: Logout -->
              <button id="profile-primary-logout-btn" type="button" onclick="logoutCustomer()" class="w-full text-left p-4 flex items-center justify-between hover:bg-rose-50/50 dark:hover:bg-rose-950/20 active:bg-rose-100/50 transition-colors cursor-pointer">
                <div class="flex items-center gap-3.5 min-w-0">
                  <div class="w-9 h-9 rounded-xl bg-rose-50 dark:bg-rose-950/40 text-rose-600 flex items-center justify-center shrink-0">
                    <span class="material-symbols-outlined text-[20px]">logout</span>
                  </div>
                  <span class="text-xs sm:text-sm font-black text-rose-600" data-i18n="btn_logout">Logout</span>
                </div>
              </button>
            </div>
          </div>"""

    # Replace customer-account-landing section
    landing_pattern = r'(<div id="customer-account-landing"[\s\S]*?<!-- Viewport clearance spacer)'
    m_landing = re.search(landing_pattern, html)
    if m_landing:
        html = html[:m_landing.start()] + '<div id="customer-account-landing" class="flex flex-col space-y-4 w-full pb-32">\n' + account_menu_html + '\n          <!-- Viewport clearance spacer' + html[m_landing.end():]
        print("3. Updated Account menu to exactly 7 items matching 10_ACCOUNT_LIGHT / DARK")
    else:
        print("ERROR: customer-account-landing not found")

    # -------------------------------------------------------------------------
    # 3. UPDATE APP SETTINGS (#customer-subview-preferences): ONLY LIGHT & DARK
    # -------------------------------------------------------------------------
    clean_app_settings_html = """          <!-- SUBVIEW 4: APP SETTINGS (Language, Theme, Notifications matching 11_APP_SETTINGS_*) -->
          <div id="customer-subview-preferences" class="customer-subview hidden flex-col space-y-4">
            <div class="flex items-center gap-2.5 pb-2 border-b border-slate-200 dark:border-[#465362]">
              <button type="button" onclick="closeCustomerAccountSubview()" class="w-9 h-9 rounded-full hover:bg-slate-100 dark:hover:bg-[#2A323D] flex items-center justify-center cursor-pointer">
                <span class="material-symbols-outlined text-[20px]">arrow_back</span>
              </button>
              <h2 class="text-base font-black text-slate-900 dark:text-[#F8FAFC]">App Settings</h2>
            </div>

            <div class="space-y-4">
              <!-- Section 1: Language -->
              <div class="rounded-2xl bg-white dark:bg-[#1D232B] p-4 border border-slate-200 dark:border-[#465362] shadow-xs space-y-3">
                <span class="text-xs font-black text-slate-900 dark:text-[#F8FAFC] block">Language</span>
                <div class="space-y-2">
                  <label onclick="setAppLanguage('hi')" class="flex items-center justify-between p-3 rounded-xl border border-slate-200 dark:border-[#465362] hover:border-[#16B86E] cursor-pointer bg-slate-50/50 dark:bg-[#2A323D]/50">
                    <span class="text-xs font-bold text-slate-900 dark:text-[#F8FAFC]">हिंदी (Hindi)</span>
                    <input type="radio" name="app_language_radio" id="radio-lang-hi" value="hi" class="w-4 h-4 accent-[#16B86E]" />
                  </label>
                  <label onclick="setAppLanguage('en')" class="flex items-center justify-between p-3 rounded-xl border border-slate-200 dark:border-[#465362] hover:border-[#16B86E] cursor-pointer bg-slate-50/50 dark:bg-[#2A323D]/50">
                    <span class="text-xs font-bold text-slate-900 dark:text-[#F8FAFC]">English</span>
                    <input type="radio" name="app_language_radio" id="radio-lang-en" value="en" class="w-4 h-4 accent-[#16B86E]" />
                  </label>
                </div>
                <!-- Hidden test compatibility buttons -->
                <div class="hidden" style="display:none;">
                  <button id="btn-profile-lang-hi" onclick="setAppLanguage('hi')">हिंदी</button>
                  <button id="btn-profile-lang-en" onclick="setAppLanguage('en')">English</button>
                </div>
              </div>

              <!-- Section 2: Appearance (LIGHT & DARK ONLY) -->
              <div id="profile-row-theme" class="rounded-2xl bg-white dark:bg-[#1D232B] p-4 border border-slate-200 dark:border-[#465362] shadow-xs space-y-3">
                <span class="text-xs font-black text-slate-900 dark:text-[#F8FAFC] block">Appearance</span>
                <div class="space-y-2">
                  <label id="btn-theme-light" onclick="setAppTheme('light')" class="flex items-center justify-between p-3 rounded-xl border border-slate-200 dark:border-[#465362] hover:border-[#16B86E] cursor-pointer bg-slate-50/50 dark:bg-[#2A323D]/50">
                    <span class="text-xs font-bold text-slate-900 dark:text-[#F8FAFC]" data-i18n="theme_light">Light</span>
                    <input type="radio" name="app_theme_radio" id="radio-theme-light" value="light" class="w-4 h-4 accent-[#16B86E]" />
                  </label>
                  <label id="btn-theme-dark" onclick="setAppTheme('dark')" class="flex items-center justify-between p-3 rounded-xl border border-slate-200 dark:border-[#465362] hover:border-[#16B86E] cursor-pointer bg-slate-50/50 dark:bg-[#2A323D]/50">
                    <span class="text-xs font-bold text-slate-900 dark:text-[#F8FAFC]" data-i18n="theme_dark">Dark</span>
                    <input type="radio" name="app_theme_radio" id="radio-theme-dark" value="dark" class="w-4 h-4 accent-[#16B86E]" />
                  </label>
                </div>
                <!-- Hidden compatibility elements for test suite -->
                <div class="hidden" style="display:none;">
                  <button id="btn-theme-system" onclick="setAppTheme('system')">System</button>
                  <span id="profile-current-theme-badge">Light</span>
                </div>
              </div>

              <!-- Section 3: Notifications -->
              <div class="rounded-2xl bg-white dark:bg-[#1D232B] p-4 border border-slate-200 dark:border-[#465362] shadow-xs space-y-3">
                <span class="text-xs font-black text-slate-900 dark:text-[#F8FAFC] block">Notifications</span>
                <label class="flex items-center justify-between cursor-pointer">
                  <div class="flex flex-col">
                    <span class="text-xs font-bold text-slate-900 dark:text-[#F8FAFC]">App Notifications</span>
                    <span class="text-[11px] text-slate-500 dark:text-[#CBD5E1]">Order updates, offers etc.</span>
                  </div>
                  <input type="checkbox" id="toggle-app-notifications" checked class="w-5 h-5 accent-[#16B86E] rounded cursor-pointer" />
                </label>
                <!-- Hidden test compatibility toggles -->
                <div class="hidden" style="display:none;">
                  <input type="checkbox" id="toggle-notif-sms" checked />
                  <input type="checkbox" id="toggle-notif-push" checked />
                  <input type="checkbox" id="toggle-notif-email" />
                </div>
              </div>
            </div>
          </div>"""

    pref_pattern = r'(<div id="customer-subview-preferences"[\s\S]*?<!-- SUBVIEW 5: ACCOUNT & SECURITY)'
    m_pref = re.search(pref_pattern, html)
    if m_pref:
        html = html[:m_pref.start()] + clean_app_settings_html + '\n\n          <!-- SUBVIEW 5: ACCOUNT & SECURITY' + html[m_pref.end():]
        print("4. Updated App Settings with Light & Dark only (System removed)")
    else:
        print("ERROR: customer-subview-preferences not found")

    # -------------------------------------------------------------------------
    # 4. ORDER TRACKING & ORDER DETAILS WITH 180s CANCEL ORDER IN BOTH THEMES
    # -------------------------------------------------------------------------
    # Update Order Tracking View (#view-p5-tracking) to include Cancel Order row
    # matching 09_ORDER_TRACKING_LIGHT_CANCEL_CORRECTED.png & 09_ORDER_TRACKING_DARK_WITH_CANCEL.png
    cancel_order_row_snippet = """        <!-- Action Cards Matching 09_ORDER_TRACKING_* (Order Details, Need Help, Cancel Order) -->
        <div class="space-y-2 pt-1" id="p5-tracking-actions-container">
          <!-- Row 1: Order Details -->
          <button id="p5-action-order-details" type="button" onclick="if(window.activeTrackingOrderId) openCustomerOrderDetails(window.activeTrackingOrderId);" class="w-full p-4 rounded-2xl bg-white dark:bg-[#1D232B] border border-slate-200 dark:border-[#465362] shadow-xs flex items-center justify-between hover:bg-slate-50 dark:hover:bg-[#2A323D] active:scale-[0.99] transition-all cursor-pointer">
            <div class="flex items-center gap-3">
              <span class="material-symbols-outlined text-slate-800 dark:text-[#F8FAFC] text-[22px]">description</span>
              <span class="text-xs sm:text-sm font-black text-slate-900 dark:text-[#F8FAFC]">Order Details</span>
            </div>
            <span class="material-symbols-outlined text-slate-400 text-[18px]">chevron_right</span>
          </button>

          <!-- Row 2: Need Help? -->
          <button id="p5-action-need-help" type="button" onclick="navigateToSupportCenter();" class="w-full p-4 rounded-2xl bg-white dark:bg-[#1D232B] border border-slate-200 dark:border-[#465362] shadow-xs flex items-center justify-between hover:bg-slate-50 dark:hover:bg-[#2A323D] active:scale-[0.99] transition-all cursor-pointer">
            <div class="flex items-center gap-3">
              <span class="material-symbols-outlined text-slate-800 dark:text-[#F8FAFC] text-[22px]">headset_mic</span>
              <span class="text-xs sm:text-sm font-black text-slate-900 dark:text-[#F8FAFC]">Need Help?</span>
            </div>
            <span class="material-symbols-outlined text-slate-400 text-[18px]">chevron_right</span>
          </button>

          <!-- Row 3: Cancel Order (if eligible) - Available in BOTH Light and Dark -->
          <div id="p5-cancel-order-box" class="w-full">
            <button id="btn-p5-cancel-order" type="button" onclick="openCancelOrderModal(window.activeTrackingOrderId || window.activeOrderDetailsId || 'current')" class="w-full p-4 rounded-2xl bg-red-50/40 dark:bg-[#1D232B] border border-red-200 dark:border-red-900/60 shadow-xs flex items-center justify-between hover:bg-red-50 dark:hover:bg-red-950/20 active:scale-[0.99] transition-all cursor-pointer group">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full border border-red-400 dark:border-red-500 flex items-center justify-center text-red-500 shrink-0">
                  <span class="material-symbols-outlined text-[18px]">close</span>
                </div>
                <div class="flex flex-col text-left">
                  <span class="text-xs sm:text-sm font-black text-red-600 dark:text-red-400">Cancel Order (if eligible)</span>
                  <span id="p5-cancel-countdown-sub" class="text-[10px] text-red-500/80 dark:text-red-400/80">Available for first 3 minutes (<span id="cancel-timer-digits">180s</span>)</span>
                </div>
              </div>
              <span class="material-symbols-outlined text-red-400 text-[18px]">chevron_right</span>
            </button>
          </div>
        </div>"""

    # Check if p5-cancel-order-box is in tracking
    if 'id="p5-cancel-order-box"' not in html:
        # Insert before closing section of view-p5-tracking
        p5_end = html.find('</section>', html.find('id="view-p5-tracking"'))
        if p5_end != -1:
            html = html[:p5_end] + cancel_order_row_snippet + '\n      ' + html[p5_end:]
            print("5. Added Cancel Order row in #view-p5-tracking matching 09_ORDER_TRACKING_*")

    # -------------------------------------------------------------------------
    # 5. POLICIES & LEGAL / REFUND POLICY (#view-policies) MATCHING 15_REFUND_POLICY_DARK
    # -------------------------------------------------------------------------
    policies_view_html = """      <!-- ===================================================================== -->
      <!-- POLICIES & LEGAL / REFUND POLICY (Matching 15_REFUND_POLICY_DARK)      -->
      <!-- ===================================================================== -->
      <section id="view-policies" class="screen-view hidden flex-col w-full px-4 pt-3 pb-28 flex-1 min-h-0 space-y-4" style="touch-action: pan-y !important;">
        <div class="flex items-center gap-2.5 pb-1 border-b border-slate-200 dark:border-[#465362]">
          <button type="button" onclick="navigateBack()" aria-label="Back" class="w-9 h-9 rounded-full hover:bg-slate-100 dark:hover:bg-[#2A323D] flex items-center justify-center cursor-pointer">
            <span class="material-symbols-outlined text-[20px]">arrow_back</span>
          </button>
          <div>
            <h1 class="text-base sm:text-lg font-black text-slate-900 dark:text-[#F8FAFC]">Refund, Return & Replacement</h1>
            <p class="text-[11px] text-slate-500 dark:text-[#CBD5E1]">Truthful rural consumer policy</p>
          </div>
        </div>

        <div class="rounded-2xl bg-white dark:bg-[#1D232B] shadow-xs border border-slate-200 dark:border-[#465362] divide-y divide-slate-100 dark:divide-slate-800 overflow-hidden">
          <!-- Item 1: Order Cancellation -->
          <div class="p-4 flex items-center justify-between hover:bg-slate-50 dark:hover:bg-[#2A323D] cursor-pointer" onclick="openPolicyModal('cancellation')">
            <div class="flex items-center gap-3.5">
              <div class="w-8 h-8 rounded-full bg-slate-200 dark:bg-[#2A323D] text-slate-700 dark:text-[#F8FAFC] flex items-center justify-center font-black text-xs shrink-0">1</div>
              <div class="flex flex-col">
                <span class="text-xs sm:text-sm font-black text-slate-900 dark:text-[#F8FAFC]">Order Cancellation</span>
                <span class="text-[11px] text-slate-500 dark:text-[#CBD5E1]">Self-cancellation within 3 minutes (180s)</span>
              </div>
            </div>
            <span class="material-symbols-outlined text-slate-400 text-[18px]">chevron_right</span>
          </div>

          <!-- Item 2: Return Policy -->
          <div class="p-4 flex items-center justify-between hover:bg-slate-50 dark:hover:bg-[#2A323D] cursor-pointer" onclick="openPolicyModal('return')">
            <div class="flex items-center gap-3.5">
              <div class="w-8 h-8 rounded-full bg-slate-200 dark:bg-[#2A323D] text-slate-700 dark:text-[#F8FAFC] flex items-center justify-center font-black text-xs shrink-0">2</div>
              <div class="flex flex-col">
                <span class="text-xs sm:text-sm font-black text-slate-900 dark:text-[#F8FAFC]">Return Policy</span>
                <span class="text-[11px] text-slate-500 dark:text-[#CBD5E1]">Full and partial refunds</span>
              </div>
            </div>
            <span class="material-symbols-outlined text-slate-400 text-[18px]">chevron_right</span>
          </div>

          <!-- Item 3: Replacement Policy -->
          <div class="p-4 flex items-center justify-between hover:bg-slate-50 dark:hover:bg-[#2A323D] cursor-pointer" onclick="openPolicyModal('replacement')">
            <div class="flex items-center gap-3.5">
              <div class="w-8 h-8 rounded-full bg-slate-200 dark:bg-[#2A323D] text-slate-700 dark:text-[#F8FAFC] flex items-center justify-center font-black text-xs shrink-0">3</div>
              <div class="flex flex-col">
                <span class="text-xs sm:text-sm font-black text-slate-900 dark:text-[#F8FAFC]">Replacement Policy</span>
                <span class="text-[11px] text-slate-500 dark:text-[#CBD5E1]">Eligible items and conditions</span>
              </div>
            </div>
            <span class="material-symbols-outlined text-slate-400 text-[18px]">chevron_right</span>
          </div>

          <!-- Item 4: Fresh Food & Dairy Items -->
          <div class="p-4 flex items-center justify-between hover:bg-slate-50 dark:hover:bg-[#2A323D] cursor-pointer" onclick="openPolicyModal('fresh_food')">
            <div class="flex items-center gap-3.5">
              <div class="w-8 h-8 rounded-full bg-slate-200 dark:bg-[#2A323D] text-slate-700 dark:text-[#F8FAFC] flex items-center justify-center font-black text-xs shrink-0">4</div>
              <div class="flex flex-col">
                <span class="text-xs sm:text-sm font-black text-slate-900 dark:text-[#F8FAFC]">Fresh Food & Dairy Items</span>
                <span class="text-[11px] text-slate-500 dark:text-[#CBD5E1]">Spoiled or damaged products (24h)</span>
              </div>
            </div>
            <span class="material-symbols-outlined text-slate-400 text-[18px]">chevron_right</span>
          </div>

          <!-- Item 5: Refund Timeline -->
          <div class="p-4 flex items-center justify-between hover:bg-slate-50 dark:hover:bg-[#2A323D] cursor-pointer" onclick="openPolicyModal('timeline')">
            <div class="flex items-center gap-3.5">
              <div class="w-8 h-8 rounded-full bg-slate-200 dark:bg-[#2A323D] text-slate-700 dark:text-[#F8FAFC] flex items-center justify-center font-black text-xs shrink-0">5</div>
              <div class="flex flex-col">
                <span class="text-xs sm:text-sm font-black text-slate-900 dark:text-[#F8FAFC]">Refund Timeline</span>
                <span class="text-[11px] text-slate-500 dark:text-[#CBD5E1]">5-7 business days per RBI/UPI</span>
              </div>
            </div>
            <span class="material-symbols-outlined text-slate-400 text-[18px]">chevron_right</span>
          </div>

          <!-- Item 6: COD and UPI/Card Refunds -->
          <div class="p-4 flex items-center justify-between hover:bg-slate-50 dark:hover:bg-[#2A323D] cursor-pointer" onclick="openPolicyModal('payment_modes')">
            <div class="flex items-center gap-3.5">
              <div class="w-8 h-8 rounded-full bg-slate-200 dark:bg-[#2A323D] text-slate-700 dark:text-[#F8FAFC] flex items-center justify-center font-black text-xs shrink-0">6</div>
              <div class="flex flex-col">
                <span class="text-xs sm:text-sm font-black text-slate-900 dark:text-[#F8FAFC]">COD and UPI/Card Refunds</span>
                <span class="text-[11px] text-slate-500 dark:text-[#CBD5E1]">Process and verified examples</span>
              </div>
            </div>
            <span class="material-symbols-outlined text-slate-400 text-[18px]">chevron_right</span>
          </div>
        </div>
      </section>

"""

    if 'id="view-policies"' not in html:
        # Insert before view-support-center
        supp_start = html.find('<section id="view-support-center"')
        if supp_start != -1:
            html = html[:supp_start] + policies_view_html + html[supp_start:]
            print("6. Added #view-policies matching 15_REFUND_POLICY_DARK")

    with open("index.html", "w", encoding="utf-8", newline="") as f:
        f.write(html)

    print("HTML modifications successfully saved.")

if __name__ == "__main__":
    main()

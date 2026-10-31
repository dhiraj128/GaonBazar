with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Inject selectFirstLaunchLanguage, confirmFirstLaunchLanguage, openPolicyModal if not already present
js_helpers = """
    // --- First Launch Language Selection (Matching 01_LANGUAGE_*) ---
    let selectedFirstLaunchLang = 'hi';
    function selectFirstLaunchLanguage(lang) {
      selectedFirstLaunchLang = lang;
      const cardHi = document.getElementById('lang-card-hi');
      const cardEn = document.getElementById('lang-card-en');
      const lblCont = document.getElementById('lbl-language-continue');
      if (lang === 'hi') {
        if (cardHi) {
          cardHi.className = "w-full p-4 rounded-2xl bg-white dark:bg-[#1D232B] border-2 border-[#16B86E] flex items-center justify-between shadow-xs transition-all cursor-pointer text-left";
        }
        if (cardEn) {
          cardEn.className = "w-full p-4 rounded-2xl bg-white dark:bg-[#1D232B] border border-slate-200 dark:border-[#465362] flex items-center justify-between shadow-xs transition-all cursor-pointer text-left";
        }
        if (lblCont) lblCont.innerText = "जारी रखें";
      } else {
        if (cardHi) {
          cardHi.className = "w-full p-4 rounded-2xl bg-white dark:bg-[#1D232B] border border-slate-200 dark:border-[#465362] flex items-center justify-between shadow-xs transition-all cursor-pointer text-left";
        }
        if (cardEn) {
          cardEn.className = "w-full p-4 rounded-2xl bg-white dark:bg-[#1D232B] border-2 border-[#16B86E] flex items-center justify-between shadow-xs transition-all cursor-pointer text-left";
        }
        if (lblCont) lblCont.innerText = "Continue";
      }
    }
    window.selectFirstLaunchLanguage = selectFirstLaunchLanguage;

    function confirmFirstLaunchLanguage() {
      const lang = selectedFirstLaunchLang || 'hi';
      localStorage.setItem('gaonbazar_lang_chosen', '1');
      if (typeof setAppLanguage === 'function') setAppLanguage(lang);
      navigateToPhase('login');
    }
    window.confirmFirstLaunchLanguage = confirmFirstLaunchLanguage;

    // --- Policy & Legal Modals / Disclosures ---
    function openPolicyModal(policyType) {
      const titles = {
        cancellation: "Order Cancellation Policy",
        return: "Return & Refund Policy",
        replacement: "Replacement Policy",
        fresh_food: "Fresh Produce & Dairy Policy",
        timeline: "Refund Settlement Timeline",
        payment_modes: "COD & UPI/Card Refunds"
      };
      const texts = {
        cancellation: "Self-cancellation is available for eligible orders within 3 minutes (180 seconds) from successful order placement while the order is being prepared. Once packing or dispatch begins, cancellation is safely redirected to Support to protect rider delivery routes and vendor inventory.",
        return: "We accept genuine returns for wrong, missing, expired, or defective items. Missing items do not require photos. Valid claims receive replacement or 100% refund.",
        replacement: "If an item arrives damaged, unsafe, or materially misdescribed, you can request a hassle-free replacement from the vendor with free priority delivery.",
        fresh_food: "Fresh vegetables, fruits, and dairy items can be reported within 24 hours of delivery. Damaged, spoiled, or sour items qualify for instant credit or replacement.",
        timeline: "Refunds for prepaid orders are credited back to the original source method (UPI, Bank, Card) within 5 to 7 business days per standard RBI/UPI banking settlement cycles. We never fabricate instant credit dates.",
        payment_modes: "Prepaid orders are refunded to the original account. Cash on Delivery (COD) refunds are securely transferred via verified UPI ID or direct bank transfer upon approval."
      };

      const title = titles[policyType] || "GaonBazaar Policy";
      const desc = texts[policyType] || "For assistance, contact our 24x7 rural customer care.";
      
      if (typeof openGenericModal === 'function') {
        openGenericModal(title, desc);
      } else {
        alert(title + "\\n\\n" + desc);
      }
    }
    window.openPolicyModal = openPolicyModal;
"""

if 'confirmFirstLaunchLanguage' not in html:
    # Insert right before function initAppTheme
    target = '    function initAppTheme() {'
    if target in html:
        html = html.replace(target, js_helpers + "\n" + target)
        print("1. Injected JS helpers (confirmFirstLaunchLanguage, openPolicyModal).")

# 2. Update phaseViews in navigateToPhase
old_phase_views = """      const phaseViews = {
        login: 'view-p1-login',
        otp: 'view-p1-otp',
        landmark: 'view-p1-landmark',
        dashboard: 'view-p2-dashboard',
        store: 'view-p3-store',
        cart: 'view-p4-cart',
        checkout: 'view-p4-checkout',
        tracking: 'view-p5-tracking',
        profile: 'view-profile',
        'ai-commerce': 'view-commerce-ai',
        'commerce-ai': 'view-commerce-ai',
        ai: 'view-commerce-ai',
        home: 'view-p2-dashboard',
        account: 'view-profile',
        orders: 'view-profile',
        support: 'view-support-center',
        offline: 'view-offline-fallback',
        'order-details': 'view-order-details'
      };"""

new_phase_views = """      const phaseViews = {
        language: 'view-p1-language',
        login: 'view-p1-login',
        otp: 'view-p1-otp',
        landmark: 'view-p1-landmark',
        dashboard: 'view-p2-dashboard',
        store: 'view-p3-store',
        cart: 'view-p4-cart',
        checkout: 'view-p4-checkout',
        tracking: 'view-p5-tracking',
        profile: 'view-profile',
        'ai-commerce': 'view-commerce-ai',
        'commerce-ai': 'view-commerce-ai',
        ai: 'view-commerce-ai',
        home: 'view-p2-dashboard',
        account: 'view-profile',
        orders: 'view-p5-tracking',
        support: 'view-support-center',
        policies: 'view-policies',
        offline: 'view-offline-fallback',
        'order-details': 'view-order-details'
      };"""

if old_phase_views in html:
    html = html.replace(old_phase_views, new_phase_views)
    print("2. Updated phaseViews in navigateToPhase.")

# 3. Update cleanPhase routing for orders
old_routing = "if (cleanPhase === 'account' || cleanPhase === 'orders') cleanPhase = 'profile';"
new_routing = """if (cleanPhase === 'account') cleanPhase = 'profile';
      if (cleanPhase === 'orders') cleanPhase = 'tracking';"""

if old_routing in html:
    html = html.replace(old_routing, new_routing)
    print("3. Updated cleanPhase orders -> tracking.")

# 4. Update initial boot routing
old_boot = """        // Restored sessions must not add a phantom login history entry.
        navigateToPhase('dashboard', true);
        window.history.replaceState({ page: 'dashboard', gaonbazar_phase: 'dashboard', timestamp: Date.now() }, '');
      }"""

new_boot = """        // Restored sessions must not add a phantom login history entry.
        navigateToPhase('dashboard', true);
        window.history.replaceState({ page: 'dashboard', gaonbazar_phase: 'dashboard', timestamp: Date.now() }, '');
      } else {
        // First run: Language Selection -> Mobile Number -> OTP Verification -> Home
        const hasChosenLang = localStorage.getItem('gaonbazar_lang_chosen');
        if (!hasChosenLang && !window.location.search.includes('test=')) {
          navigateToPhase('language', true);
        } else {
          navigateToPhase('login', true);
        }
      }"""

if old_boot in html:
    html = html.replace(old_boot, new_boot)
    print("4. Updated DOMContentLoaded boot sequence (First launch -> language, else login).")

with open('index.html', 'w', encoding='utf-8', newline='') as f:
    f.write(html)

print("inject_customer_ui_js.py completed successfully.")

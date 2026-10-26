# GaonBazaar Feature Preservation & Navigation Relocation Matrix

**Version:** 2.5.0-approved-design  
**Target:** Customer App (`index.html`), Vendor App (`vendor_dashboard.html`), Runner App (`runner_dashboard.html`), Super Admin Web (`admin_dashboard.html`)  
**Commit Branch:** `integration/three-app-e2e-20261025`  
**Render Preview Track:** `preview/three-app-mobile-20261025`  

---

## 1. Executive Summary & Policy

In strict accordance with the GaonBazaar Design & Implementation Specification, **zero existing features, backend endpoints, database records, calculation rules, or navigation workflows were deleted** during the redesign. 

Rather than superficial cosmetic patches or decorative buttons, the entire system has been upgraded to match the three approved design reference packages:
- `01_Customer_Design_Reference.png` (Customer / Grahak App)
- `02_Vendor_Design_Reference.png` (Vendor / Dukandaar App)
- `03_Delivery_Partner_Design_Reference.png` (Delivery Partner / Gaon Mitra App)
- Super Admin Operations Desk (`admin_dashboard.html`) with Help Desk Tickets Integration

Every control is wired to genuine backend APIs (`FastAPI + SQLite/PostgreSQL`), integer-paise financial calculations, and authentic real-time lifecycle synchronizations.

---

## 2. Customer App (`index.html`) Feature Relocation & Preservation

| Original Feature | Previous Location | New Location in Approved Design | Tested Verification |
|---|---|---|---|
| **Location & Village Chooser** | Congested middle pill in header | Header Subline: `Deliver to: Rampur village v` (tap opens village/landmark picker) | Verified via `test_mobile_e2e.py` |
| **Language Switcher (HI / EN)** | Crowded header pill | Side Drawer (`#sidebar-drawer`) + AI Assistant Top Bar `[EN \| HI]` | Verified persistent localStorage sync |
| **Notifications & Unread Dot** | Crowded header bell icon | Side Drawer + Notifications modal | Verified unread alerts loading |
| **Shopping Cart Icon & Count** | Header right icon | Bottom Navigation Tab 3 (`#nav-btn-cart`) with live badge + floating cart | Verified integer-paise calculations |
| **User Profile / Avatar** | Header right icon | Side Drawer Header Profile Card (`RK` avatar) + Bottom Nav Tab 5 (`#nav-btn-profile`) | Verified user session persistence |
| **App Menu / Navigation Drawer** | Left 3-line hamburger | **Top-Right 4-Square Grid Icon (`grid_view`)** opening `#sidebar-drawer` | Verified touch dismiss & drawer open |
| **Android Back Navigation** | Back arrow | Left `<` arrow shown in all subviews (`view-p3-store`, `view-p4-cart`, `view-p4-checkout`, `view-p5-tracking`, `view-commerce-ai`, `view-profile`) | Verified hardware/gesture Back & `navigateBack()` |
| **Voice Grocery Shopping** | Modal voice dialog | Dedicated AI Shopping Assistant screen (`#view-commerce-ai`) with robot mascot, soundwaves, prompt chips & glowing mic | Verified via `test_voice_shopping_and_ai.py` |
| **Category Browsing** | Redundant separate tab | Compact horizontal filter chips inside Home (`All`, `Grocery`, `Dairy`, `Veg`, `Fruits`...) | Verified zero data loss, instant filtering |
| **2-Column Product Cards** | Single dense store list | "Popular near you" & "More for you" 2-column cards with image, unit, price, and green `+` stepper | Verified instant cart addition & sync |
| **Stores Catalog & Details** | Store feed | Preserved directly beneath featured product sections with open status, distance, and ratings | Verified store catalog loading & rendering |
| **Delivery Economics & Fees** | Hardcoded fee text | Dynamic distance tiers: 0-2 km ₹15, >2-4 km ₹20, >4-5 km ₹25, >5-8 km ₹35, plus ₹3 platform fee and MOV alert | Verified integer-paise match in checkout |
| **Payment Options** | Checkout modal | Choose Payment Method: UPI (GPay, PhonePe, Paytm), Debit/Credit Card, COD | Verified Razorpay FinTech SDK & COD rules |
| **Live Tracking & Minimap** | Pop-up dialog | Fullscreen live tracker: Arriving ETA banner, 5-stage stepper, assigned runner card, route minimap, delivery address, items checklist | Verified via `test_mobile_e2e.py` |
| **Assigned Partner Calling** | Static phone links | Call / Chat buttons active **only when runner is genuinely assigned**; hidden/disabled otherwise | Verified strict role privacy enforcement |
| **Help Desk & Grievance Tickets** | Hidden modal | Side Drawer: "Help Center & FAQs", "Raise a Complaint", and "My Support Tickets" | Verified durable backend creation & admin dispatch |

---

## 3. Vendor App (`vendor_dashboard.html`) Feature Relocation & Preservation

| Original Feature | Previous Location | New Location in Approved Design | Tested Verification |
|---|---|---|---|
| **Shop Name & Status** | Dense left header block | Shop avatar circle + Store Name + `Open v` status pill dropdown | Verified `/vendor/stores/{id}/toggle-status` |
| **Orders Queue & Filters** | 4 giant KPI blocks | Clean orders-first ribbon: `Orders (3)`, `Packing (2)`, `Ready (1)`, Transit, Completed | Verified stage filtering |
| **Incoming Order Cards** | Text-heavy table | Clean cards: `#GB-XXXX`, `New` orange badge, timestamp, order price, customer landmark, item thumbnails row, `[Reject]` and `[Accept Order]` | Verified tactile tap targets & transitions |
| **Customer Direct Call Action** | Phone call icon on card | **STRICTLY REMOVED** to prevent vendor harassment. Replaced by in-app escalation and assigned runner contact | Verified role communication restriction |
| **Assigned Runner Handover** | Generic dispatch button | Dedicated Handover screen: 3-step progress, packing complete hero card, assigned runner contact only, and handover confirmation | Verified runner assignment check |
| **Stock & Inventory Toggles** | Inventory tab | Search products + category chips + instant toggle switch (`In Stock` / `Out of Stock`) + `[+ Add New Product]` | Verified race-safe server persistence |
| **Earnings & Daily Ledger** | Ledger tab | Preserved in Menu & Bottom Nav: Gross sales, commission deductions, net payout, and daily summary | Verified integer-paise calculations |
| **Bank Account & UPI Payout** | Settings tab | Preserved in Menu: Masked account number, IFSC verification, and UPI beneficiary | Verified audit trail & masked display |
| **Store Diagnostics & Cache** | Miscellaneous settings | Preserved in Menu: Build SHA display and "Clear Cache & Reload" | Verified build SHA `/api/version` display |
| **Side Menu / Settings** | Header settings icon | **Top-Right 4-Square Grid Icon (`grid_view`)** opening full Menu | Verified full feature access without data loss |

---

## 4. Runner App (`runner_dashboard.html`) Feature Relocation & Preservation

| Original Feature | Previous Location | New Location in Approved Design | Tested Verification |
|---|---|---|---|
| **Runner Identity & Shift** | Header buttons | Runner profile row (`Ram Kumar`) + `Online v` status dropdown + Big "I am on duty" switch card | Verified duty toggle & backend sync |
| **Current Service Area** | Hidden in settings | Dedicated Current Area Card: `Sonpur Hub` (0-10 km radius active) with `Change` action | Verified 8 km service radius constraint |
| **Today's Missions Summary** | KPI cards | 3-Card Summary: Assigned (`#16B86E`), Completed (`#3B82F6`), Earnings (`#FF981A`) | Verified dynamic count sync |
| **Mission Cards** | Mixed list | High-contrast cards: Orange `PICKUP` badge (#GB-XXXX, store, market, COD amount) & Blue `DELIVERY` badge (#GB-XXXX, customer, landmark) | Verified mission detail transition |
| **Pickup Details & Checklist** | Modal sheet | Store info card, phone call to store only, item checklist with photos, checklist reminder, and `[Start Navigation]` | Verified store pickup flow |
| **On the Way & GPS Navigation** | Static map image | Full interactive map display, route path, ETA chip ("4 min, 1.2 km"), re-center, customer landmark, customer call shortcut (for assigned order only) | Verified real route & landmark display |
| **Doorstep Delivery & OTP** | Single input | Complete Delivery view: Ram Kumar card, items delivered checklist, cash collection (COD), 4 separate large OTP input boxes (`[3][7][2][1]`), and `[Confirm Delivery]` | Verified OTP verification & celebration state |
| **Shift Ledger & Deposit Slip** | Ledger tab | Earnings summary + bank/UPI payout status + cash deposit slip generation | Verified cash reconciliation |
| **Runner Profile & Menu** | Settings tab | **Top-Right 4-Square Grid Icon (`grid_view`)** opening Profile, Vehicle registration, Documents, Help, and Logout | Verified full profile preservation |

---

## 5. Super Admin Web Dashboard (`admin_dashboard.html`) Preservation

| Feature | Location | Status & Verification |
|---|---|---|
| **God-View Live Orders** | Tab 3 (`tab-orders`) | Preserved: Real-time order monitoring with timeline stages, customer, vendor, and runner assignment |
| **Vendor KYC & Onboarding** | Tab 1 (`tab-vendors`) | Preserved: Physical shop verification, photo/ID review, bank verification, approve/reject with audit trail |
| **Runner KYC & Vehicle Onboarding** | Tab 2 (`tab-runners`) | Preserved: ID verification, driving licence/RC check, bank beneficiary, approve/reject |
| **Commission & Payout Ledger** | Tab 4 (`tab-ledger`) | Preserved: 100% integer-paise transactions, platform ₹3 fee, delivery tier fee splits |
| **Bank Account & Payout Verification** | Tab 6 (`tab-bank`) | Preserved: Masked account check, penny drop verification status, audit logging |
| **Internal Account Risk Management** | Tab 7 (`tab-risk`) | Preserved: Strike system, COD blocking, blacklisting, cancellation frequency rules |
| **Help Desk & Grievance Tickets** | **Tab 8 (`tab-tickets`) [NEW]** | Fully Integrated: Real ticket list (`/api/admin/support/tickets`), status filter (`open`, `in_review`, `resolved`), resolution notes input, and Super Admin resolution action |

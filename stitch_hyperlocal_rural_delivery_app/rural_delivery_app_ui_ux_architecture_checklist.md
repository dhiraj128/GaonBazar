# Hyperlocal Rural Delivery App — UI/UX Workflow & Frontend Architectural Blueprint

## Executive Summary & Design System Foundation
* **Target Audience:** Rural & peri-urban consumers, varying literacy, vernacular-first, low-bandwidth 4G/3G connectivity.
* **UX Principles:** Visual-heavy iconography, high touch targets (≥48px), prominent voice/search affordances, offline-resilient state handling, zero hidden fees, clear landmark-based navigation over complex coordinates.
* **Color Hierarchy:**
  * Primary Green: `#16A34A` (Trust, Agriculture, Delivered)
  * Warning Amber: `#F59E0B` (Order Accepted, In-Progress)
  * Info Blue: `#2563EB` (Packed & Ready)
  * Action Orange: `#EA580C` (Out for Delivery, Primary CTAs)
  * Neutral Dark: `#1F2937` (Primary Text)
  * Neutral Light: `#F3F4F6` (App Background)

---

## Phase 1: Onboarding & Location Setup

### 1.1 Phone Number Entry Screen (`/auth/login`)
- [ ] **[UI] App Header / Hero Graphic:** Minimal rural commerce illustration or brand icon with tagline (e.g., *"Apne Gaon Ki Dukaan, Aapke Ghar Tak"*).
- [ ] **[UI] Country Code Selector:** Fixed `+91` badge with national flag icon.
- [ ] **[UI] Phone Input Field:** Large numerical keypad input (`type="tel"`, `maxlength="10"`, auto-focus, large 20sp font size).
- [ ] **[UI] Consent & T&C Snippet:** Clear 1-line disclaimer regarding SMS charges and terms.
- [ ] **[UI] Action Button:** `Send OTP` / `OTP Bhejein` button (full-width sticky/prominent button, disabled until 10 digits entered).
- [ ] **[Interaction & Flow]:**
  - Clicking `Send OTP` triggers backend rate-limited SMS gateway.
  - Transitions automatically with slide-left transition to OTP Screen (`/auth/verify-otp`).

### 1.2 OTP Verification Screen (`/auth/verify-otp`)
- [ ] **[UI] Context Banner:** Displays sent phone number `+91 XXXXX-XXXXX` with an `Edit` text link.
- [ ] **[UI] 4-to-6 Digit OTP Boxes:** Auto-advance pin inputs with active focus border and numeric soft keyboard.
- [ ] **[UI] Auto-Read SMS Listener:** Android WebSMS / Web OTP API integration for zero-friction auto-fill.
- [ ] **[UI] Resend Timer:** 30s countdown timer (`Resend OTP in 0:24`) switching to clickable `Resend via SMS` or `Get OTP on Call`.
- [ ] **[Interaction & Flow]:**
  - Auto-submits immediately upon entering the final digit.
  - If existing user → navigates directly to `Phase 2: Main Dashboard`.
  - If new user registration → navigates to `/auth/profile-setup`.

### 1.3 Profile & Rural Landmark Setup Screen (`/auth/profile-setup`)
- [ ] **[UI] Name Input:** Full name field with voice-input microphone icon.
- [ ] **[UI] GPS Detection Button:** `Use Current GPS Location` card with satellite/pin icon and fallback GPS permission prompt.
- [ ] **[UI] Village / Panchayat Selector:** Searchable dropdown or autocomplete for Tehsil, Village/Gram Panchayat, and Pincode.
- [ ] **[UI] Rural Landmark Input Field (Crucial UX):** Multi-line text field with helper prompt (e.g., *"Near Shiva Temple / Behind Primary School / Next to Water Tank"*).
- [ ] **[UI] House / Farm Number (Optional):** Labeled optional to avoid drop-offs in unnumbered rural settlements.
- [ ] **[UI] Submit Button:** `Save & Enter Market` button (full-width, high contrast).
- [ ] **[Interaction & Flow]:**
  - Writes user profile, default coordinate tuple `[lat, lng]`, and landmark string to persistent local storage / cache and backend DB.
  - Navigates directly to `Phase 2: Main Dashboard` (`/home`).

---

## Phase 2: Main Dashboard & Discovery

### 2.1 Sticky Location & Search Header
- [ ] **[UI] Sticky Location Bar:** 
  - Location pin icon, active Village Name (bold), and truncated Landmark subtitle.
  - Downward chevron trigger to open a quick modal to change or re-pin location.
- [ ] **[UI] Notification Bell & Language Toggle:** Quick toggle icon (`Eng / हिंदी / Local`) in the top-right app chrome.
- [ ] **[UI] Universal Search Bar:** Integrated bar with `Search grocery, medicine, farm supplies...` and persistent audio/voice mic button.

### 2.2 Quick Category Grid
- [ ] **[UI] Horizontal / Grid Icon List:** 
  - Visual circle badges with illustrated icons and bilingual labels:
    - 🛒 Daily Kirana & Groceries
    - 💊 Medicines / Pharmacy
    - 🌾 Seeds & Agri-Supplies
    - 🥛 Dairy & Fresh Produce
    - ⚡ Emergency Household Needs
- [ ] **[Interaction & Flow]:** Tapping any category pill applies a quick filter to the store list below or opens dedicated category index.

### 2.3 Nearby Stores Feed (5km Radius)
- [ ] **[UI] Section Header:** *"Stores delivering to your village"* + distance radius chip (`Within 5 km`).
- [ ] **[UI] Store Card Component:**
  - Store thumbnail image / banner.
  - Store Name (bold 16sp) + Verified Merchant Badge.
  - Tag pill: Category (e.g., `General Store`, `Medical Store`).
  - Distance & ETA chip: `1.8 km` • `25-35 mins`.
  - Delivery Fee indicator: `₹15 Delivery` or `Free above ₹199`.
  - Operational Status: `Open Now` (green dot) or `Closes at 8 PM`.
- [ ] **[Interaction & Flow]:**
  - Tapping a store card pushes route to `Phase 3: Store & Product View` (`/store/:storeId`).

---

## Phase 3: Store & Product View

### 3.1 Store Identity Header
- [ ] **[UI] Collapsible / Sticky Top App Bar:** Back button arrow (`←`), store name, and search inside store icon.
- [ ] **[UI] Store Summary Card:**
  - Rating badge (e.g., `★ 4.6 (120+ orders)`).
  - Minimum order amount callout (e.g., `Min. order ₹50`).
  - Store contact / Call Dukandaar button (trust-builder in rural communities).

### 3.2 Category Navigation Tabs
- [ ] **[UI] Sticky Horizontal Scroll Tabs:** Category chips (`All`, `Atta & Rice`, `Cooking Oil`, `Spices`, `Soaps`, `Snacks`).
- [ ] **[Interaction & Flow]:** Clicking a tab smooth-scrolls the product catalog to the matching category section with active highlight indicator.

### 3.3 Product Catalog Grid & Add Flow
- [ ] **[UI] Product Card Component:**
  - High-res product thumbnail with zoom affordance.
  - Product title in local language + English (e.g., `Aashirvaad Shudh Chakki Atta`).
  - Unit/Weight variant picker or label (e.g., `5 kg`, `1 kg`, `500 g`).
  - Pricing container: Discounted Price (bold `₹210`) + Strikethrough MRP (`₹240`) + Green `% OFF` badge.
- [ ] **[UI] Dynamic Add Button (`State Switcher`):**
  - **State A (Empty):** Outlined `ADD +` button.
  - **State B (Added):** Solid green pill stepper with `[-]` `[Quantity: 1]` `[+]`.
- [ ] **[Interaction & Flow]:**
  - Tapping `ADD +` updates global Cart store (`itemCount + 1`), triggers haptic feedback, and displays the Bottom Sticky Cart Banner.
  - Pressing `[-]` when quantity is 1 returns the button to State A and removes item from cart.

### 3.4 Floating / Sticky Bottom Cart Banner
- [ ] **[UI] Floating Footer Bar:** Fixed overlay above safe-area bottom margin.
  - Left: Item count badge (`3 Items`) + Total (`₹485`).
  - Right: `View Cart →` CTA button with chevron icon.
- [ ] **[Interaction & Flow]:** Tap transitions to `Phase 4: Cart & Checkout` (`/cart`).

---

## Phase 4: Cart & Checkout

### 4.1 Cart Review Screen (`/cart`)
- [ ] **[UI] Screen Header:** Back button (`←`), Title (`Your Cart / Tokri`), and Store Origin Tag (`Ordering from: Sharma Kirana Store`).
- [ ] **[UI] Items List:**
  - Row item with thumbnail, title, selected weight, line item price.
  - Inline `[-] Qty [+]` controller for quick modification.
  - Trash can icon for complete item removal.
- [ ] **[UI] Bill Breakdown Card:**
  - Item Subtotal: `₹485.00`
  - Delivery Partner Fee: `₹20.00`
  - Government / Village Platform Handling: `₹3.00`
  - Total Savings callout (Green text): `You saved ₹45 on this order!`
  - Final Amount Payable: `₹508.00` (Bold 18sp).
- [ ] **[UI] Proceed to Checkout CTA:** Fixed bottom button (`Select Address & Pay →`).

### 4.2 Checkout Screen (`/checkout`)
- [ ] **[UI] Delivery Location Confirmation Card:**
  - Shows verified village name, full landmark text, and customer phone number.
  - `Change Address` quick button.
- [ ] **[UI] Delivery Instructions / Voice Note:**
  - Quick checkboxes: `Call before arriving`, `Leave with neighbor if away`.
  - Mic icon to record 15-second voice note for delivery boy (*"Panchayat ghar ke peeche aana"*).
- [ ] **[UI] Payment Method Selector:**
  - Radio Card 1: `Cash on Delivery (COD)` / *Haath mein Cash* (default for rural trust).
  - Radio Card 2: `UPI (Google Pay, PhonePe, Paytm, BHIM)` with app logos.
- [ ] **[UI] Place Order Action:**
  - Persistent sticky button: `Place Order • ₹508` (high-contrast orange/green button).
- [ ] **[Interaction & Flow]:**
  - If UPI selected → triggers UPI intent deep link.
  - On payment success or COD selection → submits order payload to backend, broadcasts push notification / WebSocket to merchant app, and redirects to `Phase 5: Live Order Tracking` (`/orders/:orderId`).

---

## Phase 5: Live Order Tracking (`/orders/:orderId`)

### 5.1 Order Header & Quick Actions
- [ ] **[UI] Order Summary Badge:** Order ID (`#RUR-9482`), estimated arrival time (`Arriving by 4:30 PM`), and total bill amount.
- [ ] **[UI] Direct Calling Actions:**
  - `Call Store` button with merchant name.
  - `Call Delivery Partner` button (enabled once out for delivery).

### 5.2 5-Stage Color-Coded Vertical Timeline
- [ ] **[UI] Step 1: Order Placed**
  - Color: **Neutral Grey (`#6B7280`)** or Green checked once confirmed.
  - Subtitle: Timestamp (`03:45 PM`) • Sent to merchant.
- [ ] **[UI] Step 2: Vendor Accepted**
  - Color: **Amber / Yellow (`#F59E0B`)**.
  - Subtitle: *Dukandaar ne order accept kiya*.
- [ ] **[UI] Step 3: Packed & Ready**
  - Color: **Royal Blue (`#2563EB`)**.
  - Subtitle: *Samaan pack ho gaya hai*.
- [ ] **[UI] Step 4: Out for Delivery**
  - Color: **Vibrant Orange (`#EA580C`)**.
  - Subtitle: Delivery partner assigned (`Ramesh Kumar - Hero HF Deluxe`).
- [ ] **[UI] Step 5: Delivered**
  - Color: **Success Green (`#16A34A`)**.
  - Subtitle: Verification via 4-digit Delivery OTP or signature.

### 5.3 Live Map / Distance Progress & Support
- [ ] **[UI] Low-Bandwidth Route Tracker:** Simplified vector route schematic showing Store ➔ Village Landmark ➔ Customer Home.
- [ ] **[UI] Emergency Help Button:** WhatsApp support or 1-tap toll-free customer care hotline.
- [ ] **[UI] Return to Home Button:** Bottom secondary CTA to return to `/home` without losing active order state.

---

## Screen Connection & State Flow Matrix

| Screen | Target Route | Trigger Element | Key State Passed |
| :--- | :--- | :--- | :--- |
| **Login** | `/auth/verify-otp` | `Send OTP` Button | `phoneNumber` |
| **Verify OTP** | `/auth/profile-setup` or `/home` | Final OTP digit / auto-fill | `authSessionToken`, `isNewUser` |
| **Profile Setup** | `/home` | `Save & Enter Market` | `userCoords`, `villageName`, `landmark` |
| **Home Dashboard** | `/store/:id` | Store Card Tap | `storeId`, `storeMeta` |
| **Store & Products** | `/cart` | Sticky Cart Banner (`View Cart`) | `cartItems[]`, `storeId`, `subtotal` |
| **Cart Review** | `/checkout` | `Proceed to Checkout` | `cartItems[]`, `billBreakdown` |
| **Checkout Screen**| `/orders/:orderId` | `Place Order` Button | `orderId`, `paymentMode`, `deliveryDetails` |
| **Order Tracking** | `/home` | `Back to Home` CTA | Order persists in background polling / sync |

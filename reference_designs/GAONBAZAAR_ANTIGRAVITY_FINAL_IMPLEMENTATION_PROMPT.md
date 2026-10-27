# GAONBAZAAR — APPROVED THREE-APP DESIGN IMPLEMENTATION + SUPER ADMIN INTEGRATION

**To:** Antigravity — sole coding and deployment agent  
**Repository:** `dhiraj128/GaonBazar`  
**Target:** Existing Customer, Vendor, Runner apps and connected Super Admin web dashboard  
**Release restriction:** Development and isolated preview only until owner approval. **Do not deploy or merge to production without verified backup/recovery and the owner's explicit approval.**

## 0. NON-NEGOTIABLE DESIGN ATTACHMENTS

The ZIP accompanying this prompt includes three individually downloadable, approved visual boards:

1. `01_Customer_Design_Reference.png` — Customer/Grahak: Home, AI voice shopping, Cart, Live Tracking, Account & Side Menu, light/dark concept.
2. `02_Vendor_Design_Reference.png` — Vendor/Dukandaar: Orders, Order Detail, Stock, Assigned Runner Handover, Menu, light/dark concept.
3. `03_Delivery_Partner_Design_Reference.png` — Runner/Gaon Mitra: Missions, Pickup, Navigation, Delivery OTP, Profile/Menu, light/dark concept.

**Read/open ALL THREE attachments before editing.** Do not describe them merely from their filenames. These boards are the owner's visual direction, not screenshots from the current deployed app.

**Visual-fidelity rule:** Recreate the illustrated information hierarchy, structural layout, header/menu placements, bottom-navigation order, card styles, tap targets, visual rhythm and relative spacing as closely as a real responsive application permits. **Do not make your own alternative design, retain the old interface as a template, or apply only superficial CSS changes.** Render native, responsive, interactive HTML/CSS/JS components; do not place the board image as a page background.

**Important distinction:** The boards are visual concepts and may contain illustrative/mock names, products, order IDs, totals, map routes or labels. These are NOT production data or authoritatively verified facts. Replace all illustrative data with genuine existing app state, backend values and valid localized strings. Resolve any illustrative contradictions by preserving business rules and the owner's stated requirements. Exact pixel placement is targeted at the illustrated reference width, while smaller/larger phone widths must reflow without overlaps.

**STOP and report** if any existing important feature would be lost, or if a reference conflicts with access-control, money, privacy or physical-delivery safety. Preserve the feature and show where it moved; never silently delete it.

## 1. GLOBAL VISUAL SYSTEM — FOLLOW ACROSS ALL THREE APPS

- Visually new interface, not the old shell with changed padding. Consistent GaonBazaar brand, but distinctive role accents: Customer emerald, Vendor emerald/orange, Runner emerald/blue.
- **Light mode:** warm cream/off-white pages, white elevated cards, dark slate text, emerald primary actions, selective orange for warnings; no monochrome black/white-only design.
- **Dark mode MUST NOT BE BLACK-ON-BLACK:** use soft blue/teal-slate for page and card surfaces. Design tokens, starting points: `page #203846`, `card #2B4858`, `elevated #365668`, `text #F6FBFD`, `secondary text #C9DCE5`, `primary #16B86E`, `orange #FF981A`, `blue #3B82F6`, `divider #476476`. Adjust values only to meet contrast/accessibility. Use clear separation between page, cards, inputs, headers and bottom nav. No near-invisible grey-on-grey text or pure black slabs.
- Both themes must expose exactly the same features; minimum ~4.5:1 for regular body text and sufficiently distinguishable focus/controls. Validate Hindi typography and real-device brightness outdoors.
- Clear icon sizes and alignment; no icon or text overlap, zero clipped cards/buttons, no unnecessary duplicate icons, no giant KPIs atop every screen. Consistent gutters (approx. 16px), card radius, 44–48px interactive touch areas and bottom safe-area padding; icon and text centered precisely.
- On phone widths 320/360/375/393/414px, headers must fit in a single clean row where shown. Long shop/person names ellipsize only when necessary with discoverable full text. Prevent right-edge clipping and horizontal body overflow. Honor keyboard opening, screen rotation and system font scaling.
- Keep bottom navigation fixed/sticky with safe-area support; avoid hiding scrollable content below it.
- English selected => interface labels/instructions in English. Hindi selected => interface labels/instructions in Hindi. Product/brand/proper names may remain as originally named. No random mixed-script UI labels; translation must include error/success text, payout status, all menus and notifications. Language switch is persistent across app sessions.
- Provide the top-right four-square/menu icon (as illustrated) and make it open the corresponding **real** menu. Avoid duplicate top-right icon + permanent duplicate menu controls that congest the header. Notifications indicated unobtrusively, accessible via the menu/bell only where appropriate.
- All icons, tabs, drawers, menus and action buttons must be connected to a real purpose. No click-to-do-nothing placeholders.

## 2. CUSTOMER APP — REFERENCE IMAGE 01

**Main screens from the approved board:**

**Home/Store feed:** village/locality header with location chooser and four-square side-menu control; prominent actual search plus microphone; categories as compact filter chips WITHIN Home; real stores and products, product imagery where available, clear prices/units/inventory and add-to-cart steppers. **Do not recreate separate redundant Stores and Categories tabs with essentially identical pages.** Keep every existing store, category, product and backend association.

**AI Voice shopping:** dedicated AI page, permission state and listening UI, Hindi/Hinglish/English understanding, product match/clarification, actual cart quantity add/remove and feedback, and voice engine fallback to typing. Test six representative voice commands in the real microphone flow, not only by injecting text directly into handlers.

**Cart + checkout:** real products, correct integer-paise totals, applicable delivery tiers and ₹3 platform fee; Razorpay-backed card/UPI as supported, COD as configured; saved payment options only if actually tokenized/supported; order confirmation from server. Never present fabricated payment success.

**Orders/live tracking:** actual order lifecycle, assigned Runner (only after assignment), backend-grounded status/ETA and interactive map if authorized/available. Call assigned Runner from the active order only; otherwise hide/disable with understandable explanation. Support escalation within the app.

**Profile + right/side menu:** preserve and reorganize the existing real drawer and functionality: My Profile, Saved Addresses, Saved Payments, Past Orders, AI Order Support (distinct from shopping AI), Help Center/FAQs, Raise Complaint, My Support Tickets (status/history), language, light/dark/system theme, Privacy & Terms, About, Logout. The top-right menu icon must open it. No hidden or deleted menu functions. Complaint submission must create a durable backend record with acknowledgement, ticket ID, status and Super Admin visibility; AI support may route/triage but must not mark unresolved tickets as resolved.

**Bottom navigation:** Home / AI / Cart / Orders / Account, as the approved board; meaningful distinct destinations. Menu drawer remains accessible in the top right.

**RURAL ADDRESSING / LOCATION (IMPORTANT):**
- Capture village, district, block, panchayat, tola/mohalla/ward (when known), landmark (school, temple, shop, etc.), house/local directions and optional map pin/GPS. Support multiple saved addresses. Avoid requiring city-street formats unsuitable for villages.
- Show readable hierarchy, e.g. `Village: Rampur • Panchayat: ... • Block: Mushahari • District: Muzaffarpur • Landmark: near Primary School`; fields may be unknown and must not be guessed. Distinguish village names which repeat across districts.
- Geocode/GPS must try for precise coordinates when permitted; never replace an exact coordinate with a made-up demo point; permit manual correction and pin placement.
- Backend, not client-supplied `distance_km`, must validate the actual service radius (current requirement 8 km) and fee; account for available route vs straight-line approximation honestly. Preserve user orders and payment flows.
- Confirm touch scroll, Android system Back gesture/button, browser history and modal dismissals in all these screens, including after repeated tab changes.

## 3. VENDOR APP — REFERENCE IMAGE 02

- **Orders first:** the compact branded header, real shop name + Open/Closed status, notification badge and four-square menu icon; distinct New/Packing/Ready workflows; tactile Accept/Reject/Pack/Ready actions; clear item thumbnails, quantities, amount and customer delivery landmark. Do not show giant finance dashboard KPI cards on Orders.
- **Order details:** show items, quantities, customer order notes and delivery location as necessary. **NO DIRECT CUSTOMER CALL ACTION** anywhere in Vendor order UI. Replace with in-app issue/escalation when the shop must resolve an item substitution/cancellation.
- **Stock & Inventory:** editable products, categories, stock quantity, available/out-of-stock toggle with authoritative server persistence and race-safe UI; add/edit product; don't lose original inventory.
- **Runner handoff:** when a genuine Runner has been assigned to the particular order, show assigned Runner details, contact action to *that assigned Runner only*, and handover status. Never use the first online Runner, fake numbers, or a generic customer phone. The Runner, not Vendor, completes OTP doorstep delivery.
- **Menu:** access Orders, Products/Inventory, Earnings/Payouts/Ledger, Bank/UPI Payout Settings, Vendor/Store KYC, Delivery Partner assignments, existing AI Sales Assistant (if truly implemented), Help & Support, complaints/tickets, Store Profile/Settings, language/theme, notifications, safe cache update and Logout. Do not invent production-active modules (e.g., tournaments, promotions, training) solely because a concept image depicts them. Preserve those only if actually implemented or separately approved.
- No payout/verification feature may disappear when relocating it to menu. Store owner permissions must be authenticated and scoped to their own store on the backend.

## 4. DELIVERY PARTNER / RUNNER APP — REFERENCE IMAGE 03

- **Missions dashboard:** compact top header, verified identity/role status, readable On/Off Duty toggle with backend sync, current real service area, current/assigned missions, earnings summary and no visually dominating KPIs.
- **Pickup details:** assigned Vendor store, actual pickup location, order item checklist, proper pickup confirmation, meaningful COD/online payment indication.
- **On-the-way:** functioning map/navigation/deep link, assigned Customer village/tola/landmark address, live location permission state, call/message relevant contacts ONLY for the assigned order, no fake route line/ETA. Runner can contact assigned Vendor or assigned Customer if operationally necessary and permitted. Call shortcuts must not reveal unrelated users' phone numbers.
- **Complete delivery:** only Runner may finalize actual doorstep delivery by server-verified OTP, enforce one-time and state transition rules, proper COD collection and order final status reflected in every app and Super Admin. Failure/retry/issue report states must work.
- **Profile and menu:** Trip History, Earnings/Bank/UPI/Payouts, vehicle type/registration as applicable, driving licence if relevant, identity KYC status, support and tickets, notification preferences, language/theme, safe updates and Logout. No pretend `verified` badge without a completed verification record.
- Light mode is fully bright/readable; **dark mode is bright slate/teal, not all black.** Map, status labels and amounts remain legible on real outdoor phones.

## 5. SUPER ADMIN — MUST BE CONNECTED TO ALL THREE APPS

**Super Admin is an existing WEB DASHBOARD, not a fourth mobile application.** Preserve its current functionality and existing roles, and provide web-responsive management views that visually harmonize with the approved GaonBazaar design. It is the authoritative control plane—not fake charts fed by hard-coded data.

**Required sections:**

1. **Overview:** actual vendors, customers, runners, stores, incoming/active/late/cancelled/delivered orders, complaint queues, settlement and failure counts; truthful online/offline data, not marketing numbers.
2. **Vendor onboarding and KYC:** view submitted identity/business/shop documents, physical shop and address details, identity and bank beneficiary checks; status `not_submitted / pending / needs_more_info / approved / rejected / suspended`, clear reason, timestamp, reviewer and audit trail. Restrict order fulfilment/payout activation according to defined onboarding policy.
3. **Runner onboarding and KYC:** consented identity verification, selfie/photo comparison when lawful, bank/UPI beneficiary verification; vehicle type, registration/RC and licence/insurance where applicable by vehicle/service rules; approve, reject, request resubmission, suspend with audit. Do not treat missing bike documentation as an automatic rejection when an approved service type does not require it. Verify only through lawful provider/manual review with clearly distinguished status.
4. **Customer management:** ordinary grocery ordering should use secure customer account/phone verification; **do not impose mandatory Aadhaar upload on every Customer** without justified lawful need and explicit owner approval. Admin sees account/order/ticket risk signals under least privilege, not unrestricted identity photos.
5. **Order operations:** real order timeline from Customer checkout -> Vendor acceptance/packing -> authorized Runner assignment -> pickup -> GPS transit -> OTP delivery -> COD/payment reconciliation, with live event state sync across all apps. Audit manual interventions and reason codes.
6. **Money/settlements:** platform ₹3 handling fee and current configurable delivery tiers (0–2 km ₹15, >2–4 ₹20, >4–5 ₹25, >5–8 ₹35) must be sourced from backend configuration rather than hardcoded UI. Current expected split: ₹10 of delivery charge to platform, remainder Runner, Vendor receives product subtotal before any explicitly documented adjustments; promotions have separate ledger impacts. Use integer paise, immutable transaction records, idempotency and historical order snapshots.
7. **Provider-confirmed payout processing:** onboard valid provider-linked payout/beneficiary details; do not claim `settled`, `transferred`, or `verified` when code only generated a local random ID. Record provider request/reference, provider webhook/status confirmation, failures and retry safety. Show `pending` or `sandbox` honestly.
8. **Complaints/Help Desk:** tickets originating from Customer, Vendor or Runner; case type, order link, assignee, severity, notes, status, evidence, escalation, resolution and notifications. AI support can propose answers but cannot silently close unresolved cases.
9. **Permissions & security:** role-specific staff permissions, access logs, audit trail, rate limits, confidential document access, notification configuration, service radius and localized village coverage; only authorized Super Admin operators may approve/reject KYC/payouts.
10. **System health:** preview/production build SHA (read-only), API health, job failures, webhook reconciliation and database migration readiness. No fake green indicators.

### 5.1 KYC — LEGAL/SECURITY SAFETY REQUIREMENTS

- For identity evidence, **Aadhaar is voluntary and consent-based**. Offer lawful alternative identity-document routes; do not force Aadhaar-only onboarding where not mandated by applicable law. Use UIDAI-compliant digitally signed Offline QR / Paperless Offline e-KYC or authorized authentication provider workflows where eligible. A plain uploaded Aadhaar photo or a matching name does NOT mean UIDAI verification succeeded.
- Before Aadhaar offline verification, provide clear notice/consent, purpose, data handling and alternatives. Protect data; do not store raw 12-digit Aadhaar numbers, biometric templates or unmasked sensitive scans unnecessarily. Where permissible, retain only minimal masked references (e.g. last four digits), status and audit trail. Never show sensitive IDs to ordinary users or expose them in logs/screenshots.
- Online Aadhaar authentication/e-KYC is NOT a public API anyone may call; use only correctly authorized requesting entities/providers and legal review. Do not implement scraping or simulated UIDAI responses.
- Bank verification: store sensitive banking details encrypted/protected, return only masked account references, and perform account-holder/beneficiary matching through supported authorized provider mechanisms, recording a genuine provider result. Without a verified provider, label `pending external verification`, not `verified`.
- Vehicle/RC/licence validation: ask only when relevant; provider-based Vahan/transport checks only with lawful access/approval, or clearly labelled manual document review. Avoid pretending to have government verification when only regex or upload validation occurred.
- Document upload is NOT approval. Review states, admin actions, consent evidence, retention/deletion policy, access restrictions and resubmission must be enforced server-side. Apply least-privilege access to documents and masked payout account information.
- Track separate verification badges such as `Identity — manually reviewed`, `Identity — verified with authorized provider`, `Bank — verified`, `Vehicle — documents reviewed`; no universal `KYC verified` if underlying checks remain incomplete.

### 5.2 MANDATORY REAL DATA SYNCHRONIZATION

| Event | Customer | Vendor | Runner | Super Admin |
|---|---|---|---|---|
| New paid/COD order | Shows confirmed order & honest payment state | Correct store queue receives order | Not assigned yet | Sees order and financial record |
| Vendor accepts/packs | Sees live status | Updates own order | Sees only if assigned | Audit timeline updates |
| Runner assigned | Assigned contact only | Assigned Runner view and call | Authorized mission | Assignment and eligibility recorded |
| Runner picks up | Updated tracking | Shows handed over | Enables directions | Pickup event, time and status |
| OTP delivered | Confirmed delivered | Completed state only | Completes with verified OTP | Immutable delivery record and settlement eligibility |
| KYC submitted/approved | Applicable status only | Own Vendor status | Own Runner status | Review queue, approver, audit reason |
| Support ticket | Own status | Own tickets only | Own tickets only | Unified priority queue and replies |
| Payment/payout | Correct transaction status | Own ledger/payout status | Own earnings/settlement | Provider-confirmed full audit ledger |

No fake data synchronization; no cross-tenant exposure; all privileged actions are authorized in the backend and protected from IDOR. All important state changes should be transactional/idempotent as appropriate, durable in the database, and propagate to the correct app after refresh/polling/event delivery.

## 6. REPEATED SCROLL AND BACK MUST BE PROVEN ON REAL PHONES

**Specific previously reported defect:** Scrolling works once but subsequent up/down swipes stop responding, especially after changing screen/view or returning from modals. Do not pass a single wheel-scroll test and claim fixed.

- At least 10 consecutive swipe reversals UP -> DOWN -> UP on **each long scroll screen** and after using tabs, cards, overlays, keyboard, menus, map, order details and theme switch. Must continue responding every time. No touchstart listeners swallowing gestures, no overflow-hidden body trap, no nested scroll containers causing freeze.
- Verify full top/bottom reachability, correct focus, safe-area bottom padding, no inaccessible last card, and pull-to-refresh conflict if present.
- Android system/edge Back, browser Back, in-app arrow, modal/drawer Back, checkout return and repeated drill-down/return must preserve expected history rather than exit immediately or reopen stale overlays. Test at least 10 navigation scenarios including log-in/account state and after asynchronous API loading.
- Microphone: real Android device + secure HTTPS origin, speech permission flow, granted/denied state, Hindi/Hinglish intent, actual cart mutation, errors and restart/retry; label simulated text-only tests accurately.
- GPS/route: physical device location permission and actual known test route/landmark, manual fallback; no static map counted as navigation.
- Automated mobile device emulation does NOT substitute for a real physical Android device. If no physical device testing is available, state explicitly `NOT PHYSICALLY VERIFIED`.

## 7. EVIDENCE / RELEASE ACCEPTANCE GATE

1. **Before editing**, take representative screenshots of CURRENT actual preview screens (Customer/Vendor/Runner) and inventory existing functionality, routes and menu entries. Show preservation mapping `old feature -> new location -> test`.
2. Implement the three design boards as **real responsive interactive UI** in a separate working branch; no screenshot-as-UI, no fake controls. Existing backend models, data, saved methods and order flows must be preserved.
3. For each app, submit matching screenshots for **all shown major screens**, at 320/360/375/393/414px and BOTH modes; provide side-by-side compare against reference images. Verify no overlap/clipping/hidden labels, uniform icon and card alignment. No copy-pasted screenshots incorrectly named as other screens.
4. Demonstrate repeated touch scrolling and Android Back; document microphone & live GPS physical-device result, not just automated test pass percentages.
5. Verify Customer -> Vendor -> assigned Runner -> OTP -> Super Admin end-to-end, tickets, KYC submission/admin review/resubmission, bank onboarding/payout status, permissions and unauthorized access rejection. Use TEST/SANDBOX data and providers for finance; no fake money flows.
6. Prove preview is running the exact new Git SHA using `/api/version`; verify intended mobile URLs and PWA service-worker cache update; avoid repeated preview-login dialogs. No production release merely because CI is green.
7. **Production data safety:** production Render SQLite may reside on ephemeral storage. Before ANY merge/deploy/cutover, independently verify offsite production backup checksum, row counts, financial totals and a test restoration, including customers, vendors, runners, orders, order lines, payment methods/tokens, banking and payout records, notifications and KYC metadata. A backup file in Git alone does not demonstrate current live data preservation. Verify PostgreSQL schema, migration, reconciliation and rollback. Do not expose sensitive backups publicly.
8. Report honest blockers and outstanding tests. **Do not declare fully complete until the owner has visually approved the new previews and data-safety gates pass.**

## 8. FINAL DELIVERABLES FROM ANTIGRAVITY

- Link to the working-branch PR and latest exact SHA.
- Hosted preview links for all three apps and Admin web, plus version/commit verification.
- Full visual before/reference/after matrix for **Customer / Vendor / Runner**: every major screen in Light and Dark mode, with screenshots that genuinely depict the claimed screen.
- `FEATURE_PRESERVATION.md`: original features still available and navigation location.
- `SUPER_ADMIN_KYC_AND_OPERATIONS.md`: status model, documented workflows, legal verification method/provider availability, manual-vs-automatic statuses, and role-based permissions.
- `E2E_REAL_MOBILE_QA.md`: consecutive swipe and Back tests, mic/GPS real-device evidence or explicit unavailable results, and failed issues.
- `PAYMENT_RECONCILIATION.md`: no false settlement, real/sandbox status and provider evidence.
- `PRODUCTION_NO_DATA_LOSS_GATE.md`: verified backups, restoration and migration/rollback status.
- Explicit owner approval request **before** any production merge or deployment.

**Final order to execute:** (a) inspect images + feature inventory, (b) build visual system and functional screens, (c) link workflows to existing backend + Super Admin, (d) validate dark/light, Hindi/English, scrolling/back/voice/GPS, (e) preview screenshots + tests + security/data gates, (f) owner approval, THEN a separately authorized production release.

**Hard rule:** Antigravity alone writes/deploys. ChatGPT does not edit GitHub/Render/Supabase. The user will attach the three PNG files and this Markdown prompt to Antigravity. Do not begin production deployment based solely on this instruction.

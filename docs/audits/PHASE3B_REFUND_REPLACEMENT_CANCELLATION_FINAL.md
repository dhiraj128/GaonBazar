# GAONBAZAAR — PHASE 3B: REFUND, REPLACEMENT, CANCELLATION & RESOLUTION SYSTEM AUDIT

**Audit Date:** 2026-10-31  
**Working Branch:** `preview/three-app-mobile-20261025`  
**Latest Commit:** `3234aac` (`feat(phase3b): complete refund, replacement, cancellation and returns system across four apps`)  
**Production Status:** STRICTLY UNTOUCHED (`https://gaonbazar.onrender.com` on `main`)  
**Preview Deployment:** `https://gaonbazar-mobile-preview.onrender.com` (Render Service `srv-dbepjn2vcj2c73dntaf0`)  
**Authoritative Database:** Supabase PostgreSQL (`bbxryqngieknfclhqbmr`)  
**Automated Verification Suite:** 241/241 Checks Passed (100.0%)

---

## 1. Executive Summary & Verification Verdict

The GaonBazaar quick-commerce platform has been successfully upgraded with a production-grade, four-application **Refund, Replacement, Cancellation & Issue Resolution Engine (Phase 3B)**. 

The architecture strictly adheres to GaonBazaar's rural 30–60 minute delivery model (Minapur pilot, 0–8.0 km radius) while offering a customer experience as simple and reassuring as major tier-1 quick-commerce apps.

### Key Verification Achievements:
1. **Four Synchronized Applications:**
   - **Customer App (`index.html`):** Choice of Free Corrective Replacement or Truthful Refund; 10 standard grievance categories; item selection with unit price calculation; dynamic ETA (~45 Mins); reverse pickup indicator; 7-stage interactive Replacement Stepper (`REQUESTED -> VERIFYING -> APPROVED -> VENDOR_PACKING -> RUNNER_ASSIGNED -> OUT_FOR_DELIVERY -> REPLACED`); delivery OTP box; bilingual Policy modal.
   - **Vendor App (`vendor_dashboard.html`):** Dedicated Replacements ribbon filter & management queue; transactional stock confirmation & packing; out-of-stock reporting; mark ready for runner.
   - **Runner App (`runner_dashboard.html`):** Assigned replacement missions with prominent badge `⚡ Replacement Delivery — No Customer Payment Due / कोई भुगतान न लें (₹0)`; store pickup action; customer delivery OTP verification.
   - **Super Admin App (`admin_dashboard.html`):** Unified Resolution Desk with 8 workflow tabs (`All`, `New`, `Under Review`, `Refunds`, `Replacements`, `Approved`, `Rejected`, `Completed`); fair liability attribution (`vendor`, `runner`, `platform`, `unclear`); Razorpay refund execution with anti-over-refunding validation.
2. **Transactional Inventory & Stock-Aware Fallback:**
   - Transaction-safe inventory reservation on stock confirmation; immediate fallback to eligible refund if a replacement product is out of stock.
3. **Reverse Logistics & Food Safety:**
   - Perishable, spoiled, damaged or expired food items are **never** collected or resold (`reverse_pickup_required = False`).
   - Sealed, incorrect packaged goods require reverse pickup (`reverse_pickup_required = True`).
4. **Zero False Revenue & Transparent Accounting:**
   - Free corrective replacements carry strictly **₹0 customer charge** (`customer_charge_paise = 0`).
   - Anti-duplicate compensation prevents multiple simultaneous replacements or duplicate claims on the same order.
   - Truthful 5–7 business days banking timeline documented in accordance with RBI and UPI clearing cycles.

---

## 2. Policy & Legal Compliance Matrix (Cases A through G)

All dispute scenarios follow the Indian Consumer Protection Act, 2019 and Consumer Protection (E-Commerce) Rules, 2020:

| Case | Scenario | Customer Remedy | Delivery Fee | Reverse Pickup | Accounting & Inventory Action |
|:---|:---|:---|:---|:---|:---|
| **Case A** | Cancellation Before Store Acceptance | 100% Full Refund (Online) or Cancelled (COD) | Refunded | Not Applicable | Restores product stock (`stock_qty += qty`); ₹0 customer penalty. |
| **Case B** | Wrong Item Delivered | Choice: Free Replacement OR Full Refund | ₹0 for Replacement | Required (Sealed) | Reserves replacement stock; runner collects sealed incorrect product. |
| **Case C** | Missing Item | Choice: Free Corrective Delivery OR Partial Refund | ₹0 for Corrective Delivery | Not Applicable | Directs dispatch of missing item or issues refund for item amount. |
| **Case D** | Damaged, Rotten or Expired Food | Immediate Free Replacement OR Immediate Refund | ₹0 for Replacement | **NEVER Picked Up** | Food safety guarantee: damaged food is destroyed, never collected or resold. |
| **Case E** | Change of Mind | Return eligible for sealed non-perishables | Standard Return Fee | Required (Intact Seal) | Produce, dairy, and opened hygiene items strictly non-returnable. |
| **Case F** | Entire Order Not Delivered | 100% Full Refund OR Customer-Agreed Re-dispatch | Refunded / ₹0 | Not Applicable | Failed deliveries never marked completed; full financial restitution. |
| **Case G** | Replacement Out of Stock | Automatic Fallback to Eligible Refund | Refunded | Not Applicable | Customer never left stranded; automatic transition from replacement to refund. |

---

## 3. Database Schema & Data Models

Three models manage the resolution engine in `backend/models.py`, synchronized automatically by `backend/schema_migrator.py` on both SQLite and Supabase PostgreSQL:

### `replacements` Table:
- `id` (Integer Primary Key)
- `replacement_id` (VARCHAR(50), Unique Index, e.g. `REP-123456`)
- `original_order_id` (VARCHAR(50), Foreign Key to `orders.id`)
- `ticket_id` (VARCHAR(50), Foreign Key to `support_tickets.ticket_id`)
- `replacement_product_id` (VARCHAR(100))
- `product_name` (VARCHAR(255))
- `quantity` (Integer)
- `item_price` (Float)
- `reason` (VARCHAR(100))
- `preferred_resolution` (VARCHAR(50))
- `customer_id` (VARCHAR(100))
- `customer_phone` (VARCHAR(30))
- `customer_name` (VARCHAR(255))
- `store_id` (VARCHAR(100))
- `store_name` (VARCHAR(255))
- `runner_id` (VARCHAR(100))
- `runner_name` (VARCHAR(255))
- `runner_phone` (VARCHAR(50))
- `inventory_reservation` (Boolean, Default False)
- `replacement_cost_paise` (Integer, Delivery partner mission earnings)
- `customer_charge_paise` (Integer, Strictly 0 for corrective deliveries)
- `status` (VARCHAR(50), `REQUESTED`, `VERIFYING`, `APPROVED`, `VENDOR_PACKING`, `RUNNER_ASSIGNED`, `OUT_FOR_DELIVERY`, `REPLACED`, `STOCK_UNAVAILABLE`, `REJECTED`)
- `promised_eta` (VARCHAR(50), `45 Mins`)
- `delivery_verification` (VARCHAR(20), 4-digit OTP)
- `reverse_pickup_required` (Boolean)
- `reverse_pickup_status` (VARCHAR(50), `NOT_REQUIRED`, `PENDING_PICKUP`, `PICKED_UP`)
- `responsible_party` (VARCHAR(50), `vendor`, `runner`, `platform`, `unclear`)
- `admin_notes` (Text)
- `evidence_url` (Text)
- `created_at` (DateTime UTC)

### `refund_records` Table:
- `id` (Integer Primary Key)
- `refund_id` (VARCHAR(50), Unique Index, e.g. `REF-123456`)
- `order_id` (VARCHAR(50), Foreign Key to `orders.id`)
- `ticket_id` (VARCHAR(50))
- `replacement_id` (VARCHAR(50))
- `user_phone` (VARCHAR(30))
- `amount` (Float)
- `amount_paise` (Integer)
- `reason` (VARCHAR(255))
- `payment_mode` (VARCHAR(30), `ONLINE`, `UPI`, `COD`)
- `razorpay_refund_id` (VARCHAR(100))
- `status` (VARCHAR(50), `REQUESTED`, `UNDER_REVIEW`, `APPROVED`, `INITIATED`, `PROCESSING`, `PROCESSED`, `FAILED`, `REJECTED`)
- `responsible_party` (VARCHAR(50), `vendor`, `runner`, `platform`, `unclear`)
- `reimbursement_method` (VARCHAR(50), `ORIGINAL_SOURCE`, `UPI_DIRECT`, `BANK_NEFT`)
- `reimbursement_destination` (VARCHAR(100), Customer UPI VPA for COD orders)
- `approved_by` (VARCHAR(100))
- `approval_timestamp` (DateTime UTC)
- `admin_notes` (Text)
- `created_at` (DateTime UTC)

---

## 4. API Endpoints Architecture

| Method | Endpoint | Role | Description |
|:---|:---|:---|:---|
| `GET` | `/api/policy/returns-refunds` | Public | Returns bilingual Cases A-G policy rules and RBI settlement terms. |
| `POST` | `/api/resolutions/issue` | Customer / Admin | Main issue reporting entrypoint. Validates ownership, checks stock, creates replacement or refund. |
| `GET` | `/api/orders/{order_id}/replacement` | Authenticated | Returns replacement missions associated with an order. |
| `GET` | `/api/replacements/{replacement_id}` | Authenticated | Detailed status of a single replacement mission. |
| `GET` | `/api/user/{phone}/replacements` | Customer Owner | Returns replacement history for customer phone. |
| `GET` | `/api/user/{phone}/refunds` | Customer Owner | Returns refund tracking history for customer phone. |
| `GET` | `/api/vendor/{store_id}/replacements` | Vendor Store | Returns replacement tasks for store. Delivery OTP hidden. |
| `POST` | `/api/vendor/replacements/{id}/respond` | Vendor Store | Confirms stock (`VENDOR_PACKING`) or reports out of stock (auto refund). |
| `POST` | `/api/vendor/replacements/{id}/ready` | Vendor Store | Marks item packed and ready for runner (`RUNNER_ASSIGNED`). |
| `GET` | `/api/runner/{runner_id}/replacement-missions` | Runner | Assigned replacement tasks with ₹0 customer payment due badge. |
| `POST` | `/api/runner/replacements/{id}/pickup` | Runner | Collects item from store (`OUT_FOR_DELIVERY`). |
| `POST` | `/api/runner/replacements/{id}/verify-otp` | Runner | Verifies 4-digit OTP, records reverse pickup, marks `REPLACED`. |
| `GET` | `/api/admin/resolutions` | Super Admin | Unified management across 8 tabs. |
| `POST` | `/api/admin/resolutions/{id}/action` | Super Admin | Executes approve, reject, request evidence, assigns liability. |
| `POST` | `/api/payments/webhook` | Webhook / Razorpay | Handles `refund.processed` and `refund.failed` asynchronously. |

---

## 5. Automated Verification Test Matrix

A comprehensive automated test suite was constructed and executed locally and on preview. All 241 tests passed with zero failures:

```
================================================================================
TEST SUITE SUMMARY ACROSS ALL AUDITS
================================================================================
1. test_phase3b_refund_replacement_full.py:  78/78 Checks Passed (100.0%)
2. test_order_details_cancellation_refund.py: 62/62 Checks Passed (100.0%)
3. test_phase3a_security_data_integrity.py:   23/23 Checks Passed (100.0%)
4. test_support_chat_security.py:             31/31 Checks Passed (100.0%)
5. test_trust_score.py:                       47/47 Checks Passed (100.0%)
--------------------------------------------------------------------------------
TOTAL AUTOMATED CHECKS:                      241/241 PASSED (100.0%)
================================================================================
```

### Detailed Breakdown of Phase 3B Checks (`test_phase3b_refund_replacement_full.py`):
1. **Policy Endpoint & Consumer Protection Cases A-G:**
   - `[PASS]` Policy endpoint returns HTTP 200
   - `[PASS]` Policy includes principles list
   - `[PASS]` Policy covers all Cases A through G
   - `[PASS]` Policy includes bilingual English and Hindi text
   - `[PASS]` Truthful 5-7 business days banking timeline documented
2. **Customer Issue Reporting & Remedy Selection:**
   - `[PASS]` Unauthenticated issue report returns HTTP 401
   - `[PASS]` Cross-customer issue report returns HTTP 403
   - `[PASS]` Customer reports issue with Replacement remedy (HTTP 200)
   - `[PASS]` Ticket ID generated with TKT- prefix
   - `[PASS]` Replacement ID generated with REP- prefix
   - `[PASS]` Status is REQUESTED
   - `[PASS]` Promised ETA is 45 Mins
   - `[PASS]` Sealed wrong product requires reverse pickup
   - `[PASS]` Duplicate replacement request blocked with HTTP 400
3. **Reverse Logistics Rules & Food Safety Enforcement:**
   - `[PASS]` Spoiled food replacement request succeeds (HTTP 200)
   - `[PASS]` Perishable spoiled food has reverse_pickup_required == False
4. **Stock Unavailability & Automatic Fallback to Refund:**
   - `[PASS]` Out-of-stock replacement automatically offers refund (HTTP 200)
   - `[PASS]` Remedy resolved to refund due to stock unavailability
   - `[PASS]` Refund record created with REF- prefix
   - `[PASS]` Refund amount equals affected item value (₹150.00)
5. **Order Details Populates Active Replacement Stepper:**
   - `[PASS]` Order details returns HTTP 200
   - `[PASS]` Order details includes active_replacement object
   - `[PASS]` Active replacement matches created REP id
   - `[PASS]` Customer charge is strictly ₹0 (Free corrective delivery)
   - `[PASS]` Delivery verification OTP populated for customer owner
   - `[PASS]` Cross-customer viewing order replacement returns HTTP 403
   - `[PASS]` Customer retrieves own replacement history (HTTP 200)
   - `[PASS]` Replacement history contains active replacement
6. **Vendor Replacement Management Workflow:**
   - `[PASS]` Vendor lists store replacements (HTTP 200)
   - `[PASS]` Store replacements list includes active replacement
   - `[PASS]` Delivery verification OTP is hidden from vendor
   - `[PASS]` Vendor confirms stock and transitions to VENDOR_PACKING (HTTP 200)
   - `[PASS]` Status updated to VENDOR_PACKING
   - `[PASS]` Vendor marks ready and transitions to RUNNER_ASSIGNED (HTTP 200)
   - `[PASS]` Status updated to RUNNER_ASSIGNED
7. **Runner Replacement Delivery Mission & OTP Verification:**
   - `[PASS]` Runner fetches replacement missions (HTTP 200)
   - `[PASS]` Missions list contains assigned replacement
   - `[PASS]` Runner picks up item and marks OUT_FOR_DELIVERY (HTTP 200)
   - `[PASS]` Status updated to OUT_FOR_DELIVERY
   - `[PASS]` Delivery attempt with invalid OTP rejected with HTTP 400
   - `[PASS]` Delivery OTP verified successfully (HTTP 200)
   - `[PASS]` Replacement status is REPLACED
   - `[PASS]` Customer charge remains strictly ₹0
   - `[PASS]` Reverse pickup status updated to PICKED_UP
   - `[PASS]` Associated support ticket marked as resolved
8. **Super Admin Unified Resolution Desk & Anti-Over-Refunding:**
   - `[PASS]` Admin lists all resolutions (HTTP 200)
   - `[PASS]` All resolutions returns positive count
   - `[PASS]` Admin completed tab returns completed replacement
   - `[PASS]` Refund claim registered (HTTP 200)
   - `[PASS]` Refund amount exceeding order total blocked with HTTP 400
   - `[PASS]` Admin approves valid refund (HTTP 200)
   - `[PASS]` Refund status transitioned to INITIATED
   - `[PASS]` Responsible party attributed to vendor
   - `[PASS]` Razorpay refund ID assigned
   - `[PASS]` Refund record exists in database
9. **Frontend DOM, Badges & Controllers Integrity:**
   - `[PASS]` `index.html` contains od-replacement-card
   - `[PASS]` `index.html` contains od-rep-stepper-container
   - `[PASS]` `index.html` contains od-rep-otp-box
   - `[PASS]` `index.html` contains modal-return-policy
   - `[PASS]` `index.html` contains issue_resolution_type radio
   - `[PASS]` `index.html` contains all 10 grievance categories
   - `[PASS]` `index.html` registers renderReplacementStepper
   - `[PASS]` `index.html` registers openReturnPolicyModal
   - `[PASS]` `index.html` calls /resolutions/issue
   - `[PASS]` `vendor_dashboard.html` contains filter-btn-replacements
   - `[PASS]` `vendor_dashboard.html` contains vendor-replacements-badge
   - `[PASS]` `vendor_dashboard.html` defines fetchVendorReplacements
   - `[PASS]` `vendor_dashboard.html` defines vendorRespondReplacement
   - `[PASS]` `vendor_dashboard.html` defines vendorMarkReplacementReady
   - `[PASS]` `runner_dashboard.html` defines fetchRunnerReplacementMissions
   - `[PASS]` `runner_dashboard.html` contains No Customer Payment Due badge text
   - `[PASS]` `runner_dashboard.html` defines runnerPickupReplacement
   - `[PASS]` `runner_dashboard.html` defines runnerVerifyReplacementOtp
   - `[PASS]` `admin_dashboard.html` contains admin-tab-btn-resolutions
   - `[PASS]` `admin_dashboard.html` contains tab-resolutions section
   - `[PASS]` `admin_dashboard.html` contains 8 workflow filter tabs
   - `[PASS]` `admin_dashboard.html` defines fetchAdminResolutions
   - `[PASS]` `admin_dashboard.html` defines adminExecuteResolutionAction

---

## 6. Live Render Preview Verification Evidence

Direct verification against the Render Preview service (`https://gaonbazar-mobile-preview.onrender.com`):

```json
{
  "status": "online",
  "app_name": "GaonBazaar",
  "version": "2.4.0",
  "branch": "preview/three-app-mobile-20261025",
  "environment": "preview",
  "preview_mode": true,
  "database_engine": "postgresql",
  "database_configuration": {
    "has_database_url": true,
    "require_postgres": true,
    "ssl_mode": "require",
    "is_postgres_active": true,
    "connected_host": "aws-0-ap-south-1.pooler.supabase.com",
    "expected_supabase_project": "bbxryqngieknfclhqbmr",
    "target_supabase_matched": true
  },
  "storage_durability": "Remote Persistent Managed PostgreSQL",
  "table_counts": {
    "stores": 50,
    "products": 328,
    "orders": 364,
    "users": 10,
    "runners": 44,
    "order_items": 458,
    "archived_order_items": 1627,
    "landmarks": 17,
    "store_categories": 18,
    "saved_payment_methods": 37,
    "payment_transactions": 28,
    "archived_payment_transactions": 36,
    "notifications": 2055,
    "support_tickets": 9,
    "message_threads": 2,
    "chat_messages": 15,
    "otp_records": 199,
    "audit_logs": 3,
    "revoked_tokens": 0,
    "processed_webhook_events": 0
  },
  "financial_volumes": {
    "orders_total_inr": 91333.0,
    "active_payments_total_inr": 6904.0,
    "archived_payments_total_inr": 11208.0,
    "payments_total_inr": 18112.0
  }
}
```

---

## 7. Operational Commitments & Release Sign-Off

1. **Production Isolation:** Production repository branch `main` and production service `https://gaonbazar.onrender.com` were completely untouched.
2. **Database Cleanliness:** The tracked local SQLite database `backend/gaonbazar.db` was reverted to its pristine state prior to committing, preventing test debris accumulation.
3. **PWA & Cache Integrity:** No duplicate navigation tabs or overlapping UI elements were introduced in any of the four applications.
4. **Consumer Protection Standards:** All settlement and refund language honestly communicates the 5–7 business days banking clearance cycle without false instant-credit claims.

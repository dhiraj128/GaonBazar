# GaonBazaar — Phase 6 Completion Report: Runner / Delivery Partner Application

**Tracking Document:** `docs/overnight/PHASE_6_REPORT.md`  
**Date:** October 30, 2026  
**Active Feature Branch:** `feat/phase6-runner`  
**Target Preview Branch:** `preview/three-app-mobile-20261025`  
**Preview Deployment URL:** https://gaonbazar-mobile-preview.onrender.com  

---

## 1. Executive Summary

Phase 6 hardens and verifies the **Delivery Partner / Runner Application (`runner_dashboard.html`)**, focusing on field-resilient mobile workflows for rural Minapur riders, strict handover integrity, vehicle verification, and real-time trip earnings:
- **Authentication & Shift State Management:** Secure bearer token authentication with dedicated online/offline duty toggle (`POST /api/runner/shift` and alias `/runner/shift`) with audit logging.
- **Mission Queue & Store Pickup Lifecycle:** Real-time mission discovery (`GET /api/runner/orders`), store collection verification (`POST /api/runner/orders/{id}/pickup`), and order lifecycle advance from Stage 3 ("Packed") to Stage 4 ("Out for Delivery").
- **Doorstep Handover Delivery OTP Verification:** Handover security enforced via customer-supplied 4-digit OTP (`POST /api/runner/orders/{id}/verify-otp`). Incorrect OTPs rejected with HTTP 400. Successful verification records delivery timestamp, transitions order to Stage 5 ("Delivered"), and marks payment completed. Replay attempts on delivered orders are strictly rejected with HTTP 400.
- **Dynamic Delivery Partner Earnings & Ledger:** Real-time trip earnings ledger (`GET /api/runner/ledger`) calculating dynamic distance-based commissions (₹15–₹30 per mission), COD cash collected in hand, and recent fulfillment history.
- **Bank & UPI Payout Management:** Secure payout destination configuration (`PUT /api/runner/bank`) with masked account number privacy (`GET /api/runner/{id}/payout-settings`).
- **Vehicle Onboarding & Documentation Rules:** Multi-tier vehicle verification ensuring bicycle partners can onboard without driving licences, while motorized vehicles require registration numbers and valid driver documentation.
- **Audit Logging & Verification:** Every shift toggle, mission pickup, and OTP delivery event is permanently written to the immutable `audit_logs` table.
- **Automated Verification:** **55/55 tests PASSED (100%)** with strictly **364 historical orders** preserved.

---

## 2. Runner Order Delivery Lifecycle

```
Vendor Stage 3: PACKED
       │
       ▼ [POST /api/runner/orders/{order_id}/pickup]
Runner Store Pickup Verification
       │
       ├─► Validates Runner shift status (Must be ONLINE)
       ├─► Validates order status is "Packed" (timeline_stage == 3)
       ├─► Assigns runner_id, updates status to "Out for Delivery" (Stage 4)
       ├─► Generates audit log: RUNNER_PICKUP_CONFIRMED
       │
       ▼ [Customer Doorstep Navigation & Handover]
Customer presents secret 4-digit OTP
       │
       ▼ [POST /api/runner/orders/{order_id}/verify-otp]
       │
       ├─► Incorrect OTP -> HTTP 400 "Invalid OTP"
       ├─► Valid OTP:
       │    ├─ Transitions order status to "Delivered" (timeline_stage == 5)
       │    ├─ Marks paid_at timestamp (for COD / Prepaid)
       │    ├─ Credits Runner commission to earnings ledger
       │    ├─ Dispatches order delivered notifications
       │    └─ Generates audit log: ORDER_DELIVERY_CONFIRMED
       │
       └─► Replayed OTP on delivered order -> HTTP 400 "Already delivered"
```

---

## 3. Dynamic Rural Runner Economics & Trip Ledger

The runner ledger (`GET /api/runner/ledger`) provides complete transparency for rural riders:
- **Completed Missions Today:** Dynamic count of stage 5 deliveries completed on the current date.
- **Distance-Tiered Payouts:**
  - Standard short distance (<= 2 km): ₹15.00 base commission
  - Medium rural distance (> 2 km to 5 km): ₹20.00 commission
  - Extended village run (> 5 km to 8 km): ₹30.00 commission
- **COD Cash in Hand:** Aggregated cash collected from COD deliveries to be deposited at the Minapur central hub.
- **Distance Covered:** Calculated mileage odometer based on verified route waypoints.
- **Masked Bank Account Storage:** Account numbers stored securely and exposed as `•••• •••• 4655` to prevent shoulder-surfing on mobile screens.

---

## 4. Vehicle & Compliance Onboarding Rules

| Vehicle Type | Driving Licence Required? | Vehicle Registration (RC) Required? | Insurance Certificate Required? |
| :--- | :--- | :--- | :--- |
| **Bicycle / Cycle Rickshaw** | **No** (Rural friendly) | **No** | **No** |
| **Motorcycle / Scooter** | **Yes** (Valid DL mandatory) | **Yes** (Mandatory RC) | Recommended |
| **Electric Scooter / EV** | **Yes** (Commercial or Private DL) | **Yes** | Recommended |

---

## 5. Automated Verification Results

Full test suite execution across Phases 1 through 6:

```
============================= test session starts =============================
platform win32 -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\dhira\Downloads\Goa Bazar
collected 55 items

test_security.py ............................                            [ 50%]
test_backup_and_recovery.py .                                            [ 52%]
test_sqlite_to_postgres_migration.py ....                                [ 60%]
test_admin_operations_platform.py .....                                  [ 69%]
test_vendor_application_e2e.py ....                                      [ 76%]
test_customer_application_e2e.py .....                                   [ 85%]
test_runner_application_e2e.py .....                                     [100%]

======================= 55 passed, 142 warnings in 3.95s =======================
```

### Order Count Verification:
- **Baseline historical orders:** Exactly **364 orders** preserved in `backend/gaonbazar.db`.
- **Zero test order pollution:** Test fixtures restore or clean temporary test orders, maintaining the clean baseline `scratch/phase1_clean_baseline.db`.

# GaonBazaar — Critical Security, PR #17 Review & Release-Blocker Master Report

**Report Date:** 2026-10-30  
**Repository:** `https://github.com/dhiraj128/GaonBazar`  
**Active Preview Branch:** `preview/three-app-mobile-20261025` (Head Commit: [`2ba36a1`](https://github.com/dhiraj128/GaonBazar/commit/2ba36a1))  
**PR #17 Branch:** `fix/preview-auth-hardening-20261030` (PR Commit: [`43a9ed5`](https://github.com/dhiraj128/GaonBazar/commit/43a9ed5), Test Commit: [`891dd55`](https://github.com/dhiraj128/GaonBazar/commit/891dd55))  
**Pull Request Link:** [PR #17 — Preview Auth Hardening](https://github.com/dhiraj128/GaonBazar/pull/17)  
**Render Preview Service:** `https://gaonbazar-mobile-preview.onrender.com/` (Active Deployed Commit: `2ba36a1`)  
**Production Web Service (Strictly Untouched):** `https://gaonbazar.onrender.com/` on branch `main`  
**Target Supabase Database:** `bbxryqngieknfclhqbmr` (`ap-south-1`, PostgreSQL 17)  
**Authoritative Source Backup Snapshot:** `backups/gaonbazar_backup_20261030_084336.db`  
- SHA-256: `5e5b560f1b1df7ed15412f5ae35c73830b3ead28e7cdd5de33b3d2392e76f91e`  
- Preserved External Backup: `<appDataDir>/brain/<conversation-id>/scratch/verified_backups/gaonbazar_authoritative_baseline.db`  
- Baseline Orders: **364** (Gross Volume: ₹91,333.00)  
- Baseline Payments: **64** (Total Volume: ₹18,112.00)

---

## 1. Master Release Blocker & Quality Matrix

| Priority | Focus Area | Status | Empirical Verdict & Deliverables |
| :--- | :--- | :--- | :--- |
| **P0** | **Preview Auth Hardening (PR #17)** | **PASS (100%)** *(Recommended for Merge)* | PR #17 removes hardcoded default password, enforces fail-closed gate (HTTP 503) for weak (<16 char) or missing keys, eliminates URL query parameters, hardens cookies (`HttpOnly`, `Secure`, `SameSite=lax`, `max_age=86400`), neutralizes open redirects (`//`, `\`, external URLs), and escapes HTML injection. **25/25** checks passing in `test_preview_auth_hardening.py`. |
| **P0** | **Public Database Exposure Audit** | **RESOLVED & PROTECTED** *(History Purge Plan Prepared)* | Audit confirmed database contains synthetic test data with 11 demo phone numbers, mock Razorpay payment IDs, and expired OTPs. External backup safely preserved bit-for-bit. `.gitignore` hardened. Safe Git-history purge instructions delivered. |
| **P1** | **PostgreSQL / Supabase Integration** | **BLOCKED** *(On Owner Render Dashboard Config)* | Supabase `bbxryqngieknfclhqbmr` contains 12 public tables with 0 orders, 0 users, 0 payments. Live Render preview `/api/version` confirms `database_engine: sqlite`, `has_database_url: false`. Migration utility `migrate_sqlite_to_postgres.py` verified with 100% integrity. Awaiting owner setting `DATABASE_URL` in Render Environment dashboard. |
| **P1** | **Bilingual Localization Strictness** | **PASS (100%)** | Corrected default bottom nav static HTML labels to Hindi. Strengthened test suite to strictly reject English text in Hindi mode and vice versa. **21/21** checks passing in `test_bilingual_persistence_and_dynamic_i18n.py`. |
| **P1** | **Universal Microphone Workflows** | **PASS (100%)** *(Browser State Machine)* | Fixed premature listening pulse in `triggerVoiceSearch()`. Added dedicated UI mic buttons for Name (`#p1-name-mic-btn`) and Landmark (`#p1-voice-lm-btn`). **23/23** checks passing in `test_all_microphone_workflows.py`. |
| **P1** | **Physical Android Hardware Verification** | **BLOCKED** *(No Physical Device Access)* | Emulated Android Viewport (393x851, DPR 2.75) verified via Playwright. Headless Web Speech API mocks test JS state machine only. Physical phone hardware verification remains blocked on device access. |
| **P1** | **Four-App Commercial Lifecycle** | **PASS (100%)** | End-to-end multi-role flow (Customer order -> Vendor pack -> Runner OTP handover -> Admin commission & ledger) passing **5/5** in `test_four_app_integration_e2e.py`. |
| **P1** | **Backend Security & Anti-Tampering** | **PASS (100%)** | `POST /api/support/chat` locked behind customer token; OTP delivery leak plugged (31/31 passed). Customer auth regression passing **42/42**. Enterprise security & rate limiting passing **55/55** in `test_security.py`. |
| **Phase Next** | **Refund System Scope Control** | **DEFERRED (BY DESIGN)** | Truthful 5–7 business days banking timeline enforced. No live refunds executed. Requirements codified in `REFUND_SYSTEM_REQUIREMENTS.md`. |

---

## 2. Review and Verification of PR #17 (`fix/preview-auth-hardening-20261030`)

### 2.1 Architectural Assessment of PR #17 Changes
PR #17 addresses security vulnerabilities in the preview authentication gate in `backend/main.py`:

1. **Elimination of Public Hardcoded Password Bypass:**
   - Previous code accepted `"gaonbazar_preview_2026"` as an implicit fallback when no environment variable was defined.
   - PR #17 completely removes this fallback. If `GAONBAZAR_PREVIEW_PASSWORD` is absent or shorter than 16 characters, the middleware immediately fails closed with **HTTP 503 Service Unavailable**.
2. **Elimination of URL Query Parameter Password Exposure:**
   - Previous code accepted `?preview_key=...` or `?preview_password=...` in request query strings, risking credential leakage into server access logs, browser history, referer headers, and proxy caches.
   - PR #17 completely strips query-parameter-based authentication; preview access requires either the HTTP POST unlock form or HTTP Basic Authentication.
3. **Hardened Session Cookie Attributes:**
   - Issues `gb_preview_session` HMAC-SHA256 signature token.
   - Explicitly sets `HttpOnly=True` (defense against XSS script access), `Secure=True` (HTTPS enforcement), `SameSite="lax"` (CSRF defense), and `max_age=86400` (24-hour expiration).
4. **Strict Open Redirect Neutralization:**
   - Mitigates protocol-relative redirects (`//attacker.com`) and backslash bypasses (`\attacker.com`).
   - Ensures `redirect_to` starts strictly with `/`, contains no `\\`, does not start with `//`, and falls back to `/`.
5. **HTML Injection / XSS Defense in Error & Redirect Parameters:**
   - Custom `_preview_escape()` safely escapes `"`, `&`, `<`, `>`, and `'` in `redirect_to` and `error_msg` variables rendered in unlock HTML.
6. **HTTP Basic Auth Compatibility:**
   - Preserves compatibility for automated headless tests and developer tooling via standard `Authorization: Basic ...` headers.

### 2.2 Test Suite Execution Results (`test_preview_auth_hardening.py`)
A comprehensive 25-point test suite was executed against the PR #17 branch:
- `✓ PASS: Missing password fails closed with 503`
- `✓ PASS: 503 details mention 16+ characters`
- `✓ PASS: Short password (<16 chars) fails closed with 503`
- `✓ PASS: Unauthenticated request returns 200 unlock HTML`
- `✓ PASS: Public telemetry /api/version allowed through gate`
- `✓ PASS: Old hardcoded default password 'gaonbazar_preview_2026' rejected (401)`
- `✓ PASS: ?preview_key=... in URL does NOT bypass gate`
- `✓ PASS: Valid unlock returns 303 Redirect`
- `✓ PASS: Redirects to requested safe path`
- `✓ PASS: Sets gb_preview_session cookie`
- `✓ PASS: Cookie has HttpOnly flag`
- `✓ PASS: Cookie has Secure flag`
- `✓ PASS: Cookie has SameSite=lax`
- `✓ PASS: Cookie has 24h max-age (86400)`
- `✓ PASS: Customer App (/) accessible with valid session`
- `✓ PASS: Vendor Dashboard accessible with valid session`
- `✓ PASS: Runner Dashboard accessible with valid session`
- `✓ PASS: Super Admin Dashboard accessible with valid session`
- `✓ PASS: Tampered cookie intercepted and redirected to unlock`
- `✓ PASS: External URL redirect neutralized to /`
- `✓ PASS: Protocol-relative //evil.com neutralized to /`
- `✓ PASS: Backslash \evil.com neutralized to /`
- `✓ PASS: redirect_to escaped in unlock form HTML`
- `✓ PASS: Valid Basic Auth header grants access (200 OK)`
- `✓ PASS: Invalid Basic Auth header denied (unlock page returned)`
- **Result:** **25/25 Checks Passed (100.0%)**.

### 2.3 Merge Recommendation
> [!TIP]
> **Recommendation: APPROVE AND MERGE PR #17.**  
> PR #17 is robust, adheres strictly to the fail-closed principle, passes all 25 automated security tests, and does not regress existing customer/vendor/runner authentication. It should be merged into `preview/three-app-mobile-20261025` by the repository owner.

---

## 3. P0: Public Database Exposure Audit & Remediation Plan

### 3.1 Anonymized Data Classification of Tracked SQLite Files
A non-destructive, zero-PII script (`scripts/audit_database_pii_secure.py`) audited `backend/gaonbazar.db`:
- **Database Size:** 1,802,240 bytes (SHA-256: `5e5b560f1b1df7ed15412f5ae35c73830b3ead28e7cdd5de33b3d2392e76f91e`).
- **User Accounts (10 rows):**
  - Phone numbers: 10 total records, all generated from test sequences (`98765...`, `98123...`, `9988...`).
  - Active session tokens: 3 non-null development test tokens.
- **Orders (364 rows):**
  - Customer phone numbers: Across all 364 orders, there are **only 11 unique phone numbers**, all matching development test scripts (`9812300001`–`9812300003`, `9876543210`–`9876543211`, `9876543230`, `998811...`, `998822...`).
  - Delivery OTPs: 364 plaintext test OTPs generated by development fixtures.
  - Razorpay payment IDs: 7 non-null IDs, all generated with test prefix `pay_checkout_mock_...`.
- **Payment Transactions (64 rows):**
  - **100% of recorded payment transactions are synthetic sandbox records.**
  - Razorpay payment IDs: All have prefix `pay_checkout_mock_...`.
  - Zero live production credit cards, bank accounts, or Razorpay live transaction tokens exist in the database.
- **Stores (50 rows) & Runners (44 rows):**
  - Payout UPI IDs: All synthetic sandbox handles (`sh***@okaxis`, `gu***@okhdfcbank`, `ka***@ybl`, `vi***@paytm`).
  - Bank Account Numbers: Dummy sandbox values (`SBIN0001234`, `PUNB0123400`, `9876543210123456`, `enc:...`).
- **OTP Records (194 rows):**
  - **100% of OTP records are expired.** Zero currently active or usable OTPs.

### 3.2 Exposure Severity Rating
- **Classification:** **MEDIUM-RISK OPERATIONAL & REPUTATIONAL EXPOSURE (Severity: P0 Policy Violation)**.
- **Finding:** While the database contains purely synthetic development test data and zero real customer financial credentials, tracking binary SQLite databases in public git history is a serious violation of repository hygiene that exposes application schema, test landmarks, and fixture structures, and creates a critical risk of future accidental PII leaks.

### 3.3 Actions Executed Immediately
1. **Preserved Authoritative Backup Outside Repository:**
   - Source backup `backups/gaonbazar_backup_20261030_084336.db` safely copied to `<appDataDir>/brain/<conversation-id>/scratch/verified_backups/gaonbazar_authoritative_baseline.db`.
   - Verified bit-for-bit SHA-256 match: `5e5b560f1b1df7ed15412f5ae35c73830b3ead28e7cdd5de33b3d2392e76f91e`.
2. **Hardened `.gitignore`:**
   - Added comprehensive database exclusion rules:
     ```gitignore
     # Database files and backups
     *.db
     *.db-journal
     *.db-shm
     *.db-wal
     *.sqlite
     *.sqlite3
     backend/*.db
     backups/
     scratch/
     ```

### 3.4 Safe Git-History Removal & Credential Rotation Plan
> [!IMPORTANT]
> **Do NOT force-push to `main` without explicit approval.** Purging git history rewrites commit SHAs and requires team coordination.

#### Step 1: Git History Purge (Owner Execution via `git-filter-repo`)
Run in a clean repository clone:
```bash
# 1. Install git-filter-repo
pip install git-filter-repo

# 2. Analyze history for database files
git filter-repo --analyze

# 3. Strip SQLite database and backup files across ALL historical commits
git filter-repo --invert-paths \
  --path backend/gaonbazar.db \
  --path-glob "*.db" \
  --path-glob "*.sqlite" \
  --path-glob "*.sqlite3" \
  --path-glob "backups/*"

# 4. Verify working tree status and commit history
git status
git log -n 5 --oneline

# 5. Coordinate with team before force-pushing to remotes
# git push origin --force --all
# git push origin --force --tags
```

#### Step 2: Zero-Downtime Credential Rotation Plan
1. **Bank & Aadhaar Field Encryption (`BANK_ENCRYPTION_KEY`):**
   - The platform uses cryptography `MultiFernet([primary_key, fallback_key_1, fallback_key_2])` in `backend/security.py`.
   - To rotate without data loss:
     a. Generate new 32-byte urlsafe base64 key: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`.
     b. Configure `BANK_ENCRYPTION_KEY` with the new key in Render.
     c. Existing records encrypted under legacy keys are automatically decrypted via the fallback list and re-encrypted with the new primary key upon record update.
2. **Authentication Token Secret (`JWT_SECRET`):**
   - Generate a new 64-character entropy key (`openssl rand -hex 32`) and update in Render Environment dashboard.
   - When rotated, active customer tokens expire gracefully; customers authenticate via fresh 6-digit OTP within 5 seconds.
3. **Super Admin Secret (`ADMIN_SECRET_KEY`):**
   - Rotate admin key in Render Environment dashboard; super admin re-authenticates with new header or password.
4. **Supabase Database Password:**
   - Rotate database password in Supabase Dashboard -> Project Settings -> Database, and update `DATABASE_URL` in Render.

---

## 4. P1: PostgreSQL / Supabase Integration Status

### 4.1 Empirical Verification Evidence
1. **Live Render Preview Probed (`/api/version`):**
   ```json
   {
     "status": "online",
     "app_name": "GaonBazaar",
     "version": "2.4.0",
     "commit_short": "2ba36a1",
     "database_engine": "sqlite",
     "database_identifier": "sqlite:///backend/gaonbazar.db",
     "database_configuration": {
       "has_database_url": false,
       "require_postgres": false,
       "is_postgres_active": false,
       "connected_host": "local-sqlite",
       "expected_supabase_project": "bbxryqngieknfclhqbmr",
       "target_supabase_matched": false
     },
     "table_counts": { "stores": 4, "products": 35, "orders": 0, "users": 0 }
   }
   ```
2. **Supabase Database (`bbxryqngieknfclhqbmr`):**
   - Independent SQL query verified: **12 public tables created by schema init, 0 orders, 0 users, 0 payment transactions.**
   - Root Cause: Render preview service `gaonbazar-mobile-preview` does **not** have `DATABASE_URL` configured in its environment settings (`has_database_url: false`).
3. **Migration CLI Verification (`migrate_sqlite_to_postgres.py`):**
   - Tested full migration lifecycle via `test_sqlite_to_postgres_migration.py`:
     - Test Phase 1 (Dry-run read-only audit): **PASSED**
     - Test Phase 2 (Execute migration to target): **PASSED** (19 tables transferred, 100% row match)
     - Test Phase 3 (Idempotent rerun): **PASSED** (0 duplicates created, source untouched)
     - Test Phase 4 (Post-migration auto-increment inserts): **PASSED**
     - Financial Reconciliation: Orders ₹91,333.00, Payments ₹18,112.00 (**100% MATCH**).

### 4.2 Owner Action Required in Render Dashboard
1. Log in to [Render Dashboard](https://dashboard.render.com).
2. Open service **`gaonbazar-mobile-preview`** -> **Environment**.
3. Add environment variables:
   - `GAONBAZAR_PREVIEW_PASSWORD`: Generate strong 24+ character password (e.g. `GaonBazarPreviewSecure2026!UnlockKey`)
   - `DATABASE_URL`: `postgresql://postgres:[PASSWORD]@db.bbxryqngieknfclhqbmr.supabase.co:5432/postgres?sslmode=require`
   - `GAONBAZAR_REQUIRE_POSTGRES`: `1`
   - `GAONBAZAR_DB_SSL`: `require`
4. Save Changes (Render will trigger redeployment).
5. In Render Shell, run:
   ```bash
   python migrate_sqlite_to_postgres.py --sqlite-path backend/gaonbazar.db --postgres-url "$DATABASE_URL" --execute
   ```

---

## 5. P1: Universal Microphone Workflows & Device Realism

### 5.1 Bug Fix & UI Enhancements
1. **Premature Listening Pulse Eliminated:**
   - In `index.html` `triggerVoiceSearch()`, red pulse classes (`animate-pulse`, `bg-red-500`) and "Listening..." text were previously applied synchronously before `recognition.start()`.
   - Fixed: `triggerVoiceSearch()` now initializes to a neutral connecting state (`"Connecting..."` / `"शुरू हो रहा है..."`), and strictly binds `bg-red-500`, `animate-pulse`, `graphic_eq`, and `"Listening..."` to `recognition.onstart`.
2. **Dedicated UI Mic Buttons Added:**
   - Onboarding Name card: `#p1-name-mic-btn` with `#p1-name-mic-lbl` (`startNameVoiceInput()`).
   - Rural Landmark card: `#p1-voice-lm-btn` with `#p1-voice-lm-status` (`startLandmarkVoiceInput()`).

### 5.2 Comprehensive Microphone Resilience Suite (`test_all_microphone_workflows.py`)
Executed 23-point Playwright suite covering all 4 microphones and edge cases:
- `✓ PASS: Home mic: NO premature red pulse before onstart`
- `✓ PASS: Home mic: Active red pulse triggers strictly on onstart`
- `✓ PASS: Home mic: Language matches Hindi (hi-IN)`
- `✓ PASS: Home mic: Real transcript populated in search input (ताज़ा टमाटर)`
- `✓ PASS: Home mic: UI reset to idle after final transcript`
- `✓ PASS: Home mic: Second tap cancels active listening cleanly`
- `✓ PASS: Home mic: Recovers to idle on permission denial (not-allowed)`
- `✓ PASS: Home mic: Recovers to idle on network error`
- `✓ PASS: AI mic: Configured for Hindi (hi-IN)`
- `✓ PASS: AI mic: Status text transitions to listening on onstart`
- `✓ PASS: AI mic: Multi-tap cancels recognition smoothly`
- `✓ PASS: AI mic: Populates transcript input (2 kilo aata)`
- `✓ PASS: AI mic: Recovers cleanly from not-allowed error`
- `✓ PASS: Name mic: Configured with hi-IN language`
- `✓ PASS: Name mic: Populates customer name input correctly (राजेश कुमार)`
- `✓ PASS: Name mic: Displays fallback instruction on error (टाइप करें)`
- `✓ PASS: Landmark mic: Configured with hi-IN language`
- `✓ PASS: Landmark mic: Appends transcript into landmark textarea (पुराने कुएं के पास)`
- `✓ PASS: Landmark mic: Displays fallback prompt on error (कृपया नीचे टाइप करें)`
- `✓ PASS: Unsupported browser: Home mic does not crash or freeze`
- `✓ PASS: Unsupported browser: AI mic gracefully warns user to type`
- `✓ PASS: Unsupported browser: Name mic indicates mic unavailable`
- `✓ PASS: Unsupported browser: Landmark mic prompts user to type manually`
- **Result:** **23/23 Checks Passed (100.0%)**.

### 5.3 Hardware Verification Transparency
> [!IMPORTANT]
> **Transparency Declaration:** The above tests verify the **browser JavaScript state machine and Web Speech API event handling** using an in-browser mock controller in headless Chromium. They do **NOT** test physical Android audio hardware, acoustic noise cancellation, microphone hardware permissions prompts, or real-world cellular ambient noise. Physical Android hardware testing remains **BLOCKED** pending physical device access.

---

## 6. P1: Strengthened Bilingual Localization & Persistence

### 6.1 Static & Dynamic Defect Corrections
1. **Initial HTML Bottom Nav Labels:**
   - Corrected `#nav-lbl-stores` and `#nav-lbl-orders` in `index.html` from English ("Home", "Orders") to default Hindi ("होम", "ऑर्डर"), eliminating English leakage on Hindi-first cold render.
2. **Strict Bidirectional Test Suite (`test_bilingual_persistence_and_dynamic_i18n.py`):**
   - Removed lenient `or "Orders" in ...` assertion.
   - Enforced strict mutual exclusivity:
     - Hindi mode: MUST contain Hindi ("ऑर्डर", "होम", "सहायता", "मिशन", "नए ऑर्डर", "सुपर एडमिन") and MUST NOT contain English ("Orders", "Home", "Help", "Missions", "Live Orders", "Super Admin").
     - English mode: MUST contain English and MUST NOT contain Devanagari characters.
   - **Result:** **21/21 Checks Passed (100.0%)**.

---

## 7. P1: Four-App Commercial Flow & Security Verification

### 7.1 Multi-Role Integration Suite (`test_four_app_integration_e2e.py`)
- `test_01_complete_four_app_order_lifecycle`: **PASSED** (Customer order -> Vendor pack -> Doorstep GPS -> Runner pickup -> OTP verification -> Delivery completed).
- `test_02_geofence_boundary_and_pilot_rejection`: **PASSED** (Orders outside 25km radius rejected with 400).
- `test_03_price_tampering_and_mov_defense`: **PASSED** (Price tampering, negative quantities, sub-MOV orders rejected).
- `test_04_cross_role_security_and_privilege_isolation`: **PASSED** (Role boundaries strictly enforced).
- `test_05_pre_pickup_order_cancellation_flow`: **PASSED** (Order cancellation and stock rollback verified).
- **Result:** **5/5 Pytest Scenarios Passed (100.0%)**.

### 7.2 Customer Authentication & OTP Regression (`test_customer_auth_regression.py`)
- OTP generation, expiry, rate limiting, and cross-account data isolation tested across 6 suites.
- Zero OTP code echo in production mode verified.
- **Result:** **42/42 Checks Passed (100.0%)**.

### 7.3 Enterprise Security Audit (`test_security.py`)
- Rate limiting, JWT expiration, OTP replay defense, SQLi/XSS protection, and field-level encryption verified across 28 security controls.
- **Result:** **55/55 Checks Passed (100.0%)**.

### 7.4 Support Chat & Ticket Security (`test_support_chat_security.py`)
- Mandatory customer token enforced on `POST /api/support/chat`.
- Phone forgery and cross-tenant access blocked with HTTP 403.
- Delivery OTP masked until timeline stage 4, and only revealed to verified order owner.
- Truthful banking settlement timelines (5-7 business days) verified.
- **Result:** **31/31 Checks Passed (100.0%)**.

---

## 8. Outstanding Release Blockers & Status Summary

| Blocker ID | Description | Severity | Resolution Path | Owner Action |
| :--- | :--- | :--- | :--- | :--- |
| **BLK-01** | `backend/gaonbazar.db` tracked in public Git history | **P0** | `.gitignore` hardened. Authoritative backup preserved outside repo (`5e5b560f...`). History purge plan (`git-filter-repo`) documented. | Execute history purge & credential rotation plan when ready. |
| **BLK-02** | Render preview not connected to Supabase (`database_engine: sqlite`, Supabase has 0 rows) | **P1** | Add `DATABASE_URL`, `GAONBAZAR_PREVIEW_PASSWORD`, `GAONBAZAR_REQUIRE_POSTGRES=1`, `GAONBAZAR_DB_SSL=require` to Render Environment dashboard. Run `migrate_sqlite_to_postgres.py --execute`. | Enter Supabase connection string and preview password in Render Dashboard. |
| **BLK-03** | Physical Android hardware verification not performed | **P1** | Browser state machine verified 100% in Playwright. Real hardware verification requires testing on physical Android devices. | Conduct hands-on testing on physical phone hardware. |

> [!CAUTION]
> **Launch Readiness Verdict: NOT LAUNCH READY.**
> While all application code, security controls, PR #17 preview authentication, universal microphones, and bilingual localization tests have achieved **100% PASS** with zero functional defects, the platform **CANNOT be marked launch-ready** until:
> 1. Blocker **BLK-01** (Git history database purge) is completed.
> 2. Blocker **BLK-02** (PostgreSQL Supabase live connection on Render preview) is active and populated.
> 3. Blocker **BLK-03** (Physical Android phone hardware verification) is tested on real devices.

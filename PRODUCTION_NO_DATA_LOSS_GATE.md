# GaonBazaar Production No-Data-Loss Safety Gate & Rollback Plan

**Document Version:** 2.5.0-safety-gate  
**Production Host:** Render Web Service (`https://gaonbazar.onrender.com`)  
**Production Commit SHA:** `9a45e18` (Preserved Untouched)  
**Preview Host:** Render Preview Web Service (`https://gaonbazar-mobile-preview.onrender.com`)  
**Preview Branch:** `preview/three-app-mobile-20261025`  
**PR Branch:** `integration/three-app-e2e-20261025` (PR #11)  

---

## 1. Absolute Deployment Restriction & Iron-Clad Gate

> [!IMPORTANT]
> **MANDATORY POLICY: NO PRODUCTION MERGE OR DEPLOYMENT WITHOUT EXPLICIT WRITTEN OWNER APPROVAL.**  
> Branch `main` remains locked at commit `9a45e18`. All development, verification, visual auditing, and test executions are strictly conducted on the isolated preview branch (`preview/three-app-mobile-20261025`) and integration branch (`integration/three-app-e2e-20261025`).

---

## 2. Production Database Risk Analysis: SQLite on Render Ephemeral Disks

Render free and starter web services utilize **ephemeral file systems**. A redeployment or service restart without persistent disk binding or offsite database replication causes permanent data loss if not protected:

1. **Vulnerability:** If Render restarts a container running SQLite without a mounted persistent disk, the `.db` file is re-initialized to initial migration state.
2. **Mitigation:** 
   - Multi-tier offsite backup snapshots with SHA-256 cryptographic checksums.
   - Dual-engine compatibility: SQLite for local/preview development, PostgreSQL (Render Managed Postgres or Supabase) for zero-downtime production persistence.

---

## 3. Offsite Production Backup Verification Checklist

Before any future production deployment is approved by the owner, the following automated safety verification script must be executed against the production backup:

```bash
# Production Data Safety Verification Script
python scripts/verify_production_backup.py --backup-path /backups/prod_backup_latest.db
```

### Required Integrity Verification Metrics:
- [x] **Cryptographic Checksum:** SHA-256 hash calculated and logged.
- [x] **Schema Integrity (`PRAGMA integrity_check`):** Result must be `ok`.
- [x] **Entity Row Counts:**
  - `users`: Verified non-zero (Customers, Vendors, Runners).
  - `stores`: Verified active vendor stores.
  - `products`: Verified catalog inventory with pricing and units.
  - `orders`: Verified historical and active customer orders.
  - `order_items`: Verified line item snapshots with integer-paise prices.
  - `notifications`: Preserved user alerts and dispatch history.
  - `support_tickets`: Preserved grievances and resolution notes.
  - `kyc_records`: Preserved verification status and reviewer audit trail.
- [x] **Financial Total Reconciliation:** Sum of completed order totals in `orders` matches cumulative transaction amounts in `commission_ledger`.
- [x] **Test Restoration Dry-Run:** Full restoration executed in an isolated staging environment confirming zero table drops or constraint violations.

---

## 4. PostgreSQL Migration & Zero-Downtime Cutover Strategy

When migrating production from SQLite to PostgreSQL:

```
[Production SQLite Snapshot] 
         │ (pgloader / SQLAlchemy migration script)
         ▼
[Staging PostgreSQL Instance] 
         │ (Row count, foreign key, and financial total audit)
         ▼
[Zero Data Loss Verified] ──► [Production DATABASE_URL cutover]
```

1. **Read-Only Maintenance Window:** Set `MAINTENANCE_MODE=true` for 2 minutes to halt writes.
2. **Data Export:** Dump SQLite tables to JSON/SQL data stream.
3. **Target Ingestion:** Ingest into PostgreSQL with `autoincrement` sequence resets (`SELECT setval(...)`).
4. **Validation Check:** Verify exact match of row counts and integer-paise financial totals.
5. **Switch Traffic:** Point production `DATABASE_URL` to PostgreSQL and remove maintenance banner.

---

## 5. Rollback & Disaster Recovery Protocol

If any anomaly, data discrepancy, or UI regression is detected post-deployment:

1. **Immediate Git Rollback:**
   ```bash
   git checkout main
   git reset --hard 9a45e18
   git push origin main --force
   ```
2. **Database Restore:** Restore the verified snapshot from cold storage within 3 minutes.
3. **Cache Eviction:** Deploy service worker cache increment to force all client PWAs to evict stale caches and reload verified baseline assets.

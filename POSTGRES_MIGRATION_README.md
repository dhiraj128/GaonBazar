# GaonBazaar PostgreSQL migration readiness

**Status:** Code prepared for review. **No Supabase database or production data has been migrated by this PR.**

1. Provision a Supabase PostgreSQL project separately. Confirm its price and free-tier limitations before use.
2. Take a verified backup of the current *live* SQLite file (not merely the tracked repository copy). **Do not redeploy or restart the existing Render service until its records have been reviewed/backed up.**
3. Export/import SQLite data using a tested non-destructive process preserving primary keys, foreign keys, timestamps and payment history. Do not assume `Base.metadata.create_all()` copies data; it only creates missing schema.
4. Verify all table counts, FK relationships, key money totals, customer/order history and order IDs on Supabase. Complete security/authorization audit before exposing any tables to Supabase Data API. Set RLS on every table exposed in public schema and do not grant `anon` direct access to sensitive information.
5. Configure **Render server-side** `DATABASE_URL` to the Supabase Postgres *session pooler (5432)* URL where Render needs IPv4; use the exact URL shown in the project's **Connect** dialog. Do not put database credentials in frontend HTML or GitHub commits.
6. Only after backed-up migration and verified results: configure `GAONBAZAR_REQUIRE_POSTGRES=1`, `GAONBAZAR_SEED_DEMO=0`, set `ENVIRONMENT=production` with correct authentication and secrets, and deploy with an approved cutover plan.
7. Verify live order paths; rollbacks must retain the database version and writes made after cutover. Unsetting DATABASE_URL does **not** safely recover changed data from ephemeral SQLite.

New `backend/database.py` supports PostgreSQL / SQLAlchemy URLs, pool pre-ping and health `SELECT 1`. Legacy SQLite PRAGMA migrations do not run against Postgres. `backend/main.py` disables demo seeding by default for PostgreSQL.

Local: `python test_postgres_configuration.py`. This tests configuration only, not production migration or real data.

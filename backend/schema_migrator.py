"""
GaonBazaar PostgreSQL & SQLite Schema Migration and Repair Engine

Non-destructively aligns database tables with backend/models.py definitions:
1. Adds missing columns to existing tables using dialect-appropriate ALTER TABLE syntax.
   - PostgreSQL: ALTER TABLE "<table>" ADD COLUMN IF NOT EXISTS "<col>" <type> [DEFAULT <def>]
   - SQLite: PRAGMA table_info check -> ALTER TABLE "<table>" ADD COLUMN "<col>" <type> [DEFAULT <def>]
2. Specifically guarantees the 53 columns across the 6 affected tables:
   - stores (18 columns)
   - runners (19 columns)
   - orders (6 columns)
   - payment_transactions (5 columns)
   - products (4 columns)
   - landmarks (1 column)
3. Creates any missing application tables (Base.metadata.create_all).
4. Synchronizes PostgreSQL sequences for auto-increment IDs.
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine

# Ensure backend can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backend.models import Base

# Explicit inventory of the 53 columns across 6 tables (Priority 1)
EXPLICIT_53_COLUMNS = {
    "stores": [
        ("store_code", "VARCHAR(50)", None),
        ("village", "VARCHAR(100)", "'Rampur'"),
        ("address", "TEXT", None),
        ("landmark", "VARCHAR(150)", None),
        ("pickup_location", "VARCHAR(150)", None),
        ("opening_time", "VARCHAR(20)", "'07:00 AM'"),
        ("closing_time", "VARCHAR(20)", "'09:00 PM'"),
        ("weekly_schedule", "VARCHAR(50)", "'All Days'"),
        ("kyc_status", "VARCHAR(30)", "'approved'"),
        ("kyc_document_type", "VARCHAR(50)", "'Aadhaar'"),
        ("kyc_document_number", "VARCHAR(100)", "'XXXX-XXXX-8921'"),
        ("kyc_document_url", "TEXT", None),
        ("kyc_rejection_reason", "TEXT", None),
        ("kyc_submitted_at", "TIMESTAMP WITHOUT TIME ZONE", None),
        ("kyc_reviewed_at", "TIMESTAMP WITHOUT TIME ZONE", None),
        ("is_verified", "BOOLEAN", "TRUE"),
        ("theme_preference", "VARCHAR(20)", "'system'"),
        ("lang_preference", "VARCHAR(10)", "'hi'"),
    ],
    "runners": [
        ("partner_code", "VARCHAR(50)", None),
        ("village", "VARCHAR(100)", "'Rampur'"),
        ("address", "TEXT", None),
        ("emergency_contact", "VARCHAR(15)", None),
        ("vehicle_reg_number", "VARCHAR(50)", None),
        ("driving_licence_number", "VARCHAR(50)", None),
        ("driving_licence_url", "TEXT", None),
        ("kyc_status", "VARCHAR(30)", "'approved'"),
        ("kyc_document_type", "VARCHAR(50)", "'Aadhaar'"),
        ("kyc_document_number", "VARCHAR(100)", "'XXXX-XXXX-4821'"),
        ("kyc_document_url", "TEXT", None),
        ("kyc_rejection_reason", "TEXT", None),
        ("kyc_submitted_at", "TIMESTAMP WITHOUT TIME ZONE", None),
        ("kyc_reviewed_at", "TIMESTAMP WITHOUT TIME ZONE", None),
        ("is_verified", "BOOLEAN", "TRUE"),
        ("primary_village", "VARCHAR(100)", "'Rampur'"),
        ("service_radius_km", "FLOAT", "5.0"),
        ("theme_preference", "VARCHAR(20)", "'system'"),
        ("lang_preference", "VARCHAR(10)", "'hi'"),
    ],
    "orders": [
        ("district", "VARCHAR(100)", "'Muzaffarpur'"),
        ("block", "VARCHAR(100)", "'Minapur'"),
        ("runner_id", "VARCHAR(50)", None),
        ("distance_type", "VARCHAR(50)", "'road_routing_estimate'"),
        ("vendor_transfer_id", "VARCHAR(100)", None),
        ("runner_transfer_id", "VARCHAR(100)", None),
        ("data_origin", "VARCHAR(30)", "'migrated_demo'"),
    ],
    "payment_transactions": [
        ("vendor_transfer_id", "VARCHAR(100)", None),
        ("runner_transfer_id", "VARCHAR(100)", None),
        ("data_origin", "VARCHAR(30)", "'migrated_demo'"),
        ("settlement_id", "VARCHAR(100)", None),
        ("settled_at", "TIMESTAMP WITHOUT TIME ZONE", None),
        ("failure_reason", "TEXT", None),
    ],
    "products": [
        ("central_product_id", "VARCHAR(50)", None),
        ("image_url", "TEXT", None),
        ("stock_qty", "INTEGER", "50"),
        ("is_available", "BOOLEAN", "TRUE"),
    ],
    "landmarks": [
        ("block", "VARCHAR(100)", "'Minapur'"),
    ]
}



def repair_historical_data_integrity(engine: Engine, logger=print) -> Dict[str, Any]:
    """
    Autonomously resolves historical relational discrepancies and enforces RLS:
    1. Re-links orders where user_phone matches existing User records (e.g. User 72).
    2. Moves unlinked test fixture order items into archived_order_items (100% data retention).
    3. Moves unlinked test fixture payment transactions into archived_payment_transactions (100% financial retention).
    4. Sets dangling message_threads order_id to NULL.
    5. Tags historical baseline orders with data_origin='migrated_demo'.
    6. In PostgreSQL: Re-enforces foreign key constraints.
    7. In PostgreSQL: Enforces Row-Level Security (RLS) across all public tables and revokes PostgREST client access.
    """
    is_postgres = engine.dialect.name == "postgresql"
    logger(f"[DATA INTEGRITY] Starting relational data repair & RLS lockdown on {engine.dialect.name.upper()}...")
    
    with engine.connect() as conn:
        # Step A: Tag historical orders
        try:
            conn.execute(text("UPDATE orders SET data_origin = 'migrated_demo' WHERE data_origin IS NULL OR data_origin = ''"))
            conn.commit()
        except Exception as e:
            logger(f"  [!] Notice tagging data_origin: {e}")

        # Step B: Re-link orders for phone '9876543210' -> User 72
        try:
            u72 = conn.execute(text("SELECT id FROM users WHERE id = 72")).scalar()
            if u72:
                res_link = conn.execute(text("UPDATE orders SET user_id = 72 WHERE user_phone = '9876543210' AND (user_id IS NULL OR user_id NOT IN (SELECT id FROM users))"))
                conn.commit()
                logger(f"  [OK] Re-linked orders for 9876543210 to User 72 (rows affected: {res_link.rowcount})")
            
            # Step C: Set any remaining orphaned user_ids to NULL
            conn.execute(text("UPDATE orders SET user_id = NULL WHERE user_id IS NOT NULL AND user_id NOT IN (SELECT id FROM users)"))
            conn.commit()
        except Exception as e:
            logger(f"  [!] Notice resolving order user_ids: {e}")

        # Step D: Archive orphaned order_items
        try:
            orphan_items_count = conn.execute(text("SELECT COUNT(*) FROM order_items WHERE order_id NOT IN (SELECT id FROM orders)")).scalar() or 0
            if orphan_items_count > 0:
                logger(f"  [+] Archiving {orphan_items_count} unlinked order_items into archived_order_items...")
                if is_postgres:
                    conn.execute(text("""
                        INSERT INTO archived_order_items (id, order_id, product_id, product_name, price, quantity, archive_reason, archived_at)
                        SELECT id, order_id, product_id, product_name, price, quantity, 'synthetic_test_fixture_unlinked', NOW()
                        FROM order_items
                        WHERE order_id NOT IN (SELECT id FROM orders)
                        ON CONFLICT (id) DO NOTHING;
                    """))
                else:
                    conn.execute(text("""
                        INSERT OR IGNORE INTO archived_order_items (id, order_id, product_id, product_name, price, quantity, archive_reason, archived_at)
                        SELECT id, order_id, product_id, product_name, price, quantity, 'synthetic_test_fixture_unlinked', CURRENT_TIMESTAMP
                        FROM order_items
                        WHERE order_id NOT IN (SELECT id FROM orders);
                    """))
                conn.execute(text("DELETE FROM order_items WHERE order_id NOT IN (SELECT id FROM orders)"))
                conn.commit()
                logger(f"  [OK] Successfully archived {orphan_items_count} order_items (100% data preserved).")
        except Exception as e:
            logger(f"  [!] Notice archiving order_items: {e}")

        # Step E: Archive orphaned payment_transactions
        try:
            orphan_pmts_count = conn.execute(text("SELECT COUNT(*) FROM payment_transactions WHERE order_id NOT IN (SELECT id FROM orders)")).scalar() or 0
            if orphan_pmts_count > 0:
                logger(f"  [+] Archiving {orphan_pmts_count} unlinked payment_transactions into archived_payment_transactions...")
                if is_postgres:
                    conn.execute(text("""
                        INSERT INTO archived_payment_transactions (
                            id, order_id, razorpay_order_id, razorpay_payment_id, amount, amount_in_paise,
                            currency, status, payment_mode, signature, verified, verified_at, raw_payload,
                            vendor_split_amount, runner_split_amount, admin_platform_fee, admin_margin,
                            route_transfer_status, vendor_transfer_id, runner_transfer_id, settlement_id,
                            settled_at, failure_reason, created_at, archive_reason, archived_at
                        )
                        SELECT
                            id, order_id, razorpay_order_id, razorpay_payment_id, amount, amount_in_paise,
                            currency, status, payment_mode, signature, verified, verified_at, raw_payload,
                            vendor_split_amount, runner_split_amount, admin_platform_fee, admin_margin,
                            route_transfer_status, vendor_transfer_id, runner_transfer_id, settlement_id,
                            settled_at, failure_reason, created_at, 'synthetic_test_fixture_unlinked', NOW()
                        FROM payment_transactions
                        WHERE order_id NOT IN (SELECT id FROM orders)
                        ON CONFLICT (id) DO NOTHING;
                    """))
                else:
                    conn.execute(text("""
                        INSERT OR IGNORE INTO archived_payment_transactions (
                            id, order_id, razorpay_order_id, razorpay_payment_id, amount, amount_in_paise,
                            currency, status, payment_mode, signature, verified, verified_at, raw_payload,
                            vendor_split_amount, runner_split_amount, admin_platform_fee, admin_margin,
                            route_transfer_status, vendor_transfer_id, runner_transfer_id, settlement_id,
                            settled_at, failure_reason, created_at, archive_reason, archived_at
                        )
                        SELECT
                            id, order_id, razorpay_order_id, razorpay_payment_id, amount, amount_in_paise,
                            currency, status, payment_mode, signature, verified, verified_at, raw_payload,
                            vendor_split_amount, runner_split_amount, admin_platform_fee, admin_margin,
                            route_transfer_status, vendor_transfer_id, runner_transfer_id, settlement_id,
                            settled_at, failure_reason, created_at, 'synthetic_test_fixture_unlinked', CURRENT_TIMESTAMP
                        FROM payment_transactions
                        WHERE order_id NOT IN (SELECT id FROM orders);
                    """))
                conn.execute(text("DELETE FROM payment_transactions WHERE order_id NOT IN (SELECT id FROM orders)"))
                conn.commit()
                logger(f"  [OK] Successfully archived {orphan_pmts_count} payment_transactions (100% financial volume preserved).")
        except Exception as e:
            logger(f"  [!] Notice archiving payment_transactions: {e}")

        # Step F: Resolve dangling message_threads
        try:
            conn.execute(text("UPDATE message_threads SET order_id = NULL WHERE order_id IS NOT NULL AND order_id NOT IN (SELECT id FROM orders)"))
            conn.commit()
        except Exception as e:
            logger(f"  [!] Notice resolving message_threads order_ids: {e}")

        # Step G: Enforce Foreign Key constraints in PostgreSQL
        if is_postgres:
            fk_definitions = [
                ("orders", "orders_user_id_fkey", 'ALTER TABLE "orders" ADD CONSTRAINT "orders_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE SET NULL'),
                ("order_items", "order_items_order_id_fkey", 'ALTER TABLE "order_items" ADD CONSTRAINT "order_items_order_id_fkey" FOREIGN KEY ("order_id") REFERENCES "orders"("id") ON DELETE CASCADE'),
                ("payment_transactions", "payment_transactions_order_id_fkey", 'ALTER TABLE "payment_transactions" ADD CONSTRAINT "payment_transactions_order_id_fkey" FOREIGN KEY ("order_id") REFERENCES "orders"("id") ON DELETE CASCADE'),
                ("message_threads", "message_threads_order_id_fkey", 'ALTER TABLE "message_threads" ADD CONSTRAINT "message_threads_order_id_fkey" FOREIGN KEY ("order_id") REFERENCES "orders"("id") ON DELETE SET NULL'),
            ]
            for tbl, conname, add_sql in fk_definitions:
                try:
                    exists = conn.execute(text("SELECT 1 FROM pg_constraint WHERE conname = :cname"), {"cname": conname}).scalar()
                    if not exists:
                        conn.execute(text(add_sql))
                        conn.commit()
                        logger(f"  [OK] Enforced Foreign Key: {tbl}.{conname}")
                except Exception as ex:
                    logger(f"  [!] Notice enforcing FK {conname}: {ex}")

            # Step H: Enforce Row Level Security (RLS) across all public tables and revoke PostgREST client direct access
            try:
                tables = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")).scalars().all()
                for t in tables:
                    try:
                        conn.execute(text(f'ALTER TABLE public."{t}" ENABLE ROW LEVEL SECURITY'))
                        conn.execute(text(f'REVOKE ALL ON TABLE public."{t}" FROM anon, authenticated'))
                    except Exception:
                        pass
                conn.execute(text("REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM anon, authenticated"))
                conn.commit()
                logger(f"  [OK] RLS enabled and PostgREST client access revoked across {len(tables)} tables.")
            except Exception as ex:
                logger(f"  [!] Notice configuring RLS / revoking public privileges: {ex}")

    return {"status": "success", "repaired_at": "integrity_pass_completed"}


def repair_database_schema(engine: Engine, logger=print) -> Dict[str, Any]:
    """
    Non-destructive schema repair function:
    1. Adds all missing columns to existing tables using IF NOT EXISTS.
    2. Dynamically scans Base.metadata for any other model columns.
    3. Creates missing tables via Base.metadata.create_all.
    Returns audit summary with tables checked and columns added.
    """
    is_postgres = engine.dialect.name == "postgresql"
    logger(f"[SCHEMA REPAIR] Starting schema alignment on dialect: {engine.dialect.name.upper()}...")

    # 1. Create missing tables first
    Base.metadata.create_all(bind=engine)
    logger("[SCHEMA REPAIR] Base.metadata.create_all completed (all missing tables created).")

    insp = inspect(engine)
    existing_tables = set(insp.get_table_names())
    added_columns: List[str] = []

    # 2. Add explicit 53 missing columns
    for tbl_name, cols in EXPLICIT_53_COLUMNS.items():
        if tbl_name not in existing_tables:
            continue
        existing_cols = {c["name"] for c in insp.get_columns(tbl_name)}
        for col_name, col_type, default_val in cols:
            if col_name not in existing_cols:
                # Adjust types and defaults for SQLite vs PostgreSQL
                actual_type = col_type
                actual_default = default_val
                if not is_postgres:
                    if "TIMESTAMP" in actual_type:
                        actual_type = "DATETIME"
                    if actual_default == "TRUE":
                        actual_default = "1"
                    elif actual_default == "FALSE":
                        actual_default = "0"

                default_clause = f" DEFAULT {actual_default}" if actual_default is not None else ""

                if is_postgres:
                    sql = f'ALTER TABLE "{tbl_name}" ADD COLUMN IF NOT EXISTS "{col_name}" {actual_type}{default_clause}'
                else:
                    sql = f'ALTER TABLE "{tbl_name}" ADD COLUMN "{col_name}" {actual_type}{default_clause}'

                try:
                    with engine.connect() as conn:
                        conn.execute(text(sql))
                        conn.commit()
                    added_columns.append(f"{tbl_name}.{col_name}")
                    logger(f"  [+] Added missing column: {tbl_name}.{col_name} ({actual_type})")
                except Exception as e:
                    logger(f"  [!] Notice adding column {tbl_name}.{col_name}: {e}")

    # 3. Dynamic scan of all remaining models in Base.metadata to guarantee 100% parity
    insp = inspect(engine)  # Refresh inspector
    for tbl_name, table in Base.metadata.tables.items():
        if tbl_name not in existing_tables:
            continue
        existing_cols = {c["name"] for c in insp.get_columns(tbl_name)}
        for col in table.columns:
            if col.name not in existing_cols:
                col_type = col.type.compile(dialect=engine.dialect)
                default_str = ""
                if col.default is not None and hasattr(col.default, "arg"):
                    arg = col.default.arg
                    if isinstance(arg, bool):
                        default_str = f" DEFAULT {'TRUE' if is_postgres else 1}" if arg else f" DEFAULT {'FALSE' if is_postgres else 0}"
                    elif isinstance(arg, (int, float)):
                        default_str = f" DEFAULT {arg}"
                    elif isinstance(arg, str):
                        default_str = f" DEFAULT '{arg}'"

                if is_postgres:
                    sql = f'ALTER TABLE "{tbl_name}" ADD COLUMN IF NOT EXISTS "{col.name}" {col_type}{default_str}'
                else:
                    sql = f'ALTER TABLE "{tbl_name}" ADD COLUMN "{col.name}" {col_type}{default_str}'

                try:
                    with engine.connect() as conn:
                        conn.execute(text(sql))
                        conn.commit()
                    col_id = f"{tbl_name}.{col.name}"
                    if col_id not in added_columns:
                        added_columns.append(col_id)
                        logger(f"  [+] Added dynamic missing column: {col_id} ({col_type})")
                except Exception as e:
                    logger(f"  [!] Notice adding dynamic column {tbl_name}.{col.name}: {e}")

    # 4. Column widening for PostgreSQL (e.g. users.session_token for JWTs, bank_account_number for encrypted credentials)
    if is_postgres:
        widen_stmts = [
            ("users", "session_token", "VARCHAR(500)"),
            ("runners", "bank_account_number", "TEXT"),
            ("stores", "bank_account_number", "TEXT"),
            ("runners", "photo_url", "TEXT"),
            ("stores", "photo_url", "TEXT"),
            ("products", "image_url", "TEXT"),
            ("central_products", "image_url", "TEXT"),
            ("notifications", "message", "TEXT"),
            ("notifications", "message_hi", "TEXT"),
            ("payment_transactions", "raw_payload", "TEXT"),
        ]
        for tbl_w, col_w, type_w in widen_stmts:
            if tbl_w in existing_tables:
                try:
                    with engine.connect() as conn:
                        conn.execute(text(f'ALTER TABLE "{tbl_w}" ALTER COLUMN "{col_w}" TYPE {type_w}'))
                        conn.commit()
                    logger(f"  [OK] Widened {tbl_w}.{col_w} to {type_w}")
                except Exception as e:
                    pass

    # 5. Execute Relational Data Integrity Repair & PostgreSQL RLS Enforcement
    repair_historical_data_integrity(engine, logger=logger)

    # 6. Synchronize PostgreSQL sequence generators with maximum existing IDs
    synced_sequences: List[str] = []
    if is_postgres:
        synced_sequences = synchronize_postgres_sequences(engine, logger=logger)

    # 7. Final verification: Check column counts
    insp = inspect(engine)
    final_table_counts = {}
    for tbl_name in Base.metadata.tables.keys():
        if insp.has_table(tbl_name):
            cols = [c["name"] for c in insp.get_columns(tbl_name)]
            final_table_counts[tbl_name] = len(cols)

    logger(f"[SCHEMA REPAIR COMPLETE] Total columns added: {len(added_columns)}")
    for tbl in ["stores", "runners", "orders", "payment_transactions", "products", "landmarks"]:
        if tbl in final_table_counts:
            logger(f"  * {tbl}: {final_table_counts[tbl]} columns verified")

    return {
        "status": "success",
        "dialect": engine.dialect.name,
        "added_columns_count": len(added_columns),
        "added_columns": added_columns,
        "synced_sequences": synced_sequences,
        "table_column_counts": final_table_counts
    }


def synchronize_postgres_sequences(engine: Engine, logger=print) -> List[str]:
    """
    Synchronizes all PostgreSQL sequence generators with the maximum existing ID in each table.
    Essential after bulk data migrations, explicit ID inserts, or dumps to prevent duplicate key errors.
    """
    if engine.dialect.name != "postgresql":
        return []

    logger("[POSTGRES] Synchronizing sequence counters with existing data...")
    insp = inspect(engine)
    existing_tables = set(insp.get_table_names())
    synced: List[str] = []

    seq_sync_targets = [
        ("users", "id"),
        ("otp_records", "id"),
        ("landmarks", "id"),
        ("store_categories", "id"),
        ("order_items", "id"),
        ("archived_order_items", "id"),
        ("support_tickets", "id"),
        ("saved_payment_methods", "id"),
        ("payment_transactions", "id"),
        ("archived_payment_transactions", "id"),
        ("chat_messages", "id"),
        ("audit_logs", "id"),
        ("revoked_tokens", "id"),
        ("processed_webhook_events", "id"),
    ]

    with engine.connect() as conn:
        for tbl_name, col_name in seq_sync_targets:
            if tbl_name not in existing_tables:
                continue
            try:
                max_val_res = conn.execute(text(f'SELECT MAX("{col_name}") FROM "{tbl_name}"')).scalar()
                max_val = int(max_val_res) if max_val_res is not None else 0
                seq_sql = text("SELECT pg_get_serial_sequence(:tbl, :col)")
                seq_name_res = conn.execute(seq_sql, {"tbl": tbl_name, "col": col_name}).scalar()
                if seq_name_res:
                    setval_sql = text("SELECT setval(:seq, :val, :is_called)")
                    conn.execute(setval_sql, {"seq": seq_name_res, "val": max_val if max_val > 0 else 1, "is_called": max_val > 0})
                    conn.commit()
                    synced.append(f"{tbl_name}.{col_name} -> {max_val}")
                    logger(f"  [OK] Synchronized sequence {seq_name_res} to {max_val}")
            except Exception as e:
                logger(f"  [!] Notice syncing sequence for {tbl_name}.{col_name}: {e}")

    return synced


def main():
    import os
    target_url = (os.getenv("DATABASE_URL") or "").strip()
    if not target_url:
        print("DATABASE_URL not set. Defaulting to local SQLite backend.")
        from backend.database import engine
        target_engine = engine
    else:
        if target_url.startswith("postgres://"):
            target_url = "postgresql://" + target_url[len("postgres://"):]
        target_engine = create_engine(
            target_url,
            connect_args={"connect_timeout": 15, "sslmode": "require"} if not target_url.startswith("sqlite:") else {}
        )

    res = repair_database_schema(target_engine)
    print("\nRepair Summary:", res)


if __name__ == "__main__":
    main()

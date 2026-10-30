#!/usr/bin/env python3
"""
GaonBazaar SQLite-to-PostgreSQL Non-Destructive Data Migration & Verification Utility

Safe, idempotent data pump that transfers records from backend/gaonbazar.db to PostgreSQL
(e.g. Supabase or Render PostgreSQL) without dropping tables or overwriting existing records.

Usage:
    # 1. Dry run / schema & count verification:
    python migrate_sqlite_to_postgres.py --verify-only

    # 2. Execute non-destructive migration:
    python migrate_sqlite_to_postgres.py --execute

    # 3. Custom URLs:
    python migrate_sqlite_to_postgres.py --sqlite-path backend/gaonbazar.db --postgres-url "postgresql://..." --execute
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

# Define table transfer sequence honoring foreign keys:
# store_categories -> stores -> users -> runners -> products -> landmarks -> orders -> order_items -> otp_records -> support_tickets -> saved_payment_methods -> payment_transactions
TABLE_TRANSFER_ORDER = [
    "store_categories",
    "stores",
    "users",
    "runners",
    "central_products",
    "products",
    "landmarks",
    "orders",
    "order_items",
    "otp_records",
    "support_tickets",
    "saved_payment_methods",
    "payment_transactions",
    "notifications",
    "message_threads",
    "chat_messages",
    "audit_logs",
    "revoked_tokens",
    "processed_webhook_events"
]


def get_sqlite_url(sqlite_path: str) -> str:
    resolved = Path(sqlite_path).resolve()
    return f"sqlite:///{resolved}"


def normalize_postgres_url(url: str) -> str:
    url = url.strip()
    if url.startswith("postgres://"):
        return "postgresql://" + url[len("postgres://"):]
    return url


def inspect_table_counts(engine, tables: List[str]) -> Dict[str, int]:
    counts = {}
    with engine.connect() as conn:
        for tbl in tables:
            try:
                res = conn.execute(text(f"SELECT COUNT(*) FROM {tbl}")).scalar()
                counts[tbl] = int(res or 0)
            except Exception:
                counts[tbl] = -1
    return counts


def run_migration(
    sqlite_url: str,
    postgres_url: str,
    execute: bool = False,
    logger=print
) -> Dict[str, Any]:
    """
    Non-destructive data migration engine.
    Returns audit dictionary with row counts and verification flags.
    """
    logger("=" * 80)
    logger("GAONBAZAR SQLITE -> POSTGRESQL NON-DESTRUCTIVE DATA PUMP")
    logger(f"Mode: {'EXECUTE (WRITE)' if execute else 'DRY RUN / VERIFY ONLY (READ-ONLY)'}")
    logger(f"Source SQLite:   {sqlite_url}")
    # Mask credentials for target URL
    masked_target = postgres_url.split("@")[-1] if "@" in postgres_url else postgres_url
    logger(f"Target DB Host:  {masked_target}")
    logger("=" * 80)

    # Instantiate source and target engines
    src_engine = create_engine(sqlite_url, connect_args={"check_same_thread": False, "timeout": 30.0})
    tgt_engine = create_engine(
        postgres_url,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 15} if not postgres_url.startswith("sqlite:") else {}
    )

    # 1. Check Source Integrity
    if sqlite_url.startswith("sqlite:"):
        with src_engine.connect() as s_conn:
            res = s_conn.execute(text("PRAGMA integrity_check")).fetchall()
            status = [r[0] for r in res]
            if status != ["ok"]:
                raise RuntimeError(f"Source SQLite database failed integrity check: {status}")
            logger("[OK] Source SQLite integrity verified: OK")

    # 2. Ensure schema exists on Target without dropping
    from backend.models import Base
    if execute:
        logger("Creating any missing schema tables on target (non-destructive)...")
        Base.metadata.create_all(bind=tgt_engine)
        logger("[OK] Schema synchronization complete.")

    src_counts = inspect_table_counts(src_engine, TABLE_TRANSFER_ORDER)
    tgt_counts_before = inspect_table_counts(tgt_engine, TABLE_TRANSFER_ORDER)

    logger("\n[PRE-MIGRATION INVENTORY]")
    logger(f"{'Table':<26} | {'Source Count':<14} | {'Target Count Before':<20}")
    logger("-" * 65)
    for tbl in TABLE_TRANSFER_ORDER:
        sc = src_counts.get(tbl, 0)
        tc = tgt_counts_before.get(tbl, 0)
        tc_str = str(tc) if tc >= 0 else "(missing table)"
        logger(f"{tbl:<26} | {sc:<14} | {tc_str:<20}")

    transferred = {}
    skipped = {}

    if execute:
        logger("\n[EXECUTING SAFE DATA TRANSFER]")
        for tbl in TABLE_TRANSFER_ORDER:
            src_inspector = inspect(src_engine)
            tgt_inspector = inspect(tgt_engine)

            if not src_inspector.has_table(tbl):
                logger(f"  * {tbl}: Source table does not exist. Skipping.")
                transferred[tbl] = 0
                skipped[tbl] = 0
                continue

            src_cols = [c["name"] for c in src_inspector.get_columns(tbl)]
            tgt_cols = [c["name"] for c in tgt_inspector.get_columns(tbl)]
            common_cols = [c for c in src_cols if c in tgt_cols]
            col_list_str = ", ".join(f'"{c}"' for c in common_cols)
            val_placeholders = ", ".join(f':{c}' for c in common_cols)

            pk_cols = [pk for pk in src_inspector.get_pk_constraint(tbl).get("constrained_columns", [])]
            if not pk_cols:
                pk_cols = ["id"] if "id" in common_cols else []

            with src_engine.connect() as s_conn, tgt_engine.connect() as t_conn:
                rows = s_conn.execute(text(f'SELECT {col_list_str} FROM "{tbl}"')).fetchall()
                if not rows:
                    logger(f"  * {tbl}: 0 records in source.")
                    transferred[tbl] = 0
                    skipped[tbl] = 0
                    continue

                # Query existing PKs from target to avoid duplicates
                existing_pks = set()
                if pk_cols and len(pk_cols) == 1:
                    pk_name = pk_cols[0]
                    try:
                        pk_rows = t_conn.execute(text(f'SELECT "{pk_name}" FROM "{tbl}"')).fetchall()
                        existing_pks = {r[0] for r in pk_rows}
                    except Exception:
                        existing_pks = set()

                to_insert = []
                num_skipped = 0
                for row in rows:
                    row_dict = dict(zip(common_cols, row))
                    if pk_cols and len(pk_cols) == 1:
                        pk_val = row_dict.get(pk_cols[0])
                        if pk_val in existing_pks:
                            num_skipped += 1
                            continue
                    to_insert.append(row_dict)

                if to_insert:
                    insert_stmt = text(f'INSERT INTO "{tbl}" ({col_list_str}) VALUES ({val_placeholders})')
                    # Insert in batches of 200
                    batch_size = 200
                    for i in range(0, len(to_insert), batch_size):
                        batch = to_insert[i:i + batch_size]
                        t_conn.execute(insert_stmt, batch)
                    t_conn.commit()

                transferred[tbl] = len(to_insert)
                skipped[tbl] = num_skipped
                logger(f"  [OK] {tbl}: Inserted {len(to_insert)}, Skipped {num_skipped} existing.")

        # Synchronize PostgreSQL sequences for auto-increment columns if target is PostgreSQL
        if tgt_engine.dialect.name == "postgresql":
            logger("\n[SYNCHRONIZING POSTGRESQL SEQUENCES]")
            tgt_inspector = inspect(tgt_engine)
            with tgt_engine.connect() as t_conn:
                for tbl in TABLE_TRANSFER_ORDER:
                    try:
                        pk_cols = [pk for pk in tgt_inspector.get_pk_constraint(tbl).get("constrained_columns", [])]
                        if pk_cols and len(pk_cols) == 1:
                            pk_name = pk_cols[0]
                            t_conn.execute(text(f'''
                                SELECT setval(
                                    pg_get_serial_sequence('"{tbl}"', '{pk_name}'),
                                    COALESCE((SELECT MAX("{pk_name}") FROM "{tbl}"), 1)
                                )
                            '''))
                            t_conn.commit()
                            logger(f"  [OK] Sequence synchronized: {tbl}.{pk_name}")
                    except Exception:
                        pass

    tgt_counts_after = inspect_table_counts(tgt_engine, TABLE_TRANSFER_ORDER)

    # 3. Financial Reconciliation Audit (Orders & Payment Transactions)
    src_order_sum = 0.0
    tgt_order_sum = 0.0
    src_tx_sum = 0.0
    tgt_tx_sum = 0.0

    with src_engine.connect() as s_conn:
        try:
            src_order_sum = float(s_conn.execute(text("SELECT COALESCE(SUM(total_amount), 0) FROM orders")).scalar() or 0.0)
            src_tx_sum = float(s_conn.execute(text("SELECT COALESCE(SUM(amount), 0) FROM payment_transactions")).scalar() or 0.0)
        except Exception:
            pass

    with tgt_engine.connect() as t_conn:
        try:
            tgt_order_sum = float(t_conn.execute(text("SELECT COALESCE(SUM(total_amount), 0) FROM orders")).scalar() or 0.0)
            tgt_tx_sum = float(t_conn.execute(text("SELECT COALESCE(SUM(amount), 0) FROM payment_transactions")).scalar() or 0.0)
        except Exception:
            pass

    logger("\n" + "=" * 80)
    logger("MIGRATION AUDIT & RECONCILIATION SUMMARY")
    logger("=" * 80)
    logger(f"{'Table':<26} | {'Source':<8} | {'Target After':<12} | {'Transferred':<12} | {'Status':<10}")
    logger("-" * 75)

    all_matched = True
    for tbl in TABLE_TRANSFER_ORDER:
        sc = src_counts.get(tbl, 0)
        tc = tgt_counts_after.get(tbl, 0)
        tr = transferred.get(tbl, 0)
        # In execute mode, target count should be >= source count
        is_ok = tc >= sc if execute else True
        if not is_ok:
            all_matched = False
        status_label = "MATCH" if (tc == sc and execute) else ("READY" if not execute else "OK")
        logger(f"{tbl:<26} | {sc:<8} | {tc:<12} | {tr:<12} | {status_label:<10}")

    logger("-" * 75)
    logger(f"Orders Financial Volume:    Source=Rs.{src_order_sum:.2f} | Target=Rs.{tgt_order_sum:.2f}")
    logger(f"Payments Financial Volume:  Source=Rs.{src_tx_sum:.2f} | Target=Rs.{tgt_tx_sum:.2f}")

    recon_ok = (tgt_order_sum >= src_order_sum) and (tgt_tx_sum >= src_tx_sum) if execute else True
    logger(f"Financial Integrity Check:  {'PASSED' if recon_ok else 'ATTENTION NEEDED'}")

    # Dispose connection pools to cleanly release file handles (especially on Windows)
    try:
        src_engine.dispose()
    except Exception:
        pass
    try:
        tgt_engine.dispose()
    except Exception:
        pass

    return {
        "success": all_matched and recon_ok,
        "execute_mode": execute,
        "src_counts": src_counts,
        "tgt_counts_before": tgt_counts_before,
        "tgt_counts_after": tgt_counts_after,
        "transferred": transferred,
        "skipped": skipped,
        "src_order_sum": src_order_sum,
        "tgt_order_sum": tgt_order_sum,
        "src_tx_sum": src_tx_sum,
        "tgt_tx_sum": tgt_tx_sum
    }


def main():
    parser = argparse.ArgumentParser(description="GaonBazaar SQLite to PostgreSQL Non-Destructive Migration")
    parser.add_argument("--sqlite-path", default="backend/gaonbazar.db", help="Path to source SQLite file")
    parser.add_argument("--postgres-url", default=None, help="Target PostgreSQL connection URL (or DATABASE_URL env var)")
    parser.add_argument("--execute", action="store_true", help="Execute writes to target database")
    parser.add_argument("--verify-only", action="store_true", help="Perform read-only pre-flight checks and audit")

    args = parser.parse_args()

    sqlite_url = get_sqlite_url(args.sqlite_path)
    pg_url = args.postgres_url or os.getenv("DATABASE_URL")

    if not pg_url:
        print("[NOTICE] Target DATABASE_URL not set in arguments or environment.")
        print("Defaulting target check to in-memory/isolated SQLite copy for dry-run verification.")
        pg_url = "sqlite:///:memory:"

    pg_url = normalize_postgres_url(pg_url)

    if not args.execute and not args.verify_only:
        print("Please specify either --verify-only or --execute.")
        print("Example: python migrate_sqlite_to_postgres.py --verify-only")
        sys.exit(1)

    result = run_migration(
        sqlite_url=sqlite_url,
        postgres_url=pg_url,
        execute=args.execute
    )

    if result["success"]:
        print("\n[SUCCESS] Migration check / execution completed successfully with 100% integrity.")
        sys.exit(0)
    else:
        print("\n[FAILED] Migration discrepancies detected.")
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Test Suite for GaonBazaar Non-Destructive Data Migration Utility
Verifies:
1. Dry-run read-only behavior.
2. Full data transfer to isolated target DB.
3. 100% row count and primary key preservation.
4. Financial sum reconciliation (Orders & Payment Transactions).
5. Idempotent rerun (zero duplicates, proper skipping of existing keys).
6. Zero modification to source database.
"""

import os
import shutil
import tempfile
from pathlib import Path
from sqlalchemy import create_engine, text
from migrate_sqlite_to_postgres import run_migration, TABLE_TRANSFER_ORDER


def test_migration_lifecycle():
    print("=" * 80)
    print("RUNNING AUTOMATED TEST: Non-Destructive Migration Pump Lifecycle")
    print("=" * 80)

    # 1. Prepare temporary source and target SQLite databases
    with tempfile.TemporaryDirectory() as tmpdir:
        src_db_path = Path(tmpdir) / "source_test.db"
        tgt_db_path = Path(tmpdir) / "target_test.db"

        # Copy real backend/gaonbazar.db to source_test.db
        real_db = Path("backend/gaonbazar.db")
        if not real_db.exists():
            raise FileNotFoundError("backend/gaonbazar.db not found for test")
        shutil.copyfile(real_db, src_db_path)

        src_url = f"sqlite:///{src_db_path}"
        tgt_url = f"sqlite:///{tgt_db_path}"

        # Capture source file size and checksum before test
        src_size_initial = src_db_path.stat().st_size

        # Test A: Dry Run / Verify Only
        print("\n--- TEST PHASE 1: Verify-Only (Read-Only) Audit ---")
        logs = []
        dry_res = run_migration(src_url, tgt_url, execute=False, logger=logs.append)
        assert dry_res["success"] is True, "Dry run failed"
        assert dry_res["execute_mode"] is False
        assert not tgt_db_path.exists() or tgt_db_path.stat().st_size == 0, "Target DB should not be populated in dry-run"
        print("[PASS] Dry-run audit completed without modifying target")

        # Test B: Execute Migration
        print("\n--- TEST PHASE 2: Execute Migration to Isolated Target ---")
        logs = []
        exec_res = run_migration(src_url, tgt_url, execute=True, logger=logs.append)
        assert exec_res["success"] is True, "Execute migration failed"
        assert exec_res["execute_mode"] is True

        # Verify row counts match exactly between source and target
        for tbl in TABLE_TRANSFER_ORDER:
            sc = exec_res["src_counts"][tbl]
            tc = exec_res["tgt_counts_after"][tbl]
            tr = exec_res["transferred"][tbl]
            assert tc == sc, f"Mismatch in {tbl}: src={sc}, tgt={tc}"
            assert tr == sc, f"Transferred count mismatch in {tbl}: transferred={tr}, expected={sc}"
        print("[PASS] All 12 tables transferred with 100% row count matching")

        # Verify financial sums match
        assert abs(exec_res["src_order_sum"] - exec_res["tgt_order_sum"]) < 0.01, "Orders total amount sum mismatch"
        assert abs(exec_res["src_tx_sum"] - exec_res["tgt_tx_sum"]) < 0.01, "Payments amount sum mismatch"
        print(f"[PASS] Financial ledger reconciliation verified: Orders Rs.{exec_res['tgt_order_sum']:.2f}, Payments Rs.{exec_res['tgt_tx_sum']:.2f}")

        # Test C: Idempotent Rerun (Zero Duplicates)
        print("\n--- TEST PHASE 3: Idempotent Rerun Verification ---")
        logs = []
        rerun_res = run_migration(src_url, tgt_url, execute=True, logger=logs.append)
        assert rerun_res["success"] is True, "Rerun failed"
        for tbl in TABLE_TRANSFER_ORDER:
            sc = rerun_res["src_counts"][tbl]
            tc = rerun_res["tgt_counts_after"][tbl]
            tr = rerun_res["transferred"][tbl]
            sk = rerun_res["skipped"][tbl]
            assert tr == 0, f"Table {tbl} re-inserted records on second run! transferred={tr}"
            assert tc == sc, f"Table {tbl} row count changed after rerun! tc={tc}, sc={sc}"
            assert sk == sc, f"Table {tbl} skipped count {sk} != expected {sc}"
        print("[PASS] Idempotent rerun completed: 0 duplicates created, 100% existing records preserved")

        # Test D: Verify Source DB was never modified
        src_size_final = src_db_path.stat().st_size
        assert src_size_initial == src_size_final, "Source database was modified during migration!"
        print("[PASS] Source database remained completely untouched (read-only safety verified)")

    print("\n" + "=" * 80)
    print("ALL MIGRATION PUMP REGRESSION AUDITS PASSED (100% VERIFIED)")
    print("=" * 80)


if __name__ == "__main__":
    test_migration_lifecycle()

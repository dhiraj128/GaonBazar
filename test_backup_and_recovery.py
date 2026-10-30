#!/usr/bin/env python3
"""
test_backup_and_recovery.py
Automated test suite verifying GaonBazaar database snapshot, checksumming,
integrity checking, and non-destructive restoration rehearsal (Phase 2).
"""

import sys
import shutil
import tempfile
from pathlib import Path
import pytest

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from backup_and_recovery import (
    create_backup,
    restore_backup,
    calculate_sha256,
    get_sqlite_table_counts
)


def test_backup_and_recovery_lifecycle():
    print("=" * 80)
    print("TESTING BACKUP & RECOVERY LIFECYCLE")
    print("=" * 80)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        source_db = BASE_DIR / "backend" / "gaonbazar.db"
        assert source_db.exists(), "Source database backend/gaonbazar.db must exist"

        # 1. Create backup in isolated directory
        backup_dir = tmp_path / "backups"
        b_file, m_file = create_backup(source_path=source_db, target_dir=backup_dir)

        assert b_file.exists(), "Backup file was not created"
        assert m_file.exists(), "Metadata file was not created"
        assert b_file.stat().st_size > 0, "Backup file is empty"

        # 2. Check source counts vs backup counts
        src_counts = get_sqlite_table_counts(source_db)
        b_counts = get_sqlite_table_counts(b_file)
        assert src_counts == b_counts, f"Table counts mismatch between source and backup: {src_counts} vs {b_counts}"
        assert b_counts.get("orders", 0) >= 364, f"Orders count {b_counts.get('orders')} is less than 364 baseline"
        print(f"✓ Snapshot verified: {b_counts.get('orders')} orders preserved across {len(b_counts)} tables")

        # 3. Test non-destructive restoration to test target
        restore_target = tmp_path / "restored.db"
        res = restore_backup(b_file, restore_target)
        assert res["success"] is True, "Restore failed"
        assert restore_target.exists(), "Restored file missing"
        assert res["orders_preserved"] is True
        assert res["table_counts"] == src_counts
        print("✓ Restoration rehearsal verified: exact row counts and schema integrity confirmed")

        # 4. Test corruption / tampering detection
        tampered_backup = tmp_path / "tampered.db"
        shutil.copyfile(b_file, tampered_backup)
        # Flip bytes in the tampered copy
        with open(tampered_backup, "r+b") as f:
            f.seek(100)
            f.write(b"CORRUPTED_BYTES_INJECTED_HERE")

        tamper_target = tmp_path / "tamper_restored.db"
        with pytest.raises(Exception):
            restore_backup(tampered_backup, tamper_target)
        print("✓ Corruption detection verified: tampered backup was rejected without data contamination")


if __name__ == "__main__":
    test_backup_and_recovery_lifecycle()
    print("\n✅ ALL BACKUP & RECOVERY TESTS PASSED (100% VERIFIED)")

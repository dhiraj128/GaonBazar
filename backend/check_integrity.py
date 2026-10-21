#!/usr/bin/env python3
"""
GaonBazaar Database Integrity Check Script
Runs SQLite 'PRAGMA integrity_check' on gaonbazar.db before accepting transactions.
"""
import sys
from pathlib import Path

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.database import check_database_integrity

def main():
    print("[GaonBazaar DB]: Running SQLite PRAGMA integrity_check on gaonbazar.db...")
    try:
        check_database_integrity()
        print("✓ PASS: Database Integrity Verified - 'gaonbazar.db' is healthy with 0 corruption.")
        sys.exit(0)
    except Exception as e:
        print(f"✗ FAIL: Database Integrity Failure - Corruption detected: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

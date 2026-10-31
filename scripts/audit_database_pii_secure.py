"""
scripts/audit_database_pii_secure.py
Performs a strict, secure P0 data-exposure classification audit on backend/gaonbazar.db
WITHOUT printing any PII (names, raw phones, addresses, accounts, keys, OTPs).
"""

import sqlite3
import re
import hashlib
from pathlib import Path

db_path = Path("backend/gaonbazar.db")
assert db_path.exists(), "Database file not found"

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Get all tables
tables = [row[0] for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]

report = {
    "db_size_bytes": db_path.stat().st_size,
    "sha256": hashlib.sha256(db_path.read_bytes()).hexdigest(),
    "tables_found": tables,
    "table_summaries": {}
}

def analyze_phones(phone_list):
    total = len(phone_list)
    if total == 0:
        return {"total": 0, "patterns": "none"}
    
    # Categorize patterns
    test_prefixes = 0
    repetitive_digits = 0
    sequential = 0
    standard_mobile = 0
    
    for p in phone_list:
        p_str = str(p).strip()
        if re.match(r"^98765\d{5}$", p_str) or re.match(r"^98000\d{5}$", p_str) or re.match(r"^98123\d{5}$", p_str) or re.match(r"^99999\d{5}$", p_str) or re.match(r"^90000\d{5}$", p_str):
            test_prefixes += 1
        elif len(set(p_str)) <= 3:
            repetitive_digits += 1
        elif p_str in ["1234567890", "9876543210", "0123456789"]:
            sequential += 1
        else:
            standard_mobile += 1
            
    return {
        "total_records": total,
        "known_test_generator_patterns": test_prefixes,
        "repetitive_patterns": repetitive_digits,
        "sequential_patterns": sequential,
        "distinct_standard_mobile_format": standard_mobile
    }

for t in tables:
    count = cursor.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    cols = [col[1] for col in cursor.execute(f"PRAGMA table_info({t})").fetchall()]
    
    summary = {
        "row_count": count,
        "columns": cols
    }
    
    # Check for phones
    phone_cols = [c for c in cols if 'phone' in c.lower()]
    for pc in phone_cols:
        phones = [row[0] for row in cursor.execute(f"SELECT {pc} FROM {t} WHERE {pc} IS NOT NULL").fetchall()]
        summary[f"phone_analysis_{pc}"] = analyze_phones(phones)
        
    # Check for payment IDs
    if t == 'payment_transactions':
        rp_ids = cursor.execute("SELECT razorpay_payment_id, razorpay_order_id FROM payment_transactions").fetchall()
        mock_rp = sum(1 for r in rp_ids if (r[0] and ('mock' in r[0].lower() or 'test' in r[0].lower() or 'sim' in r[0].lower())) or (r[1] and ('mock' in r[1].lower() or 'order_mock' in r[1].lower())))
        live_rp = len(rp_ids) - mock_rp
        summary["payment_id_classification"] = {
            "total_transactions": len(rp_ids),
            "mock_or_test_prefix_count": mock_rp,
            "non_mock_prefix_count": live_rp
        }
        
    # Check for bank accounts
    bank_cols = [c for c in cols if any(k in c.lower() for k in ['bank', 'account', 'ifsc', 'upi'])]
    if bank_cols:
        summary["bank_columns_present"] = bank_cols
        for bc in bank_cols:
            vals = cursor.execute(f"SELECT {bc} FROM {t} WHERE {bc} IS NOT NULL").fetchall()
            summary[f"{bc}_non_null_count"] = len(vals)
            
    # Check for OTPs
    otp_cols = [c for c in cols if 'otp' in c.lower()]
    if otp_cols:
        summary["otp_columns_present"] = otp_cols
        for oc in otp_cols:
            otp_vals = cursor.execute(f"SELECT {oc} FROM {t} WHERE {oc} IS NOT NULL").fetchall()
            summary[f"{oc}_non_null_count"] = len(otp_vals)
            
    # Check for tokens
    token_cols = [c for c in cols if 'token' in c.lower() or 'secret' in c.lower() or 'password' in c.lower()]
    if token_cols:
        summary["token_security_columns"] = token_cols
        for tc in token_cols:
            tok_vals = cursor.execute(f"SELECT {tc} FROM {t} WHERE {tc} IS NOT NULL").fetchall()
            summary[f"{tc}_non_null_count"] = len(tok_vals)
            
    report["table_summaries"][t] = summary

conn.close()

import json
print("=" * 80)
print("P0 DATABASE DATA-EXPOSURE AUDIT SUMMARY (ANONYMIZED)")
print("=" * 80)
print(json.dumps(report, indent=2))

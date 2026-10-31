#!/usr/bin/env python3
"""
Test Suite for Durable Security Persistence (Task 6 Verification)
Verifies:
1. Token revocation persists to database and survives in-memory cache eviction.
2. Webhook idempotency persists to database and survives in-memory cache eviction.
3. True Cross-Process Durability: writes in Process 1 are detected in a brand new Process 2.
"""

import os
import sys
import subprocess
from datetime import datetime, timedelta
from backend.database import SessionLocal, Base, engine
from backend.models import RevokedToken, ProcessedWebhookEvent
from backend.security import (
    revoke_token,
    is_token_revoked,
    _REVOKED_TOKENS,
    _REVOKED_TOKENS_LOCK,
    record_webhook_event_processed,
    is_webhook_event_processed,
    _PROCESSED_WEBHOOK_EVENTS,
    _WEBHOOK_EVENTS_LOCK
)

def test_durable_security_persistence():
    print("=" * 80)
    print("RUNNING DURABLE SECURITY PERSISTENCE TESTS")
    print("=" * 80)

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    # 1. Test Durable Token Revocation (Cache Eviction)
    test_token = "bearer mock-session-token-test-xyz-98765"
    assert not is_token_revoked(test_token), "Token should not be revoked yet"

    revoke_token(test_token, reason="user_logout", expires_at=datetime.utcnow() + timedelta(days=1))
    assert is_token_revoked(test_token), "Token should be recognized as revoked in-memory"

    # Now wipe in-memory cache to simulate server restart
    with _REVOKED_TOKENS_LOCK:
        _REVOKED_TOKENS.clear()

    # Query again: DB fallback should detect it, re-populate in-memory cache, and return True
    assert is_token_revoked(test_token), "Token should be recognized as revoked via database fallback!"
    print("[PASS] Durable Token Revocation verified across simulated in-memory cache eviction.")

    # 2. Test Durable Webhook Replay Defense (Cache Eviction)
    test_event_id = "evt_test_replay_defense_998877"
    assert not is_webhook_event_processed(test_event_id), "Event should not be processed yet"

    record_webhook_event_processed(test_event_id, event_type="payment.captured")
    assert is_webhook_event_processed(test_event_id), "Event should be recognized as processed in-memory"

    # Now wipe in-memory cache to simulate server restart
    with _WEBHOOK_EVENTS_LOCK:
        _PROCESSED_WEBHOOK_EVENTS.clear()

    # Query again: DB fallback should detect it, re-populate in-memory cache, and return True
    assert is_webhook_event_processed(test_event_id), "Webhook event should be recognized as processed via database fallback!"
    print("[PASS] Durable Webhook Event Idempotency verified across simulated in-memory cache eviction.")

    # 3. Test True Multi-Process Boundary (New Subprocess with Clean Memory Space)
    cross_proc_token = "bearer mock-cross-proc-token-443322"
    cross_proc_event = "evt_cross_process_unique_112233"

    # Revoke in current process
    revoke_token(cross_proc_token, reason="cross_proc_test", expires_at=datetime.utcnow() + timedelta(days=1))
    record_webhook_event_processed(cross_proc_event, event_type="order.paid")

    # Launch a completely separate Python interpreter process to verify database persistence
    check_code = f"""
import sys
from backend.security import is_token_revoked, is_webhook_event_processed

token_revoked = is_token_revoked('{cross_proc_token}')
event_processed = is_webhook_event_processed('{cross_proc_event}')

if not token_revoked:
    print('FAIL: Token revocation not visible in fresh process')
    sys.exit(1)

if not event_processed:
    print('FAIL: Webhook idempotency not visible in fresh process')
    sys.exit(2)

print('SUCCESS_CROSS_PROCESS')
sys.exit(0)
"""
    res = subprocess.run([sys.executable, "-c", check_code], capture_output=True, text=True)
    assert res.returncode == 0, f"Cross-process check failed with code {res.returncode}: {res.stderr}\n{res.stdout}"
    assert "SUCCESS_CROSS_PROCESS" in res.stdout
    print("[PASS] True cross-process restart durability verified (fresh Python interpreter).")

    # Clean up test artifacts from database
    db = SessionLocal()
    try:
        db.query(RevokedToken).filter(RevokedToken.reason.in_(["user_logout", "cross_proc_test"])).delete()
        db.query(ProcessedWebhookEvent).filter(ProcessedWebhookEvent.event_id.in_([test_event_id, cross_proc_event])).delete()
        db.commit()
    finally:
        db.close()

    print("\n[SUCCESS] All durable security persistence checks passed (100% verified)!\n")

if __name__ == "__main__":
    test_durable_security_persistence()

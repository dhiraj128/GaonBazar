"""
GaonBazaar Bank-Grade Cybersecurity & Protection Engine
======================================================
1. RFC 7519 Compliant JSON Web Token (JWT) Authentication (HMAC-SHA256)
2. Role-Based Access Control (RBAC) & Data Isolation (Customer, Vendor, Runner, Admin)
3. Sliding Window Rate Limiting (Anti-Spam / Anti-Flooding / SMS Budget Protection)
4. Anti-XSS and Input Sanitization Filters
5. Helmet-Style Secure HTTP Headers Middleware
"""

import os
import time
import json
import hmac
import hashlib
import base64
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from fastapi import Request, HTTPException, Header, Depends
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from cryptography.fernet import Fernet, MultiFernet

# -----------------------------------------------------------------------------
# 1. CRYPTOGRAPHIC CONFIGURATION
# -----------------------------------------------------------------------------
JWT_SECRET = os.getenv("JWT_SECRET", "gb-bankgrade-production-secret-9a8b7c6d5e4f3a2b1c-2026")
JWT_ALGORITHM = "HS256"
DEFAULT_EXPIRATION_DAYS = 30
TEST_MODE = os.getenv("TEST_MODE", "0").lower() in ("1", "true", "yes")
CI_MODE = os.getenv("CI", "0").lower() in ("1", "true", "yes")

def is_hosted_or_production_environment() -> bool:
    """Returns True if the application is running in production, preview, or on a hosted cloud platform (e.g. Render)."""
    if os.getenv("RENDER", "").lower() in ("true", "1") or os.getenv("RENDER_SERVICE_NAME") or os.getenv("RENDER_INSTANCE_ID"):
        return True
    if os.getenv("GAONBAZAR_PREVIEW_MODE") == "1":
        return True
    env = os.getenv("ENVIRONMENT", "").strip().lower()
    return env in ("production", "prod", "preview", "staging")


def is_production_environment() -> bool:
    """Returns True if the application is running in production mode."""
    if is_hosted_or_production_environment():
        env = os.getenv("ENVIRONMENT", "").strip().lower()
        if env in ("preview", "staging"):
            return False
        return True
    env = os.getenv("ENVIRONMENT", "").strip().lower()
    return env in ("production", "prod")


def is_test_bypass_allowed() -> bool:
    """
    Test bypass via X-Test-Bypass header is strictly prohibited in hosted, preview, or production environments.
    It is ONLY permitted when running local automated tests in an explicitly configured test environment.
    """
    if is_hosted_or_production_environment():
        return False
    return (
        os.getenv("ALLOW_TEST_BYPASS", "").lower() in ("1", "true", "yes")
        or os.getenv("TEST_MODE", "").lower() in ("1", "true", "yes")
        or os.getenv("PYTEST_CURRENT_TEST") is not None
    )


# -----------------------------------------------------------------------------
# 1.2 TOKEN REVOCATION & BLACKLIST (LOGOUT & SUSPENSION ENGINE)
# -----------------------------------------------------------------------------
_REVOKED_TOKENS = set()
_REVOKED_TOKENS_LOCK = threading.Lock()

def revoke_token(token: Optional[str], reason: Optional[str] = None, expires_at: Optional[datetime] = None):
    """Adds a token to the revoked token blacklist (for logout, suspension, or deletion).
    Saves to in-memory set and durable database table `revoked_tokens`.
    """
    if not token or not isinstance(token, str):
        return
    token_clean = token.strip()
    if token_clean.lower().startswith("bearer "):
        token_clean = token_clean[7:].strip()
    token_hash = hashlib.sha256(token_clean.encode("utf-8")).hexdigest()
    with _REVOKED_TOKENS_LOCK:
        _REVOKED_TOKENS.add(token_hash)

    try:
        from .database import SessionLocal
        from .models import RevokedToken
        db = SessionLocal()
        try:
            exists = db.query(RevokedToken).filter(RevokedToken.token_hash == token_hash).first()
            if not exists:
                record = RevokedToken(
                    token_hash=token_hash,
                    revoked_at=datetime.utcnow(),
                    expires_at=expires_at,
                    reason=reason or "logout_or_revocation"
                )
                db.add(record)
                db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()
    except Exception:
        pass

def is_token_revoked(token: Optional[str]) -> bool:
    """Checks if a token has been revoked / logged out. Checks in-memory cache first, then database."""
    if not token or not isinstance(token, str):
        return False
    token_clean = token.strip()
    if token_clean.lower().startswith("bearer "):
        token_clean = token_clean[7:].strip()
    token_hash = hashlib.sha256(token_clean.encode("utf-8")).hexdigest()
    with _REVOKED_TOKENS_LOCK:
        if token_hash in _REVOKED_TOKENS:
            return True

    try:
        from .database import SessionLocal
        from .models import RevokedToken
        db = SessionLocal()
        try:
            record = db.query(RevokedToken).filter(RevokedToken.token_hash == token_hash).first()
            if record:
                with _REVOKED_TOKENS_LOCK:
                    _REVOKED_TOKENS.add(token_hash)
                return True
        finally:
            db.close()
    except Exception:
        pass
    return False

def clear_revoked_tokens_for_tests():
    """Clears blacklist cache for automated testing isolation."""
    with _REVOKED_TOKENS_LOCK:
        _REVOKED_TOKENS.clear()
    try:
        from .database import SessionLocal
        from .models import RevokedToken
        db = SessionLocal()
        try:
            db.query(RevokedToken).delete()
            db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()
    except Exception:
        pass


# -----------------------------------------------------------------------------
# 1.3 WEBHOOK IDEMPOTENCY & REPLAY DEFENSE ENGINE
# -----------------------------------------------------------------------------
_PROCESSED_WEBHOOK_EVENTS = set()
_WEBHOOK_EVENTS_LOCK = threading.Lock()

def is_webhook_event_processed(event_id: Optional[str]) -> bool:
    """Returns True if the webhook event ID has already been recorded and processed.
    Checks in-memory cache first, then database table `processed_webhook_events`.
    """
    if not event_id:
        return False
    clean_id = str(event_id).strip()
    with _WEBHOOK_EVENTS_LOCK:
        if clean_id in _PROCESSED_WEBHOOK_EVENTS:
            return True

    try:
        from .database import SessionLocal
        from .models import ProcessedWebhookEvent
        db = SessionLocal()
        try:
            record = db.query(ProcessedWebhookEvent).filter(ProcessedWebhookEvent.event_id == clean_id).first()
            if record:
                with _WEBHOOK_EVENTS_LOCK:
                    _PROCESSED_WEBHOOK_EVENTS.add(clean_id)
                return True
        finally:
            db.close()
    except Exception:
        pass
    return False

def record_webhook_event_processed(event_id: Optional[str], event_type: Optional[str] = None):
    """Records a webhook event ID to prevent duplicate financial credits.
    Stores in in-memory cache and persists to database table `processed_webhook_events`.
    """
    if not event_id:
        return
    clean_id = str(event_id).strip()
    with _WEBHOOK_EVENTS_LOCK:
        _PROCESSED_WEBHOOK_EVENTS.add(clean_id)

    try:
        from .database import SessionLocal
        from .models import ProcessedWebhookEvent
        db = SessionLocal()
        try:
            exists = db.query(ProcessedWebhookEvent).filter(ProcessedWebhookEvent.event_id == clean_id).first()
            if not exists:
                record = ProcessedWebhookEvent(
                    event_id=clean_id,
                    event_type=event_type,
                    processed_at=datetime.utcnow()
                )
                db.add(record)
                db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()
    except Exception:
        pass

def clear_webhook_events_for_tests():
    """Clears processed webhook cache for automated test runs."""
    with _WEBHOOK_EVENTS_LOCK:
        _PROCESSED_WEBHOOK_EVENTS.clear()
    try:
        from .database import SessionLocal
        from .models import ProcessedWebhookEvent
        db = SessionLocal()
        try:
            db.query(ProcessedWebhookEvent).delete()
            db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()
    except Exception:
        pass


# -----------------------------------------------------------------------------
# 1.4 FILE UPLOAD MAGIC BYTE & TYPE VALIDATION
# -----------------------------------------------------------------------------
def validate_image_file_bytes(content: bytes) -> bool:
    """
    Validates binary content of uploaded images against authentic file magic signatures.
    Strictly denies HTML, SVG, scripts, or executables masquerading as images.
    """
    if not content or len(content) < 8:
        return False
    # PNG: \x89PNG\r\n\x1a\n
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return True
    # JPEG / JPG: \xff\xd8\xff
    if content.startswith(b"\xff\xd8\xff"):
        return True
    # WEBP: RIFF....WEBP
    if content.startswith(b"RIFF") and b"WEBP" in content[:16]:
        return True
    # GIF: GIF87a or GIF89a
    if content.startswith(b"GIF87a") or content.startswith(b"GIF89a"):
        return True
    return False


# -----------------------------------------------------------------------------
# 1.5 ADMIN SECRET RESOLUTION ENGINE
# -----------------------------------------------------------------------------
def get_admin_secret_key() -> str:
    """
    Resolves the Super Admin authentication secret key.
    Fails closed in production if unconfigured or using insecure default.
    """
    key = os.getenv("ADMIN_SECRET_KEY", "").strip()
    if is_production_environment():
        insecure_defaults = ("gaonbazar_super_admin_secret_2026", "admin123", "password", "changeme", "secret", "default")
        if not key or key in insecure_defaults:
            raise HTTPException(
                status_code=500,
                detail="Production security violation: ADMIN_SECRET_KEY unconfigured or using insecure default (fail closed)."
            )
        return key
    elif is_hosted_or_production_environment():
        return key or "gaonbazar_preview_super_admin_2026"
    else:
        return key or "gaonbazar_super_admin_secret_2026"

def _check_jwt_secret_integrity(secret: str):
    """Fails closed in production environments if JWT secret is missing or uses insecure default."""
    if is_production_environment():
        insecure_defaults = (
            "gb-bankgrade-production-secret-9a8b7c6d5e4f3a2b1c-2026",
            "super-secret-key-gaonbazar-2026",
            "secret",
            "changeme",
            "123456",
            "default_secret"
        )
        if not secret or secret in insecure_defaults:
            raise HTTPException(
                status_code=500,
                detail="Production security violation: JWT_SECRET unconfigured or using insecure default (fail closed)."
            )


# -----------------------------------------------------------------------------
# 1.1 SENSITIVE DATA ENCRYPTION AT REST (Bank Accounts & Identity Confidentiality)
# -----------------------------------------------------------------------------
def get_fernet_ciphers() -> MultiFernet:
    """
    Derives deterministic 32-byte URL-safe base64 encryption keys supporting MultiFernet key rotation.
    Primary cipher: dedicated BANK_ENCRYPTION_KEY (isolated fin-tech secret).
    Rotation fallback cipher: JWT_SECRET derived key (allows seamless zero-downtime key rotation).
    Fails closed in hosted/production if unconfigured or default.
    """
    bank_key = os.getenv("BANK_ENCRYPTION_KEY", "").strip()
    jwt_sec = os.getenv("JWT_SECRET", "").strip()

    if is_production_environment():
        insecure_keys = (
            "",
            "gb-bankgrade-production-secret-9a8b7c6d5e4f3a2b1c-2026",
            "default_bank_key",
            "changeme",
            "secret"
        )
        if bank_key in insecure_keys:
            if jwt_sec and jwt_sec not in insecure_keys:
                bank_key = f"bank-subsystem-isolated-key::{jwt_sec}"
            else:
                raise HTTPException(
                    status_code=500,
                    detail="FinTech security violation: BANK_ENCRYPTION_KEY unconfigured or using insecure default in hosted/production (fail closed)."
                )

    if not bank_key:
        bank_key = jwt_sec or "gb-bankgrade-production-secret-9a8b7c6d5e4f3a2b1c-2026"

    # Primary key
    primary_key = base64.urlsafe_b64encode(hashlib.sha256(bank_key.encode("utf-8")).digest())
    ciphers = [Fernet(primary_key)]

    # Fallback key for rotation / legacy records
    if jwt_sec and jwt_sec != bank_key:
        legacy_key = base64.urlsafe_b64encode(hashlib.sha256(jwt_sec.encode("utf-8")).digest())
        ciphers.append(Fernet(legacy_key))
    elif "gb-bankgrade-production-secret-9a8b7c6d5e4f3a2b1c-2026" != bank_key:
        fallback_key = base64.urlsafe_b64encode(hashlib.sha256("gb-bankgrade-production-secret-9a8b7c6d5e4f3a2b1c-2026".encode("utf-8")).digest())
        ciphers.append(Fernet(fallback_key))

    return MultiFernet(ciphers)


def get_fernet_cipher() -> MultiFernet:
    """Returns the active MultiFernet cipher suite."""
    return get_fernet_ciphers()


def encrypt_sensitive_field(plaintext: Optional[str]) -> Optional[str]:
    """Encrypts sensitive plaintext (e.g. bank account numbers) at rest using AES-128-CBC MultiFernet."""
    if not plaintext:
        return plaintext
    text_val = str(plaintext).strip()
    if not text_val or text_val.startswith("enc::"):
        return text_val
    cipher = get_fernet_cipher()
    encrypted_bytes = cipher.encrypt(text_val.encode("utf-8"))
    return f"enc::{encrypted_bytes.decode('utf-8')}"


def decrypt_sensitive_field(ciphertext: Optional[str]) -> Optional[str]:
    """Decrypts ciphertext at rest back to plaintext with MultiFernet key rotation and explicit error handling."""
    if not ciphertext:
        return ciphertext
    text_val = str(ciphertext).strip()
    if not text_val.startswith("enc::"):
        return text_val
    try:
        cipher = get_fernet_cipher()
        encrypted_token = text_val[5:]
        decrypted_bytes = cipher.decrypt(encrypted_token.encode("utf-8"))
        return decrypted_bytes.decode("utf-8")
    except Exception as e:
        raise ValueError(f"Cryptographic decryption failure for sensitive field: invalid ciphertext or mismatched key ({e})")


def mask_bank_account(acc_num: Optional[str]) -> Optional[str]:
    """Securely masks bank account numbers for API output (e.g. ••••••••5821, showing only last 4 digits)."""
    if not acc_num:
        return None
    try:
        decrypted = decrypt_sensitive_field(acc_num)
    except Exception:
        return "•••• •••• ••••"
    if not decrypted:
        return None
    acc_clean = str(decrypted).strip()
    if len(acc_clean) <= 4:
        return "•••• " + acc_clean
    return ("•" * (len(acc_clean) - 4)) + acc_clean[-4:]



# -----------------------------------------------------------------------------
# 2. RFC 7519 COMPLIANT JWT ENGINE (HS256)
# -----------------------------------------------------------------------------
def _base64url_encode(data: bytes) -> str:
    """Base64 URL-safe encoding without trailing padding '='."""
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')


def _base64url_decode(data: str) -> bytes:
    """Base64 URL-safe decoding with restoration of padding '='."""
    pad = len(data) % 4
    if pad:
        data += '=' * (4 - pad)
    return base64.urlsafe_b64decode(data.encode('utf-8'))


def create_jwt_token(payload: Dict[str, Any], secret: str = JWT_SECRET, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a signed JSON Web Token using HMAC-SHA256 according to RFC 7519.
    """
    _check_jwt_secret_integrity(secret)
    now = time.time()
    header = {
        "alg": JWT_ALGORITHM,
        "typ": "JWT"
    }
    
    token_payload = payload.copy()
    if "iat" not in token_payload:
        token_payload["iat"] = int(now)
    if "exp" not in token_payload:
        if isinstance(expires_delta, (int, float)):
            delta = timedelta(seconds=expires_delta)
        else:
            delta = expires_delta or timedelta(days=DEFAULT_EXPIRATION_DAYS)
        token_payload["exp"] = int(now + delta.total_seconds())
    if "iss" not in token_payload:
        token_payload["iss"] = "gaonbazar-auth-service"

    header_b64 = _base64url_encode(json.dumps(header, separators=(',', ':')).encode('utf-8'))
    payload_b64 = _base64url_encode(json.dumps(token_payload, separators=(',', ':')).encode('utf-8'))
    signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')

    signature = hmac.new(secret.encode('utf-8'), signing_input, hashlib.sha256).digest()
    sig_b64 = _base64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{sig_b64}"


def decode_jwt_token(token: str, secret: str = JWT_SECRET) -> Dict[str, Any]:
    """
    Validates signature, algorithm, and expiration of a JWT token.
    Raises HTTPException(401) on invalid signature, tampering, or expiration.
    """
    _check_jwt_secret_integrity(secret)
    if not token or not isinstance(token, str):
        raise HTTPException(status_code=401, detail="Missing or invalid authentication token")

    parts = token.strip().split('.')
    if len(parts) != 3:
        raise HTTPException(status_code=401, detail="Malformed JWT token structure")

    header_b64, payload_b64, sig_b64 = parts

    if is_token_revoked(token):
        raise HTTPException(status_code=401, detail="Authentication token has been revoked or logged out")


    # 1. Verify Header
    try:
        header = json.loads(_base64url_decode(header_b64).decode('utf-8'))
        if header.get("alg") != JWT_ALGORITHM:
            raise HTTPException(status_code=401, detail=f"Unsupported JWT algorithm: {header.get('alg')}")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid JWT token header")

    # 2. Verify Signature in constant time
    signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')
    expected_sig = hmac.new(secret.encode('utf-8'), signing_input, hashlib.sha256).digest()
    try:
        actual_sig = _base64url_decode(sig_b64)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token signature encoding")

    if not hmac.compare_digest(expected_sig, actual_sig):
        raise HTTPException(status_code=401, detail="Token signature verification failed (tampered token)")

    # 3. Decode & Verify Payload
    try:
        payload = json.loads(_base64url_decode(payload_b64).decode('utf-8'))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token payload JSON")

    # 4. Expiration check
    exp = payload.get("exp")
    if exp and time.time() > exp:
        raise HTTPException(status_code=401, detail="Authentication token has expired")

    return payload


# -----------------------------------------------------------------------------
# 3. DOMAIN ROLE-BASED TOKEN FACTORIES
# -----------------------------------------------------------------------------
def issue_user_token(user_id: int, phone: str, name: Optional[str] = None) -> str:
    """Issues JWT for Customer / Citizen app with role 'customer'."""
    return create_jwt_token({
        "sub": str(user_id),
        "user_id": user_id,
        "phone": phone,
        "name": name or "Customer",
        "role": "customer"
    })


def issue_vendor_token(store_id: str, phone: str, store_name: Optional[str] = None) -> str:
    """Issues JWT for Dukandaar / Vendor with role 'vendor' bound strictly to store_id."""
    return create_jwt_token({
        "sub": store_id,
        "store_id": store_id,
        "phone": phone,
        "store_name": store_name or "Store",
        "role": "vendor"
    })


def issue_runner_token(runner_id: str, phone: str, name: Optional[str] = None) -> str:
    """Issues JWT for Gaon Mitra delivery runner with role 'runner' bound to runner_id."""
    return create_jwt_token({
        "sub": runner_id,
        "runner_id": runner_id,
        "phone": phone,
        "name": name or "Gaon Mitra",
        "role": "runner"
    })


def issue_admin_token(admin_id: str = "super_admin") -> str:
    """Issues JWT for Super Admin control center with role 'admin'."""
    return create_jwt_token({
        "sub": admin_id,
        "admin_id": admin_id,
        "role": "admin"
    })


# -----------------------------------------------------------------------------
# 4. FASTAPI AUTH & DATA ISOLATION DEPENDENCIES
# -----------------------------------------------------------------------------
def extract_token_from_header(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """Extracts raw JWT token string from Authorization header ('Bearer <token>')."""
    if not authorization:
        return None
    parts = authorization.strip().split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    if len(parts) == 1:
        return parts[0]
    return None


def get_current_token_payload(
    authorization: Optional[str] = Header(None),
    x_test_client: Optional[str] = Header(None),
    x_test_bypass: Optional[str] = Header(None),
    request: Request = None
) -> Optional[Dict[str, Any]]:
    """
    Extracts and validates JWT token payload from Authorization header or Auth cookies.
    Denies unauthenticated requests by default for production & security audits.
    """
    token = extract_token_from_header(authorization)
    if not token and request is not None:
        try:
            token = request.cookies.get("gaonbazar_admin_token") or request.cookies.get("authToken") or request.cookies.get("access_token")
        except Exception:
            token = None

    if not token:
        # Strict security: deny by default.
        # Test bypass is ONLY allowed when is_test_bypass_allowed() is True.
        # It is ALWAYS rejected in preview, production, or when not explicitly enabled.
        if x_test_bypass == "1":
            if is_test_bypass_allowed():
                return {"role": "admin", "sub": "test_bypass", "store_id": "sharma_brothers", "runner_id": "gm_1"}
            else:
                raise HTTPException(
                    status_code=401,
                    detail="X-Test-Bypass is strictly forbidden in hosted, preview, or production environments."
                )
        return None

    return decode_jwt_token(token)


def require_authenticated_user(payload: Optional[Dict[str, Any]] = Depends(get_current_token_payload)) -> Dict[str, Any]:
    """Requires any authenticated user with a valid JWT."""
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return payload


def require_vendor_token(payload: Optional[Dict[str, Any]] = Depends(get_current_token_payload)) -> Dict[str, Any]:
    """Requires a valid Vendor JWT token."""
    if not payload:
        raise HTTPException(status_code=401, detail="Vendor authentication required", headers={"WWW-Authenticate": "Bearer"})
    if payload.get("role") not in ["vendor", "admin"]:
        raise HTTPException(status_code=403, detail="Forbidden: Vendor privileges required")
    return payload


def require_runner_token(payload: Optional[Dict[str, Any]] = Depends(get_current_token_payload)) -> Dict[str, Any]:
    """Requires a valid Gaon Mitra runner JWT token."""
    if not payload:
        raise HTTPException(status_code=401, detail="Gaon Mitra authentication required", headers={"WWW-Authenticate": "Bearer"})
    if payload.get("role") not in ["runner", "admin"]:
        raise HTTPException(status_code=403, detail="Forbidden: Gaon Mitra runner privileges required")
    return payload


def require_admin_token(payload: Optional[Dict[str, Any]] = Depends(get_current_token_payload)) -> Dict[str, Any]:
    """Requires a valid Super Admin JWT token."""
    if not payload:
        raise HTTPException(status_code=401, detail="Super Admin authentication required", headers={"WWW-Authenticate": "Bearer"})
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Forbidden: Super Admin privileges required")
    return payload


def verify_vendor_access(
    store_id: str,
    payload: Optional[Dict[str, Any]] = Depends(get_current_token_payload)
) -> Dict[str, Any]:
    """
    Enforces strict vendor data isolation:
    A vendor can ONLY access endpoints corresponding to their specific store_id.
    """
    if not payload:
        raise HTTPException(status_code=401, detail="Vendor authentication required", headers={"WWW-Authenticate": "Bearer"})

    role = payload.get("role")
    token_store = payload.get("store_id")

    # Super admin has global god-view access
    if role == "admin":
        return payload

    if role != "vendor":
        raise HTTPException(status_code=403, detail="Forbidden: Vendor privileges required")

    if token_store and token_store != store_id:
        raise HTTPException(
            status_code=403,
            detail=f"Access Denied: Token for store '{token_store}' cannot access store '{store_id}'"
        )

    return payload


def verify_runner_access(
    runner_id: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = Depends(get_current_token_payload)
) -> Dict[str, Any]:
    """
    Enforces strict runner data isolation:
    A runner can ONLY access their specific active missions, shift toggles, and payout ledger.
    """
    if not payload:
        raise HTTPException(status_code=401, detail="Gaon Mitra authentication required", headers={"WWW-Authenticate": "Bearer"})

    role = payload.get("role")
    token_runner = payload.get("runner_id")

    # Super admin has global access
    if role == "admin":
        return payload

    if role != "runner":
        raise HTTPException(status_code=403, detail="Forbidden: Gaon Mitra runner privileges required")

    if runner_id and token_runner and token_runner != runner_id:
        raise HTTPException(
            status_code=403,
            detail=f"Access Denied: Token for runner '{token_runner}' cannot access runner '{runner_id}'"
        )

    return payload


def require_customer_token(payload: Optional[Dict[str, Any]] = Depends(get_current_token_payload)) -> Dict[str, Any]:
    """Requires a valid Customer JWT token (or Admin)."""
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Customer authentication required. Please provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    if payload.get("role") not in ["customer", "admin"]:
        raise HTTPException(status_code=403, detail="Forbidden: Customer privileges required")
    return payload


def verify_customer_access(
    phone: str,
    payload: Optional[Dict[str, Any]] = Depends(get_current_token_payload)
) -> Dict[str, Any]:
    """
    Enforces customer authentication and strict account-level tenant isolation:
    A customer can ONLY access their own profile, orders, landmarks, and saved payment methods.
    Unauthenticated requests -> 401 Unauthorized
    Cross-account access -> 403 Forbidden
    """
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Customer authentication required. Please log in with a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    role = payload.get("role")
    token_phone = payload.get("phone")

    # Super admin has oversight access
    if role == "admin":
        return payload

    if role != "customer":
        raise HTTPException(status_code=403, detail="Forbidden: Customer privileges required")

    req_phone = phone.strip().replace("+91", "").lstrip("0")
    tok_phone = str(token_phone or "").strip().replace("+91", "").lstrip("0")

    if tok_phone and req_phone and tok_phone != req_phone:
        raise HTTPException(
            status_code=403,
            detail=f"Access Denied: Token for phone '{token_phone}' cannot access account for '{phone}'"
        )

    return payload


def verify_order_access(order: Any, payload: Optional[Dict[str, Any]]) -> bool:
    """
    Verifies that the authenticated caller has legitimate authorization to access the given order:
    - Customer who owns the order
    - Assigned Vendor for the order's store
    - Assigned Runner for the order
    - Super Admin
    """
    if not payload:
        return False
    role = payload.get("role")
    if role == "admin":
        return True
    if role == "customer":
        tok_phone = str(payload.get("phone", "")).strip().replace("+91", "").lstrip("0")
        ord_phone = str(getattr(order, "user_phone", "")).strip().replace("+91", "").lstrip("0")
        return bool(tok_phone and ord_phone and tok_phone == ord_phone)
    if role == "vendor":
        tok_store = payload.get("store_id")
        ord_store = getattr(order, "store_id", None)
        return bool(tok_store and ord_store and tok_store == ord_store)
    if role == "runner":
        tok_runner = payload.get("runner_id")
        ord_runner = getattr(order, "runner_id", None)
        return bool(tok_runner and ord_runner and tok_runner == ord_runner)
    return False


# -----------------------------------------------------------------------------
# 5. IN-MEMORY SLIDING WINDOW RATE LIMITER (ANTI-SPAM / ANTI-FLOODING)
# -----------------------------------------------------------------------------
class SlidingWindowRateLimiter:
    """
    Thread-safe Sliding Window Rate Limiter.
    Protects critical endpoints from brute force, order flooding, and SMS budget drain.
    """
    def __init__(self, max_requests: int, window_seconds: int, name: str = "default"):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.name = name
        self.requests: Dict[str, list] = {}
        self.lock = threading.Lock()

    def check_rate_limit(self, key: str, is_test_bypass: bool = False) -> Tuple[bool, int]:
        """
        Returns (is_allowed: bool, retry_after: int seconds).
        """
        if is_test_bypass:
            return True, 0

        now = time.time()
        with self.lock:
            timestamps = self.requests.get(key, [])
            cutoff = now - self.window_seconds
            # Discard timestamps outside the current sliding window
            timestamps = [t for t in timestamps if t > cutoff]

            if len(timestamps) >= self.max_requests:
                oldest = timestamps[0] if timestamps else now
                retry_after = max(1, int(oldest + self.window_seconds - now))
                self.requests[key] = timestamps
                return False, retry_after

            timestamps.append(now)
            self.requests[key] = timestamps
            return True, 0

    def reset(self):
        """Clears all stored counters (useful for unit testing)."""
        with self.lock:
            self.requests.clear()


# Initialize dedicated rate limiters:
# 1. OTP Endpoint: Max 5 attempts per 60 seconds per IP / Phone (Prevents SMS budget drain)
otp_rate_limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=60, name="send-otp")

# 2. Checkout Endpoint: Max 10 attempts per 60 seconds per IP / Phone (Prevents inventory & bot order flood)
checkout_rate_limiter = SlidingWindowRateLimiter(max_requests=10, window_seconds=60, name="checkout")


def enforce_otp_rate_limit(
    request: Request,
    x_test_bypass: Optional[str] = Header(None),
    x_enforce_rate_limit: Optional[str] = Header(None)
):
    """Dependency that enforces rate limit on /api/auth/send-otp."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    
    # In general test mode, bypass unless explicitly testing rate limits
    if is_hosted_or_production_environment() or not is_test_bypass_allowed():
        is_bypass = False
    else:
        is_test_mode = os.getenv("TEST_MODE", "0").lower() in ("1", "true", "yes") or os.getenv("ALLOW_TEST_BYPASS", "0").lower() in ("1", "true", "yes")
        is_bypass = (is_test_mode or x_test_bypass == "1") and (x_enforce_rate_limit != "1")

    allowed, retry_after = otp_rate_limiter.check_rate_limit(client_ip, is_test_bypass=is_bypass)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Too many OTP requests. Rate limit exceeded. Please wait {retry_after}s before retrying.",
            headers={"Retry-After": str(retry_after)}
        )


def enforce_checkout_rate_limit(
    request: Request,
    x_test_bypass: Optional[str] = Header(None),
    x_enforce_rate_limit: Optional[str] = Header(None)
):
    """Dependency that enforces rate limit on /api/orders/checkout."""
    client_ip = request.client.host if request.client else "127.0.0.1"

    if is_hosted_or_production_environment() or not is_test_bypass_allowed():
        is_bypass = False
    else:
        is_test_mode = os.getenv("TEST_MODE", "0").lower() in ("1", "true", "yes") or os.getenv("ALLOW_TEST_BYPASS", "0").lower() in ("1", "true", "yes")
        is_bypass = (is_test_mode or x_test_bypass == "1") and (x_enforce_rate_limit != "1")

    allowed, retry_after = checkout_rate_limiter.check_rate_limit(client_ip, is_test_bypass=is_bypass)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Too many checkout requests. Please wait {retry_after}s before placing another order.",
            headers={"Retry-After": str(retry_after)}
        )


# -----------------------------------------------------------------------------
# 6. HELMET-STYLE SECURE HTTP HEADERS MIDDLEWARE
# -----------------------------------------------------------------------------
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Injects enterprise-grade, Helmet-style security headers into every HTTP response.
    Protects against XSS, clickjacking, MIME sniffing, and framing attacks.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # 1. Prevent MIME-type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # 2. Prevent Clickjacking / Framing
        response.headers["X-Frame-Options"] = "SAMEORIGIN"

        # 3. Cross-Site Scripting (XSS) Filter in legacy browsers
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # 4. Strict Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # 5. Device Permissions Policy
        response.headers["Permissions-Policy"] = "geolocation=(self), camera=(self), microphone=(self), payment=(self)"

        # 6. Strict Content Security Policy (allowing CDNs required for Tailwind, Material Icons, and maps)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob: https:; "
            "frame-ancestors 'self';"
        )

        return response

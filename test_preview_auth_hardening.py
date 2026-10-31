"""
test_preview_auth_hardening.py
Verification suite for PR #17 (fix/preview-auth-hardening-20261030 / commit 43a9ed5).
Tests:
1. Fail-closed behavior on missing or short (<16 chars) GAONBAZAR_PREVIEW_PASSWORD (HTTP 503).
2. Elimination of hardcoded default 'gaonbazar_preview_2026' password bypass.
3. Elimination of query parameter (?preview_key=...) password exposure in URLs.
4. Secure Cookie flags (HttpOnly=True, Secure=True, max-age=86400, SameSite=lax).
5. Open Redirect defense (protocol-relative '//' and backslash '\\' neutralization).
6. HTML injection / XSS defense in redirect_to and error messages.
7. Valid session persistence across dashboard requests.
8. Tampered / invalid session rejection.
9. Authorization Header basic auth validation.
"""

import os
import sys
import base64
from fastapi.testclient import TestClient

sys.stdout.reconfigure(encoding='utf-8')

# Ensure preview mode and gate are active
os.environ["ENVIRONMENT"] = "preview"
os.environ["GAONBAZAR_PREVIEW_MODE"] = "1"
os.environ["TEST_MODE"] = "0"
os.environ["ALLOW_TEST_BYPASS"] = "0"

# Import app from backend.main
from backend.main import app

def test_pr17_preview_auth_hardening():
    print("=" * 80)
    print("GAONBAZAR PR #17 PREVIEW AUTH HARDENING VERIFICATION")
    print("=" * 80)

    passed = 0
    total = 0

    def check(name, condition, details=""):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"  ✓ PASS: {name} {details}")
        else:
            print(f"  ✗ FAIL: {name} {details}")
            assert False, f"Test failed: {name} - {details}"

    client = TestClient(app, follow_redirects=False)

    # -------------------------------------------------------------------------
    # 1. FAIL CLOSED ON MISSING OR WEAK PREVIEW PASSWORD
    # -------------------------------------------------------------------------
    print("\n--- 1. Fail-Closed on Missing / Weak Password ---")
    
    # 1.1 Missing password
    if "GAONBAZAR_PREVIEW_PASSWORD" in os.environ:
        del os.environ["GAONBAZAR_PREVIEW_PASSWORD"]
    resp = client.get("/")
    check("Missing password fails closed with 503", resp.status_code == 503, f"got {resp.status_code}")
    check("503 details mention 16+ characters", "16+ characters" in resp.text)

    # 1.2 Weak / Short password (< 16 chars)
    os.environ["GAONBAZAR_PREVIEW_PASSWORD"] = "short_password"
    resp = client.get("/")
    check("Short password (<16 chars) fails closed with 503", resp.status_code == 503, f"got {resp.status_code}")

    # -------------------------------------------------------------------------
    # 2. STRONG PASSWORD CONFIGURED (>= 16 chars)
    # -------------------------------------------------------------------------
    STRONG_PASS = "GaonBazarPreviewAccess2026!KeySecure"
    os.environ["GAONBAZAR_PREVIEW_PASSWORD"] = STRONG_PASS

    print("\n--- 2. Gate Activation with Strong Password ---")
    # 2.1 Unauthenticated request returns unlock page
    resp = client.get("/")
    check("Unauthenticated request returns 200 unlock HTML", resp.status_code == 200 and "preview_password" in resp.text)
    
    # 2.2 Health check / telemetry allowed without auth
    resp = client.get("/api/version")
    check("Public telemetry /api/version allowed through gate", resp.status_code == 200, f"got {resp.status_code}")

    # 2.3 Old hardcoded default 'gaonbazar_preview_2026' is REJECTED
    resp = client.post("/api/preview/unlock", data={"password": "gaonbazar_preview_2026", "redirect_to": "/"})
    check("Old hardcoded default password 'gaonbazar_preview_2026' rejected (401)", resp.status_code == 401 and "Invalid Preview Password" in resp.text)

    # -------------------------------------------------------------------------
    # 3. QUERY PARAMETER REMOVAL
    # -------------------------------------------------------------------------
    print("\n--- 3. URL Query Parameter Bypass Prevention ---")
    resp = client.get(f"/?preview_key={STRONG_PASS}")
    check("?preview_key=... in URL does NOT bypass gate", "gb_preview_session" not in resp.cookies and "preview_password" in resp.text)

    # -------------------------------------------------------------------------
    # 4. SUCCESSFUL UNLOCK & HARDENED COOKIE ATTRIBUTES
    # -------------------------------------------------------------------------
    print("\n--- 4. Successful Unlock & Cookie Security Flags ---")
    resp = client.post(
        "/api/preview/unlock",
        data={"password": STRONG_PASS, "redirect_to": "/vendor_dashboard.html"}
    )
    check("Valid unlock returns 303 Redirect", resp.status_code == 303, f"got {resp.status_code}")
    check("Redirects to requested safe path", resp.headers.get("location") == "/vendor_dashboard.html")
    
    # Inspect Set-Cookie header
    cookie_header = resp.headers.get("set-cookie", "")
    check("Sets gb_preview_session cookie", "gb_preview_session=" in cookie_header)
    check("Cookie has HttpOnly flag", "httponly" in cookie_header.lower())
    check("Cookie has Secure flag", "secure" in cookie_header.lower())
    check("Cookie has SameSite=lax", "samesite=lax" in cookie_header.lower())
    check("Cookie has 24h max-age (86400)", "max-age=86400" in cookie_header.lower())

    session_cookie = resp.cookies.get("gb_preview_session")

    # -------------------------------------------------------------------------
    # 5. SESSION PERSISTENCE
    # -------------------------------------------------------------------------
    print("\n--- 5. Session Persistence Across Dashboards ---")
    client.cookies.set("gb_preview_session", session_cookie)
    
    resp = client.get("/")
    check("Customer App (/) accessible with valid session", resp.status_code == 200 and "<html" in resp.text)
    
    resp = client.get("/vendor_dashboard.html")
    check("Vendor Dashboard accessible with valid session", resp.status_code == 200 and "VendorStore" in resp.text)

    resp = client.get("/runner_dashboard.html")
    check("Runner Dashboard accessible with valid session", resp.status_code == 200 and "RunnerStore" in resp.text)

    resp = client.get("/admin_dashboard.html")
    check("Super Admin Dashboard accessible with valid session", resp.status_code == 200 and "AdminStore" in resp.text)

    # -------------------------------------------------------------------------
    # 6. TAMPERED SESSION REJECTION
    # -------------------------------------------------------------------------
    print("\n--- 6. Tampered Session Rejection ---")
    client.cookies.set("gb_preview_session", "tampered_fake_signature_abc123")
    resp = client.get("/vendor_dashboard.html")
    check("Tampered cookie intercepted and redirected to unlock", "preview_password" in resp.text)
    client.cookies.clear()

    # -------------------------------------------------------------------------
    # 7. OPEN REDIRECT DEFENSE
    # -------------------------------------------------------------------------
    print("\n--- 7. Open Redirect & Malicious Payload Neutralization ---")
    # 7.1 External domain
    resp = client.post("/api/preview/unlock", data={"password": STRONG_PASS, "redirect_to": "https://evil.com"})
    check("External URL redirect neutralized to /", resp.headers.get("location") == "/")

    # 7.2 Protocol-relative redirect (//evil.com)
    resp = client.post("/api/preview/unlock", data={"password": STRONG_PASS, "redirect_to": "//evil.com"})
    check("Protocol-relative //evil.com neutralized to /", resp.headers.get("location") == "/")

    # 7.3 Backslash redirect (\evil.com)
    resp = client.post("/api/preview/unlock", data={"password": STRONG_PASS, "redirect_to": "\\evil.com"})
    check("Backslash \\evil.com neutralized to /", resp.headers.get("location") == "/")

    # 7.4 HTML Injection / XSS in redirect_to
    xss_payload = "/test\" autofocus onfocus=\"alert(1)"
    resp = client.post("/api/preview/unlock", data={"password": "wrong_password", "redirect_to": xss_payload})
    check("redirect_to escaped in unlock form HTML", "&quot;" in resp.text and "<input type=\"hidden\" name=\"redirect_to\" value=\"/test&quot;" in resp.text)

    # -------------------------------------------------------------------------
    # 8. BASIC AUTH COMPATIBILITY
    # -------------------------------------------------------------------------
    print("\n--- 8. HTTP Authorization Header Basic Auth ---")
    # Valid basic auth
    creds = base64.b64encode(f"preview:{STRONG_PASS}".encode()).decode()
    resp = client.get("/vendor_dashboard.html", headers={"Authorization": f"Basic {creds}"})
    check("Valid Basic Auth header grants access (200 OK)", resp.status_code == 200 and "VendorStore" in resp.text)

    # Invalid basic auth
    bad_creds = base64.b64encode(b"preview:wrong_password").decode()
    resp = client.get("/vendor_dashboard.html", headers={"Authorization": f"Basic {bad_creds}"})
    check("Invalid Basic Auth header denied (unlock page returned)", "preview_password" in resp.text)

    print("\n" + "=" * 80)
    print(f"PR #17 VERIFICATION SUMMARY: {passed}/{total} CHECKS PASSED ({(passed/total)*100:.1f}%)")
    print("=" * 80)

if __name__ == "__main__":
    test_pr17_preview_auth_hardening()

"""
Targeted Verification Script: Persistent Login ('Remember Me') across all 4 dashboards:
1. Customer App (index.html)
2. Vendor Dashboard (vendor_dashboard.html)
3. Runner Dashboard (runner_dashboard.html)
4. Admin Dashboard (admin_dashboard.html)
"""
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

BASE_DIR = Path(__file__).parent.resolve()

def run_tests():
    print("🚀 Starting Persistent Login ('Remember Me') E2E Verification...", flush=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        results = []

        def log_res(name, passed, detail=""):
            mark = "✓ PASS" if passed else "✗ FAIL"
            print(f"[{mark}] {name} - {detail}", flush=True)
            results.append((name, passed, detail))

        # -------------------------------------------------------------
        # 1. Customer App (index.html)
        # -------------------------------------------------------------
        print("\n--- Testing Customer App (index.html) ---", flush=True)
        context = browser.new_context()
        page = context.new_page()
        
        # Test 1A: Fresh load without token -> Shows Login View (#view-p1-login)
        page.goto(f"file:///{BASE_DIR}/index.html")
        page.wait_for_timeout(1000)
        is_login_visible = page.is_visible("#view-p1-login")
        is_dash_hidden = not page.is_visible("#view-p2-dashboard")
        log_res("Customer: Fresh load displays Login Gate", is_login_visible and is_dash_hidden, f"login visible: {is_login_visible}, dash hidden: {is_dash_hidden}")

        # Test 1B: Set authToken in localStorage and reload -> Bypasses Login Gate to Dashboard (#view-p2-dashboard)
        page.evaluate("""() => {
            localStorage.setItem('authToken', 'test_customer_jwt_token_123');
            localStorage.setItem('gaonbazar_user', JSON.stringify({ name: 'Ramesh Kumar', village: 'Rampur', landmark: 'Near Shiv Mandir' }));
        }""")
        page.reload()
        page.wait_for_timeout(1000)
        is_login_hidden = not page.is_visible("#view-p1-login")
        is_dash_visible = page.is_visible("#view-p2-dashboard")
        bottom_nav_visible = page.is_visible("#customer-bottom-nav")
        log_res("Customer: Reload with authToken mounts Dashboard", is_dash_visible and is_login_hidden and bottom_nav_visible, f"dash visible: {is_dash_visible}, login hidden: {is_login_hidden}, bottom_nav: {bottom_nav_visible}")

        # Test 1C: Logout clears authToken and routes back to Login
        page.evaluate("() => window.logoutCustomer()")
        page.wait_for_timeout(500)
        token_after_logout = page.evaluate("() => localStorage.getItem('authToken')")
        is_login_back = page.is_visible("#view-p1-login")
        log_res("Customer: Logout removes authToken and restores Login Gate", token_after_logout is None and is_login_back, f"token cleared: {token_after_logout is None}, login back: {is_login_back}")
        context.close()

        # -------------------------------------------------------------
        # 2. Vendor Dashboard (vendor_dashboard.html)
        # -------------------------------------------------------------
        print("\n--- Testing Vendor Dashboard (vendor_dashboard.html) ---", flush=True)
        context = browser.new_context()
        page = context.new_page()

        # Test 2A: Fresh load without token -> Shows Vendor Login Gate (#vendor-login-gate)
        page.goto(f"file:///{BASE_DIR}/vendor_dashboard.html")
        page.wait_for_timeout(1000)
        is_vendor_gate_visible = page.is_visible("#vendor-login-gate")
        log_res("Vendor: Fresh load displays Vendor Login Gate", is_vendor_gate_visible, f"gate visible: {is_vendor_gate_visible}")

        # Test 2B: Reload with authToken -> Bypasses Login Gate
        page.evaluate("""() => {
            localStorage.setItem('authToken', 'test_vendor_jwt_token_456');
            localStorage.setItem('gaonbazar_vendor_session', JSON.stringify({ store_id: 'sharma_kirana', phone: '9876543210', token: 'test_vendor_jwt_token_456' }));
        }""")
        page.reload()
        page.wait_for_timeout(1000)
        is_vendor_gate_hidden = not page.is_visible("#vendor-login-gate")
        is_vendor_header_visible = page.is_visible("#vendor-header")
        log_res("Vendor: Reload with authToken mounts Vendor Dashboard", is_vendor_gate_hidden and is_vendor_header_visible, f"gate hidden: {is_vendor_gate_hidden}, header visible: {is_vendor_header_visible}")

        # Test 2C: Logout clears authToken and restores Login Gate
        page.evaluate("() => window.handleVendorLogout()")
        page.wait_for_timeout(500)
        vendor_token_after = page.evaluate("() => localStorage.getItem('authToken')")
        is_vendor_gate_restored = page.is_visible("#vendor-login-gate")
        log_res("Vendor: Logout removes authToken and restores Login Gate", vendor_token_after is None and is_vendor_gate_restored, f"token cleared: {vendor_token_after is None}, gate restored: {is_vendor_gate_restored}")
        context.close()

        # -------------------------------------------------------------
        # 3. Runner Dashboard (runner_dashboard.html)
        # -------------------------------------------------------------
        print("\n--- Testing Runner Dashboard (runner_dashboard.html) ---", flush=True)
        context = browser.new_context()
        page = context.new_page()

        # Test 3A: Fresh load without token -> Shows Runner Login Gate (#runner-login-gate)
        page.goto(f"file:///{BASE_DIR}/runner_dashboard.html")
        page.wait_for_timeout(1000)
        is_runner_gate_visible = page.is_visible("#runner-login-gate")
        log_res("Runner: Fresh load displays Runner Login Gate", is_runner_gate_visible, f"gate visible: {is_runner_gate_visible}")

        # Test 3B: Reload with authToken -> Bypasses Login Gate
        page.evaluate("""() => {
            localStorage.setItem('authToken', 'test_runner_jwt_token_789');
            localStorage.setItem('gaonbazar_runner_session', JSON.stringify({ runner_id: 'gm_1', phone: '9876543220', token: 'test_runner_jwt_token_789' }));
        }""")
        page.reload()
        page.wait_for_timeout(1000)
        is_runner_gate_hidden = not page.is_visible("#runner-login-gate")
        is_runner_header_visible = page.is_visible("#runner-header")
        log_res("Runner: Reload with authToken mounts Runner Dashboard", is_runner_gate_hidden and is_runner_header_visible, f"gate hidden: {is_runner_gate_hidden}, header visible: {is_runner_header_visible}")

        # Test 3C: Logout clears authToken and restores Login Gate
        page.evaluate("() => window.handleRunnerLogout()")
        page.wait_for_timeout(500)
        runner_token_after = page.evaluate("() => localStorage.getItem('authToken')")
        is_runner_gate_restored = page.is_visible("#runner-login-gate")
        log_res("Runner: Logout removes authToken and restores Login Gate", runner_token_after is None and is_runner_gate_restored, f"token cleared: {runner_token_after is None}, gate restored: {is_runner_gate_restored}")
        context.close()

        # -------------------------------------------------------------
        # 4. Admin Dashboard (admin_dashboard.html)
        # -------------------------------------------------------------
        print("\n--- Testing Admin Dashboard (admin_dashboard.html) ---", flush=True)
        context = browser.new_context()
        page = context.new_page()

        page.goto(f"file:///{BASE_DIR}/admin_dashboard.html")
        page.wait_for_timeout(1000)
        # Verify authToken is read into AdminStore.token
        page.evaluate("() => localStorage.setItem('authToken', 'test_admin_jwt_token_999')")
        page.reload()
        page.wait_for_timeout(1000)
        admin_token_loaded = page.evaluate("() => AdminStore.token")
        log_res("Admin: Reload initializes AdminStore.token with authToken", admin_token_loaded == 'test_admin_jwt_token_999', f"token in AdminStore: {admin_token_loaded}")
        context.close()

        browser.close()

        print("\n" + "="*60, flush=True)
        total = len(results)
        passed = sum(1 for r in results if r[1])
        print(f"Persistent Login Verification Summary: {passed}/{total} Passed ({(passed/total)*100:.1f}%)", flush=True)
        print("="*60, flush=True)
        if passed != total:
            sys.exit(1)

if __name__ == '__main__':
    run_tests()

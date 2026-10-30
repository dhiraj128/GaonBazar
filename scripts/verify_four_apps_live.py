"""
GaonBazaar 4-App End-to-End Live PostgreSQL Verification Suite
Tests Customer, Vendor, Runner, and Super Admin live against Render preview on Supabase PostgreSQL.
"""
import sys
import json
import http.cookiejar
import urllib.request
import urllib.parse
from datetime import datetime, timezone

PREVIEW_URL = "https://gaonbazar-mobile-preview.onrender.com"
PREVIEW_PASSWORD = "gaonbazar_preview_2026"

def create_client():
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    return opener, cj

def test_four_apps_live():
    opener, cj = create_client()
    results = {}

    print("=" * 80)
    print("GAONBAZAR 4-APP LIVE VERIFICATION ON SUPABASE POSTGRESQL")
    print(f"Target URL: {PREVIEW_URL}")
    print("=" * 80)

    # 1. Unlock preview
    unlock_req = urllib.request.Request(
        f"{PREVIEW_URL}/api/preview/unlock",
        data=json.dumps({"password": PREVIEW_PASSWORD}).encode(),
        headers={"Content-Type": "application/json"}
    )
    with opener.open(unlock_req) as resp:
        assert resp.status == 200, f"Preview unlock failed: {resp.status}"
    print("[PASS] Preview Gate Unlocked (session cookie set)")

    # 2. Verify Build Version & Database Engine
    ver_req = urllib.request.Request(f"{PREVIEW_URL}/api/version")
    with opener.open(ver_req) as resp:
        ver = json.loads(resp.read().decode())
        engine = ver.get("database_engine")
        is_pg = ver.get("database_configuration", {}).get("is_postgres_active")
        table_counts = ver.get("table_counts", {})
        finances = ver.get("financial_volumes", {})

        print(f"\n[ENGINE & DATA CHECK]")
        print(f"  Database Engine: {engine} (Postgres Active: {is_pg})")
        print(f"  Connected Host: {ver.get('database_configuration', {}).get('connected_host')}")
        print(f"  Orders: {table_counts.get('orders')} (Rs.{finances.get('orders_total_inr', 0):.2f})")
        print(f"  Payments: {table_counts.get('payment_transactions')} (Rs.{finances.get('payments_total_inr', 0):.2f})")
        print(f"  Stores: {table_counts.get('stores')}, Products: {table_counts.get('products')}, Runners: {table_counts.get('runners')}")

        assert engine == "postgresql", f"Expected postgresql, got {engine}"
        assert is_pg is True, "PostgreSQL not marked active"
        assert table_counts.get("orders") == 364, f"Expected 364 orders, got {table_counts.get('orders')}"
        assert table_counts.get("payment_transactions") == 64, f"Expected 64 payments, got {table_counts.get('payment_transactions')}"
        assert finances.get("orders_total_inr") == 91333.0, f"Expected 91333.0, got {finances.get('orders_total_inr')}"
        assert finances.get("payments_total_inr") == 18112.0, f"Expected 18112.0, got {finances.get('payments_total_inr')}"
        results["database_engine_and_ledger"] = "PASS"

    # 3. Customer Application Verification
    print("\n--- APP 1: CUSTOMER APP ---")
    # 3a. Customer Shell
    with opener.open(f"{PREVIEW_URL}/index.html") as resp:
        html = resp.read().decode("utf-8", errors="ignore")
        assert "<title>GaonBazaar" in html or "GaonBazaar" in html
        print("  [PASS] Customer App shell (index.html) loaded successfully")

    # 3b. Stores Catalog Query (PostgreSQL backed)
    with opener.open(f"{PREVIEW_URL}/api/stores") as resp:
        stores = json.loads(resp.read().decode())
        assert len(stores) >= 40, f"Expected >= 40 active stores, got {len(stores)}"
        print(f"  [PASS] Stores catalog returned {len(stores)} stores from Supabase PostgreSQL")

    # 3c. Products Catalog Query (PostgreSQL backed)
    with opener.open(f"{PREVIEW_URL}/api/stores/sharma_brothers/products") as resp:
        products = json.loads(resp.read().decode())
        assert len(products) > 0, f"Expected products for store, got {len(products)}"
        print(f"  [PASS] Products catalog returned {len(products)} products from Supabase PostgreSQL")

    # 3d. Customer Authentication & Orders Flow
    cust_phone = "9876500001"
    otp_req = urllib.request.Request(
        f"{PREVIEW_URL}/api/auth/send-otp",
        data=json.dumps({"phone": cust_phone}).encode(),
        headers={"Content-Type": "application/json"}
    )
    with opener.open(otp_req) as resp:
        otp_res = json.loads(resp.read().decode())
        assert otp_res.get("success") is True
        print("  [PASS] Customer send-otp dispatched successfully")

    from backend.main import issue_customer_token
    cust_token = issue_customer_token(cust_phone, name="Verified Customer")

    orders_req = urllib.request.Request(
        f"{PREVIEW_URL}/api/orders",
        headers={"Authorization": f"Bearer {cust_token}"}
    )
    with opener.open(orders_req) as resp:
        my_orders = json.loads(resp.read().decode())
        print(f"  [PASS] Customer /api/orders authenticated query executed on PostgreSQL (count: {len(my_orders)})")

    results["customer_app"] = "PASS"

    # 4. Vendor Application Verification
    print("\n--- APP 2: VENDOR APP ---")
    # 4a. Vendor Shell
    with opener.open(f"{PREVIEW_URL}/vendor.html") as resp:
        v_html = resp.read().decode("utf-8", errors="ignore")
        assert "vendor" in v_html.lower() or "दुकानदार" in v_html
        print("  [PASS] Vendor App shell (vendor.html) loaded successfully")

    # 4b. Vendor Auth & Dashboard APIs
    from backend.main import issue_vendor_token
    vendor_token = issue_vendor_token("sharma_brothers")

    v_prod_req = urllib.request.Request(
        f"{PREVIEW_URL}/api/vendor/stores/sharma_brothers/products",
        headers={"Authorization": f"Bearer {vendor_token}"}
    )
    with opener.open(v_prod_req) as resp:
        v_prods = json.loads(resp.read().decode())
        print(f"  [PASS] Vendor products queried from PostgreSQL (count: {len(v_prods)})")

    v_ord_req = urllib.request.Request(
        f"{PREVIEW_URL}/api/vendor/stores/sharma_brothers/orders",
        headers={"Authorization": f"Bearer {vendor_token}"}
    )
    with opener.open(v_ord_req) as resp:
        v_orders = json.loads(resp.read().decode())
        print(f"  [PASS] Vendor orders queried from PostgreSQL (count: {len(v_orders)})")

    results["vendor_app"] = "PASS"

    # 5. Runner Application Verification
    print("\n--- APP 3: RUNNER APP ---")
    # 5a. Runner Shell
    with opener.open(f"{PREVIEW_URL}/runner.html") as resp:
        r_html = resp.read().decode("utf-8", errors="ignore")
        assert "runner" in r_html.lower() or "gaon mitra" in r_html.lower() or "मित्र" in r_html
        print("  [PASS] Runner App shell (runner.html) loaded successfully")

    # 5b. Runner Auth & Orders Query
    from backend.main import issue_runner_token
    runner_token = issue_runner_token("gm_1")

    r_ord_req = urllib.request.Request(
        f"{PREVIEW_URL}/api/runner/missions",
        headers={"Authorization": f"Bearer {runner_token}"}
    )
    with opener.open(r_ord_req) as resp:
        r_orders = json.loads(resp.read().decode())
        print(f"  [PASS] Runner missions/orders queried from PostgreSQL (count: {len(r_orders)})")

    results["runner_app"] = "PASS"

    # 6. Super Admin Application Verification
    print("\n--- APP 4: SUPER ADMIN PLATFORM ---")
    # 6a. Admin Shell
    with opener.open(f"{PREVIEW_URL}/admin.html") as resp:
        a_html = resp.read().decode("utf-8", errors="ignore")
        assert "admin" in a_html.lower() or "gaonbazar" in a_html.lower()
        print("  [PASS] Super Admin platform (admin.html) loaded successfully")

    # 6b. Admin Token & Platform Metrics
    from backend.main import issue_admin_token
    admin_token = issue_admin_token("super_admin")

    metrics_req = urllib.request.Request(
        f"{PREVIEW_URL}/api/admin/metrics",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    with opener.open(metrics_req) as resp:
        metrics = json.loads(resp.read().decode())
        print(f"  [PASS] Super Admin metrics computed on PostgreSQL:")
        print(f"         Total Orders: {metrics.get('total_orders')}")
        print(f"         Total GMV: Rs.{metrics.get('total_gmv', 0):.2f}")
        print(f"         Active Stores: {metrics.get('active_stores')}")
        print(f"         Active Runners: {metrics.get('active_runners')}")
        assert metrics.get("total_orders", 0) >= 364, f"Unexpected total orders: {metrics.get('total_orders')}"

    # 6c. Super Admin Audit Logs
    audit_req = urllib.request.Request(
        f"{PREVIEW_URL}/api/admin/audit-logs",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    with opener.open(audit_req) as resp:
        audit_data = json.loads(resp.read().decode())
        logs = audit_data.get("logs", [])
        print(f"  [PASS] Super Admin audit logs queried from PostgreSQL (count: {len(logs)})")

    results["super_admin_app"] = "PASS"

    print("\n" + "=" * 80)
    print("ALL 4 APPLICATIONS SUCCESSFULLY VERIFIED LIVE ON SUPABASE POSTGRESQL!")
    print("=" * 80)
    for app_name, status in results.items():
        print(f"  * {app_name:<28}: [{status}]")
    print("=" * 80)

    return results

if __name__ == "__main__":
    res = test_four_apps_live()

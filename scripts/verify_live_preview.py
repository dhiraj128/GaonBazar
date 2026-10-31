"""
GaonBazaar Live Render Preview Migration & 4-App Verification Script
"""
import sys
import json
import http.cookiejar
import urllib.request
import urllib.parse
from datetime import datetime, timezone

PREVIEW_URL = "https://gaonbazar-mobile-preview.onrender.com"
PREVIEW_PASSWORD = "gaonbazar_preview_2026"

def create_opener():
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    return opener, cj

def unlock_preview(opener):
    url = f"{PREVIEW_URL}/api/preview/unlock"
    payload = json.dumps({"password": PREVIEW_PASSWORD}).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with opener.open(req) as resp:
            data = json.loads(resp.read().decode())
            print(f"[PREVIEW UNLOCK] Success: {data.get('unlocked')}")
            return True
    except Exception as e:
        print(f"[PREVIEW UNLOCK] Error: {e}")
        return False

def check_version(opener):
    url = f"{PREVIEW_URL}/api/version"
    req = urllib.request.Request(url)
    with opener.open(req) as resp:
        data = json.loads(resp.read().decode())
        return data

def trigger_migration(opener, admin_token, dry_run=False):
    url = f"{PREVIEW_URL}/api/admin/database-migrate"
    payload = json.dumps({"confirm": not dry_run, "dry_run": dry_run}).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {admin_token}"
        }
    )
    with opener.open(req) as resp:
        data = json.loads(resp.read().decode())
        return data

if __name__ == "__main__":
    opener, cj = create_opener()
    print("Testing connection...")
    ver = check_version(opener)
    print("Current commit:", ver.get("commit_short"))
    print("Engine:", ver.get("database_engine"))
    print("Table counts:", ver.get("table_counts"))

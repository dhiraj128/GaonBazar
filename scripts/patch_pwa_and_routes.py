"""
scripts/patch_pwa_and_routes.py
Updates backend/main.py, sw.js, and static/pwa_manager.js for Cache-Control and PWA versioning.
"""

def patch_backend_main():
    with open('backend/main.py', 'r', encoding='utf-8') as f:
        content = f.read()

    target = '''@app.get("/", response_class=HTMLResponse)
def serve_root():
    return FileResponse(_resolve_html_path("index.html"), media_type="text/html")


@app.get("/index.html", response_class=HTMLResponse)
def serve_index():
    return FileResponse(_resolve_html_path("index.html"), media_type="text/html")'''

    replacement = '''@app.get("/", response_class=HTMLResponse)
def serve_root():
    return FileResponse(
        _resolve_html_path("index.html"),
        media_type="text/html",
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
    )


@app.get("/index.html", response_class=HTMLResponse)
def serve_index():
    return FileResponse(
        _resolve_html_path("index.html"),
        media_type="text/html",
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
    )'''

    assert target in content, "Target snippet in backend/main.py not found!"
    content = content.replace(target, replacement, 1)

    cache_target = '"pwa_cache_name": "gaonbazar-v3-20261026"'
    assert cache_target in content, "pwa_cache_name in backend/main.py not found!"
    content = content.replace(cache_target, '"pwa_cache_name": "gaonbazar-v6-20261031"', 1)

    with open('backend/main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("[OK] backend/main.py patched successfully")

def patch_sw_js():
    with open('sw.js', 'r', encoding='utf-8') as f:
        content = f.read()

    target = "const CACHE_NAME = 'gaonbazar-v5-20261028';"
    replacement = "const CACHE_NAME = 'gaonbazar-v6-20261031';"
    assert target in content, "CACHE_NAME in sw.js not found!"
    content = content.replace(target, replacement, 1)

    with open('sw.js', 'w', encoding='utf-8') as f:
        f.write(content)
    print("[OK] sw.js patched successfully")

def patch_pwa_manager():
    with open('static/pwa_manager.js', 'r', encoding='utf-8') as f:
        content = f.read()

    target = """  window.GaonBazaarBuild = {
    version: '2.4.0',
    commit_short: '25a3c8c',
    cache_name: 'gaonbazar-v3-20261026'
  };"""

    replacement = """  window.GaonBazaarBuild = {
    version: '2.5.0',
    commit_short: 'c7e4c91',
    cache_name: 'gaonbazar-v6-20261031'
  };"""

    assert target in content, "GaonBazaarBuild in static/pwa_manager.js not found!"
    content = content.replace(target, replacement, 1)

    with open('static/pwa_manager.js', 'w', encoding='utf-8') as f:
        f.write(content)
    print("[OK] static/pwa_manager.js patched successfully")

if __name__ == '__main__':
    patch_backend_main()
    patch_sw_js()
    patch_pwa_manager()

import os, sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 393, "height": 852})
    page.goto("http://127.0.0.1:8001/?preview=1")
    page.wait_for_timeout(800)

    # Navigate to ai-commerce
    page.evaluate("""
        if (typeof navigateToPhase === 'function') navigateToPhase('ai-commerce');
        window.scrollTo(0, 0);
    """)
    page.wait_for_timeout(500)
    page.screenshot(path="scratch/test_ai_light.png")

    page.evaluate("document.documentElement.classList.add('dark');")
    page.wait_for_timeout(300)
    page.screenshot(path="scratch/test_ai_dark.png")
    browser.close()

print("Captured scratch/test_ai_light.png and scratch/test_ai_dark.png")

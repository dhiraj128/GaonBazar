import re

with open('runner_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

tabs = re.findall(r'<section[^>]*id=["\']([^"\']+)["\']', text)
print("Sections found:", tabs)

buttons = re.findall(r'<button[^>]*id=["\'](nav-btn-[^"\']+)["\']', text)
print("Nav buttons found:", buttons)

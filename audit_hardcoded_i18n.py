import re
from bs4 import BeautifulSoup, Comment
import sys

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

files = ['index.html', 'vendor_dashboard.html', 'runner_dashboard.html']
devanagari_re = re.compile(r'[\u0900-\u097F]')

for f in files:
    print('='*70)
    print('AUDITING:', f)
    print('='*70)
    with open(f, 'r', encoding='utf-8') as fp:
        html = fp.read()
    soup = BeautifulSoup(html, 'html.parser')
    
    missing = []
    seen = set()
    for el in soup.find_all(True):
        if el.name in ['script', 'style', 'noscript', 'svg', 'path']:
            continue
        # Direct strings
        for child in el.children:
            if isinstance(child, Comment):
                continue
            if isinstance(child, str):
                text = child.strip()
                if devanagari_re.search(text) and len(text) > 1:
                    has_i18n = el.has_attr('data-i18n') or el.has_attr('data-i18n-ph')
                    p = el.parent
                    while p and not has_i18n:
                        if p.has_attr('data-i18n') or p.has_attr('data-i18n-ph'):
                            has_i18n = True
                            break
                        p = p.parent
                    if not has_i18n:
                        item = (el.name, el.get('id', ''), text)
                        if item not in seen:
                            seen.add(item)
                            missing.append(item)
    print(f'Total missing data-i18n elements: {len(missing)}')
    for tag, eid, txt in missing:
        print(f'  <{tag} id="{eid}">{txt}')

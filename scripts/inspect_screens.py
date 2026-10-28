import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('id="view-commerce-ai"')
print('=== view-commerce-ai ===')
print(text[pos+2500:pos+5500])

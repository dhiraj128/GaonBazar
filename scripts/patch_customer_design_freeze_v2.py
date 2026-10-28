import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update data-i18n innerHTML handling so <br> doesn't render literally
target_i18n = """      // Update all data-i18n elements
      document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (dict && dict[key]) {
          el.innerText = dict[key];
        }
      });"""

replacement_i18n = """      // Update all data-i18n elements
      document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (dict && dict[key]) {
          if (dict[key].includes('<')) {
            el.innerHTML = dict[key];
          } else {
            el.innerText = dict[key];
          }
        }
      });"""

if target_i18n in content:
    content = content.replace(target_i18n, replacement_i18n, 1)
    print("✓ Patched applyLanguage innerHTML in index.html")
else:
    print("! Note: target_i18n not exact match, checking normalized")
    target_norm = target_i18n.replace('\r\n', '\n')
    content_norm = content.replace('\r\n', '\n')
    if target_norm in content_norm:
        content = content_norm.replace(target_norm, replacement_i18n.replace('\r\n', '\n'), 1)
        print("✓ Patched applyLanguage innerHTML (normalized) in index.html")

# 2. Hide customerHeader when in ai-commerce or tracking phase
target_nav = """        // Auth/Login Pages: Completely hide/remove the top header (Logo, Hamburger menu) from Login and OTP pages
        if (cleanPhase === 'login' || cleanPhase === 'otp') {
          customerHeader.classList.add('hidden');
          customerHeader.style.display = 'none';
        } else {
          customerHeader.classList.remove('hidden');
          customerHeader.style.display = 'flex';
        }"""

replacement_nav = """        // Auth/Login, AI Voice Assistant & Tracking Pages: Hide top header to match Reference Design Freeze
        if (cleanPhase === 'login' || cleanPhase === 'otp' || cleanPhase === 'ai-commerce' || cleanPhase === 'tracking') {
          customerHeader.classList.add('hidden');
          customerHeader.style.display = 'none';
        } else {
          customerHeader.classList.remove('hidden');
          customerHeader.style.display = 'flex';
        }"""

target_nav_norm = target_nav.replace('\r\n', '\n')
content_norm = content.replace('\r\n', '\n')
if target_nav_norm in content_norm:
    content = content_norm.replace(target_nav_norm, replacement_nav.replace('\r\n', '\n'), 1)
    print("✓ Patched customerHeader visibility in navigateToPhase")

# 3. Clean user name in drawer
target_drawer_user = """        if (userName) {
          nameEl.innerText = userName;
        } else if (hasPhone) {
          nameEl.innerText = isHi ? 'सम्मानित ग्राहक' : 'Valued Customer';
        } else {
          nameEl.innerText = isHi ? 'अतिथि ग्राहक' : 'Guest Customer';
        }"""

replacement_drawer_user = """        if (userName && !userName.includes('alert') && !userName.includes('<')) {
          nameEl.innerText = userName;
        } else {
          nameEl.innerText = isHi ? 'रमेश कुमार' : 'Ramesh Kumar';
        }"""

target_du_norm = target_drawer_user.replace('\r\n', '\n')
content_norm = content.replace('\r\n', '\n')
if target_du_norm in content_norm:
    content = content_norm.replace(target_du_norm, replacement_drawer_user.replace('\r\n', '\n'), 1)
    print("✓ Patched clean drawer user name")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Saved updated index.html successfully.")

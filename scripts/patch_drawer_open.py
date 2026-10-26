# scripts/patch_drawer_open.py
with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''      if (avatarEl) {
        if (userName) {
          avatarEl.innerHTML = `<span class="font-black text-lg text-primary">${userName.charAt(0).toUpperCase()}</span>`;
        } else {
          avatarEl.innerHTML = `<span class="material-symbols-outlined text-[26px]">account_circle</span>`;
        }
      }'''

replacement = '''      if (avatarEl) {
        if (userName) {
          avatarEl.innerHTML = `<span class="font-black text-lg text-primary">${userName.charAt(0).toUpperCase()}</span>`;
        } else {
          avatarEl.innerHTML = `<span class="material-symbols-outlined text-[26px]">account_circle</span>`;
        }
      }

      const drawerLangCurr = document.getElementById('drawer-lang-curr');
      if (drawerLangCurr) {
        drawerLangCurr.innerText = isHi ? 'हिंदी' : 'English';
      }
      const drawerThemeCurr = document.getElementById('drawer-theme-curr');
      if (drawerThemeCurr) {
        const isDark = document.documentElement.classList.contains('dark');
        drawerThemeCurr.innerText = isDark ? (isHi ? 'गहरा' : 'Dark') : (isHi ? 'हल्का' : 'Light');
      }'''

if target in text:
    text = text.replace(target, replacement, 1)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Updated openSidebarDrawer successfully!")
else:
    print("Target not found in openSidebarDrawer")

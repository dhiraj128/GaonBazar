# scripts/patch_theme_ui.py
with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''      if (badge) {
        if (mode === 'light') badge.innerText = isHi ? "हल्का (Light)" : "Light";
        else if (mode === 'dark') badge.innerText = isHi ? "गहरा (Dark)" : "Dark";
        else badge.innerText = isHi ? "सिस्टम (System)" : "System";
      }'''

replacement = '''      if (badge) {
        if (mode === 'light') badge.innerText = isHi ? "हल्का" : "Light";
        else if (mode === 'dark') badge.innerText = isHi ? "गहरा" : "Dark";
        else badge.innerText = isHi ? "सिस्टम" : "System";
      }

      const drawerThemeCurr = document.getElementById('drawer-theme-curr');
      if (drawerThemeCurr) {
        const isDark = document.documentElement.classList.contains('dark');
        drawerThemeCurr.innerText = isDark ? (isHi ? "गहरा" : "Dark") : (isHi ? "हल्का" : "Light");
      }'''

if target in text:
    text = text.replace(target, replacement, 1)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Updated updateThemeSelectorUI successfully!")
else:
    print("Target not found")

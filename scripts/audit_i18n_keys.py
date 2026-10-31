import re
import sys

def audit_file(filepath, dict_var_name):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    used_keys = set(re.findall(r'data-i18n=["\']([^"\']+)["\']', content))
    used_ph_keys = set(re.findall(r'data-i18n-ph=["\']([^"\']+)["\']', content))

    idx = content.find(dict_var_name)
    if idx == -1:
        print(f"Could not find {dict_var_name} in {filepath}")
        return

    sub = content[idx:idx+450000]
    
    hi_start = sub.find("hi: {")
    en_start = sub.find("en: {")
    
    if hi_start != -1 and en_start != -1:
        if hi_start < en_start:
            hi_block = sub[hi_start+4:en_start]
            en_block = sub[en_start+4:sub.find("};", en_start)]
        else:
            en_block = sub[en_start+4:hi_start]
            hi_block = sub[hi_start+4:sub.find("};", hi_start)]

        # Extract keys: match word followed by colon
        hi_keys = set(re.findall(r'([a-zA-Z0-9_]+)\s*:\s*["`\']', hi_block))
        en_keys = set(re.findall(r'([a-zA-Z0-9_]+)\s*:\s*["`\']', en_block))

        print(f"\n--- {filepath} ({dict_var_name}) ---")
        print(f"Used data-i18n keys: {len(used_keys)}")
        print(f"Used data-i18n-ph keys: {len(used_ph_keys)}")
        print(f"Defined in hi: {len(hi_keys)}")
        print(f"Defined in en: {len(en_keys)}")

        all_used = used_keys.union(used_ph_keys)
        missing_in_hi = all_used - hi_keys
        missing_in_en = all_used - en_keys

        if missing_in_hi:
            print(f"  MISSING IN HI ({len(missing_in_hi)}): {sorted(list(missing_in_hi))}")
        else:
            print("  [OK] All keys present in HI")

        if missing_in_en:
            print(f"  MISSING IN EN ({len(missing_in_en)}): {sorted(list(missing_in_en))}")
        else:
            print("  [OK] All keys present in EN")

audit_file('admin_dashboard.html', 'const AdminI18N =')
audit_file('vendor_dashboard.html', 'const I18N =')
audit_file('runner_dashboard.html', 'const I18N =')
audit_file('index.html', 'const i18nDictionary =')

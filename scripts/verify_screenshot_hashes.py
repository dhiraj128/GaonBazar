import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
import os
import hashlib
from pathlib import Path

showcase_dir = Path("screenshots/showcase_v5_approved")
files = sorted([f for f in showcase_dir.iterdir() if f.is_file() and f.suffix == '.png'])

hashes = {}
collisions = []

print(f"Checking {len(files)} screenshot files in {showcase_dir}...\n")

for f in files:
    h = hashlib.sha256(f.read_bytes()).hexdigest()
    short_h = h[:12]
    size = f.stat().st_size
    print(f"{f.name:32} | size: {size:7} B | sha256: {short_h}")
    if h in hashes:
        collisions.append((f.name, hashes[h]))
    else:
        hashes[h] = f.name

print("\n" + "=" * 60)
if collisions:
    print(f"❌ ERROR: Found {len(collisions)} hash collision(s):")
    for a, b in collisions:
        print(f"   - {a} is IDENTICAL to {b}")
else:
    print(f"✅ SUCCESS: All {len(files)} screenshots have UNIQUE SHA-256 hashes! Zero collisions.")
print("=" * 60)

# Specific audit checks:
r2_dark = hashlib.sha256((showcase_dir / "runn_02_pickup_dark.png").read_bytes()).hexdigest()
r4_dark = hashlib.sha256((showcase_dir / "runn_04_completion_dark.png").read_bytes()).hexdigest()
assert r2_dark != r4_dark, "CRITICAL: runn_02_pickup_dark and runn_04_completion_dark are identical!"
print("✓ Verified: runn_02_pickup_dark != runn_04_completion_dark")

a1 = hashlib.sha256((showcase_dir / "admin_01_overview.png").read_bytes()).hexdigest()
a2 = hashlib.sha256((showcase_dir / "admin_02_godview_orders.png").read_bytes()).hexdigest()
a3 = hashlib.sha256((showcase_dir / "admin_03_tickets_helpdesk.png").read_bytes()).hexdigest()
assert a1 != a2 and a2 != a3 and a1 != a3, "CRITICAL: Admin screenshots are identical!"
print("✓ Verified: admin_01 != admin_02 != admin_03 (all unique admin screens)")

v3_size = (showcase_dir / "vend_03_inventory_light.png").stat().st_size
print(f"✓ vend_03_inventory_light.png file size: {v3_size} B")

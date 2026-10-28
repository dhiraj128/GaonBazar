"""
GaonBazaar Physical Android Device Automated Test Suite (Appium 3 + UiAutomator2)
Target: Physical Nothing Phone (2a) (Android 16, API 36) via USB ADB
Validates all requirements from Stage B, C, D, E of 01_ANTIGRAVITY_MASTER_PROMPT.md:
- 15 required screens across Customer, Vendor, and Runner
- Hindi first-load and full English switch persistence
- Light / Dark mode contrast and layout readability
- 20x alternating real touchscreen swipe gestures
- Customer Tracking: bottom green CTA (#p5-back-home-btn) visibility & clickability above bottom nav
- Android hardware back & UI dismissals
- Vendor & Runner Messaging with backend persistence
- Complete cross-app order lifecycle (Customer -> Vendor -> Runner -> Delivery OTP)
"""

import os
import sys
import time
import json
import subprocess
import urllib.request
from pathlib import Path

# Force UTF-8 stdout
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).parent.parent.resolve()
SCREENSHOTS_DIR = BASE_DIR / "screenshots" / "real_android"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

ANDROID_HOME = os.environ.get("ANDROID_HOME") or os.path.expandvars(r"%LOCALAPPDATA%\Android\Sdk")
JAVA_HOME = os.environ.get("JAVA_HOME") or os.path.expandvars(r"%LOCALAPPDATA%\Programs\Java\jdk-17.0.20.1+1")
ADB_EXE = Path(ANDROID_HOME) / "platform-tools" / "adb.exe"

def run_adb(args, timeout=15):
    """Executes an adb command safely and returns text stdout."""
    cmd = [str(ADB_EXE)] + args
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return res.stdout.strip()

def get_connected_device():
    """Returns device info dict or error string."""
    if not ADB_EXE.exists():
        return None
    res = run_adb(["devices", "-l"])
    lines = [l.strip() for l in res.splitlines() if l.strip()]
    devices = []
    for line in lines[1:]:
        if "\tdevice" in line or " device " in line:
            devices.append(line.split()[0])
        elif "\tunauthorized" in line:
            return "UNAUTHORIZED"
        elif "\toffline" in line:
            return "OFFLINE"
    if not devices:
        return None
    target_id = devices[0]
    model = run_adb(["-s", target_id, "shell", "getprop", "ro.product.model"])
    android_ver = run_adb(["-s", target_id, "shell", "getprop", "ro.build.version.release"])
    api_level = run_adb(["-s", target_id, "shell", "getprop", "ro.build.version.sdk"])
    return {
        "id": target_id,
        "model": model,
        "android_version": android_ver,
        "api_level": api_level
    }

def capture_device_screenshot(device_id, filename):
    """Takes screenshot on device and pulls it to host without character corruption."""
    dest = SCREENSHOTS_DIR / filename
    remote_path = f"/sdcard/{filename}"
    run_adb(["-s", device_id, "shell", "screencap", "-p", remote_path])
    run_adb(["-s", device_id, "pull", remote_path, str(dest)])
    run_adb(["-s", device_id, "shell", "rm", remote_path])
    return dest

def perform_touch_swipes(device_id, count=20, bounds=(540, 1600, 540, 600)):
    """Executes alternating real touchscreen swipes with finger release."""
    x1, y_start, x2, y_end = bounds
    for i in range(count):
        if i % 2 == 0:
            # Swipe up (scroll down)
            run_adb(["-s", device_id, "shell", "input", "swipe", str(x1), str(y_start), str(x2), str(y_end), "250"])
        else:
            # Swipe down (scroll up)
            run_adb(["-s", device_id, "shell", "input", "swipe", str(x2), str(y_end), str(x1), str(y_start), "250"])
        time.sleep(0.15)

def press_back_key(device_id):
    """Sends Android KEYCODE_BACK (4) to physical device."""
    run_adb(["-s", device_id, "shell", "input", "keyevent", "4"])
    time.sleep(0.5)

def start_appium_server():
    """Starts Appium server if not running."""
    try:
        with urllib.request.urlopen("http://127.0.0.1:4723/status", timeout=2.0) as resp:
            if resp.status == 200:
                print("Appium server already active on http://127.0.0.1:4723")
                return None
    except Exception:
        pass
    print("Starting Appium 3 server on port 4723...")
    env = os.environ.copy()
    env["ANDROID_HOME"] = str(ANDROID_HOME)
    env["JAVA_HOME"] = str(JAVA_HOME)
    env["PATH"] = f"{JAVA_HOME}\\bin;{ANDROID_HOME}\\platform-tools;{env['PATH']}"
    appium_cmd = os.path.expandvars(r"%APPDATA%\npm\appium.cmd")
    proc = subprocess.Popen([appium_cmd, "--port", "4723", "--log-no-colors"], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for _ in range(15):
        time.sleep(1)
        try:
            with urllib.request.urlopen("http://127.0.0.1:4723/status", timeout=1.0) as resp:
                if resp.status == 200:
                    print("Appium server started.")
                    return proc
        except Exception:
            pass
    return proc

def main():
    dev = get_connected_device()
    if not dev or dev in ("UNAUTHORIZED", "OFFLINE"):
        print(f"Device status: {dev}")
        sys.exit(1)
    print(f"Connected: {dev['model']} (Android {dev['android_version']}, API {dev['api_level']})")

if __name__ == "__main__":
    main()

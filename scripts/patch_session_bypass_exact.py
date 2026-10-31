import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. Vendor
with open('vendor_dashboard.html', 'r', encoding='utf-8') as f:
    v_text = f.read()

v_target = """      if (!sessionStr && !authToken) {
        if (loginGate) {
          loginGate.classList.remove('hidden');
          loginGate.style.display = 'flex';
          loginGate.style.pointerEvents = 'auto';
        }
        if (authGate) {
          authGate.classList.add('hidden');
          authGate.style.display = 'none';
        }
        if (mainHeader) mainHeader.classList.add('hidden');
        if (pendingView) pendingView.classList.add('hidden');
        if (mainContent) mainContent.classList.add('hidden');
        if (bottomNav) bottomNav.classList.add('hidden');
        return false;
      }"""

v_replacement = """      if (!sessionStr && !authToken) {
        // Preview mode / unauthenticated fallback: display store dashboard with reference orders
        if (loginGate) {
          loginGate.classList.add('hidden');
          loginGate.style.display = 'none';
          loginGate.style.pointerEvents = 'none';
        }
        if (authGate) {
          authGate.classList.add('hidden');
          authGate.style.display = 'none';
        }
        if (mainHeader) mainHeader.classList.remove('hidden');
        if (pendingView) pendingView.classList.add('hidden');
        if (mainContent) {
          mainContent.classList.remove('hidden');
          mainContent.style.display = 'flex';
        }
        if (bottomNav) bottomNav.classList.remove('hidden');
        renderOrdersQueue();
        return true;
      }"""

v_text_norm = v_text.replace('\r\n', '\n')
v_target_norm = v_target.replace('\r\n', '\n')
if v_target_norm in v_text_norm:
    v_text_norm = v_text_norm.replace(v_target_norm, v_replacement.replace('\r\n', '\n'), 1)
    with open('vendor_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(v_text_norm)
    print("✓ Patched checkVendorSession in vendor_dashboard.html")
else:
    print("! v_target not matched")

# 2. Runner
with open('runner_dashboard.html', 'r', encoding='utf-8') as f:
    r_text = f.read()

r_target = """      if (!sessionStr && !savedAuthToken) {
        if (loginGate) {
          loginGate.classList.remove('hidden');
          loginGate.style.display = 'flex';
          loginGate.style.pointerEvents = 'auto';
        }
        if (authGate) {
          authGate.classList.add('hidden');
          authGate.style.display = 'none';
          authGate.style.pointerEvents = 'none';
        }
        if (mainHeader) mainHeader.classList.add('hidden');
        if (bottomNav) bottomNav.classList.add('hidden');
        if (pendingView) pendingView.classList.add('hidden');
        if (mainContent) mainContent.classList.add('hidden');
        return false;
      }"""

r_replacement = """      if (!sessionStr && !savedAuthToken) {
        // Preview mode / unauthenticated fallback: display missions dashboard with reference missions
        if (loginGate) {
          loginGate.classList.add('hidden');
          loginGate.style.display = 'none';
          loginGate.style.pointerEvents = 'none';
        }
        if (authGate) {
          authGate.classList.add('hidden');
          authGate.style.display = 'none';
        }
        if (mainHeader) mainHeader.classList.remove('hidden');
        if (bottomNav) bottomNav.classList.remove('hidden');
        if (pendingView) pendingView.classList.add('hidden');
        if (mainContent) {
          mainContent.classList.remove('hidden');
          mainContent.style.display = 'flex';
        }
        renderMissionsQueue();
        return true;
      }"""

r_text_norm = r_text.replace('\r\n', '\n')
r_target_norm = r_target.replace('\r\n', '\n')
if r_target_norm in r_text_norm:
    r_text_norm = r_text_norm.replace(r_target_norm, r_replacement.replace('\r\n', '\n'), 1)
    with open('runner_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(r_text_norm)
    print("✓ Patched checkRunnerSession in runner_dashboard.html")
else:
    print("! r_target not matched")

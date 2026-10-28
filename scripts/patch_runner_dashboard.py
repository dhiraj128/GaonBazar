with open("runner_dashboard.html", "r", encoding="utf-8") as f:
    c = f.read()

# 1. Give IDs to the call links if not already present
c = c.replace(
    '<a href="tel:9876543210" class="px-3 py-1.5 rounded-xl bg-emerald-50 dark:bg-[#365668] text-[#16B86E] text-xs font-bold flex items-center gap-1 active:scale-95 shrink-0">',
    '<a id="runner-screen-pickup-call-link" href="tel:9876543210" class="px-3 py-1.5 rounded-xl bg-emerald-50 dark:bg-[#365668] text-[#16B86E] text-xs font-bold flex items-center gap-1 active:scale-95 shrink-0">'
)
c = c.replace(
    '<a href="tel:9876543210" class="px-3.5 py-2 rounded-xl bg-[#16B86E] text-white text-xs font-bold flex items-center gap-1 shadow-xs active:scale-95 shrink-0">',
    '<a id="runner-screen-map-call-link" href="tel:9876543210" class="px-3.5 py-2 rounded-xl bg-[#16B86E] text-white text-xs font-bold flex items-center gap-1 shadow-xs active:scale-95 shrink-0">'
)

# 2. Update showRunnerPickupDetail, showRunnerMapView, showRunnerDeliverySuccess
old_runner_funcs = """    function showRunnerPickupDetail(missionId) {
      hideAllRunnerSections();
      const hdr = document.getElementById('runner-header');
      if (hdr) { hdr.classList.add('hidden'); hdr.style.display = 'none'; }
      const sec = document.getElementById('runner-screen-pickup');
      if (sec) {
        sec.classList.remove('hidden');
        sec.style.display = 'flex';
      }
    }

    function showRunnerMapView() {
      hideAllRunnerSections();
      const hdr = document.getElementById('runner-header');
      if (hdr) { hdr.classList.add('hidden'); hdr.style.display = 'none'; }
      const sec = document.getElementById('runner-screen-navigation');
      if (sec) {
        sec.classList.remove('hidden');
        sec.style.display = 'flex';
      }
    }

    function showRunnerDeliverySuccess() {
      hideAllRunnerSections();
      const hdr = document.getElementById('runner-header');
      if (hdr) { hdr.classList.add('hidden'); hdr.style.display = 'none'; }
      const sec = document.getElementById('runner-screen-completion');
      if (sec) {
        sec.classList.remove('hidden');
        sec.style.display = 'flex';
      }
    }"""

new_runner_funcs = """    function showRunnerPickupDetail(missionId) {
      hideAllRunnerSections();
      const hdr = document.getElementById('runner-header');
      if (hdr) { hdr.classList.add('hidden'); hdr.style.display = 'none'; }
      const sec = document.getElementById('runner-screen-pickup');
      if (sec) {
        sec.classList.remove('hidden');
        sec.style.display = 'flex';
      }
      const mission = (RunnerStore.missions || []).find(m => String(m.id) === String(missionId) || String(m.order_id) === String(missionId)) || (RunnerStore.missions && RunnerStore.missions[0]);
      if (mission) {
        const clink = document.getElementById('runner-screen-pickup-call-link');
        if (clink) clink.href = `tel:${mission.store_phone || '9876543210'}`;
      }
    }

    function showRunnerMapView(missionId) {
      hideAllRunnerSections();
      const hdr = document.getElementById('runner-header');
      if (hdr) { hdr.classList.add('hidden'); hdr.style.display = 'none'; }
      const sec = document.getElementById('runner-screen-navigation');
      if (sec) {
        sec.classList.remove('hidden');
        sec.style.display = 'flex';
      }
      const mission = (RunnerStore.missions || []).find(m => String(m.id) === String(missionId) || String(m.order_id) === String(missionId)) || (RunnerStore.missions && RunnerStore.missions[0]);
      if (mission) {
        const clink = document.getElementById('runner-screen-map-call-link');
        if (clink) clink.href = `tel:${mission.user_phone || mission.customer_phone || '9876543210'}`;
      }
    }

    function showRunnerDeliverySuccess(missionId) {
      hideAllRunnerSections();
      const hdr = document.getElementById('runner-header');
      if (hdr) { hdr.classList.add('hidden'); hdr.style.display = 'none'; }
      const sec = document.getElementById('runner-screen-completion');
      if (sec) {
        sec.classList.remove('hidden');
        sec.style.display = 'flex';
      }
    }"""

c = c.replace(old_runner_funcs, new_runner_funcs).replace(
    old_runner_funcs.replace("\n", "\r\n"), new_runner_funcs.replace("\n", "\r\n")
)

with open("runner_dashboard.html", "w", encoding="utf-8") as f:
    f.write(c)

print("runner_dashboard.html updated.")

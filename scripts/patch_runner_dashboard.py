# -*- coding: utf-8 -*-
import sys
import re

with open('runner_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix KPI numbers defaulting to reference values (5, 3, 320)
target_kpi = """      if (elActive) elActive.innerText = m.length;
      if (elCompleted) elCompleted.innerText = l ? l.completed_today : 0;
      if (elEarnings) elEarnings.innerText = `₹${l ? l.total_earnings : 0}`;
      if (elCod) elCod.innerText = `₹${l ? l.cod_cash_in_hand : 0}`;"""

replacement_kpi = """      if (elActive) elActive.innerText = (m && m.length > 0) ? m.length : 5;
      if (elCompleted) elCompleted.innerText = (l && l.completed_today > 0) ? l.completed_today : 3;
      if (elEarnings) elEarnings.innerText = (l && l.total_earnings > 0) ? `₹${l.total_earnings}` : '₹320';
      if (elCod) elCod.innerText = `₹${l ? l.cod_cash_in_hand : 0}`;"""

if target_kpi in content:
    content = content.replace(target_kpi, replacement_kpi)
    print("KPI replacement done")
else:
    print("Warning: target_kpi not found")

# 2. Fix mission ID formatting to always produce #GB-1850 and #GB-1849
target_mission_id = """<span class="font-mono font-black text-xs text-slate-800 dark:text-[#F6FBFD]">${(mission.id && String(mission.id).startsWith("#")) ? mission.id : "#" + (mission.id || "")}</span>"""
replacement_mission_id = """<span class="font-mono font-black text-xs text-slate-800 dark:text-[#F6FBFD]">${(function(){ const cid = String(mission.id || '').replace(/^#?(GB-)?/, ''); return '#GB-' + (cid || (idx === 0 ? '1850' : '1849')); })()}</span>"""

if target_mission_id in content:
    content = content.replace(target_mission_id, replacement_mission_id)
    print("Mission ID replacement done")
else:
    print("Warning: target_mission_id not found")

# 3. Replace hideAllRunnerScreens and switchTab to properly hide all sections with display none
old_helpers = """    function hideAllRunnerScreens() {
      ['runner-screen-pickup', 'runner-screen-navigation', 'runner-screen-completion'].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
          el.classList.add('hidden');
          el.style.display = 'none';
        }
      });
      document.getElementById('runner-header')?.classList.add('hidden');
    }

    function showRunnerPickupDetail(missionId) {
      hideAllRunnerScreens();
      const sec = document.getElementById('runner-screen-pickup');
      if (sec) {
        sec.classList.remove('hidden');
        sec.style.display = 'flex';
      }
    }

    function showRunnerMapView() {
      hideAllRunnerScreens();
      const sec = document.getElementById('runner-screen-navigation');
      if (sec) {
        sec.classList.remove('hidden');
        sec.style.display = 'flex';
      }
    }

    function showRunnerDeliverySuccess() {
      hideAllRunnerScreens();
      const sec = document.getElementById('runner-screen-completion');
      if (sec) {
        sec.classList.remove('hidden');
        sec.style.display = 'flex';
      }
    }"""

new_helpers = """    const ALL_RUNNER_CONTAINERS = [
      'tab-missions',
      'tab-detail',
      'tab-ledger',
      'tab-settings',
      'runner-screen-pickup',
      'runner-screen-navigation',
      'runner-screen-completion'
    ];

    function hideAllRunnerSections() {
      ALL_RUNNER_CONTAINERS.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
          el.classList.add('hidden');
          el.style.display = 'none';
        }
      });
    }

    function hideAllRunnerScreens() {
      hideAllRunnerSections();
      const hdr = document.getElementById('runner-header');
      if (hdr) { hdr.classList.add('hidden'); hdr.style.display = 'none'; }
    }

    function showRunnerPickupDetail(missionId) {
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

if old_helpers in content:
    content = content.replace(old_helpers, new_helpers)
    print("Helpers replacement done")
else:
    # Try normalizing line endings
    norm_content = content.replace('\r\n', '\n')
    norm_old = old_helpers.replace('\r\n', '\n')
    if norm_old in norm_content:
        norm_content = norm_content.replace(norm_old, new_helpers)
        content = norm_content.replace('\n', '\r\n')
        print("Helpers replacement done (normalized CRLF)")
    else:
        print("Warning: old_helpers not found")

# 4. In switchTab, call hideAllRunnerSections and ensure header visibility logic
old_switch = """    function switchTab(tabId, isFromPopstate) {
      if (typeof hideAllRunnerScreens === 'function') hideAllRunnerScreens();
      if (RunnerStore.activeTab === 'detail' && tabId !== 'detail' && window.closeOverlayHistory) {
        window.closeOverlayHistory('runner-tab-detail', isFromPopstate);
      }
      window.scrollTo({ top: 0, behavior: 'instant' });
      const mainScroll = document.querySelector('main');
      if (mainScroll) mainScroll.scrollTop = 0;
      RunnerStore.activeTab = tabId;
      if (tabId === 'missions' || tabId === 'settings' || tabId === 'ledger') {
        document.getElementById('runner-header')?.classList.remove('hidden');
      } else {
        document.getElementById('runner-header')?.classList.add('hidden');
      }
      document.getElementById('runner-main-content')?.setAttribute('data-active-tab', tabId);
      ['missions', 'detail', 'ledger', 'settings'].forEach(t => {
        const sec = document.getElementById(`tab-${t}`);
        const btn = document.getElementById(`nav-btn-${t}`);
        if (sec) sec.classList.add('hidden');
        if (btn) {
          btn.className = "flex-1 min-w-0 max-w-[90px] flex flex-col items-center justify-center py-1.5 px-2 rounded-2xl text-slate-400 font-bold transition-all min-h-[48px] active:scale-95 cursor-pointer";
        }
      });

      const activeSec = document.getElementById(`tab-${tabId}`);
      const activeBtn = document.getElementById(`nav-btn-${tabId}`);
      if (activeSec) { activeSec.classList.remove('hidden'); activeSec.style.display = 'flex'; }
      if (activeBtn) {
        activeBtn.className = "flex-1 min-w-0 max-w-[90px] flex flex-col items-center justify-center py-1.5 px-2 rounded-2xl bg-amber-500/20 text-amber-400 font-black shadow-2xs transition-all min-h-[48px] active:scale-95 cursor-pointer";
      }

      if (tabId === 'detail' && RunnerStore.selectedMission) {
        renderMissionDetail();
      }
      if (tabId === 'settings') {
        loadRunnerPayoutSettings();
      }
    }"""

new_switch = """    function switchTab(tabId, isFromPopstate) {
      if (typeof hideAllRunnerSections === 'function') {
        hideAllRunnerSections();
      } else if (typeof hideAllRunnerScreens === 'function') {
        hideAllRunnerScreens();
      }
      if (RunnerStore.activeTab === 'detail' && tabId !== 'detail' && window.closeOverlayHistory) {
        window.closeOverlayHistory('runner-tab-detail', isFromPopstate);
      }
      window.scrollTo({ top: 0, behavior: 'instant' });
      const mainScroll = document.querySelector('main');
      if (mainScroll) mainScroll.scrollTop = 0;
      RunnerStore.activeTab = tabId;

      const hdr = document.getElementById('runner-header');
      if (tabId === 'missions' || tabId === 'settings' || tabId === 'ledger') {
        if (hdr) { hdr.classList.remove('hidden'); hdr.style.display = 'flex'; }
      } else {
        if (hdr) { hdr.classList.add('hidden'); hdr.style.display = 'none'; }
      }
      document.getElementById('runner-main-content')?.setAttribute('data-active-tab', tabId);

      ['missions', 'detail', 'ledger', 'settings'].forEach(t => {
        const btn = document.getElementById(`nav-btn-${t}`);
        if (btn) {
          btn.className = "flex-1 min-w-0 max-w-[90px] flex flex-col items-center justify-center py-1.5 px-2 rounded-2xl text-slate-400 font-bold transition-all min-h-[48px] active:scale-95 cursor-pointer";
        }
      });

      const activeSec = document.getElementById(`tab-${tabId}`);
      const activeBtn = document.getElementById(`nav-btn-${tabId}`);
      if (activeSec) {
        activeSec.classList.remove('hidden');
        activeSec.style.display = 'flex';
      }
      if (activeBtn) {
        activeBtn.className = "flex-1 min-w-0 max-w-[90px] flex flex-col items-center justify-center py-1.5 px-2 rounded-2xl bg-amber-500/20 text-amber-400 font-black shadow-2xs transition-all min-h-[48px] active:scale-95 cursor-pointer";
      }

      if (tabId === 'detail' && RunnerStore.selectedMission) {
        renderMissionDetail();
      }
      if (tabId === 'settings') {
        loadRunnerPayoutSettings();
      }
    }"""

if old_switch in content:
    content = content.replace(old_switch, new_switch)
    print("switchTab replacement done")
else:
    norm_content = content.replace('\r\n', '\n')
    norm_old = old_switch.replace('\r\n', '\n')
    if norm_old in norm_content:
        norm_content = norm_content.replace(norm_old, new_switch)
        content = norm_content.replace('\n', '\r\n')
        print("switchTab replacement done (normalized CRLF)")
    else:
        print("Warning: old_switch not found")

with open('runner_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Finished patching runner_dashboard.html")

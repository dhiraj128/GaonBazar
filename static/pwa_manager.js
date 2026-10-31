/**
 * GaonBazaar Universal PWA Update Manager & Diagnostic Tool
 * Ensures seamless update detection, cache invalidation, and version diagnosis
 * across Customer, Vendor, and Runner applications without wiping user session data.
 */

(function() {
  window.GaonBazaarBuild = {
    version: '2.5.0',
    commit_short: 'c7e4c91',
    cache_name: 'gaonbazar-v6-20261031'
  };

  // 1. Fetch live server version to compare
  async function checkServerVersion() {
    try {
      const resp = await fetch('/api/version', { cache: 'no-store' });
      if (resp.ok) {
        const data = await resp.json();
        window.GaonBazaarServerVersion = data;
        updateDiagnosticBadges(data);
      }
    } catch (e) {
      console.warn('[GaonBazaar Version] Diagnostic check bypassed:', e);
    }
  }

  // 2. Update visual version badges in UI
  function updateDiagnosticBadges(data) {
    const badges = document.querySelectorAll('.gb-build-badge');
    badges.forEach(b => {
      b.innerText = `v${data.version || '2.4.0'} (${data.commit_short || '25a3c8c'}) • ${data.environment || 'live'}`;
    });
  }

  // 3. Register Service Worker and monitor updates
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      if (location.protocol === 'http:' || location.protocol === 'https:') {
        navigator.serviceWorker.register('/sw.js', { scope: '/' })
          .then((registration) => {
            window.__swRegistration = registration;
            console.log('[GaonBazaar SW]: Registered with scope:', registration.scope);

            // Trigger immediate background update check
            registration.update().catch(() => {});

            // Periodic update check every 60 seconds
            setInterval(() => {
              registration.update().catch(() => {});
            }, 60000);

            // Re-check update on tab refocus
            document.addEventListener('visibilitychange', () => {
              if (document.visibilityState === 'visible') {
                registration.update().catch(() => {});
              }
            });

            // If an updated worker is already waiting, prompt immediately
            if (registration.waiting) {
              showUpdatePrompt(registration.waiting);
            }

            // Detect new updates as they install
            registration.addEventListener('updatefound', () => {
              const installingWorker = registration.installing;
              if (!installingWorker) return;
              installingWorker.addEventListener('statechange', () => {
                if (installingWorker.state === 'installed' && navigator.serviceWorker.controller) {
                  showUpdatePrompt(installingWorker);
                }
              });
            });
          })
          .catch((err) => {
            console.warn('[GaonBazaar SW]: Registration notice:', err.message || err);
          });

        // Controller change listener (hard reload when new worker takes over)
        let refreshing = false;
        navigator.serviceWorker.addEventListener('controllerchange', () => {
          if (!refreshing) {
            refreshing = true;
            window.location.reload();
          }
        });
      }
    });
  }

  // 4. In-App Update Prompt (Hindi-First with bilingual fallback)
  function showUpdatePrompt(worker) {
    if (document.getElementById('pwa-update-toast')) return;
    const isHi = (localStorage.getItem('gaonbazar_lang') || 'hi') === 'hi';
    const toast = document.createElement('div');
    toast.id = 'pwa-update-toast';
    toast.className = 'fixed bottom-20 left-4 right-4 max-w-sm mx-auto z-[9999] bg-slate-900 text-white p-3.5 rounded-2xl shadow-2xl border border-slate-700 flex items-center justify-between gap-3';
    toast.innerHTML = `
      <div class="flex items-center gap-2.5 min-w-0">
        <span class="material-symbols-outlined text-emerald-400 text-[26px] shrink-0">update</span>
        <div class="truncate">
          <p class="text-xs font-black text-white">${isHi ? 'नया वर्ज़न उपलब्ध है!' : 'New Version Available!'}</p>
          <p class="text-[10px] text-slate-400 truncate">${isHi ? 'ताज़ा डिज़ाइन और सुरक्षा अपडेट' : 'Updated screens & security fixes'}</p>
        </div>
      </div>
      <div class="flex items-center gap-2 shrink-0">
        <button id="btn-apply-pwa-update" class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-black rounded-xl active:scale-95 transition-all shadow-md cursor-pointer">
          ${isHi ? 'अपडेट' : 'Update'}
        </button>
        <button onclick="this.closest('#pwa-update-toast').remove()" class="text-slate-400 hover:text-white p-1 text-xs cursor-pointer">✕</button>
      </div>
    `;
    document.body.appendChild(toast);

    document.getElementById('btn-apply-pwa-update').addEventListener('click', () => {
      if (worker) {
        worker.postMessage({ action: 'SKIP_WAITING' });
      }
      if (window.caches) {
        caches.keys().then((names) => Promise.all(names.map((n) => caches.delete(n)))).then(() => {
          window.location.reload();
        });
      } else {
        window.location.reload();
      }
    });
  }

  // 5. Global Manual Cache Flush & Reload
  window.forceClearCacheAndReload = async function() {
    const isHi = (localStorage.getItem('gaonbazar_lang') || 'hi') === 'hi';
    const confirmed = confirm(isHi 
      ? 'क्या आप कैश साफ करके ताज़ा वर्ज़न लोड करना चाहते हैं? आपका लॉगिन और डेटा सुरक्षित रहेगा।' 
      : 'Clear local cache and reload latest version? Your login and data will be preserved.');
    if (!confirmed) return;

    if ('serviceWorker' in navigator && window.__swRegistration) {
      try {
        await window.__swRegistration.unregister();
      } catch (e) {}
    }
    if (window.caches) {
      try {
        const keys = await caches.keys();
        await Promise.all(keys.map(k => caches.delete(k)));
      } catch (e) {}
    }
    window.location.href = window.location.pathname + '?refresh=' + Date.now();
  };

  // Run initial diagnostic check
  document.addEventListener('DOMContentLoaded', checkServerVersion);
})();

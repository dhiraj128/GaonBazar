/**
 * GaonBazaar (गांव बाज़ार) - Service Worker (sw.js)
 * Production Rural Offline-First Caching & Resilience Strategy:
 * 
 * 1. Cache-First Strategy:
 *    - Applied to static assets (HTML, JS, CSS, images, fonts, icons).
 *    - Serves instantly from local cache without waiting for slow 2G/3G rural cell towers.
 * 
 * 2. Network-First Strategy:
 *    - Applied to dynamic REST API calls (/api/*).
 *    - Always attempts to fetch live data first; falls back to cached responses or offline JSON on network drop.
 * 
 * 3. Total Network Dropout Interception:
 *    - Intercepts failed navigation/page fetch requests and delivers the bilingual /offline.html fallback page.
 *    - Eliminates the browser's "No Internet" dinosaur screen.
 */

const CACHE_NAME = 'gaonbazar-v5-20261028';
const PRECACHE_ASSETS = [
  '/',
  '/index.html',
  '/vendor_dashboard.html',
  '/runner_dashboard.html',
  '/offline.html',
  '/sw.js'
];

// --- 1. SERVICE WORKER INSTALLATION ---
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(async (cache) => {
      // Precache critical offline pages and shell
      try {
        await cache.addAll(PRECACHE_ASSETS);
      } catch (err) {
        console.warn('[SW Install]: Precache addAll partial failure, caching individually:', err);
        for (const asset of PRECACHE_ASSETS) {
          try {
            await cache.add(asset);
          } catch (e) {
            console.warn('[SW Install]: Could not precache:', asset, e);
          }
        }
      }
    }).then(() => self.skipWaiting())
  );
});

// --- 2. SERVICE WORKER ACTIVATION ---
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((name) => {
          if (name !== CACHE_NAME) {
            console.log('[GaonBazaar SW]: Purging obsolete cache:', name);
            return caches.delete(name);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});



// --- 2.5 SERVICE WORKER MESSAGE DISPATCHER ---
self.addEventListener('message', (event) => {
  if (!event.data) return;
  if (event.data.action === 'SKIP_WAITING') {
    self.skipWaiting();
  } else if (event.data.action === 'CLEAR_ALL_CACHES') {
    caches.keys().then((names) => Promise.all(names.map((n) => caches.delete(n))));
  }
});

// --- 3. INTELLIGENT FETCH INTERCEPTION ---
self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = new URL(request.url);

  // Ignore non-HTTP(S) schemes (e.g. chrome-extension, data:)
  if (!url.protocol.startsWith('http')) return;

  // ---------------------------------------------------------------------------
  // STRATEGY A: Network-First for API Calls (/api/*)
  // ---------------------------------------------------------------------------
  if (url.pathname.startsWith('/api/')) {
    const isSensitiveAuth = url.pathname.includes('/user/') || 
                            url.pathname.includes('/auth/') || 
                            url.pathname.includes('/payments/') || 
                            url.pathname.includes('/orders/') || 
                            request.headers.has('Authorization');

    event.respondWith(
      fetch(request)
        .then((response) => {
          // If valid GET response and not a sensitive/user-specific route, cache for offline catalog browsing
          if (!isSensitiveAuth && request.method === 'GET' && response && response.status === 200) {
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, responseClone));
          }
          return response;
        })
        .catch(async () => {
          // Network dropped entirely! Check cache only for public catalog data
          if (!isSensitiveAuth && request.method === 'GET') {
            const cachedResponse = await caches.match(request);
            if (cachedResponse) {
              return cachedResponse;
            }
          }

          // Return structured bilingual offline JSON fallback
          return new Response(
            JSON.stringify({
              offline: true,
              error: 'Network offline',
              detail: 'गांव बाज़ार ऑफ़लाइन मोड: नेटवर्क कनेक्शन उपलब्ध नहीं है / GaonBazaar Offline: Connection unavailable'
            }),
            {
              status: 503,
              statusText: 'Service Unavailable (Offline)',
              headers: { 'Content-Type': 'application/json' }
            }
          );
        })
    );
    return;
  }

  // ---------------------------------------------------------------------------
  // STRATEGY B: Navigation / HTML Requests (Total Dropout Fallback to offline.html)
  // ---------------------------------------------------------------------------
  const isNavigate = request.mode === 'navigate';
  const acceptsHtml = request.headers.get('accept') && request.headers.get('accept').includes('text/html');

  if (isNavigate || acceptsHtml) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response && response.status === 200) {
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, responseClone));
          }
          return response;
        })
        .catch(async () => {
          // Network failed! Try matching cached version of requested URL
          const cached = await caches.match(request);
          if (cached) {
            return cached;
          }

          // Return bilingual offline.html fallback page
          const offlinePage = await caches.match('/offline.html');
          if (offlinePage) {
            return offlinePage;
          }

          // Relative fallback
          return (await caches.match('offline.html')) || Response.error();
        })
    );
    return;
  }

  // ---------------------------------------------------------------------------
  // STRATEGY C-IMG: Network-First with Cache Fallback for Images
  // Guarantees immediate display of fresh catalog assets and banners
  // ---------------------------------------------------------------------------
  const isImage = request.destination === 'image' || 
                  url.pathname.includes('/images/') || 
                  /\.(png|jpe?g|webp|svg|gif)(\?.*)?$/i.test(url.pathname);

  if (isImage) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response && response.status === 200 && request.method === 'GET') {
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, responseClone));
          }
          return response;
        })
        .catch(async () => {
          const cached = await caches.match(request);
          if (cached) return cached;
          return new Response('', { status: 408, statusText: 'Image offline' });
        })
    );
    return;
  }

  // ---------------------------------------------------------------------------
  // STRATEGY C: Cache-First for Static Assets (JS, CSS, Images, Fonts, Icons)
  // ---------------------------------------------------------------------------
  event.respondWith(
    caches.match(request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }

      // Not in cache: fetch from network and dynamically cache
      return fetch(request)
        .then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200 && request.method === 'GET') {
            const responseClone = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, responseClone));
          }
          return networkResponse;
        })
        .catch(async () => {
          // If a static asset fails, fallback gracefully
          return new Response('', { status: 408, statusText: 'Request Timeout / Offline' });
        });
    })
  );
});

// Service Worker Oficial do JARVIS Kids OS - Suporte 100% Offline e PWA
const CACHE_NAME = 'jarvis-kids-os-v3.9.7';
const ASSETS_TO_CACHE = [
  '/',
  '/pais',
  '/manifest.json',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
  '/static/libs/animate.min.css',
  '/static/libs/canvas-confetti.min.js',
  '/static/libs/sweetalert2.all.min.js',
  '/static/libs/sortable.min.js',
  '/static/vendor/mediapipe/camera_utils.js',
  '/static/vendor/mediapipe/hands.js'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS_TO_CACHE)).catch(() => {})
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) return caches.delete(key);
        })
      )
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;
  const url = new URL(event.request.url);

  // 1. Rotas de API dinamicas: sempre rede primeiro com fallback JSON offline
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(event.request).catch(() => {
        return new Response(
          JSON.stringify({ ok: false, offline: true, error: 'Dispositivo operando em modo offline local' }),
          { headers: { 'Content-Type': 'application/json' } }
        );
      })
    );
    return;
  }

  // 2. Paginas HTML (/, /pais, /admin, /engenharia): Network-First com fallback em Cache
  // Garante que atualizacoes do sistema aparecam na primeira abertura sem exigir F5 duplo
  const isHtmlNav =
    event.request.mode === 'navigate' ||
    url.pathname === '/' ||
    url.pathname === '/pais' ||
    url.pathname === '/admin' ||
    url.pathname === '/engenharia';

  if (isHtmlNav) {
    event.respondWith(
      fetch(event.request)
        .then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            const clone = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          }
          return networkResponse;
        })
        .catch(() => caches.match(event.request))
    );
    return;
  }

  // 3. Assets estaticos (/static/, WASM, icones, libs): Cache-First + atualizacao em background
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      const fetchPromise = fetch(event.request)
        .then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            const responseToCache = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, responseToCache));
          }
          return networkResponse;
        })
        .catch(() => cachedResponse);

      return cachedResponse || fetchPromise;
    })
  );
});

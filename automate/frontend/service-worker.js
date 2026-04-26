// autoMate service worker.
//
// Goal: install the SPA shell so the app launches offline-first when the user
// has it pinned to home screen. API calls always go to the network — the hub
// is the source of truth.

const SHELL = "automate-shell-v1";
const ASSETS = [
  "/", "/index.html", "/app.js", "/styles.css",
  "/icon-192.png", "/icon-512.png",
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(SHELL).then((c) => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== SHELL).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  // API + WebSocket: always network. We never cache them.
  if (url.pathname.startsWith("/api/") || url.pathname.startsWith("/oauth/")) return;
  if (e.request.method !== "GET") return;
  // Static shell: cache-first, network fallback.
  e.respondWith(
    caches.match(e.request).then((hit) =>
      hit || fetch(e.request).then((res) => {
        if (res.ok) {
          const copy = res.clone();
          caches.open(SHELL).then((c) => c.put(e.request, copy));
        }
        return res;
      }).catch(() => caches.match("/index.html"))
    )
  );
});

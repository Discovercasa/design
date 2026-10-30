// Service worker do Design: só para se poder instalar como app (não guarda páginas nem trabalha sem rede).
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', (e) => e.waitUntil(self.clients.claim()));

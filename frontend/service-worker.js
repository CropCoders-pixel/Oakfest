const CACHE_NAME = 'farm-to-table-v1';
const STATIC_CACHE_URLS = [
    '/',
    '/index.html',
    '/css/styles.css',
    '/css/soft-ui.css',
    '/js/config.js',
    '/js/api.js',
    '/js/auth.js',
    '/js/ui.js',
    '/js/main.js',
    '/images/logo.png',
    '/images/favicon.ico'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(STATIC_CACHE_URLS))
            .then(() => self.skipWaiting())
    );
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys()
            .then(cacheNames => {
                return Promise.all(
                    cacheNames
                        .filter(cacheName => cacheName !== CACHE_NAME)
                        .map(cacheName => caches.delete(cacheName))
                );
            })
            .then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', event => {
    if (event.request.url.includes('/api/')) {
        return;
    }

    event.respondWith(
        caches.match(event.request)
            .then(response => {
                if (response) {
                    return response;
                }

                return fetch(event.request)
                    .then(response => {
                        if (!response || response.status !== 200) {
                            return response;
                        }

                        const responseToCache = response.clone();
                        caches.open(CACHE_NAME)
                            .then(cache => {
                                cache.put(event.request, responseToCache);
                            });

                        return response;
                    });
            })
    );
});

self.addEventListener('push', event => {
    if (!event.data) return;

    const data = event.data.json();
    const options = {
        body: data.message,
        icon: '/images/logo.png',
        badge: '/images/badge.png',
        vibrate: [100, 50, 100],
        data: {
            url: data.link || '/'
        }
    };

    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

self.addEventListener('notificationclick', event => {
    event.notification.close();

    event.waitUntil(
        clients.matchAll({ type: 'window' })
            .then(windowClients => {
                if (windowClients.length > 0) {
                    windowClients[0].focus();
                    return;
                }

                clients.openWindow('/');
            })
    );
});

self.addEventListener('sync', event => {
    if (event.tag === 'sync-orders') {
        event.waitUntil(syncOrders());
    } else if (event.tag === 'sync-waste-reports') {
        event.waitUntil(syncWasteReports());
    }
});

async function syncOrders() {
    try {
        const db = await openDB();
        const orders = await db.getAll('offline-orders');

        for (const order of orders) {
            try {
                const response = await fetch('/api/orders/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${order.token}`
                    },
                    body: JSON.stringify(order.data)
                });

                if (response.ok) {
                    await db.delete('offline-orders', order.id);
                }
            } catch (error) {
                console.error('Failed to sync order:', error);
            }
        }
    } catch (error) {
        console.error('Failed to sync orders:', error);
    }
}

async function syncWasteReports() {
    try {
        const db = await openDB();
        const reports = await db.getAll('offline-waste-reports');

        for (const report of reports) {
            try {
                const response = await fetch('/api/waste/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${report.token}`
                    },
                    body: JSON.stringify(report.data)
                });

                if (response.ok) {
                    await db.delete('offline-waste-reports', report.id);
                }
            } catch (error) {
                console.error('Failed to sync waste report:', error);
            }
        }
    } catch (error) {
        console.error('Failed to sync waste reports:', error);
    }
}

function openDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('farm-to-table', 1);

        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);

        request.onupgradeneeded = event => {
            const db = event.target.result;

            if (!db.objectStoreNames.contains('offline-orders')) {
                db.createObjectStore('offline-orders', { keyPath: 'id' });
            }
            if (!db.objectStoreNames.contains('offline-waste-reports')) {
                db.createObjectStore('offline-waste-reports', { keyPath: 'id' });
            }
        };
    });
}

/* Service worker: nhận thông báo đẩy khi app đang đóng (điện thoại + máy tính). */
importScripts("https://www.gstatic.com/firebasejs/10.12.2/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.12.2/firebase-messaging-compat.js");
importScripts("/firebase-config.js");

firebase.initializeApp(self.FIREBASE_CONFIG);
firebase.messaging(); // thông báo có trường "notification" sẽ tự hiển thị

self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (e) => e.waitUntil(self.clients.claim()));

// Bấm vào thông báo: mở / focus app tới đúng bài
self.addEventListener("notificationclick", (event) => {
  const d = event.notification?.data || {};
  const postId = d.postId || d.FCM_MSG?.data?.postId || event.notification?.tag;
  const url = postId ? `/?id=${postId}` : "/";
  event.notification.close();
  event.waitUntil(
    clients.matchAll({ type: "window", includeUncontrolled: true }).then((list) => {
      for (const c of list) {
        if ("focus" in c) {
          c.postMessage({ type: "open-post", postId });
          return c.focus();
        }
      }
      return clients.openWindow(url);
    })
  );
});

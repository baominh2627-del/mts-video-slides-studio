// ĐIỀN THÔNG TIN TỪ FIREBASE CONSOLE (xem HUONG_DAN.md).
// File này được dùng chung cho trang web và service worker (thông báo nền).
self.FIREBASE_CONFIG = {
  apiKey: "AIzaSyDKoXH9n26zbpTukWYHBwsAikAds-Sjljk",
  authDomain: "tool-tu-dong-fb.firebaseapp.com",
  projectId: "tool-tu-dong-fb",
  storageBucket: "tool-tu-dong-fb.firebasestorage.app",
  messagingSenderId: "542531091298",
  appId: "1:542531091298:web:6f6e38eb2ede1a116a4a3b",
  measurementId: "G-5NC2L2WB9F",
};

// Project settings → Cloud Messaging → Web Push certificates → Key pair
self.VAPID_KEY = "BGTHW-1jGNBmwLCgs69M0HBmKtnW8cosIsDogxaSJbR-k6ommiD-KZMvij750qIcfgLon8dqnje4lW7OGCjQzGE";

// Chỉ tài khoản Google này được đăng nhập app (phải trùng với firestore.rules)
self.OWNER_EMAIL = "baominh2627@gmail.com";

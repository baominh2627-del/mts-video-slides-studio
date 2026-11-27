// Background service worker:
// 1. Nhận bài quét từ content.js -> đẩy về radar.py (http://127.0.0.1:8765/ingest)
// 2. Tự động làm mới nhẹ tab theo dõi (/groups/feed hoặc /notifications) mỗi 3 phút để luôn thấy bài mới nhất.

const RADAR_URL = "http://127.0.0.1:8765/ingest";
const HEALTH_URL = "http://127.0.0.1:8765/health";
const ALARM_NAME = "radar-auto-refresh";

async function ensureAlarm() {
  const { autoRefresh = true, intervalMin = 3 } = await chrome.storage.local.get(["autoRefresh", "intervalMin"]);
  await chrome.alarms.clear(ALARM_NAME);
  if (autoRefresh) {
    chrome.alarms.create(ALARM_NAME, { periodInMinutes: Math.max(2, Number(intervalMin) || 3) });
  }
}

chrome.runtime.onInstalled.addListener(() => {
  ensureAlarm();
  checkHealth();
});
chrome.runtime.onStartup.addListener(() => {
  ensureAlarm();
  checkHealth();
});

async function checkHealth() {
  try {
    const r = await fetch(HEALTH_URL);
    if (r.ok) {
      chrome.action.setBadgeBackgroundColor({ color: "#16a34a" });
      chrome.action.setBadgeText({ text: "ON" });
      return true;
    }
  } catch {}
  chrome.action.setBadgeBackgroundColor({ color: "#dc2626" });
  chrome.action.setBadgeText({ text: "OFF" });
  return false;
}

chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name !== ALARM_NAME) return;
  const { autoRefresh = true } = await chrome.storage.local.get(["autoRefresh"]);
  if (!autoRefresh) return;

  // Chỉ làm mới các tab theo dõi chuyên dụng (/groups/feed hoặc /notifications) khi bạn không đang gõ chữ trên đó
  const tabs = await chrome.tabs.query({
    url: [
      "https://www.facebook.com/groups/feed*",
      "https://www.facebook.com/notifications*",
      "https://web.facebook.com/groups/feed*",
      "https://web.facebook.com/notifications*",
    ],
  });
  for (const t of tabs) {
    if (!t.active && t.id) {
      chrome.tabs.reload(t.id);
    }
  }
});

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg?.type === "RADAR_CONFIG_CHANGED") {
    ensureAlarm().then(() => sendResponse({ ok: true }));
    return true;
  }
  if (msg?.type === "RADAR_HEALTH") {
    checkHealth().then((ok) => sendResponse({ ok }));
    return true;
  }
  if (msg?.type !== "RADAR_NOTIFS" || !Array.isArray(msg.items) || !msg.items.length) {
    return false;
  }
  fetch(RADAR_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ items: msg.items }),
  })
    .then((r) => r.json())
    .then(async (data) => {
      chrome.action.setBadgeBackgroundColor({ color: "#16a34a" });
      chrome.action.setBadgeText({ text: "ON" });
      const prev = await chrome.storage.local.get(["totalScanned", "totalMatched"]);
      await chrome.storage.local.set({
        totalScanned: (prev.totalScanned || 0) + (data.new || 0),
        totalMatched: (prev.totalMatched || 0) + (data.matched || 0),
        lastScanAt: new Date().toLocaleTimeString("vi-VN"),
      });
      sendResponse({ ok: true, data });
    })
    .catch((err) => {
      chrome.action.setBadgeBackgroundColor({ color: "#dc2626" });
      chrome.action.setBadgeText({ text: "OFF" });
      sendResponse({ ok: false, error: String(err) });
    });
  return true;
});

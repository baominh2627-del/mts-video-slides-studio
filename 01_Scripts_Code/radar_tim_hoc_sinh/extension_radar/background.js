// Background service worker v3:
// - Lưu danh sách nhóm đã biết (knownGroups) & danh sách nhóm tích chọn (selectedGroupIds)
// - Chế độ 1 (rotate): dùng 1 tab ghim chạy nền, mỗi ~60s mở lần lượt từng Group đã tích ở chế độ Bài mới nhất (?sorting_setting=CHRONOLOGICAL&radar_watch=1)
// - Chế độ 2 (manual): không tự chuyển trang, chỉ quét khi bạn tự xem Facebook
// - Gửi bài quét được về radar.py (http://127.0.0.1:8765/ingest)

const RADAR_INGEST = "http://127.0.0.1:8765/ingest";
const RADAR_HEALTH = "http://127.0.0.1:8765/health";
const RADAR_RECENT = "http://127.0.0.1:8765/recent";
const ALARM_ROTATE = "radar-rotate-group";

// Các nhóm gia sư thu thập sẵn từ lịch sử thông báo của bạn để có sẵn ngay khi mở
const SEED_GROUPS = [
  { id: "280811807457314", name: "Tìm Gia Sư – Kết Nối Học Sinh & Giáo Viên" },
  { id: "453699015081222", name: "Gia sư Hà Nội" },
  { id: "giasudaykemonline", name: "Gia Sư Online - Dạy Kèm Online" },
  { id: "giasudaytoan", name: "GIA SƯ TOÁN - GIA SƯ DẠY TOÁN" },
  { id: "timgiasumienphihn", name: "Tìm Gia Sư Miễn Phí Hà Nội" },
  { id: "congdonggiasusinhvien", name: "Cộng Đồng Gia Sư Sinh Viên" },
  { id: "giasuhanoi.banmai", name: "Gia sư Hà Nội (Ban Mai)" },
  { id: "vatlyphysics", name: "VẬT LÝ PHYSICS" },
  { id: "Trungtamgiasuhanoi", name: "Trung Tâm Gia Sư Hà Nội" },
  { id: "giaoviengiasutrogiang", name: "Giáo Viên - Gia Sư - Trợ Giảng" },
  { id: "vieclamgiaovientrogiangtimgiasu", name: "Việc Làm Giáo Viên, Trợ Giảng, Tìm Gia Sư" }
];

const DEFAULT_SELECTED = [
  "280811807457314",
  "453699015081222",
  "giasudaykemonline",
  "giasudaytoan",
  "timgiasumienphihn",
  "congdonggiasusinhvien"
];

async function initDefaults() {
  const st = await chrome.storage.local.get(["knownGroups", "selectedGroupIds", "mode", "intervalSec"]);
  const map = new Map();
  for (const g of SEED_GROUPS) map.set(g.id, g);
  for (const g of st.knownGroups || []) {
    if (g?.id) map.set(g.id, { id: g.id, name: g.name || map.get(g.id)?.name || g.id });
  }
  const updates = { knownGroups: Array.from(map.values()) };
  if (!Array.isArray(st.selectedGroupIds)) {
    updates.selectedGroupIds = DEFAULT_SELECTED;
  }
  if (!st.mode) updates.mode = "rotate";
  if (!st.intervalSec) updates.intervalSec = 60;
  await chrome.storage.local.set(updates);
  await syncAlarm();
  await checkHealth();
}

async function syncAlarm() {
  const { mode = "rotate", intervalSec = 60, selectedGroupIds = [] } = await chrome.storage.local.get([
    "mode",
    "intervalSec",
    "selectedGroupIds",
  ]);
  await chrome.alarms.clear(ALARM_ROTATE);
  if (mode === "rotate" && selectedGroupIds.length > 0) {
    const periodMin = Math.max(0.75, (Number(intervalSec) || 60) / 60);
    chrome.alarms.create(ALARM_ROTATE, { delayInMinutes: 0.5, periodInMinutes: periodMin });
  }
}

async function checkHealth() {
  try {
    const r = await fetch(RADAR_HEALTH);
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

async function stepRotateGroup(forceOpen = false) {
  const st = await chrome.storage.local.get([
    "mode",
    "selectedGroupIds",
    "knownGroups",
    "rotateIndex",
    "watcherTabId",
  ]);
  if (!forceOpen && st.mode !== "rotate") return { ok: false, reason: "manual_mode" };
  const ids = st.selectedGroupIds || [];
  if (!ids.length) return { ok: false, reason: "no_groups" };

  const idx = ((st.rotateIndex || 0) % ids.length + ids.length) % ids.length;
  const gid = ids[idx];
  const gInfo = (st.knownGroups || []).find((x) => x.id === gid);
  const targetUrl = `https://www.facebook.com/groups/${encodeURIComponent(gid)}/?sorting_setting=CHRONOLOGICAL&radar_watch=1`;

  let tab = null;
  if (st.watcherTabId) {
    try {
      tab = await chrome.tabs.get(st.watcherTabId);
    } catch {
      tab = null;
    }
  }
  // Tìm tab radar_watch đang có sẵn nếu mất ID
  if (!tab) {
    const existing = await chrome.tabs.query({ url: ["*://*.facebook.com/*radar_watch=1*"] });
    if (existing.length > 0) tab = existing[0];
  }

  if (tab?.id) {
    await chrome.tabs.update(tab.id, { url: targetUrl, pinned: true });
  } else {
    tab = await chrome.tabs.create({ url: targetUrl, active: false, pinned: true });
  }

  await chrome.storage.local.set({
    watcherTabId: tab.id,
    rotateIndex: (idx + 1) % ids.length,
    currentWatchGroup: gInfo?.name || gid,
    lastRotateAt: new Date().toLocaleTimeString("vi-VN"),
  });
  return { ok: true, groupId: gid, groupName: gInfo?.name || gid };
}

chrome.runtime.onInstalled.addListener(() => initDefaults());
chrome.runtime.onStartup.addListener(() => initDefaults());

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === ALARM_ROTATE) {
    stepRotateGroup(false);
  }
});

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg?.type === "RADAR_HEALTH") {
    checkHealth().then((ok) => sendResponse({ ok }));
    return true;
  }

  if (msg?.type === "RADAR_RECENT") {
    fetch(RADAR_RECENT)
      .then((r) => r.json())
      .then((d) => sendResponse(d))
      .catch(() => sendResponse({ ok: false, events: [], templates: {} }));
    return true;
  }

  if (msg?.type === "RADAR_CONFIG_CHANGED") {
    syncAlarm().then(() => sendResponse({ ok: true }));
    return true;
  }

  if (msg?.type === "RADAR_STEP_NOW") {
    stepRotateGroup(true).then((res) => sendResponse(res));
    return true;
  }

  if (msg?.type === "RADAR_DISCOVERED_GROUPS" && Array.isArray(msg.groups)) {
    chrome.storage.local.get(["knownGroups"]).then(async (st) => {
      const map = new Map();
      for (const g of st.knownGroups || []) {
        if (g?.id) map.set(g.id, g);
      }
      let added = 0;
      for (const g of msg.groups) {
        if (!g?.id) continue;
        const prev = map.get(g.id);
        const betterName =
          g.name && g.name !== g.id && (!prev?.name || prev.name === prev.id || g.name.length > prev.name.length)
            ? g.name
            : prev?.name || g.name || g.id;
        if (!prev) added++;
        map.set(g.id, { id: g.id, name: betterName });
      }
      await chrome.storage.local.set({ knownGroups: Array.from(map.values()) });
      sendResponse({ ok: true, total: map.size, added });
    });
    return true;
  }

  if (msg?.type === "RADAR_NOTIFS" && Array.isArray(msg.items) && msg.items.length) {
    fetch(RADAR_INGEST, {
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
  }
  return false;
});

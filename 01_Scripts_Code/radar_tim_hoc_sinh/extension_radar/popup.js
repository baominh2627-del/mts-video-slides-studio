const $ = (s) => document.querySelector(s);

async function init() {
  chrome.runtime.sendMessage({ type: "RADAR_HEALTH" }, (res) => {
    $("#status").textContent = res?.ok
      ? "🟢 Đã kết nối radar.py (đang chạy ngầm)"
      : "🔴 Chưa thấy radar.py — hãy bật chay_ngam_radar.vbs";
  });

  const st = await chrome.storage.local.get(["autoRefresh", "totalScanned", "totalMatched", "lastScanAt"]);
  $("#auto-refresh").checked = st.autoRefresh !== false;
  $("#stats").textContent = `Đã đọc: ${st.totalScanned || 0} tin · Đạt chuẩn: ${st.totalMatched || 0}` +
    (st.lastScanAt ? ` · Lúc ${st.lastScanAt}` : "");
}

$("#auto-refresh").onchange = async (e) => {
  await chrome.storage.local.set({ autoRefresh: e.target.checked });
  chrome.runtime.sendMessage({ type: "RADAR_CONFIG_CHANGED" });
};

$("#open-feed").onclick = () => {
  chrome.tabs.create({ url: "https://www.facebook.com/groups/feed/?sorting_setting=CHRONOLOGICAL", active: true });
};

$("#open-app").onclick = () => {
  chrome.tabs.create({ url: "https://tool-tu-dong-fb.web.app/", active: true });
};

$("#scan-now").onclick = async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (tab?.id) {
    chrome.tabs.sendMessage(tab.id, { type: "FORCE_SCAN" }, () => {
      $("#status").textContent = "✅ Đã quét lại trang hiện tại!";
    });
  }
};

init();

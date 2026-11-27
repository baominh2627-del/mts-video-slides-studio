const $ = (s) => document.querySelector(s);
const RESERVED = new Set(["feed", "discover", "joins", "create", "notifications", "search"]);

function parseGroupFromTab(tab) {
  if (!tab?.url) return null;
  try {
    const u = new URL(tab.url);
    if (!u.hostname.includes("facebook.com")) return null;
    const m = u.pathname.match(/^\/groups\/([^/?#]+)/);
    if (m && !RESERVED.has(m[1].toLowerCase())) {
      const name = (tab.title || m[1]).replace(/^\(\d+\)\s*/, "").replace(/\s*\|\s*Facebook.*$/i, "").trim();
      return { id: m[1], name: name || m[1] };
    }
  } catch {}
  return null;
}

async function refreshUI() {
  chrome.runtime.sendMessage({ type: "RADAR_HEALTH" }, (res) => {
    $("#status").textContent = res?.ok
      ? "🟢 Đang kết nối radar.py chạy ngầm"
      : "🔴 Chưa bật radar.py — hãy chạy chay_ngam_radar.vbs";
  });

  const st = await chrome.storage.local.get([
    "mode", "intervalSec", "selectedGroupIds", "knownGroups", "currentWatchGroup", "lastRotateAt"
  ]);
  const selected = new Set(st.selectedGroupIds || []);
  $("#mode").value = st.mode || "rotate";
  $("#interval").value = String(st.intervalSec || 60);
  $("#row-interval").style.display = ($("#mode").value === "rotate") ? "flex" : "none";
  $("#grp-count").textContent = selected.size;
  $("#watch-info").textContent = st.currentWatchGroup
    ? `Đang canh: ${st.currentWatchGroup}` + (st.lastRotateAt ? ` (${st.lastRotateAt})` : "")
    : "Bấm 'Chuyển nhóm ngay' để mở tab canh tự động.";

  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const curGrp = parseGroupFromTab(tab);
  const addBtn = $("#add-current");
  if (curGrp) {
    addBtn.classList.remove("hidden");
    const isTicked = selected.has(curGrp.id);
    addBtn.textContent = isTicked
      ? `✅ Nhóm "${curGrp.name.slice(0, 26)}" đã được tích canh`
      : `➕ Tích chọn nhóm "${curGrp.name.slice(0, 26)}"`;
    addBtn.onclick = async () => {
      const map = new Map((st.knownGroups || []).map((g) => [g.id, g]));
      map.set(curGrp.id, curGrp);
      if (selected.has(curGrp.id)) selected.delete(curGrp.id);
      else selected.add(curGrp.id);
      await chrome.storage.local.set({
        knownGroups: Array.from(map.values()),
        selectedGroupIds: Array.from(selected),
      });
      chrome.runtime.sendMessage({ type: "RADAR_CONFIG_CHANGED" });
      refreshUI();
    };
  } else {
    addBtn.classList.add("hidden");
  }

  chrome.runtime.sendMessage({ type: "RADAR_RECENT" }, (res) => {
    const evs = res?.events || [];
    const box = $("#recent");
    if (!evs.length) return;
    box.innerHTML = "";
    for (const ev of evs.slice(0, 6)) {
      const d = document.createElement("div");
      d.className = "ev" + (ev.ok ? " hit" : "");
      d.textContent = `${ev.ok ? "✅ ĐẠT" : "⏭"} [${ev.time}] ${ev.snippet || ev.group} — (${ev.reason})`;
      box.appendChild(d);
    }
  });
}

$("#mode").onchange = async (e) => {
  await chrome.storage.local.set({ mode: e.target.value });
  chrome.runtime.sendMessage({ type: "RADAR_CONFIG_CHANGED" });
  refreshUI();
};

$("#interval").onchange = async (e) => {
  await chrome.storage.local.set({ intervalSec: Number(e.target.value) });
  chrome.runtime.sendMessage({ type: "RADAR_CONFIG_CHANGED" });
};

$("#open-groups").onclick = () => chrome.runtime.openOptionsPage();

$("#step-now").onclick = () => {
  chrome.runtime.sendMessage({ type: "RADAR_STEP_NOW" }, () => setTimeout(refreshUI, 400));
};

$("#scan-now").onclick = async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (tab?.id && tab.url && tab.url.includes("facebook.com")) {
    chrome.tabs.sendMessage(tab.id, { type: "FORCE_SCAN" }, () => {
      void chrome.runtime.lastError;
      setTimeout(refreshUI, 900);
    });
  } else {
    $("#status").textContent = "ℹ️ Hãy đứng ở tab Facebook rồi bấm Quét trang này";
  }
};

$("#open-app").onclick = () => {
  chrome.tabs.create({ url: "https://tool-tu-dong-fb.web.app/", active: true });
};

refreshUI();

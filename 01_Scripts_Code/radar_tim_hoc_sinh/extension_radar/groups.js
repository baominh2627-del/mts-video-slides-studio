const $ = (s) => document.querySelector(s);
let knownGroups = [];
let selectedIds = new Set();

async function loadState() {
  const st = await chrome.storage.local.get(["knownGroups", "selectedGroupIds"]);
  knownGroups = st.knownGroups || [];
  selectedIds = new Set(st.selectedGroupIds || []);
  render();
}

async function saveSelection() {
  await chrome.storage.local.set({
    knownGroups,
    selectedGroupIds: Array.from(selectedIds),
  });
  chrome.runtime.sendMessage({ type: "RADAR_CONFIG_CHANGED" });
  render();
}

function render() {
  const q = ($("#search").value || "").toLowerCase().trim();
  $("#summary").textContent = `Đang tích chọn: ${selectedIds.size} / ${knownGroups.length} nhóm`;
  const list = $("#list");
  list.innerHTML = "";

  const sorted = [...knownGroups].sort((a, b) => {
    const sa = selectedIds.has(a.id) ? 0 : 1;
    const sb = selectedIds.has(b.id) ? 0 : 1;
    if (sa !== sb) return sa - sb;
    return (a.name || a.id).localeCompare(b.name || b.id, "vi");
  });

  for (const g of sorted) {
    const textMatch = `${g.name || ""} ${g.id}`.toLowerCase();
    if (q && !textMatch.includes(q)) continue;

    const checked = selectedIds.has(g.id);
    const lbl = document.createElement("label");
    lbl.className = "item" + (checked ? " checked" : "");
    lbl.innerHTML = `
      <div class="left">
        <input type="checkbox" ${checked ? "checked" : ""} />
        <div>
          <div style="font-weight:600;">${escapeHtml(g.name || g.id)}</div>
          <div class="muted" style="font-size:12px;">ID: ${escapeHtml(g.id)}</div>
        </div>
      </div>
      <a href="https://www.facebook.com/groups/${encodeURIComponent(g.id)}/?sorting_setting=CHRONOLOGICAL" target="_blank" rel="noopener">Mở xem nhóm ↗</a>
    `;
    lbl.querySelector("input").onchange = (e) => {
      if (e.target.checked) selectedIds.add(g.id);
      else selectedIds.delete(g.id);
      saveSelection();
    };
    list.appendChild(lbl);
  }
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

$("#search").oninput = render;

$("#scan-fb").onclick = () => {
  chrome.tabs.create({ url: "https://www.facebook.com/groups/joins/", active: true });
};

$("#smart-pick").onclick = () => {
  const kw = /(gia sư|gia su|giasu|toán|toan|lý|li|vật lý|vatly|hóa|hoa|dạy kèm|daykem)/i;
  for (const g of knownGroups) {
    if (kw.test(`${g.name} ${g.id}`)) selectedIds.add(g.id);
  }
  saveSelection();
};

$("#clear-all").onclick = () => {
  selectedIds.clear();
  saveSelection();
};

$("#btn-add").onclick = () => {
  const raw = ($("#add-url").value || "").trim();
  if (!raw) return;
  let gid = raw;
  const m = raw.match(/facebook\.com\/groups\/([^/?#]+)/i);
  if (m) gid = m[1];
  gid = gid.trim();
  if (!gid) return;
  if (!knownGroups.some((x) => x.id === gid)) {
    knownGroups.unshift({ id: gid, name: `Nhóm ${gid}` });
  }
  selectedIds.add(gid);
  $("#add-url").value = "";
  saveSelection();
};

chrome.storage.onChanged.addListener((changes, area) => {
  if (area === "local" && (changes.knownGroups || changes.selectedGroupIds)) {
    loadState();
  }
});

loadState();

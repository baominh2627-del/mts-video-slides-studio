// Content script (100% chỉ đọc, không click, không bình luận):
// Đọc cả 2 nguồn trên Facebook:
//   1) Chuông thông báo (/notifications, bảng chuông, popup góc dưới trái)
//   2) Bài đăng trực tiếp trong các Nhóm (/groups/...) và Bảng feed Nhóm (/groups/feed/)

(() => {
  const seenKeys = new Set();
  let timer = null;

  function simpleHash(str) {
    let h = 2166136261;
    for (let i = 0; i < str.length; i++) {
      h ^= str.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return (h >>> 0).toString(36);
  }

  function extractPostUrlFromHref(href) {
    if (!href || !href.includes("facebook.com")) return null;
    try {
      const u = new URL(href, location.origin);
      let m = u.pathname.match(/\/groups\/([^/?#]+)\/(?:posts|permalink)\/(\d+|pfbid[A-Za-z0-9]+)/);
      if (m) return `https://www.facebook.com/groups/${m[1]}/posts/${m[2]}/`;

      const mp = u.searchParams.get("multi_permalinks");
      if (mp) {
        const g = u.pathname.match(/\/groups\/([^/?#]+)/);
        if (g) return `https://www.facebook.com/groups/${g[1]}/posts/${mp}/`;
      }

      const setParam = u.searchParams.get("set") || "";
      m = setParam.match(/^(?:gm|pcb)\.(\d+)/);
      if (m) {
        const g = location.pathname.match(/\/groups\/([^/?#]+)/);
        if (g && g[1] !== "feed") return `https://www.facebook.com/groups/${g[1]}/posts/${m[1]}/`;
      }

      m = u.pathname.match(/\/share\/p\/([A-Za-z0-9]+)/);
      if (m) return `https://www.facebook.com/share/p/${m[1]}/`;

      const sfb = u.searchParams.get("story_fbid");
      const id = u.searchParams.get("id");
      if (sfb && id) return `https://www.facebook.com/permalink.php?story_fbid=${sfb}&id=${id}`;
    } catch {}
    return null;
  }

  function extractKey(href, fallbackText = "") {
    const clean = extractPostUrlFromHref(href);
    if (clean) return "post:" + clean;
    try {
      const u = new URL(href, location.origin);
      const nid = u.searchParams.get("notif_id");
      if (nid) return "nid:" + nid;
    } catch {}
    return "txt:" + simpleHash(fallbackText.slice(0, 140));
  }

  // 1) Quét Chuông thông báo
  function collectNotifications(batch) {
    const anchors = document.querySelectorAll(
      'a[href*="notif_id="], div[role="alert"] a[href*="/groups/"], div[aria-label*="Thông báo"] a[href*="/groups/"], div[aria-label*="Notifications"] a[href*="/groups/"]'
    );
    for (const a of anchors) {
      const href = a.href;
      if (!href || !href.includes("facebook.com")) continue;
      const text = (a.innerText || "").trim();
      if (text.length < 10) continue;
      const key = extractKey(href, text);
      if (seenKeys.has(key)) continue;
      seenKeys.add(key);
      batch.push({ source: "bell", key, href, text });
    }
  }

  // Kiểm tra 1 node có nằm bên trong phần Bình luận của bài viết không
  function isInsideComment(el) {
    const art = el.closest('[role="article"]');
    if (!art) return false;
    const lbl = art.getAttribute("aria-label") || "";
    return /^(Bình luận|Phản hồi|Comment|Reply)/i.test(lbl);
  }

  // Lấy text bài đăng từ 1 thẻ bài viết (bỏ qua phần bình luận bên dưới)
  function extractCardBody(card) {
    // Ưu tiên vùng nội dung chính thức của bài viết trên Facebook
    const msgNodes = card.querySelectorAll('[data-ad-comet-preview="message"], [data-ad-preview="message"]');
    for (const m of msgNodes) {
      if (!isInsideComment(m)) {
        const t = (m.innerText || "").trim();
        if (t.length >= 6) return t;
      }
    }

    // Dự phòng cho bài chữ to nền màu / bài ngắn không gắn data-ad-preview
    const clone = card.cloneNode(true);
    clone.querySelectorAll('[role="article"], ul, form').forEach((n) => n.remove());
    const rawLines = (clone.innerText || "").split(/\n+/).map((s) => s.trim()).filter(Boolean);
    const stopRe = /^(Tất cả cảm xúc|Xem thêm bình luận|Xem \d+ bình luận|Viết bình luận|Viết câu trả lời|Thích$|Bình luận$|Chia sẻ$)/i;
    const bodyLines = [];
    for (const ln of rawLines) {
      if (stopRe.test(ln)) break;
      if (/^(\d+\s*(giây|phút|giờ|ngày|tuần)|Vừa xong|Đáng chú ý|Phù hợp nhất)/i.test(ln)) continue;
      if (ln === "Theo dõi" || ln === "Tham gia" || ln === "Bài viết ẩn danh") continue;
      bodyLines.push(ln);
    }
    // Bỏ 1-2 dòng đầu nếu là tên nhóm / tên người đăng ngắn
    if (bodyLines.length >= 2 && bodyLines[0].length < 55) {
      return bodyLines.slice(1).join("\n").trim();
    }
    return bodyLines.join("\n").trim();
  }

  function extractCardGroupAndLink(card) {
    let postUrl = null;
    let groupUrl = null;
    let groupName = "";

    const links = card.querySelectorAll("a[href]");
    for (const a of links) {
      if (isInsideComment(a)) continue;
      const h = a.href || "";
      if (!postUrl) {
        postUrl = extractPostUrlFromHref(h);
      }
      if (!groupUrl && h.includes("/groups/")) {
        const m = h.match(/https:\/\/(?:www|web)\.facebook\.com\/groups\/([^/?#]+)/);
        if (m && m[1] !== "feed" && m[1] !== "discover") {
          groupUrl = `https://www.facebook.com/groups/${m[1]}/?sorting_setting=CHRONOLOGICAL`;
          const txt = (a.innerText || "").trim();
          if (txt && txt.length > 2 && txt.length < 90 && !/^\d+\s*(giây|phút|giờ|ngày)/i.test(txt)) {
            groupName = txt;
          }
        }
      }
    }

    if (!groupUrl) {
      const m = location.pathname.match(/\/groups\/([^/?#]+)/);
      if (m && m[1] !== "feed" && m[1] !== "discover") {
        groupUrl = `https://www.facebook.com/groups/${m[1]}/?sorting_setting=CHRONOLOGICAL`;
        groupName = document.title.replace(/^\(\d+\)\s*/, "").replace(/\s*\|\s*Facebook.*$/i, "").trim();
      }
    }

    return {
      href: postUrl || groupUrl || location.href,
      groupName: groupName || "Nhóm Facebook",
    };
  }

  // 2) Quét Bài viết trực tiếp trên trang Nhóm (/groups/...) & Bảng feed Nhóm (/groups/feed)
  function collectGroupFeedPosts(batch) {
    if (!location.pathname.startsWith("/groups") && location.pathname !== "/") return;

    const candidateCards = new Set();
    document.querySelectorAll('[role="feed"] > div').forEach((el) => {
      if (el.offsetHeight > 80) candidateCards.add(el);
    });
    document.querySelectorAll('[data-ad-comet-preview="message"], [data-ad-preview="message"]').forEach((msg) => {
      if (isInsideComment(msg)) return;
      let cur = msg;
      for (let i = 0; i < 10 && cur.parentElement; i++) {
        cur = cur.parentElement;
        if (cur.getAttribute("role") === "feed" || cur.getAttribute("role") === "main") break;
        if (cur.querySelectorAll('[data-ad-comet-preview="message"], [data-ad-preview="message"]').length > 1) {
          break;
        }
        if (cur.offsetHeight > 110 && cur.querySelector('a[href*="/groups/"], [aria-label*="Bình luận"], [aria-label*="bình luận"], [aria-label*="Comment"]')) {
          candidateCards.add(cur);
          break;
        }
      }
    });

    for (const card of candidateCards) {
      if (isInsideComment(card)) continue;
      const body = extractCardBody(card);
      if (!body || body.length < 8) continue;
      const { href, groupName } = extractCardGroupAndLink(card);
      const normBody = body.replace(/\s+/g, " ").trim();
      const key = postKey(href, groupName, normBody);
      if (seenKeys.has(key)) continue;
      seenKeys.add(key);
      batch.push({
        source: "feed",
        key,
        href,
        text: `Bây giờ trong ${groupName}: ${body}`,
      });
    }
  }

  function postKey(href, groupName, normBody) {
    const clean = extractPostUrlFromHref(href);
    if (clean) return "post:" + clean;
    return "feed:" + simpleHash(groupName + "|" + normBody.slice(0, 120));
  }

  function scanAll() {
    const batch = [];
    collectNotifications(batch);
    collectGroupFeedPosts(batch);
    if (batch.length > 0) {
      chrome.runtime.sendMessage({ type: "RADAR_NOTIFS", items: batch }, () => {
        void chrome.runtime.lastError;
      });
    }
  }

  function scheduleScan() {
    if (timer) clearTimeout(timer);
    timer = setTimeout(scanAll, 800);
  }

  chrome.runtime.onMessage.addListener((msg, _s, sendResponse) => {
    if (msg?.type === "FORCE_SCAN") {
      seenKeys.clear();
      scanAll();
      sendResponse({ ok: true });
    }
  });

  const obs = new MutationObserver(scheduleScan);
  obs.observe(document.documentElement, { childList: true, subtree: true });
  setTimeout(scanAll, 1200);
  setTimeout(scanAll, 3500);
})();

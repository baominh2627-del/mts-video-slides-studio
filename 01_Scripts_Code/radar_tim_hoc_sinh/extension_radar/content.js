// Content script v3.2:
// 1. Tự mở "Xem thêm" (See more) trên bài viết để đọc trọn nội dung bên dưới (không bao giờ sót dòng Địa chỉ ở cuối bài!).
// 2. Bắt mọi kiểu bài đăng: chữ thường, chữ to 1 dòng, chữ trên nền màu/ảnh nền.
// 3. Khảo sát thời gian đăng bài: bài <= 2 ngày mới nhận, quá 2 ngày tự loại.
// 4. Cuộn sâu liên tục trong Group để quét nhiều bài nhất có thể cho tới khi gặp loạt bài quá 2 ngày mới dừng.
// 5. Khi mở bài từ App Radar HS (#radar_q=...&radar_cmt=...), tự cuộn tới đúng bài + hiện khung Bình luận soạn sẵn.

(() => {
  const seenKeys = new Set();
  const cardByKey = new Map();
  let scanTimer = null;
  let crawlRunning = false;

  const RESERVED_GROUP_SLUGS = new Set([
    "feed", "discover", "joins", "create", "notifications", "search", "categories", "your_groups"
  ]);

  function simpleHash(str) {
    let h = 2166136261;
    for (let i = 0; i < str.length; i++) {
      h ^= str.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return (h >>> 0).toString(36);
  }

  function currentGroupIdFromUrl() {
    const m = location.pathname.match(/^\/groups\/([^/?#]+)/);
    if (m && !RESERVED_GROUP_SLUGS.has(m[1].toLowerCase())) return m[1];
    return null;
  }

  function extractPostUrlFromHref(href, fallbackGroupId = null) {
    if (!href || !href.includes("facebook.com")) return null;
    try {
      const u = new URL(href, location.origin);
      let m = u.pathname.match(/\/groups\/([^/?#]+)\/(?:posts|permalink)\/(\d+|pfbid[A-Za-z0-9]+)/);
      if (m && !RESERVED_GROUP_SLUGS.has(m[1].toLowerCase())) {
        return `https://www.facebook.com/groups/${m[1]}/posts/${m[2]}/`;
      }
      const mp = u.searchParams.get("multi_permalinks");
      if (mp) {
        const g = u.pathname.match(/\/groups\/([^/?#]+)/);
        const gid = (g && !RESERVED_GROUP_SLUGS.has(g[1].toLowerCase()) ? g[1] : null) || fallbackGroupId;
        if (gid) return `https://www.facebook.com/groups/${gid}/posts/${mp}/`;
      }
      const setParam = u.searchParams.get("set") || "";
      m = setParam.match(/^(?:gm|pcb)\.(\d+)/);
      if (m) {
        const gid = fallbackGroupId || currentGroupIdFromUrl();
        if (gid) return `https://www.facebook.com/groups/${gid}/posts/${m[1]}/`;
      }
      m = u.pathname.match(/\/share\/p\/([A-Za-z0-9]+)/);
      if (m) return `https://www.facebook.com/share/p/${m[1]}/`;
      const sfb = u.searchParams.get("story_fbid");
      const id = u.searchParams.get("id");
      if (sfb && id) return `https://www.facebook.com/permalink.php?story_fbid=${sfb}&id=${id}`;
    } catch {}
    return null;
  }

  function isInsideComment(el) {
    const art = el.closest('[role="article"]');
    if (!art) return false;
    const lbl = art.getAttribute("aria-label") || "";
    return /^(Bình luận|Phản hồi|Comment|Reply)/i.test(lbl);
  }

  function isVisibleNode(el) {
    if (!el || !(el instanceof HTMLElement)) return false;
    if (el.closest('[aria-hidden="true"]')) return false;
    if (el.offsetWidth <= 1 || el.offsetHeight <= 1) return false;
    const st = getComputedStyle(el);
    if (st.display === "none" || st.visibility === "hidden" || parseFloat(st.opacity) === 0 || parseFloat(st.fontSize) === 0) {
      return false;
    }
    return true;
  }

  // --------------------------------------------------- 1) Tự thu thập tên các Nhóm đã tham gia
  function discoverGroupsOnPage() {
    const found = [];
    const curGid = currentGroupIdFromUrl();
    if (curGid) {
      const h1 = document.querySelector('[role="main"] h1, h1');
      const titleName = (h1?.innerText || document.title.replace(/^\(\d+\)\s*/, "").replace(/\s*\|\s*Facebook.*$/i, "")).trim();
      if (titleName && titleName.length > 2 && titleName.toLowerCase() !== "facebook" && !titleName.includes("Bây giờ trong")) {
        found.push({ id: curGid, name: titleName.split("\n")[0].trim() });
      }
    }
    if (location.pathname.startsWith("/groups/joins") || location.pathname.startsWith("/groups/feed")) {
      document.querySelectorAll('a[href*="/groups/"]').forEach((a) => {
        if (a.closest('[aria-label*="Thông báo"], [aria-label*="Notifications"]')) return;
        try {
          const u = new URL(a.href, location.origin);
          const m = u.pathname.match(/^\/groups\/([^/?#]+)\/?$/);
          if (!m) return;
          const gid = m[1];
          if (RESERVED_GROUP_SLUGS.has(gid.toLowerCase())) return;
          let txt = (a.innerText || "").trim().split("\n")[0].trim();
          if (!txt || txt.length < 3 || txt.length > 90) return;
          if (/^(Chưa đọc|Bây giờ trong|Truy cập|Xem nhóm|Tham gia|Đã tham gia|Visit|View group|\d+\s*(thành viên|bài viết|phút|giờ))/i.test(txt)) return;
          found.push({ id: gid, name: txt });
        } catch {}
      });
    }
    if (found.length) {
      chrome.runtime.sendMessage({ type: "RADAR_DISCOVERED_GROUPS", groups: found }, () => void chrome.runtime.lastError);
    }
  }

  // --------------------------------------------------- 2) Parse thời gian đăng bài (giờ)
  function parseAgeString(raw) {
    if (!raw) return null;
    const s = raw.replace(/\s+/g, " ").trim().toLowerCase();
    if (!s || s.length > 45) return null;

    if (/^(vừa xong|bây giờ|just now|now)$/i.test(s)) {
      return { ageHours: 0.02, ageText: "Vừa xong" };
    }
    if (/^(hôm qua|yesterday)(\s+lúc.*|\s+at.*)?$/i.test(s)) {
      return { ageHours: 24, ageText: "Hôm qua" };
    }

    let m = s.match(/^(\d+)\s*(giây|sec|seconds?|s)(?:\s+trước|\s+ago)?$/i);
    if (m) return { ageHours: 0.02, ageText: `${m[1]} giây` };

    m = s.match(/^(\d+)\s*(phút|phut|mins?|minutes?|m)(?:\s+trước|\s+ago)?$/i);
    if (m) return { ageHours: Number(m[1]) / 60, ageText: `${m[1]} phút` };

    m = s.match(/^(\d+)\s*(giờ|gio|hrs?|hours?|h)(?:\s+trước|\s+ago)?$/i);
    if (m) return { ageHours: Number(m[1]), ageText: `${m[1]} giờ` };

    m = s.match(/^(\d+)\s*(ngày|ngay|days?|d)(?:\s+trước|\s+ago)?$/i);
    if (m) {
      const d = Number(m[1]);
      return { ageHours: d * 24, ageText: `${d} ngày` };
    }

    m = s.match(/^(\d+)\s*(tuần|tuan|weeks?|wks?|w)(?:\s+trước|\s+ago)?$/i);
    if (m) {
      const w = Number(m[1]);
      return { ageHours: w * 168, ageText: `${w} tuần` };
    }

    m = s.match(/^(\d+)\s*(tháng|thang|năm|nam|months?|years?)(?:\s+trước|\s+ago)?$/i);
    if (m) return { ageHours: 999, ageText: `${m[1]} ${m[2]}` };

    // Dạng ngày cụ thể: "25 tháng 11", "24 thg 11 lúc 22:17", "12 tháng 10, 2025"
    m = s.match(/^(\d{1,2})\s*(?:tháng|thg)\s*(\d{1,2})(?:\s*,?\s*(\d{4}))?/i);
    if (m) {
      const now = new Date();
      const day = Number(m[1]);
      const month = Number(m[2]) - 1;
      const year = m[3] ? Number(m[3]) : now.getFullYear();
      const dt = new Date(year, month, day, 12, 0, 0);
      if (!isNaN(dt.getTime())) {
        const diffH = Math.max(0, (now.getTime() - dt.getTime()) / 3600000);
        return { ageHours: diffH, ageText: `${day}/${month + 1}` };
      }
    }
    return null;
  }

  function extractCardAge(card) {
    const cardTop = card.getBoundingClientRect().top;
    // Chỉ xét vùng header đầu bài (tránh nhầm chữ "1 tuần 3 buổi" trong nội dung bài)
    const candidates = card.querySelectorAll("a[href], a[role='link'], span");
    for (const el of candidates) {
      if (isInsideComment(el)) continue;
      if (el.closest('[data-ad-comet-preview="message"], [data-ad-preview="message"]')) continue;
      const r = el.getBoundingClientRect();
      if (r.height === 0 || r.top - cardTop > 125) continue;

      const aria = el.getAttribute("aria-label");
      if (aria) {
        const pa = parseAgeString(aria);
        if (pa) return pa;
      }
      if (el.children.length <= 2) {
        const txt = (el.innerText || "").replace(/·/g, " ").trim();
        const pt = parseAgeString(txt);
        if (pt) return pt;
      }
    }
    return { ageHours: null, ageText: "" };
  }

  // --------------------------------------------------- 3) Mở rộng "Xem thêm" để lấy trọn phần dưới bài viết
  function expandSeeMoreInCard(card) {
    let clicked = false;
    const btns = card.querySelectorAll('div[role="button"], span[role="button"]');
    for (const b of btns) {
      if (isInsideComment(b)) continue;
      const t = (b.textContent || "").trim();
      if (t === "Xem thêm" || t === "See more") {
        if (b.dataset.radarClicked === "1") continue;
        b.dataset.radarClicked = "1";
        try {
          b.click();
          clicked = true;
        } catch {}
      }
    }
    if (clicked) {
      card.dataset.radarExpandAt = String(Date.now());
    }
    return clicked;
  }

  function isCardWaitingExpand(card) {
    const t0 = Number(card.dataset.radarExpandAt || "0");
    return t0 > 0 && Date.now() - t0 < 650;
  }

  // --------------------------------------------------- 4) Định vị chuẩn từng thẻ bài viết
  function countPostFooters(container) {
    let count = 0;
    const btns = container.querySelectorAll(
      '[aria-label="Viết bình luận"], [aria-label="Để lại bình luận"], [aria-label="Leave a comment"], [aria-label*="Gửi nội dung này"], [aria-label*="Send this to friends"]'
    );
    for (const b of btns) {
      if (!isInsideComment(b)) count++;
    }
    if (count > 0) return count;
    container.querySelectorAll('div[role="button"], span').forEach((el) => {
      if (el.children.length === 0 && !isInsideComment(el)) {
        const t = (el.textContent || "").trim();
        if (t === "Chia sẻ" || t === "Share") count++;
      }
    });
    return count;
  }

  function findPostCards() {
    const roots = document.querySelectorAll('[role="dialog"], [role="main"]');
    const seeds = new Set();

    (roots.length ? roots : [document.body]).forEach((root) => {
      root.querySelectorAll(
        'h2, h3, h4, [data-ad-comet-preview="message"], [data-ad-preview="message"], [aria-label="Viết bình luận"], [aria-label="Để lại bình luận"]'
      ).forEach((el) => {
        if (!isInsideComment(el) && !el.closest('[role="complementary"], [role="navigation"], [role="banner"]')) {
          seeds.add(el);
        }
      });
    });

    const cards = [];
    const seenEl = new Set();

    for (const seed of seeds) {
      let cur = seed;
      let best = null;
      for (let depth = 0; depth < 14 && cur && cur !== document.body; depth++) {
        const role = cur.getAttribute("role");
        if (role === "feed" || role === "main") break;
        if (cur.offsetWidth >= 300 && cur.offsetHeight >= 95) {
          const fCount = countPostFooters(cur);
          if (fCount > 1) break;
          const hasHeader = !!cur.querySelector('h2, h3, h4, strong, a[role="link"]');
          if (hasHeader && (fCount === 1 || cur.querySelector('[aria-label*="bình luận"], [aria-label*="Bình luận"], [aria-label*="Comment"], [aria-label="Thích"], [aria-label="Like"]'))) {
            best = cur;
          }
        }
        cur = cur.parentElement;
      }
      if (best && !seenEl.has(best)) {
        seenEl.add(best);
        cards.push(best);
      }
    }

    return cards.filter((c) => !cards.some((other) => other !== c && c.contains(other)));
  }

  const UI_NOISE_RE = /^(Xem thêm|See more|Ẩn bớt|Xem bản dịch|See translation|Đáng chú ý|Phù hợp nhất|Bài viết mới|Tất cả cảm xúc|Thích|Bình luận|Chia sẻ|Viết bình luận.*|Theo dõi|Tham gia|Bài viết ẩn danh|\d+\s*(giây|phút|giờ|ngày|tuần|bình luận|lượt chia sẻ).*|Vừa xong)$/i;

  function extractCardDetails(card) {
    const pageGroupId = currentGroupIdFromUrl();
    let groupId = pageGroupId;
    let groupName = "";
    let author = "";
    let postUrl = null;

    if (pageGroupId) {
      const h1 = document.querySelector('[role="main"] h1, h1');
      if (h1) groupName = (h1.innerText || "").trim().split("\n")[0].trim();
    }

    const allLinks = card.querySelectorAll("a[href]");
    for (const a of allLinks) {
      const h = a.href || "";
      if (!groupId && !isInsideComment(a) && h.includes("/groups/")) {
        const gm = h.match(/facebook\.com\/groups\/([^/?#]+)/);
        if (gm && !RESERVED_GROUP_SLUGS.has(gm[1].toLowerCase())) {
          groupId = gm[1];
          const lt = (a.innerText || "").trim().split("\n")[0].trim();
          if (lt && lt.length > 2 && lt.length < 90 && !/^\d+\s*(giây|phút|giờ|ngày)/i.test(lt)) {
            groupName = groupName || lt;
          }
        }
      }
      if (!postUrl) {
        postUrl = extractPostUrlFromHref(h, groupId);
      }
    }

    const headers = card.querySelectorAll("h2, h3, h4");
    for (const hd of headers) {
      if (isInsideComment(hd)) continue;
      const ht = (hd.innerText || "").trim().split("\n")[0].trim();
      if (!ht) continue;
      if (!groupName && groupId && hd.querySelector(`a[href*="/groups/${groupId}"]`)) {
        groupName = ht;
      } else if (!author && ht !== groupName) {
        author = ht;
      }
    }

    const { ageHours, ageText } = extractCardAge(card);

    const pieces = [];
    const seenPiece = new Set();
    const addPiece = (raw) => {
      for (const ln of (raw || "").split(/\n+/)) {
        const s = ln.replace(/\s+/g, " ").trim();
        if (!s || s.length < 2) continue;
        if (UI_NOISE_RE.test(s)) continue;
        if (s === groupName || s === author) continue;
        if (/^Facebook(?:Facebook)+$/i.test(s)) continue;
        if (!seenPiece.has(s)) {
          seenPiece.add(s);
          pieces.push(s);
        }
      }
    };

    card.querySelectorAll('[data-ad-comet-preview="message"], [data-ad-preview="message"]').forEach((m) => {
      if (!isInsideComment(m) && isVisibleNode(m)) addPiece(m.innerText);
    });

    if (pieces.length === 0) {
      card.querySelectorAll('div[dir="auto"], blockquote').forEach((d) => {
        if (isInsideComment(d)) return;
        if (d.closest('h1, h2, h3, h4, [role="button"], form, ul, nav')) return;
        if (!isVisibleNode(d)) return;
        const childDir = Array.from(d.querySelectorAll('div[dir="auto"]')).some((c) => c !== d && isVisibleNode(c));
        if (childDir) return;
        addPiece(d.innerText);
      });
    }

    if (pieces.length === 0) {
      card.querySelectorAll('div[role="img"][aria-label], div[style*="background-image"][aria-label]').forEach((bg) => {
        if (!isInsideComment(bg) && bg.offsetHeight >= 140) {
          addPiece(bg.getAttribute("aria-label") || "");
        }
      });
    }

    const body = pieces.join("\n").trim();
    const fallbackUrl = groupId
      ? `https://www.facebook.com/groups/${groupId}/?sorting_setting=CHRONOLOGICAL`
      : location.href.split("#")[0];

    return {
      groupName: groupName || "Nhóm Facebook",
      author,
      body,
      href: postUrl || fallbackUrl,
      hasExactPostUrl: !!postUrl,
      ageHours,
      ageText,
    };
  }

  // --------------------------------------------------- 5) Quét Chuông (chỉ phụ trợ, bỏ bài có dấu "…" cắt cụt dài nghi ngờ thiếu địa chỉ? Vẫn kiểm tra thời gian <= 2 ngày)
  function collectBellNotifications(batch) {
    const anchors = document.querySelectorAll(
      'a[href*="notif_id="], div[role="alert"] a[href*="/groups/"], div[aria-label*="Thông báo"] a[href*="/groups/"], div[aria-label*="Notifications"] a[href*="/groups/"]'
    );
    for (const a of anchors) {
      const href = a.href;
      if (!href || !href.includes("facebook.com")) continue;
      const text = (a.innerText || "").trim();
      if (text.length < 10) continue;

      // Tìm dòng thời gian ở cuối thông báo chuông ("3 ngày", "1 tuần"...)
      let ageHours = null;
      let ageText = "";
      const lines = text.split(/\n+/).map((s) => s.trim()).filter(Boolean);
      if (lines.length >= 2) {
        const tail = lines[lines.length - 1].split("·")[0].trim();
        const pa = parseAgeString(tail);
        if (pa) {
          ageHours = pa.ageHours;
          ageText = pa.ageText;
        }
      }

      const clean = extractPostUrlFromHref(href);
      let key = clean ? "post:" + clean : "";
      if (!key) {
        try {
          const nid = new URL(href, location.origin).searchParams.get("notif_id");
          if (nid) key = "nid:" + nid;
        } catch {}
      }
      if (!key) key = "bell:" + simpleHash(text.slice(0, 120));
      if (seenKeys.has(key)) continue;
      seenKeys.add(key);
      batch.push({ source: "bell", key, href: clean || href, text, ageHours, ageText });
    }
  }

  function highlightMatchedCard(card, reason, comment) {
    if (card.dataset.radarHighlighted) return;
    card.dataset.radarHighlighted = "1";
    card.style.outline = "3px solid #22c55e";
    card.style.borderRadius = "12px";

    const bar = document.createElement("div");
    bar.style.cssText =
      "display:flex;align-items:center;justify-content:space-between;gap:8px;padding:8px 12px;margin:6px 0;" +
      "background:#052e16;color:#bbf7d0;border:1px solid #22c55e;border-radius:10px;font:13px/1.4 system-ui,sans-serif;z-index:9;";
    const lbl = document.createElement("span");
    lbl.textContent = `🎯 ĐÚNG MỤC TIÊU (${reason})`;
    const btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = "📋 Copy bình luận mẫu";
    btn.style.cssText =
      "padding:5px 10px;border-radius:8px;border:0;background:#16a34a;color:#fff;font-weight:600;cursor:pointer;";
    btn.onclick = async (e) => {
      e.stopPropagation();
      try {
        await navigator.clipboard.writeText(comment || "");
        btn.textContent = "✅ Đã copy! Dán Ctrl+V bên dưới";
      } catch {}
    };
    bar.append(lbl, btn);
    card.prepend(bar);
  }

  function collectFeedPosts(batch) {
    if (!location.pathname.startsWith("/groups") && location.pathname !== "/" && !document.querySelector('[role="dialog"]')) {
      return { cards: [], pendingExpand: false };
    }
    const cards = findPostCards();
    let pendingExpand = false;

    for (const card of cards) {
      // Mở "Xem thêm" trước khi đọc để lấy trọn cả dòng Địa chỉ ở cuối bài!
      if (expandSeeMoreInCard(card) || isCardWaitingExpand(card)) {
        pendingExpand = true;
        continue;
      }

      const info = extractCardDetails(card);
      if (!info.body || info.body.length < 6) continue;
      const normBody = info.body.replace(/\s+/g, " ").trim();
      const key = info.hasExactPostUrl
        ? "post:" + info.href
        : "feed:" + simpleHash(`${info.groupName}|${info.author}|${normBody.slice(0, 140)}`);
      cardByKey.set(key, card);
      if (seenKeys.has(key)) continue;
      seenKeys.add(key);
      batch.push({
        source: "feed",
        key,
        href: info.href,
        groupName: info.groupName,
        author: info.author,
        body: info.body,
        ageHours: info.ageHours,
        ageText: info.ageText,
        text: `Bây giờ trong ${info.groupName}: ${info.body}`,
      });
    }
    return { cards, pendingExpand };
  }

  function scanAll() {
    discoverGroupsOnPage();
    const batch = [];
    collectBellNotifications(batch);
    const { pendingExpand } = collectFeedPosts(batch);
    if (pendingExpand) {
      scheduleScan(750);
    }
    if (batch.length > 0) {
      chrome.runtime.sendMessage({ type: "RADAR_NOTIFS", items: batch }, (res) => {
        void chrome.runtime.lastError;
        const matched = res?.data?.matchedItems || [];
        for (const m of matched) {
          const card = cardByKey.get(m.key);
          if (card) highlightMatchedCard(card, m.reason, m.comment);
        }
      });
    }
  }

  function scheduleScan(delay = 700) {
    if (scanTimer) clearTimeout(scanTimer);
    scanTimer = setTimeout(scanAll, delay);
  }

  // --------------------------------------------------- 6) Cuộn sâu quét TẤT CẢ bài <= 2 ngày trong Nhóm rồi mới dừng!
  function sleep(ms) {
    return new Promise((r) => setTimeout(r, ms));
  }

  async function runDeepCrawlUntil2Days(maxSteps = 55) {
    if (crawlRunning) return;
    crawlRunning = true;
    const startUrl = location.href.split("#")[0];
    let unchangedHeightCount = 0;
    let lastScrollHeight = 0;

    try {
      await sleep(1800);
      for (let step = 0; step < maxSteps; step++) {
        if (location.href.split("#")[0] !== startUrl) break;

        // Bước 1: Mở hết các nút "Xem thêm" đang hiện trên màn hình để lộ phần Địa chỉ cuối bài
        const cardsBefore = findPostCards();
        let anyExpanded = false;
        for (const c of cardsBefore) {
          if (expandSeeMoreInCard(c)) anyExpanded = true;
        }
        if (anyExpanded) {
          await sleep(750);
        }

        // Bước 2: Quét toàn bộ bài đã mở đầy đủ
        scanAll();

        // Bước 3: Kiểm tra mốc 2 ngày (bỏ qua 2 thẻ đầu tiên phòng bài ghim cũ của Admin)
        const cardsNow = findPostCards();
        if (cardsNow.length >= 5) {
          const nonPinned = cardsNow.slice(2);
          let tailOldStreak = 0;
          for (let i = nonPinned.length - 1; i >= 0; i--) {
            const { ageHours } = extractCardAge(nonPinned[i]);
            if (ageHours === null) continue;
            if (ageHours > 54) tailOldStreak++;
            else break;
          }
          // Đã gặp liên tiếp >= 3 bài cũ hơn 2 ngày ở cuối danh sách -> đã vét sạch bài dưới 2 ngày!
          if (tailOldStreak >= 3) {
            break;
          }
        }

        // Bước 4: Cuộn xuống để tải tiếp loạt bài tiếp theo
        const curH = document.documentElement.scrollHeight;
        if (curH <= lastScrollHeight + 20) {
          unchangedHeightCount++;
          if (unchangedHeightCount >= 4) break;
        } else {
          unchangedHeightCount = 0;
          lastScrollHeight = curH;
        }

        window.scrollBy({ top: Math.max(700, Math.round(window.innerHeight * 0.88)), behavior: "smooth" });
        await sleep(2000);
      }
      scanAll();
    } finally {
      crawlRunning = false;
    }
  }

  if (location.search.includes("radar_watch=1")) {
    runDeepCrawlUntil2Days(55);
  }

  // --------------------------------------------------- 7) Nhảy trúng bài + Hiện sẵn khung Bình luận từ App Radar HS
  function handleAppHandoff() {
    if (!location.hash || (!location.hash.includes("radar_cmt=") && !location.hash.includes("radar_q="))) return;
    const params = new URLSearchParams(location.hash.slice(1));
    const targetSnippet = (params.get("radar_q") || "").trim();
    const draftComment = (params.get("radar_cmt") || "").trim();

    history.replaceState(null, "", location.pathname + location.search);

    if (draftComment) {
      showFloatingDraftBox(draftComment);
    }
    if (targetSnippet) {
      locateAndScrollToPost(targetSnippet, 0);
    }
  }

  function locateAndScrollToPost(snippet, attempt) {
    const needle = snippet.toLowerCase().replace(/\s+/g, " ").slice(0, 42);
    if (!needle) return;
    const cards = findPostCards();
    for (const c of cards) {
      const txt = (c.innerText || "").toLowerCase().replace(/\s+/g, " ");
      if (txt.includes(needle)) {
        expandSeeMoreInCard(c);
        c.style.outline = "4px solid #3b82f6";
        c.style.borderRadius = "12px";
        c.scrollIntoView({ behavior: "smooth", block: "center" });
        const tag = document.createElement("div");
        tag.textContent = "🎯 BÀI ĐĂNG BẠN VỪA MỞ TỪ RADAR HS — BẤM VÀO Ô BÌNH LUẬN BÊN DƯỚI RỒI NHẤN CTRL + V";
        tag.style.cssText =
          "padding:8px 12px;background:#1d4ed8;color:#fff;font:600 13px system-ui,sans-serif;border-radius:10px;margin-bottom:6px;";
        c.prepend(tag);
        return;
      }
    }
    if (attempt < 7) {
      if (attempt >= 1) window.scrollBy({ top: 750, behavior: "smooth" });
      setTimeout(() => locateAndScrollToPost(snippet, attempt + 1), 1300);
    }
  }

  function showFloatingDraftBox(initialComment) {
    const old = document.getElementById("radar-draft-floating");
    if (old) old.remove();

    const box = document.createElement("div");
    box.id = "radar-draft-floating";
    box.style.cssText =
      "position:fixed;right:18px;bottom:18px;width:340px;max-width:92vw;z-index:2147483647;" +
      "background:#0f172a;color:#e2e8f0;border:2px solid #2563eb;border-radius:14px;padding:12px;" +
      "box-shadow:0 12px 32px rgba(0,0,0,.55);font:13.5px/1.45 system-ui,sans-serif;";

    box.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
        <strong style="color:#93c5fd;">💬 Bình luận soạn sẵn (Radar HS)</strong>
        <button id="rd-close" style="background:none;border:0;color:#94a3b8;font-size:16px;cursor:pointer;">✕</button>
      </div>
      <div id="rd-chips" style="display:flex;gap:6px;margin-bottom:6px;">
        <button data-m="toan" style="flex:1;padding:4px;border-radius:7px;border:1px solid #334155;background:#1e293b;color:#e2e8f0;cursor:pointer;font-size:12px;">📘 Toán</button>
        <button data-m="ly" style="flex:1;padding:4px;border-radius:7px;border:1px solid #334155;background:#1e293b;color:#e2e8f0;cursor:pointer;font-size:12px;">⚡ Lý</button>
        <button data-m="hoa" style="flex:1;padding:4px;border-radius:7px;border:1px solid #334155;background:#1e293b;color:#e2e8f0;cursor:pointer;font-size:12px;">🧪 Hóa</button>
      </div>
      <textarea id="rd-ta" rows="5" style="width:100%;box-sizing:border-box;background:#1e293b;color:#fff;border:1px solid #334155;border-radius:8px;padding:8px;font:inherit;resize:vertical;"></textarea>
      <div style="display:flex;gap:8px;margin-top:8px;align-items:center;">
        <button id="rd-copy" style="flex:1;padding:8px;border-radius:8px;border:0;background:#2563eb;color:#fff;font-weight:600;cursor:pointer;">📋 Copy bình luận</button>
      </div>
      <div id="rd-msg" style="color:#86efac;font-size:12px;margin-top:5px;">Đã copy sẵn — bấm ô bình luận FB rồi nhấn Ctrl + V!</div>
    `;
    document.body.appendChild(box);

    const ta = box.querySelector("#rd-ta");
    const msg = box.querySelector("#rd-msg");
    ta.value = initialComment;
    navigator.clipboard?.writeText(initialComment).catch(() => {});

    box.querySelector("#rd-close").onclick = () => box.remove();
    box.querySelector("#rd-copy").onclick = async () => {
      try {
        await navigator.clipboard.writeText(ta.value);
        msg.textContent = "✅ Đã copy vào bộ nhớ tạm — nhấn Ctrl + V để dán!";
      } catch {
        ta.select();
        msg.textContent = "Hãy nhấn Ctrl + C để copy đoạn đang bôi đen";
      }
    };

    chrome.runtime.sendMessage({ type: "RADAR_RECENT" }, (res) => {
      void chrome.runtime.lastError;
      const tpls = res?.templates || {};
      box.querySelectorAll("[data-m]").forEach((b) => {
        b.onclick = async () => {
          const val = tpls[b.dataset.m];
          if (val) {
            ta.value = val;
            try { await navigator.clipboard.writeText(val); } catch {}
            msg.textContent = `✅ Đã đổi & copy mẫu ${b.textContent}!`;
          }
        };
      });
    });
  }

  chrome.runtime.onMessage.addListener((msg, _s, sendResponse) => {
    if (msg?.type === "FORCE_SCAN") {
      seenKeys.clear();
      if (location.pathname.startsWith("/groups/")) {
        runDeepCrawlUntil2Days(40);
      } else {
        scanAll();
      }
      sendResponse({ ok: true });
    }
  });

  const obs = new MutationObserver(() => scheduleScan(700));
  obs.observe(document.documentElement, { childList: true, subtree: true });
  handleAppHandoff();
  setTimeout(scanAll, 1200);
  setTimeout(scanAll, 3000);
})();

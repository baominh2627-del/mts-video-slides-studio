import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import {
  getAuth, GoogleAuthProvider, signInWithPopup, signInWithRedirect, onAuthStateChanged, signOut,
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";
import {
  getFirestore, collection, query, orderBy, limit, onSnapshot, doc, updateDoc, setDoc, serverTimestamp,
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js";
import {
  getMessaging, getToken, onMessage, isSupported,
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-messaging.js";

const app = initializeApp(self.FIREBASE_CONFIG);
const auth = getAuth(app);
const db = getFirestore(app);

const $ = (s) => document.querySelector(s);
let posts = [];
let templates = { toan: "", ly: "", hoa: "" };
let currentTab = "new";
let focusId = new URLSearchParams(location.search).get("id");
let unsub = null;
let unsubTpls = null;
let swReg = null;

// ---------------------------------------------------------------- tiện ích
function toast(msg, ms = 2500) {
  const t = $("#toast");
  t.textContent = msg;
  t.classList.remove("hidden");
  clearTimeout(toast._t);
  toast._t = setTimeout(() => t.classList.add("hidden"), ms);
}

async function copyText(txt, okMsg = "📋 Đã sao chép!") {
  if (!txt || !txt.trim()) return toast("Chưa có nội dung để sao chép");
  try {
    await navigator.clipboard.writeText(txt);
    toast(okMsg);
  } catch {
    toast("Không copy tự động được, hãy bôi đen copy tay");
  }
}

function guessTemplateByReason(reason = "") {
  if (reason.includes("Toán") && templates.toan) return templates.toan;
  if (reason.includes("Lý") && templates.ly) return templates.ly;
  if (reason.includes("Hóa") && templates.hoa) return templates.hoa;
  return templates.toan || templates.ly || templates.hoa || "";
}

function timeAgo(date) {
  if (!date) return "";
  const s = Math.floor((Date.now() - date.getTime()) / 1000);
  if (s < 60) return "vừa xong";
  if (s < 3600) return `${Math.floor(s / 60)} phút trước`;
  if (s < 86400) return `${Math.floor(s / 3600)} giờ trước`;
  return date.toLocaleString("vi-VN");
}

const isIOS = /iphone|ipad|ipod/i.test(navigator.userAgent);
const isStandalone = matchMedia("(display-mode: standalone)").matches || navigator.standalone;

// ---------------------------------------------------------------- đăng nhập
$("#btn-login").onclick = async () => {
  const provider = new GoogleAuthProvider();
  try {
    await signInWithPopup(auth, provider);
  } catch (e) {
    if (e.code === "auth/popup-blocked" || e.code === "auth/operation-not-supported-in-this-environment") {
      await signInWithRedirect(auth, provider);
    } else {
      $("#login-error").textContent = e.message;
    }
  }
};
$("#btn-logout").onclick = () => signOut(auth);

onAuthStateChanged(auth, async (user) => {
  if (unsub) { unsub(); unsub = null; }
  if (unsubTpls) { unsubTpls(); unsubTpls = null; }
  if (!user) {
    $("#login").classList.remove("hidden");
    $("#main").classList.add("hidden");
    return;
  }
  if (self.OWNER_EMAIL && user.email !== self.OWNER_EMAIL) {
    $("#login-error").textContent = `Tài khoản ${user.email} không có quyền dùng app này.`;
    await signOut(auth);
    return;
  }
  $("#login").classList.add("hidden");
  $("#main").classList.remove("hidden");
  if (isIOS && !isStandalone) $("#ios-hint").classList.remove("hidden");
  listenTemplates();
  listenPosts();
  initPush(false);
});

// ---------------------------------------------------------------- mẫu bình luận nhanh
function listenTemplates() {
  unsubTpls = onSnapshot(doc(db, "settings", "templates"), (snap) => {
    if (snap.exists()) {
      const d = snap.data();
      templates = { toan: d.toan || "", ly: d.ly || "", hoa: d.hoa || "" };
      if (document.activeElement !== $("#tpl-toan")) $("#tpl-toan").value = templates.toan;
      if (document.activeElement !== $("#tpl-ly")) $("#tpl-ly").value = templates.ly;
      if (document.activeElement !== $("#tpl-hoa")) $("#tpl-hoa").value = templates.hoa;
      render();
    }
  });
}

document.querySelectorAll("[data-copy-tpl]").forEach((btn) => {
  btn.onclick = () => {
    const k = btn.dataset.copyTpl;
    const label = { toan: "Toán", ly: "Lý", hoa: "Hóa" }[k] || k;
    const val = $(`#tpl-${k}`).value;
    copyText(val, `📋 Đã sao chép mẫu môn ${label}!`);
  };
});

$("#btn-save-tpls").onclick = async () => {
  const data = {
    toan: $("#tpl-toan").value.trim(),
    ly: $("#tpl-ly").value.trim(),
    hoa: $("#tpl-hoa").value.trim(),
    updatedAt: serverTimestamp(),
  };
  await setDoc(doc(db, "settings", "templates"), data, { merge: true });
  toast("✅ Đã lưu mẫu bình luận!");
};

// ---------------------------------------------------------------- dữ liệu bài viết
function listenPosts() {
  const q = query(collection(db, "posts"), orderBy("createdAt", "desc"), limit(200));
  let first = true;
  unsub = onSnapshot(q, (snap) => {
    posts = snap.docs.map((d) => ({ id: d.id, ...d.data() }));
    if (!first) {
      const added = snap.docChanges().filter((c) => c.type === "added").length;
      if (added) toast(`🔔 Có ${added} bài mới!`);
    }
    first = false;
    if (focusId) {
      const p = posts.find((x) => x.id === focusId);
      if (p) currentTab = p.status || "new";
    }
    render();
  }, (err) => toast("Lỗi tải dữ liệu: " + err.message, 5000));
}

async function setStatus(id, status) {
  await updateDoc(doc(db, "posts", id), { status, updatedAt: serverTimestamp() });
}

// ---------------------------------------------------------------- giao diện
document.querySelectorAll(".tab").forEach((b) => {
  b.onclick = () => { currentTab = b.dataset.tab; focusId = null; render(); };
});

function render() {
  document.querySelectorAll(".tab").forEach((b) => b.classList.toggle("active", b.dataset.tab === currentTab));
  $("#count-new").textContent = posts.filter((p) => (p.status || "new") === "new").length;

  const list = $("#list");
  list.innerHTML = "";
  const items = posts.filter((p) => (p.status || "new") === currentTab);
  $("#empty").classList.toggle("hidden", items.length > 0);
  const tpl = $("#card-tpl");

  for (const p of items) {
    const el = tpl.content.firstElementChild.cloneNode(true);
    el.querySelector(".reason").textContent = p.reason || "";
    el.querySelector(".time").textContent = timeAgo(p.createdAt?.toDate?.());
    el.querySelector(".subject").textContent = p.subject || "";
    const text = el.querySelector(".text");
    text.textContent = p.text || "";
    if ((p.text || "").length > 300) {
      text.classList.add("clamp");
      const more = el.querySelector(".more");
      more.classList.remove("hidden");
      more.onclick = () => { text.classList.toggle("clamp"); more.textContent = text.classList.contains("clamp") ? "Xem thêm" : "Thu gọn"; };
    }
    const ta = el.querySelector(".comment");
    ta.value = p.comment || guessTemplateByReason(p.reason);

    el.querySelectorAll("[data-pick]").forEach((chip) => {
      chip.onclick = () => {
        const k = chip.dataset.pick;
        const label = { toan: "Toán", ly: "Lý", hoa: "Hóa" }[k] || k;
        const val = $(`#tpl-${k}`)?.value || templates[k] || "";
        if (val) {
          ta.value = val;
          copyText(val, `📋 Đã đổi & copy mẫu ${label}!`);
        }
      };
    });

    el.querySelector(".act-open").onclick = async () => {
      if (ta.value.trim()) {
        await copyText(ta.value, "📋 Đã copy bình luận — dán vào Facebook nhé!");
      }
      if (p.link) window.open(p.link, "_blank", "noopener");
      else toast("Bài này không có link trực tiếp");
    };
    el.querySelector(".act-done").onclick = () => setStatus(p.id, "done");
    el.querySelector(".act-skip").onclick = () => setStatus(p.id, "skip");
    const restore = el.querySelector(".act-restore");
    if (currentTab !== "new") {
      restore.classList.remove("hidden");
      restore.onclick = () => setStatus(p.id, "new");
      el.querySelector(currentTab === "done" ? ".act-done" : ".act-skip").classList.add("hidden");
    }

    if (p.id === focusId) el.classList.add("highlight");
    list.appendChild(el);
  }
  if (focusId) {
    const h = list.querySelector(".highlight");
    if (h) h.scrollIntoView({ behavior: "smooth", block: "center" });
  }
}

// ---------------------------------------------------------------- thông báo đẩy
async function initPush(askPermission) {
  const btn = $("#btn-notify");
  if (!("serviceWorker" in navigator) || !(await isSupported())) {
    btn.textContent = isIOS ? "🔔 Cần thêm vào MH chính" : "🔕 Trình duyệt không hỗ trợ";
    btn.disabled = true;
    return;
  }
  swReg = swReg || await navigator.serviceWorker.register("/firebase-messaging-sw.js");

  if (Notification.permission === "denied") {
    btn.textContent = "🔕 Thông báo bị chặn";
    btn.onclick = () => toast("Hãy cho phép thông báo trong cài đặt trình duyệt/điện thoại", 5000);
    return;
  }
  if (Notification.permission !== "granted") {
    btn.textContent = "🔔 Bật thông báo";
    btn.onclick = () => initPush(true);
    if (!askPermission) return;
    const perm = await Notification.requestPermission();
    if (perm !== "granted") return initPush(false);
  }

  try {
    const messaging = getMessaging(app);
    const token = await getToken(messaging, { vapidKey: self.VAPID_KEY, serviceWorkerRegistration: swReg });
    await setDoc(doc(db, "tokens", token), {
      token, ua: navigator.userAgent, updatedAt: serverTimestamp(),
    });
    btn.textContent = "🔔 Đã bật";
    btn.classList.add("on");
    btn.onclick = () => toast("Thiết bị này đã nhận thông báo");

    onMessage(messaging, (payload) => {
      const n = payload.notification || {};
      toast(n.title || "Có bài mới");
      swReg.showNotification(n.title || "Có bài mới", {
        body: n.body, icon: "/icons/icon-192.png", tag: payload.data?.postId,
        data: { postId: payload.data?.postId },
      });
    });
  } catch (e) {
    toast("Không bật được thông báo: " + e.message, 5000);
  }
}

navigator.serviceWorker?.addEventListener("message", (e) => {
  if (e.data?.type === "open-post" && e.data.postId) {
    focusId = e.data.postId;
    const p = posts.find((x) => x.id === focusId);
    if (p) currentTab = p.status || "new";
    render();
  }
});

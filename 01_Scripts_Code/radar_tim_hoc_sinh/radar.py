# -*- coding: utf-8 -*-
"""
RADAR TÌM HỌC SINH
------------------
Đọc email thông báo bài viết mới trong Group mà Facebook gửi vào Gmail của bạn,
lọc bài tìm gia sư phù hợp, (tuỳ chọn) nhờ AI soạn sẵn bình luận,
rồi đẩy thông báo về APP RIÊNG (điện thoại + máy tính) và/hoặc Telegram
để BẠN TỰ vào bình luận.

Không đăng nhập, không quét, không thao tác gì trên Facebook.

Cách chạy:
    python radar.py                    # chạy liên tục, kiểm tra mỗi N phút
    python radar.py --once             # kiểm tra 1 lần rồi thoát
    python radar.py --once --dry-run   # in ra màn hình, không gửi đi đâu
    python radar.py --test-notify      # gửi 1 thông báo thử tới các kênh đã bật
    python radar.py --test-text "em cần tìm gia sư lý 12 ạ"   # thử bộ lọc + AI
"""

import argparse
import email
import imaplib
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from email.policy import default as default_policy
from html.parser import HTMLParser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"
SEEN_PATH = BASE_DIR / "seen.json"

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ----------------------------------------------------------------- tiện ích
def log(msg):
    print(f"[{datetime.now():%H:%M:%S}] {msg}", flush=True)


def bo_dau(text):
    """Bỏ dấu tiếng Việt + viết thường để so khớp ('Vật Lý' -> 'vat ly')."""
    text = text.replace("đ", "d").replace("Đ", "D")
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", text.lower())


def _pattern(kw):
    return r"(?<![a-z0-9])" + re.escape(bo_dau(kw).strip()) + r"(?![a-z0-9])"


def co_tu_khoa(text_norm, keywords):
    """Trả về các từ khoá xuất hiện (khớp nguyên từ, không phân biệt dấu)."""
    return [kw for kw in keywords if bo_dau(kw).strip() and re.search(_pattern(kw), text_norm)]


def load_json(path, fallback):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return fallback


def save_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ----------------------------------------------------------- đọc nội dung email
class _HTMLText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts, self.links = [], []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script", "head"):
            self._skip += 1
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)
        if tag in ("br", "p", "div", "tr", "td", "li"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("style", "script", "head") and self._skip:
            self._skip -= 1
        if tag in ("p", "div", "tr", "td", "li", "a", "span", "table"):
            self.parts.append("\n")

    def handle_data(self, data):
        if not self._skip:
            self.parts.append(data)


BOILERPLATE = [
    "huy dang ky", "unsubscribe", "meta platforms", "facebook, inc", "1 meta way",
    "menlo park", "tin nhan nay da duoc gui", "this message was sent", "thong bao qua email",
    "cai dat thong bao", "notification settings", "xem tren facebook", "view on facebook",
    "to help keep your account secure", "de giu an toan cho tai khoan",
]


def doc_email(msg):
    """Trả về (tiêu đề, nội dung text, danh sách link)."""
    subject = str(msg.get("Subject", ""))
    text, links = "", []
    plain, html = None, None
    for part in msg.walk():
        ctype = part.get_content_type()
        if ctype == "text/plain" and plain is None:
            plain = part.get_content()
        elif ctype == "text/html" and html is None:
            html = part.get_content()
    if html:
        p = _HTMLText()
        p.feed(html)
        links = p.links
        text = "".join(p.parts)
    if plain and (not text.strip() or len(plain) > 30):
        text = plain
        links += re.findall(r"https?://\S+", plain)
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("http"):
            continue
        if any(b in bo_dau(line) for b in BOILERPLATE):
            continue
        lines.append(line)
    return subject, "\n".join(lines), links


def chon_link_bai(links):
    """Ưu tiên link dẫn tới bài viết trong group."""
    def decoded(u):
        return urllib.parse.unquote(urllib.parse.unquote(u))
    for u in links:
        d = decoded(u)
        if "facebook.com" in d and "groups" in d and ("posts" in d or "permalink" in d or "multi_permalinks" in d):
            return u
    for u in links:
        d = decoded(u)
        if "facebook.com" in d and "groups" in d:
            return u
    for u in links:
        if "facebook.com" in u:
            return u
    return None


# ------------------------------------------------------------------- bộ lọc
def danh_gia_bai(text, cfg):
    """Trả về (đạt?, lý do).

    Thứ tự:
      1. Có từ loại trừ (offline, dạy ở nhà, kèm 1:1, nhận dạy...)  -> BỎ
      2. Không có cụm nhu cầu (tìm gia sư, cần gs...)               -> BỎ
      3. Không có môn cần tìm (toán, lý, hoá)                        -> BỎ
      4. Có ghi lớp nhưng không phải lớp cho phép (10, 11, 12)       -> BỎ
         Không ghi lớp                                              -> vẫn NHẬN
    """
    f = cfg["bo_loc"]
    norm = bo_dau(text)

    loai = co_tu_khoa(norm, f.get("tu_loai_tru", []))
    if loai:
        return False, f"có từ loại trừ: {', '.join(loai)}"

    nhu_cau = co_tu_khoa(norm, f.get("tu_nhu_cau", []))
    if not nhu_cau:
        return False, "không phải bài tìm gia sư"

    # xoá các cụm dễ gây nhầm môn: "toàn bộ" -> "toan", "Thanh Hóa" -> "hoa", "lý do" -> "ly"...
    norm_mon = norm
    for cum in f.get("cum_de_nham", []):
        norm_mon = re.sub(_pattern(cum), " ", norm_mon)

    mon = co_tu_khoa(norm_mon, f.get("mon_hoc", []))
    if not mon:
        return False, "không đúng môn"
    ten_mon = {}
    for m in mon:
        goc = bo_dau(m).replace("vat ", "").replace(" hoc", "").replace("li", "ly")
        ten_mon.setdefault(goc, {"toan": "Toán", "ly": "Lý", "hoa": "Hóa"}.get(goc, m.capitalize()))
    ly_do = [f"Môn: {', '.join(ten_mon.values())}"]

    lop_cho_phep = {int(x) for x in f.get("lop", [])}
    if lop_cho_phep:
        tien_to = "|".join(re.escape(bo_dau(t)) for t in
                           ["lớp", "lop", "khối", "l"] + f.get("mon_hoc", []))
        lop_thay = {int(n) for n in re.findall(
            r"(?<![a-z0-9])(?:" + tien_to + r")\s*(\d{1,2})(?!\d)", norm_mon) if 1 <= int(n) <= 12}
        if lop_thay:
            hop_le = sorted(lop_thay & lop_cho_phep)
            if not hop_le:
                return False, f"lớp {', '.join(map(str, sorted(lop_thay)))} không nằm trong danh sách"
            ly_do.append(f"Lớp: {', '.join(map(str, hop_le))}")
        else:
            ly_do.append("Không ghi lớp")

    return True, " | ".join(ly_do)


# --------------------------------------------------------------- AI soạn bình luận
def soan_binh_luan(text, cfg):
    ai = cfg.get("ai", {})
    key = ai.get("gemini_api_key", "").strip()
    if not ai.get("bat", False) or not key or key.startswith("DIEN_"):
        return None
    prompt = (
        "Bạn là gia sư đang trả lời một bài đăng tìm gia sư trên Facebook.\n"
        "Viết MỘT bình luận tiếng Việt ngắn (3-6 dòng), tự nhiên, lịch sự, "
        "nhắc đúng nhu cầu trong bài (môn, lớp, mục tiêu nếu có), "
        "chỉ dùng thông tin có thật trong hồ sơ, không bịa thành tích. "
        "Kết thúc bằng lời mời liên hệ Zalo. Không dùng hashtag. Chỉ trả về nội dung bình luận.\n\n"
        f"HỒ SƠ GIA SƯ:\n{cfg.get('ho_so_gia_su', '')}\n\n"
        f"BÀI ĐĂNG:\n{text[:1500]}"
    )
    model = ai.get("model", "gemini-2.5-flash")
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key="
           + urllib.parse.quote(key))
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read().decode("utf-8"))
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        log(f"AI lỗi: {e}")
        return None


# ----------------------------------------------------------------- gửi thông báo
def gui_telegram(post, cfg):
    tg = cfg.get("telegram", {})
    lines = ["🔔 BÀI TÌM GIA SƯ MỚI", f"✅ {post['reason']}", "",
             f"📌 {post['subject']}", post["text"][:1200], "",
             f"👉 Mở bài: {post['link']}" if post["link"] else "👉 (Không có link — mở email trong Gmail)"]
    if post.get("comment"):
        lines += ["", "💬 Bình luận gợi ý:", "", post["comment"]]
    body = urllib.parse.urlencode({
        "chat_id": tg["chat_id"], "text": "\n".join(lines)[:4000],
        "disable_web_page_preview": "true",
    }).encode("utf-8")
    url = f"https://api.telegram.org/bot{tg['bot_token']}/sendMessage"
    with urllib.request.urlopen(urllib.request.Request(url, data=body), timeout=30) as r:
        return json.loads(r.read().decode("utf-8")).get("ok", False)


def gui_thong_bao(post, cfg, dry_run=False):
    """Gửi tới mọi kênh đã bật. Trả về True nếu ít nhất 1 kênh thành công."""
    if dry_run:
        print("\n" + "=" * 60)
        print(json.dumps(post, ensure_ascii=False, indent=2))
        print("=" * 60 + "\n")
        return True
    ok_any = False
    for kenh in cfg.get("kenh_thong_bao", ["app"]):
        try:
            if kenh == "app":
                import firebase_app
                ok = firebase_app.gui(post, cfg)
            elif kenh == "telegram":
                ok = gui_telegram(post, cfg)
            else:
                log(f"Kênh không hỗ trợ: {kenh}")
                continue
            log(f"   → {kenh}: {'OK' if ok else 'thất bại'}")
            ok_any = ok_any or ok
        except Exception as e:
            log(f"   → {kenh} lỗi: {e}")
    return ok_any


# ------------------------------------------------------------------ Gmail (IMAP)
def kiem_tra_gmail(cfg, dry_run=False):
    g = cfg["gmail"]
    seen = load_json(SEEN_PATH, {"ids": []})
    seen_ids = set(seen["ids"])

    since = (datetime.now() - timedelta(days=int(g.get("so_ngay_quet_lai", 1)))).strftime("%d-%b-%Y")
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(g["email"], g["app_password"].replace(" ", ""))
    imap.select(g.get("thu_muc", "INBOX"), readonly=True)  # chỉ đọc, không đánh dấu đã xem
    _, data = imap.search(None, f'(FROM "facebookmail.com" SINCE {since})')
    nums = data[0].split()
    log(f"Có {len(nums)} email từ Facebook kể từ {since}")

    moi, dat = 0, 0
    for num in nums:
        _, hdr = imap.fetch(num, "(BODY.PEEK[HEADER.FIELDS (MESSAGE-ID)])")
        mid = email.message_from_bytes(hdr[0][1]).get("Message-ID", "").strip() or f"num-{num.decode()}"
        if mid in seen_ids:
            continue
        _, raw = imap.fetch(num, "(BODY.PEEK[])")
        msg = email.message_from_bytes(raw[0][1], policy=default_policy)
        subject, text, links = doc_email(msg)
        moi += 1
        ok, ly_do = danh_gia_bai(subject + "\n" + text, cfg)
        if ok:
            dat += 1
            log(f"✅ ĐẠT: {subject[:70]} ({ly_do})")
            post = {
                "subject": subject, "text": text[:3000], "link": chon_link_bai(links) or "",
                "reason": ly_do, "comment": soan_binh_luan(text, cfg) or "",
            }
            if not gui_thong_bao(post, cfg, dry_run):
                continue  # chưa gửi được thì lần sau thử lại
        else:
            log(f"   bỏ qua: {subject[:70]} ({ly_do})")
        seen_ids.add(mid)

    imap.logout()
    if not dry_run:
        seen["ids"] = list(seen_ids)[-5000:]
        save_json(SEEN_PATH, seen)
    log(f"Xong: {moi} email mới, {dat} bài phù hợp")


# ------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="Radar tìm học sinh")
    ap.add_argument("--once", action="store_true", help="kiểm tra 1 lần rồi thoát")
    ap.add_argument("--dry-run", action="store_true", help="in ra màn hình, không gửi đi đâu")
    ap.add_argument("--test-notify", action="store_true", help="gửi 1 thông báo thử")
    ap.add_argument("--test-text", help="thử bộ lọc + AI với 1 đoạn văn bản")
    args = ap.parse_args()

    if not CONFIG_PATH.exists():
        print("Chưa có config.json. Hãy copy config.example.json -> config.json rồi điền thông tin.")
        sys.exit(1)
    cfg = load_json(CONFIG_PATH, {})

    if args.test_notify:
        ok = gui_thong_bao({
            "subject": "🧪 Thông báo thử từ Radar",
            "text": "em cần tìm gia sư lý 12, cả học và cả ôn thi ạ, học online ạ",
            "link": "https://www.facebook.com/", "reason": "Môn: Lý | Lớp: 12",
            "comment": "Chào em, anh nhận kèm Lý 12 online... (bình luận mẫu)",
        }, cfg)
        print("Gửi thành công!" if ok else "Gửi thất bại — xem lỗi ở trên.")
        return

    if args.test_text:
        ok, ly_do = danh_gia_bai(args.test_text, cfg)
        print(f"{'ĐẠT     ' if ok else 'BỎ QUA  '} | {ly_do} | {args.test_text}")
        if ok and cfg.get("ai", {}).get("bat"):
            print("Bình luận gợi ý:\n" + (soan_binh_luan(args.test_text, cfg) or "(AI lỗi)"))
        return

    phut = int(cfg.get("chu_ky_phut", 3))
    while True:
        try:
            kiem_tra_gmail(cfg, args.dry_run)
        except Exception as e:
            log(f"Lỗi: {e}")
        if args.once:
            break
        time.sleep(phut * 60)


if __name__ == "__main__":
    main()

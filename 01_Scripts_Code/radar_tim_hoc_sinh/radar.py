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
import threading
import time
import unicodedata
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from email.policy import default as default_policy
from html.parser import HTMLParser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"
SEEN_PATH = BASE_DIR / "seen.json"
LOG_PATH = BASE_DIR / "radar.log"
LOCK_PATH = BASE_DIR / "radar.lock"
_lock_fh = None
_seen_lock = threading.Lock()
_recent_events = []

try:
    if sys.stdout:
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ----------------------------------------------------------------- tiện ích
def log(msg):
    line = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    if sys.stdout:
        print(line, flush=True)
    try:
        if LOG_PATH.exists() and LOG_PATH.stat().st_size > 512_000:
            LOG_PATH.replace(BASE_DIR / "radar.log.old")
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def giu_khoa_duy_nhat():
    """Đảm bảo chỉ có 1 tiến trình radar.py chạy ngầm tại một thời điểm."""
    global _lock_fh
    try:
        import msvcrt
        _lock_fh = LOCK_PATH.open("a+b")
        _lock_fh.seek(0)
        msvcrt.locking(_lock_fh.fileno(), msvcrt.LK_NBLCK, 1)
        return True
    except OSError:
        return False
    except ImportError:
        return True


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
    """Trích xuất link trực tiếp dẫn tới đúng bài viết Facebook từ các link trong email."""
    def decoded(u):
        return html_unescape(urllib.parse.unquote(urllib.parse.unquote(u)))

    def html_unescape(s):
        return s.replace("&amp;", "&")

    # 1) Ưu tiên rút trích link sạch thẳng tới bài viết (không lo hết hạn token email)
    for u in links:
        d = decoded(u)
        if "facebook.com" not in d:
            continue
        m = re.search(r"groups/([^/?&#]+)/(?:posts|permalink)/(\d+)", d)
        if m:
            return f"https://www.facebook.com/groups/{m.group(1)}/posts/{m.group(2)}/"
        m = re.search(r"groups/([^/?&#]+)/?[?&][^#]*multi_permalinks=(\d+)", d)
        if m:
            return f"https://www.facebook.com/groups/{m.group(1)}/posts/{m.group(2)}/"
        m = re.search(r"share/p/([A-Za-z0-9]+)", d)
        if m:
            return f"https://www.facebook.com/share/p/{m.group(1)}/"
        if "story_fbid=" in d:
            sfb = re.search(r"story_fbid=([^&#\s\"']+)", d)
            uid = re.search(r"[?&]id=([^&#\s\"']+)", d)
            if sfb and uid:
                return f"https://www.facebook.com/permalink.php?story_fbid={sfb.group(1)}&id={uid.group(1)}"

    # 2) Fallback: link group nhưng bỏ qua link trang cá nhân / cài đặt thông báo
    bad_parts = ("/user/", "actor_profile", "profile_link", "notification_settings", "unsubscribe")
    for u in links:
        d = decoded(u)
        if "facebook.com" in d and "groups" in d and not any(b in d for b in bad_parts):
            return html_unescape(u)
    return None


# ------------------------------------------------------------------- bộ lọc
def tach_ten_nhom(subject):
    """Tách tên nhóm khỏi tiêu đề ('A đã đăng trong NHÓM X', 'Bây giờ trong NHÓM X')."""
    s_low = subject.lower()
    for sep in (
        " đã đăng trong ", " đã chia sẻ một bài viết trong ", " vừa đăng trong ",
        "bây giờ trong ", "mới trong ", "nổi bật trong ", "hoạt động mới trong ",
        " posted in ", " shared a post in ",
    ):
        idx = s_low.find(sep)
        if idx != -1:
            return subject[idx + len(sep):].strip().rstrip(".:")
    m = re.match(r"^\[([^\]]+)\]", subject.strip())
    return m.group(1).strip() if m else ""


_NHU_CAU_RE = re.compile(
    r"(?<![a-z0-9])(?:"
    r"(?:tim|can|muon tim|kiem|kim|tuyen|hoi)\b[^.!?\n]{0,32}?\b(?:gia su|gs|gsu|giao vien|gv|thay|co|"
    r"nguoi day|nguoi kem|ban day|ban kem|sv day|sv kem|sinh vien day|sinh vien kem|anh chi day|anh chi kem|ac day|ac kem)"
    r"|(?:co ai|ai nhan|anh chi nao|ban nao|thay co nao|ai day|ai kem)\b[^.!?\n]{0,24}?\b(?:day|kem|gia su|gs|mon|toan|ly|li|vat ly|vat li|hoa)"
    r"|(?:can kem|can hoc kem|muon hoc kem|pass lop|nhuong lop)"
    r")(?![a-z0-9])"
)

# Nhận diện bài của GIA SƯ / SINH VIÊN / TRUNG TÂM tự đăng tìm lớp, tìm học sinh, chào phụ huynh kèm CV
_GIA_SU_TU_PR_RE = re.compile(
    r"(?<![a-z0-9])(?:"
    r"(?:tim|can tim|muon tim|kiem|kim|xin|nhan)\s+(?:them\s+)?(?:lop\s+(?:gia su|gs|day|kem)|hoc sinh|hoc vien)"
    r"|(?:kinh chao|chao|kinh gui|gui)\s+(?:cac bac\s+|quy\s+)?phu huynh"
    r"|(?:phu huynh|ba me|bo me)\s+(?:nao\s+)?(?:co nhu cau|quan tam)"
    r"|(?:em|minh|con|anh|chi|toi)\s+(?:hien\s+)?(?:dang\s+)?la\s+(?:sinh vien|sv|giao vien|gv|cu nhan|thac si|gia su)"
    r"|con/em\s+(?:dang|xin|nhan|cam on|se)"
    r"|(?:theo|dinh kem)\s+cv\b|cv\s+(?:duoi day|ben duoi|cua em|cua minh)"
    r"|doi tuong nhan day"
    r"|nhan\s+(?:day|kem|on|gia su|gs|lop|boi duong|lay lai goc)"
    r"|goc\s+tim\s+(?:lop|hoc sinh|hoc vien)"
    r"|(?:mo\s+lop|gom\s+nhom|chieu\s+sinh|tuyen\s+sinh|tuyen\s+(?:them\s+)?(?:hoc sinh|hoc vien))"
    r")(?![a-z0-9])"
)

# Nhận diện bài ghi rõ địa chỉ nhà / đường / ngõ / phường / quận (tức dạy trực tiếp offline)
_DIA_CHI_ACCENT_RE = re.compile(
    r"(?<![a-zà-ỹ0-9])(?:"
    r"địa\s*chỉ|đ/c|đc\s*:|dc\s*:|khu\s*vực\s*:|kv\s*:|nơi\s*học\s*:|nơi\s*dạy\s*:|địa\s*điểm\s*:"
    r"|số\s*nhà|nhà\s+ở|ngõ\s+\w+|ngách\s+\w+|hẻm\s+\w+|kiệt\s+\w+|ấp\s+\w+|thôn\s+\w+|xóm\s+\w+"
    r"|(?<!quãng\s)(?<!con\s)(?<!tương\s)đường\s+(?!(?:tròn|thẳng|cao|phân\s+giác|trung\s+tuyến|trung\s+trực|tiệm\s+cận|sức|cong|chéo|kính|sinh|chuẩn|biểu\s+diễn|lối|dài|đi|truyền|dẫn|dây)\b)[a-zà-ỹ0-9]"
    r"|chung\s*cư|khu\s*đô\s*thị|kđt\b|kdc\b|tòa\s+nhà|bến\s*xe"
    r"|phường\s+[a-zà-ỹ0-9]|quận\s+[a-zà-ỹ0-9]|huyện\s+[a-zà-ỹ0-9]|tp\.?\s*thủ\s*đức"
    r"|(?:bạn|anh|chị|thầy|cô|ai)\s+nào\s+đi\s+được|cần\s+[^\n.!?]{0,20}\bđến\s+(?:nhà|ôn|dạy|kèm)"
    r"|(?:\b\d{1,4}[a-z]?(?:/\d{1,4})?\s+(?:lạc\s+long\s+quân|xuân\s+thủy|cầu\s+giấy|nguyễn\s+trãi|giải\s+phóng|minh\s+khai|chùa\s+láng|láng\s+hạ|đê\s+la\s+thành|tây\s+sơn|trường\s+chinh|phạm\s+văn\s+đồng|hoàng\s+quốc\s+việt|nguyễn\s+chí\s+thanh|kim\s+mã|liễu\s+giai|đội\s+cấn|thụy\s+khuê|âu\s+cơ|nguyễn\s+văn\s+cừ|vườn\s+lài))"
    r")",
    re.IGNORECASE,
)

# Chỉ áp dụng sau TÊN MÔN (không có chữ "lớp"): tránh nhầm "Toán 2 buổi", "Lý 100k", "Toán 1 tuần 3 buổi" thành số lớp
_AFTER_MON_BAD_RE = re.compile(
    r"^\s*(?:buoi|tieng|gio|phut|k\b|nghin|ngan|tr\b|trieu|d\b|dong|thang|nam\s+kinh\s+nghiem|"
    r"ban\b|hoc\s+sinh|hs\b|:|-)"
)

_LOP_CHU_MAP = {
    "lop mot": 1, "lop hai": 2, "lop ba": 3, "lop bon": 4, "lop tu": 4,
    "lop nam": 5, "lop sau": 6, "lop bay": 7, "lop tam": 8, "lop chin": 9,
    "lop muoi mot": 11, "lop muoi hai": 12, "lop muoi": 10,
}

_NAM_SINH_MAP = {
    "2k8": 12, "2008": 12,
    "2k9": 12, "2009": 12,
    "2k10": 11, "2010": 11,
    "2k11": 10, "2011": 10,
    "2k12": 9, "2k13": 8, "2k14": 7, "2k15": 6, "2k16": 5, "2k17": 4, "2k18": 3,
}


def danh_gia_bai(text, cfg, subject="", age_hours=None, age_text=""):
    """Trả về (đạt?, lý do).

    Thứ tự:
      0. Quá giới hạn thời gian đăng (mặc định > 2 ngày / 54 giờ)             -> BỎ
      1. Có địa chỉ trực tiếp / từ loại trừ (offline, ở nhà, 1:1, cấp 1/2...) -> BỎ
      2. Bài gia sư / sinh viên / trung tâm tự đăng tìm lớp                   -> BỎ
      3. Không có nhu cầu tìm người dạy / gia sư                              -> BỎ
      4. Không có môn Toán / Lý / Hóa                                         -> BỎ
      5. Có ghi lớp nhưng ngoài 10, 11, 12                                    -> BỎ
         Không ghi lớp (chỉ ghi tìm gia sư Toán/Lý/Hóa)                       -> ĐẠT
    """
    f = cfg["bo_loc"]
    max_hours = float(f.get("gio_toi_da", 54))
    if age_hours is not None:
        try:
            ah = float(age_hours)
            if ah > max_hours:
                return False, f"quá 2 ngày ({age_text or f'{int(ah // 24)} ngày'})"
        except (TypeError, ValueError):
            pass

    lines_raw = (text or "").splitlines()
    if subject:
        tn = bo_dau(tach_ten_nhom(subject)).strip()
        if tn:
            lines_raw = [ln for ln in lines_raw if bo_dau(ln).strip() != tn]
    raw_clean = "\n".join(lines_raw)
    norm = bo_dau(raw_clean)

    m_dc = _DIA_CHI_ACCENT_RE.search(raw_clean)
    if m_dc:
        return False, f"ghi địa chỉ trực tiếp ({m_dc.group(0).strip()})"

    loai = co_tu_khoa(norm, f.get("tu_loai_tru", []))
    if loai:
        return False, f"có từ loại trừ: {', '.join(loai)}"

    m_pr = _GIA_SU_TU_PR_RE.search(norm)
    if m_pr:
        return False, f"bài gia sư tự đăng tìm lớp ({m_pr.group(0)})"

    nhu_cau = co_tu_khoa(norm, f.get("tu_nhu_cau", []))
    if not nhu_cau and not _NHU_CAU_RE.search(norm):
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
        goc = bo_dau(m)
        if goc in ("dai so", "hinh hoc", "giai tich", "toan"):
            ten_mon.setdefault("toan", "Toán")
        elif goc in ("ly", "li", "vat ly", "vat li"):
            ten_mon.setdefault("ly", "Lý")
        elif goc in ("hoa", "hoa hoc"):
            ten_mon.setdefault("hoa", "Hóa")
        elif goc in ("khoi a", "khoi a00"):
            for k, v in (("toan", "Toán"), ("ly", "Lý"), ("hoa", "Hóa")):
                ten_mon.setdefault(k, v)
        elif goc == "khoi a01":
            for k, v in (("toan", "Toán"), ("ly", "Lý")):
                ten_mon.setdefault(k, v)
        else:
            ten_mon.setdefault(goc, m.capitalize())
    ly_do = [f"Môn: {', '.join(ten_mon.values())}"]

    lop_cho_phep = {int(x) for x in f.get("lop", [])}
    if lop_cho_phep:
        lop_thay = set()

        # 1) Ghi rõ tiền tố lớp ("lớp 5 Tuần 3", "khối 8", "k12", "lớp 6, 7") -> LUÔN LÀ SỐ LỚP
        for m_gl in re.finditer(r"(?<![a-z0-9])(?:lop|khoi|k|l)\s*(\d{1,2})(?![0-9a-z:])(?:\s*[-/,&]\s*(\d{1,2})(?![0-9a-z:]))?", norm_mon):
            for grp in (m_gl.group(1), m_gl.group(2)):
                if grp and 1 <= int(grp) <= 12:
                    lop_thay.add(int(grp))

        # 2) Ghi số ngay sau tên môn ("Toán 12", "Lý 8 tuần 2 buổi", "Hóa 10, 11")
        mon_tt = "|".join(re.escape(bo_dau(t)) for t in f.get("mon_hoc", []))
        for m_ml in re.finditer(r"(?<![a-z0-9])(?:" + mon_tt + r")\s*(\d{1,2})(?![0-9a-z:])", norm_mon):
            n_val = int(m_ml.group(1))
            duoi = norm_mon[m_ml.end():]
            if not (1 <= n_val <= 12):
                continue
            if _AFTER_MON_BAD_RE.match(duoi):
                continue
            if n_val == 1 and re.match(r"^\s*tuan\b", duoi):
                continue  # "Toán 1 tuần 3 buổi" -> 1 tuần, không phải lớp 1
            lop_thay.add(n_val)

        # 3) Ghi lớp bằng chữ ("lớp năm", "lớp tám"...) hoặc tuổi ("bé 10 tuổi" -> cấp 1/2)
        for cum_chu, lop_so in _LOP_CHU_MAP.items():
            if re.search(r"(?<![a-z0-9])" + re.escape(cum_chu) + r"(?![a-z0-9])", norm_mon):
                lop_thay.add(lop_so)
        for m_tuoi in re.finditer(r"(?<![0-9])(\d{1,2})\s*tuoi(?![a-z0-9])", norm_mon):
            tuoi = int(m_tuoi.group(1))
            if 6 <= tuoi <= 14:
                lop_thay.add(max(1, tuoi - 5))
            elif 15 <= tuoi <= 18:
                lop_thay.add(min(12, tuoi - 5))

        for ns, lop_qd in _NAM_SINH_MAP.items():
            if re.search(r"(?<![a-z0-9])" + re.escape(ns) + r"(?![a-z0-9])", norm_mon):
                lop_thay.add(lop_qd)
        if lop_thay:
            hop_le = sorted(lop_thay & lop_cho_phep)
            if not hop_le:
                return False, f"lớp {', '.join(map(str, sorted(lop_thay)))} không nằm trong danh sách"
            ly_do.append(f"Lớp: {', '.join(map(str, hop_le))}")
        else:
            ly_do.append("Không ghi lớp")

    return True, " | ".join(ly_do)


# --------------------------------------------------------------- AI soạn bình luận
def chon_mau_theo_mon(ly_do, cfg):
    theo_mon = cfg.get("mau_theo_mon", {})
    if "Toán" in (ly_do or "") and theo_mon.get("toan"):
        return theo_mon["toan"].strip()
    if "Lý" in (ly_do or "") and theo_mon.get("ly"):
        return theo_mon["ly"].strip()
    if "Hóa" in (ly_do or "") and theo_mon.get("hoa"):
        return theo_mon["hoa"].strip()
    return cfg.get("mau_binh_luan_mac_dinh", "").strip()


def soan_binh_luan(text, cfg, ly_do=""):
    mac_dinh = chon_mau_theo_mon(ly_do, cfg)
    ai = cfg.get("ai", {})
    key = ai.get("gemini_api_key", "").strip()
    if not ai.get("bat", False) or not key or key.startswith("DIEN_"):
        return mac_dinh or None
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


# --------------------------------------------------- Nhận từ Chuông FB (Extension)
_TIME_RE = re.compile(
    r"^(\d+\s*(giây|phút|giờ|ngày|tuần|tháng|năm|seconds?|minutes?|hours?|days?|weeks?|m|h|d|w)\b.*"
    r"|vừa xong|bây giờ|hôm qua|just now|yesterday)(\s*trước|\s*ago)?$",
    re.IGNORECASE,
)


def tach_thong_bao_fb(raw_text):
    """Tách chuỗi thông báo trên chuông Facebook thành (tiêu_đề_nhóm, nội_dung_bài)."""
    cleaned = re.sub(r"^\s*(?:Chưa đọc|Unread)\s*", "", raw_text or "", flags=re.IGNORECASE)
    lines = []
    for ln in cleaned.splitlines():
        s = re.sub(r"^\s*(?:Chưa đọc|Unread)\s*", "", ln.strip(), flags=re.IGNORECASE).strip()
        if not s:
            continue
        if bo_dau(s) in ("chua doc", "unread", "thong bao moi", "new notification"):
            continue
        if _TIME_RE.match(s):
            continue
        lines.append(s)
    joined = "\n".join(lines).strip()
    m = re.match(
        r"^((?:Bây giờ|Mới|Nổi bật|Hoạt động mới)\s+trong\s+[^:\n]+"
        r"|[^\n:]{1,90}?\s+(?:đã đăng|đã chia sẻ[^:\n]*|vừa đăng|posted|shared[^:\n]*)\s+trong\s+[^:\n]+)\s*:\s*(.+)$",
        joined,
        re.IGNORECASE | re.DOTALL,
    )
    if m:
        return m.group(1).strip(), m.group(2).strip()
    if len(lines) >= 2 and " trong " in lines[0].lower():
        return lines[0], "\n".join(lines[1:]).strip()
    return "Thông báo nhóm Facebook", joined


def xu_ly_thong_bao_extension(items, cfg, dry_run=False):
    moi, dat = 0, 0
    matched_items = []
    with _seen_lock:
        seen = load_json(SEEN_PATH, {"ids": []})
        seen_ids = set(seen["ids"])

        for it in items:
            href = (it.get("href") or "").strip()
            raw_text = (it.get("text") or "").strip()
            clean_link = chon_link_bai([href]) or href
            is_permalink = any(x in clean_link for x in ("/posts/", "/permalink/", "story_fbid=", "/share/p/"))

            if it.get("body"):
                gname = (it.get("groupName") or "Nhóm Facebook").strip()
                author = (it.get("author") or "").strip()
                subject = f"{gname} · {author}" if author and author.lower() != gname.lower() else gname
                body = it["body"].strip()
            else:
                subject, body = tach_thong_bao_fb(raw_text)

            age_hours = it.get("ageHours")
            age_text = (it.get("ageText") or "").strip()

            uid = "fb:" + (clean_link if is_permalink else (it.get("key") or f"{subject}|{body[:120]}"))
            if uid in seen_ids:
                continue
            moi += 1
            ok, ly_do = danh_gia_bai(body, cfg, subject=subject, age_hours=age_hours, age_text=age_text)
            if ok and age_text:
                ly_do = f"{ly_do} | ⏱ {age_text}"
            cmt = (soan_binh_luan(body, cfg, ly_do) or "") if ok else ""

            _recent_events.append({
                "time": datetime.now().strftime("%H:%M:%S"),
                "ok": ok,
                "group": subject[:60],
                "snippet": " ".join(body.split())[:90],
                "reason": ly_do,
                "link": clean_link,
            })
            del _recent_events[:-20]

            if ok:
                dat += 1
                log(f"🔔 [FB] ĐẠT: {subject[:55]} -> {body[:70]} ({ly_do})")
                post = {
                    "subject": subject,
                    "text": body[:3000],
                    "link": clean_link,
                    "reason": ly_do,
                    "comment": cmt,
                }
                if not gui_thong_bao(post, cfg, dry_run):
                    continue
                matched_items.append({
                    "key": it.get("key") or "",
                    "reason": ly_do,
                    "comment": cmt,
                    "link": clean_link,
                })
            else:
                log(f"   [FB] bỏ qua: {subject[:45]} | {body[:55]} ({ly_do})")
            seen_ids.add(uid)

        if moi and not dry_run:
            seen["ids"] = list(seen_ids)[-5000:]
            save_json(SEEN_PATH, seen)
    return {"new": moi, "matched": dat, "matchedItems": matched_items}


def khoi_dong_cong_extension(cfg, dry_run=False):
    port = int(cfg.get("cong_extension", 8765))

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            return

        def _json(self, code, obj):
            data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path.startswith("/health"):
                return self._json(200, {"ok": True})
            if self.path.startswith("/recent"):
                fresh_cfg = load_json(CONFIG_PATH, cfg)
                return self._json(200, {
                    "ok": True,
                    "events": list(reversed(_recent_events)),
                    "templates": fresh_cfg.get("mau_theo_mon", {}),
                })
            self._json(404, {"ok": False})

        def do_POST(self):
            if not self.path.startswith("/ingest"):
                return self._json(404, {"ok": False})
            try:
                n = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(n).decode("utf-8"))
                fresh_cfg = load_json(CONFIG_PATH, cfg)
                res = xu_ly_thong_bao_extension(payload.get("items", []), fresh_cfg, dry_run)
                self._json(200, {"ok": True, **res})
            except Exception as e:
                log(f"Lỗi nhận từ Extension: {e}")
                self._json(500, {"ok": False, "error": str(e)})

    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    log(f"🌐 Cổng nhận thông báo Chuông FB đã mở tại http://127.0.0.1:{port}/ingest")


# ------------------------------------------------------------------ Gmail (IMAP)
def kiem_tra_gmail(cfg, dry_run=False):
    g = cfg["gmail"]
    with _seen_lock:
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
        ok, ly_do = danh_gia_bai(text or subject, cfg, subject=subject)
        if ok:
            dat += 1
            log(f"✅ ĐẠT: {subject[:70]} ({ly_do})")
            post = {
                "subject": subject, "text": text[:3000], "link": chon_link_bai(links) or "",
                "reason": ly_do, "comment": soan_binh_luan(text, cfg, ly_do) or "",
            }
            if not gui_thong_bao(post, cfg, dry_run):
                continue  # chưa gửi được thì lần sau thử lại
        else:
            log(f"   bỏ qua: {subject[:70]} ({ly_do})")
        seen_ids.add(mid)

    imap.logout()
    if not dry_run:
        with _seen_lock:
            cur = set(load_json(SEEN_PATH, {"ids": []})["ids"])
            seen["ids"] = list(cur | seen_ids)[-5000:]
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
            "subject": "🧪 [BÀI MẪU THỬ KẾT NỐI — không phải bài thật trên FB]",
            "text": "em cần tìm gia sư lý 12, cả học và cả ôn thi ạ, học online ạ",
            "link": "", "reason": "Môn: Lý | Lớp: 12",
            "comment": cfg.get("mau_binh_luan_mac_dinh") or "Chào em, anh nhận kèm Lý 12 online... (bình luận mẫu)",
        }, cfg)
        print("Gửi thành công!" if ok else "Gửi thất bại — xem lỗi ở trên.")
        return

    if args.test_text:
        ok, ly_do = danh_gia_bai(args.test_text, cfg)
        print(f"{'ĐẠT     ' if ok else 'BỎ QUA  '} | {ly_do} | {args.test_text}")
        if ok and cfg.get("ai", {}).get("bat"):
            print("Bình luận gợi ý:\n" + (soan_binh_luan(args.test_text, cfg) or "(AI lỗi)"))
        return

    if not args.once and not giu_khoa_duy_nhat():
        log("Radar đã có 1 tiến trình khác đang chạy ngầm, tự thoát để tránh trùng.")
        return

    if not args.once:
        khoi_dong_cong_extension(cfg, args.dry_run)

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

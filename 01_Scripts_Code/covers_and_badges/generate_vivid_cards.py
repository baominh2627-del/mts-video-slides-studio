import os, sys
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8')
CARDS_DIR = r"c:\Users\DELL\Documents\CODE\DU_AN\vivid_cards"
os.makedirs(CARDS_DIR, exist_ok=True)

# Common fonts
FONT_BOLD = r'C:\Windows\Fonts\arialbd.ttf'
FONT_REG = r'C:\Windows\Fonts\arial.ttf'
FONT_SEGOE = r'C:\Windows\Fonts\segoeuib.ttf'
FONT_EMOJI = r'C:\Windows\Fonts\seguiemj.ttf'

font_pill = ImageFont.truetype(FONT_BOLD, 26)
font_card_tag = ImageFont.truetype(FONT_BOLD, 24)
font_card_main = ImageFont.truetype(FONT_SEGOE, 32)
font_card_sub = ImageFont.truetype(FONT_BOLD, 22)

# 1. Helper to create a Top-Right Phase Pill (380 x 68)
def create_top_pill(text, icon="📌", border_color=(56, 189, 248)):
    w, h = 420, 68
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # Dark rounded pill
    d.rounded_rectangle([2, 2, w-2, h-2], radius=20, fill=(15, 23, 42, 235), outline=border_color, width=2)
    # Text
    bbox = font_pill.getbbox(text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (w - tw) // 2
    ty = (h - th) // 2 - 2
    d.text((tx, ty), text, fill=(255, 255, 255), font=font_pill)
    return im

# 2. Helper to create Lower-Third Insight Card (980 x 190)
def create_insight_card(tag, main_text, sub_text="", border_color=(56, 189, 248), bg_color=(15, 23, 42, 240), tag_color=(56, 189, 248), main_color=(255, 255, 255)):
    w, h = 980, 190
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # Card background with border
    d.rounded_rectangle([3, 3, w-3, h-3], radius=22, fill=bg_color, outline=border_color, width=3)
    
    # Tag bar / title
    d.text((36, 18), tag, fill=tag_color, font=font_card_tag)
    
    # Main formula / text
    d.text((36, 62), main_text, fill=main_color, font=font_card_main)
    
    # Sub explanation text
    if sub_text:
        d.text((36, 128), sub_text, fill=(203, 213, 225), font=font_card_sub)
    
    return im

# Generate all 10 phase assets
phases = [
    {
        "id": "phase1",
        "start": 0.0, "end": 15.0,
        "pill": "📖 ĐỀ BÀI TRỌNG TÂM",
        "pill_border": (56, 189, 248),
        "tag": "🌡️ HIỆN TƯỢNG: NHIỆT ĐỘ TĂNG BẬC NHẤT THEO ĐỘ CAO",
        "main": "Đáy 4°C (lớp lạnh ❄️)  →  Mặt trên 13°C (lớp nóng 🔥)",
        "sub": "Thành & nắp cách nhiệt hoàn toàn · Sau cân bằng, tìm t₀ = ?",
        "card_border": (56, 189, 248),
        "tag_color": (56, 189, 248),
        "main_color": (253, 230, 138)
    },
    {
        "id": "phase2",
        "start": 15.0, "end": 32.0,
        "pill": "🔍 PHÂN TÍCH HIỆN TƯỢNG",
        "pill_border": (251, 191, 36),
        "tag": "🛡️ NGUYÊN LÝ: BẢO TOÀN NHIỆT LƯỢNG TRONG HỆ CÔ LẬP",
        "main": "Lớp lạnh (dưới) Thu nhiệt  +  Lớp nóng (trên) Tỏa nhiệt  =  0",
        "sub": "💡 Phương pháp: Chia nước thành các lớp lát mỏng dh rồi tích phân!",
        "card_border": (251, 191, 36),
        "tag_color": (251, 191, 36),
        "main_color": (255, 255, 255)
    },
    {
        "id": "phase3",
        "start": 32.0, "end": 54.0,
        "pill": "1️⃣ NHIỆT ĐỘ THEO ĐỘ CAO",
        "pill_border": (56, 189, 248),
        "tag": "📌 BƯỚC 1: HÀM NHIỆT ĐỘ BẬC NHẤT t(h) = a·h + b",
        "main": "t(h)  =  4  +  9 · (h / H)",
        "sub": "✓ Tại đáy (h = 0): t = 4°C    |    ✓ Tại mặt trên (h = H): t = 13°C",
        "card_border": (56, 189, 248),
        "tag_color": (56, 189, 248),
        "main_color": (251, 191, 36)
    },
    {
        "id": "phase4",
        "start": 54.0, "end": 80.0,
        "pill": "2️⃣ KHỐI LƯỢNG LỚP NƯỚC dm",
        "pill_border": (56, 189, 248),
        "tag": "📐 BƯỚC 2: TAM GIÁC ĐỒNG DẠNG (BỀ RỘNG x / L = h / H)",
        "main": "dm  =  ρ · dV  =  k · h · dh       (với k = ρLℓ/H = hằng số)",
        "sub": "Khối lượng lớp nước tỷ lệ thuận với độ cao h từ đỉnh đáy!",
        "card_border": (56, 189, 248),
        "tag_color": (56, 189, 248),
        "main_color": (255, 255, 255)
    },
    {
        "id": "phase5",
        "start": 80.0, "end": 110.0,
        "pill": "3️⃣ PHƯƠNG TRÌNH CÂN BẰNG",
        "pill_border": (245, 158, 11),
        "tag": "⚡ BƯỚC 3: PHƯƠNG TRÌNH CÂN BẰNG NHIỆT TOÀN BÌNH",
        "main": "t₀  =  ∫ t dm  /  ∫ dm   =   Tử số N  /  Mẫu số M",
        "sub": "Bản chất: t₀ chính là nhiệt độ trung bình theo khối lượng!",
        "card_border": (245, 158, 11),
        "tag_color": (245, 158, 11),
        "main_color": (253, 230, 138)
    },
    {
        "id": "phase7",
        "start": 110.0, "end": 130.0,
        "pill": "4️⃣ TÍNH MẪU SỐ (TỔNG M)",
        "pill_border": (56, 189, 248),
        "tag": "⚖️ BƯỚC 4: TỔNG KHỐI LƯỢNG NƯỚC TRONG BÌNH M",
        "main": "M  =  ∫₀ᴴ k h dh  =  ½ · k · H²",
        "sub": "✓ Kiểm tra hình học: M = ρ · (½ L H) · ℓ = ½ k H² (hoàn toàn khớp!)",
        "card_border": (56, 189, 248),
        "tag_color": (56, 189, 248),
        "main_color": (255, 255, 255)
    },
    {
        "id": "phase8",
        "start": 130.0, "end": 152.0,
        "pill": "5️⃣ TÍNH TỬ SỐ (TỔNG N)",
        "pill_border": (56, 189, 248),
        "tag": "🔢 BƯỚC 5: TỔNG NĂNG LƯỢNG NHIỆT TỬ SỐ N = ∫ t dm",
        "main": "N  =  k · ∫ (4h + 9h²/H) dh  =  k · (2H² + 3H²)  =  5 k H²",
        "sub": "Tách 2 tích phân cơ bản: ∫ 4h dh = 2H²  và  ∫ 9h²/H dh = 3H²",
        "card_border": (56, 189, 248),
        "tag_color": (56, 189, 248),
        "main_color": (251, 191, 36)
    },
    {
        "id": "phase9",
        "start": 152.0, "end": 166.0,
        "pill": "🎯 KẾT QUẢ t₀ = 10°C",
        "pill_border": (251, 191, 36),
        "tag": "🎉 BƯỚC 6: RÚT GỌN TÌM NHIỆT ĐỘ CÂN BẰNG t₀",
        "main": "t₀  =  N / M  =  5 k H²  /  (½ k H²)   =   10°C",
        "sub": "⭐ Hằng số k & chiều cao H triệt tiêu ⇒ Không phụ thuộc kích thước bình!",
        "card_border": (251, 191, 36),
        "tag_color": (251, 191, 36),
        "main_color": (251, 191, 36)
    },
    {
        "id": "phase10",
        "start": 166.0, "end": 184.0,
        "pill": "⚡ BÍ KÍP GIẢI NHANH 10S",
        "pill_border": (245, 158, 11),
        "tag": "💡 MẸO ĐỈNH CAO: NHIỆT ĐỘ TẠI TRỌNG TÂM TAM GIÁC G",
        "main": "h_G = ⅔ H   ⇒   t₀ = t(h_G) = 4 + 9 · (⅔)   =   10°C",
        "sub": "⚡ Không cần đặt bút tích phân! Áp dụng cho mọi bình có t(h) bậc nhất!",
        "card_border": (245, 158, 11),
        "tag_color": (245, 158, 11),
        "main_color": (253, 230, 138)
    },
    {
        "id": "phase11",
        "start": 184.0, "end": 190.0,
        "pill": "✨ TỔNG KẾT & FOLLOW",
        "pill_border": (56, 189, 248),
        "tag": "🏆 ĐÁP SỐ CHUẨN XÁC: t₀ = 10°C",
        "main": "Lưu lại & Follow MTSEducation để xem thêm bài hay!",
        "sub": "🔔 Cùng học Vật lí trực quan, dễ hiểu và đạt điểm cao mỗi ngày!",
        "card_border": (56, 189, 248),
        "tag_color": (56, 189, 248),
        "main_color": (255, 255, 255)
    }
]

for p in phases:
    # Pill
    pill_img = create_top_pill(p['pill'], border_color=p['pill_border'])
    pill_path = os.path.join(CARDS_DIR, f"{p['id']}_pill.png")
    pill_img.save(pill_path)
    
    # Card
    card_img = create_insight_card(p['tag'], p['main'], p['sub'], border_color=p['card_border'], tag_color=p['tag_color'], main_color=p['main_color'])
    card_path = os.path.join(CARDS_DIR, f"{p['id']}_card.png")
    card_img.save(card_path)

print(f"Generated {len(phases)} visual pill & card assets!")

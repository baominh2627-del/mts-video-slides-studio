import os, sys, math
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8')
CARDS_DIR = r"c:\Users\DELL\Documents\CODE\DU_AN\vivid_cards_v2"
os.makedirs(CARDS_DIR, exist_ok=True)

FONT_SEGOE_BOLD = r'C:\Windows\Fonts\segoeuib.ttf'

font_badge = ImageFont.truetype(FONT_SEGOE_BOLD, 22)
font_title = ImageFont.truetype(FONT_SEGOE_BOLD, 24)
font_formula = ImageFont.truetype(FONT_SEGOE_BOLD, 33)
font_sub = ImageFont.truetype(FONT_SEGOE_BOLD, 22)

def draw_vector_icon(d, icon_type, cx, cy, color):
    if icon_type == 'play':
        d.polygon([(cx - 7, cy - 8), (cx + 8, cy), (cx - 7, cy + 8)], fill=color)
    elif icon_type == 'star':
        pts = []
        for i in range(10):
            r = 11 if i % 2 == 0 else 5
            angle = i * math.pi / 5 - math.pi / 2
            pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
        d.polygon(pts, fill=color)
    elif icon_type == 'bolt':
        bolt = [(cx + 2, cy - 10), (cx - 6, cy + 1), (cx, cy + 1), (cx - 3, cy + 11), (cx + 6, cy - 1), (cx, cy - 1)]
        d.polygon(bolt, fill=color)
    elif icon_type == 'target':
        d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], outline=color, width=2)
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=color)
    elif icon_type == 'check':
        d.line([(cx - 8, cy), (cx - 2, cy + 7), (cx + 8, cy - 7)], fill=color, width=3)

def make_card(badge_text, title_text, formula_text, sub_text, icon='play', theme_color=(56, 189, 248), glow=False):
    w, h = 1000, 210
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    
    # Outer container with rounded corners and rich dark translucent slate
    bg_color = (12, 19, 36, 245)
    border_w = 4 if glow else 3
    d.rounded_rectangle([2, 2, w-2, h-2], radius=24, fill=bg_color, outline=theme_color, width=border_w)
    
    if glow:
        d.rounded_rectangle([6, 6, w-6, h-6], radius=20, outline=(*theme_color[:3], 140), width=2)
    
    # Inner subtle glow line at top inside
    d.line([(28, 6), (w-28, 6)], fill=(*theme_color[:3], 150), width=1)
    
    # Badge Pill (Left)
    b_bbox = font_badge.getbbox(badge_text)
    bw = b_bbox[2] - b_bbox[0] + 56
    bh = 38
    bx, by = 28, 18
    d.rounded_rectangle([bx, by, bx+bw, by+bh], radius=12, fill=theme_color)
    
    # Icon inside badge pill
    icon_color = (10, 15, 30)
    draw_vector_icon(d, icon, bx + 22, by + bh // 2, icon_color)
    
    # Text inside badge pill
    d.text((bx + 38, by + 4), badge_text, font=font_badge, fill=icon_color)
    
    # Title (Next to Badge)
    tx = bx + bw + 18
    d.text((tx, by + 4), title_text, font=font_title, fill=theme_color)
    
    # Separator thin line
    d.line([(28, 68), (w-28, 68)], fill=(45, 60, 95, 220), width=1)
    
    # Main Formula (Centered or fitted)
    f_bbox = font_formula.getbbox(formula_text)
    fw = f_bbox[2] - f_bbox[0]
    fx = (w - fw) // 2 if fw < 940 else 30
    d.text((fx, 82), formula_text, font=font_formula, fill=(255, 255, 255))
    
    # Sub / Insight line
    s_bbox = font_sub.getbbox(sub_text)
    sw = s_bbox[2] - s_bbox[0]
    sx = (w - sw) // 2 if sw < 940 else 30
    d.text((sx, 152), sub_text, font=font_sub, fill=(203, 213, 225))
    
    return im

card_specs = [
    {
        "id": "card1", "start": 0.0, "end": 15.0,
        "badge": "ĐỀ BÀI TRỌNG TÂM", "icon": "star", "theme": (56, 189, 248),
        "title": "BÌNH LĂNG TRỤ TAM GIÁC ĐỨNG",
        "formula": "Đáy 4°C (lớp lạnh)   -->   Mặt trên 13°C (lớp nóng)",
        "sub": "Cách nhiệt hoàn toàn · Tìm nhiệt độ cân bằng t₀ khi ổn định",
        "glow": False
    },
    {
        "id": "card2", "start": 15.0, "end": 32.0,
        "badge": "PHÂN TÍCH HIỆN TƯỢNG", "icon": "star", "theme": (245, 158, 11),
        "title": "BẢO TOÀN NHIỆT LƯỢNG TRONG HỆ CÔ LẬP",
        "formula": "Nhiệt lượng Thu (lớp dưới) + Nhiệt lượng Tỏa (lớp trên) = 0",
        "sub": "Phương pháp: Chia nước thành các lát mỏng dh rồi tích phân toàn bình",
        "glow": False
    },
    {
        "id": "card3", "start": 32.0, "end": 54.0,
        "badge": "BƯỚC 1 / 6", "icon": "play", "theme": (56, 189, 248),
        "title": "HÀM NHIỆT ĐỘ THEO ĐỘ CAO t(h)",
        "formula": "t(h)  =  4  +  9 · (h / H)",
        "sub": "Tại đáy (h = 0): t = 4°C   |   Tại mặt trên (h = H): t = 13°C",
        "glow": False
    },
    {
        "id": "card4", "start": 54.0, "end": 80.0,
        "badge": "BƯỚC 2 / 6", "icon": "play", "theme": (16, 185, 129),
        "title": "KHỐI LƯỢNG LỚP NƯỚC MỎNG dm",
        "formula": "dm  =  ρ · dV  =  k · h · dh       (với k = ρ·L·ℓ / H = hằng số)",
        "sub": "Tam giác đồng dạng: Khối lượng lớp nước tỷ lệ thuận với độ cao h",
        "glow": False
    },
    {
        "id": "card5", "start": 80.0, "end": 110.0,
        "badge": "BƯỚC 3 / 6", "icon": "play", "theme": (168, 85, 247),
        "title": "PHƯƠNG TRÌNH CÂN BẰNG NHIỆT TOÀN BÌNH",
        "formula": "t₀  =  ∫ t dm  /  ∫ dm   =   Tử số N  /  Mẫu số M",
        "sub": "Bản chất: t₀ chính là nhiệt độ trung bình tính theo khối lượng nước",
        "glow": False
    },
    {
        "id": "card6", "start": 110.0, "end": 130.0,
        "badge": "BƯỚC 4 / 6", "icon": "play", "theme": (14, 165, 233),
        "title": "TÍNH MẪU SỐ M (TỔNG KHỐI LƯỢNG NƯỚC)",
        "formula": "M  =  ∫ k·h dh  (từ 0 đến H)   =   ½ · k · H²",
        "sub": "Hoàn toàn trùng khớp diện tích thiết diện tam giác: S = ½·L·H",
        "glow": False
    },
    {
        "id": "card7", "start": 130.0, "end": 152.0,
        "badge": "BƯỚC 5 / 6", "icon": "play", "theme": (245, 158, 11),
        "title": "TÍNH TỬ SỐ N = ∫ t dm",
        "formula": "N  =  k · ∫ (4h + 9h²/H) dh  =  k · (2H² + 3H²)  =  5 · k · H²",
        "sub": "Tách 2 tích phân cơ bản: ∫ 4h dh = 2H²  và  ∫ (9/H)h² dh = 3H²",
        "glow": False
    },
    {
        "id": "card8", "start": 152.0, "end": 166.0,
        "badge": "KẾT QUẢ CUỐI CÙNG", "icon": "target", "theme": (251, 191, 36),
        "title": "NHIỆT ĐỘ CÂN BẰNG CỦA NƯỚC TRONG BÌNH",
        "formula": "t₀  =  N / M  =  5·k·H²  /  (½·k·H²)   =   10°C",
        "sub": "Hằng số k và chiều cao H triệt tiêu  ==>  Không phụ thuộc kích thước bình!",
        "glow": True
    },
    {
        "id": "card9", "start": 166.0, "end": 184.0,
        "badge": "BÍ KÍP GIẢI NHANH 10S", "icon": "bolt", "theme": (244, 63, 94),
        "title": "MẸO TRỌNG TÂM TAM GIÁC ĐỈNH CAO",
        "formula": "h_G = ⅔ H   ==>   t₀ = t(h_G) = 4 + 9 · (⅔)   =   10°C",
        "sub": "Không cần tích phân! Áp dụng cho mọi bình có t(h) bậc nhất!",
        "glow": True
    },
    {
        "id": "card10", "start": 184.0, "end": 190.0,
        "badge": "MTSEducation", "icon": "star", "theme": (56, 189, 248),
        "title": "CHÚC BẠN HỌC TỐT & ĐẠT ĐIỂM CAO VẬT LÍ",
        "formula": "Đáp số chuẩn xác: t₀ = 10°C  |  Lưu lại & Ôn tập ngay!",
        "sub": "Follow MTSEducation để xem thêm nhiều bài giảng hay & mẹo giải nhanh!",
        "glow": False
    }
]

for spec in card_specs:
    im = make_card(
        spec['badge'], spec['title'], spec['formula'], spec['sub'],
        icon=spec['icon'], theme_color=spec['theme'], glow=spec['glow']
    )
    fpath = os.path.join(CARDS_DIR, f"{spec['id']}.png")
    im.save(fpath)
    print(f"Generated {spec['id']}.png")

print("All 10 insight cards regenerated cleanly!")

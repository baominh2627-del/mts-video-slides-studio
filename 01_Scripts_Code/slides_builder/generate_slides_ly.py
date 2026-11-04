# -*- coding: utf-8 -*-
"""
Script tạo trọn bộ ảnh slide thuyết trình phần của Ly:
2. Cấu trúc và nguyên lý hoạt động của hệ thống AS/RS
- Thiết kế: Nền trắng, chữ đen / than, tối giản, thanh lịch, chuẩn slide thuyết trình 16:9 (1920x1080)
- Lưu vào: C:\\Users\\DELL\\Documents\\Downloads
"""

import os
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = r"C:\Users\DELL\Documents\Downloads"
os.makedirs(OUTPUT_DIR, exist_ok=True)

WIDTH = 1920
HEIGHT = 1080

FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_REG = "C:/Windows/Fonts/segoeui.ttf"

# Bảng màu tối giản hiện đại (Minimalist Monochrome)
BG_COLOR = (255, 255, 255)         # Nền trắng thuần #FFFFFF
TEXT_MAIN = (15, 23, 42)           # Chữ đen than đậm #0F172A
TEXT_MUTED = (100, 116, 139)       # Chữ phụ / mô tả xám xanh #64748B
TEXT_BODY = (30, 41, 59)           # Chữ nội dung #1E293B
CARD_BG = (248, 250, 252)          # Nền thẻ xám rất nhẹ #F8FAFC
CARD_BORDER = (226, 232, 240)      # Viền thẻ #E2E8F0
BADGE_BG = (15, 23, 42)            # Nền huy hiệu đen
BADGE_FG = (255, 255, 255)         # Chữ huy hiệu trắng
ACCENT_LINE = (226, 232, 240)      # Đường kẻ ngăn cách

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

def wrap_text(draw, text, font, max_width):
    words = text.split()
    if not words:
        return []
    lines = []
    current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                lines.append(word)
                current_line = []
    if current_line:
        lines.append(" ".join(current_line))
    return lines

def create_base():
    img = Image.new("RGB", (WIDTH, HEIGHT), color=BG_COLOR)
    draw = ImageDraw.Draw(img)
    return img, draw

def draw_header(draw, badge_text, title_text, subtitle_text=""):
    # Badge
    f_badge = get_font(FONT_BOLD, 15)
    bbox_b = draw.textbbox((0, 0), badge_text, font=f_badge)
    bw = bbox_b[2] - bbox_b[0] + 28
    bh = bbox_b[3] - bbox_b[1] + 14
    draw.rounded_rectangle([90, 45, 90 + bw, 45 + bh], radius=6, fill=BADGE_BG)
    draw.text((90 + 14, 45 + 6), badge_text, font=f_badge, fill=BADGE_FG)

    # Title
    f_title = get_font(FONT_BOLD, 36)
    draw.text((90, 96), title_text, font=f_title, fill=TEXT_MAIN)

    # Subtitle
    if subtitle_text:
        f_sub = get_font(FONT_REG, 20)
        draw.text((90, 146), subtitle_text, font=f_sub, fill=TEXT_MUTED)

    # Horizontal divider rule
    draw.line([(90, 186), (WIDTH - 90, 186)], fill=ACCENT_LINE, width=2)

def draw_footer(draw, page_num, total_pages=8):
    y = 1010
    draw.line([(90, y), (WIDTH - 90, y)], fill=ACCENT_LINE, width=2)
    f_foot = get_font(FONT_REG, 16)
    f_foot_b = get_font(FONT_BOLD, 16)
    
    left_text = "HỆ THỐNG AS/RS • PHẦN 2: CẤU TRÚC VÀ NGUYÊN LÝ HOẠT ĐỘNG • NỘI DUNG CỦA LY"
    draw.text((90, y + 18), left_text, font=f_foot, fill=TEXT_MUTED)
    
    right_text = f"Slide {page_num:02d} / {total_pages:02d}"
    bbox_r = draw.textbbox((0, 0), right_text, font=f_foot_b)
    rw = bbox_r[2] - bbox_r[0]
    draw.text((WIDTH - 90 - rw, y + 18), right_text, font=f_foot_b, fill=TEXT_MAIN)

def draw_card(draw, box, fill=CARD_BG, outline=CARD_BORDER, radius=14, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

def draw_bullet_card(draw, x1, y, x2, b_title, b_desc, f_title, f_desc, max_text_width):
    paragraphs = b_desc.split("\n")
    all_lines = []
    for p in paragraphs:
        if p.strip():
            wrapped = wrap_text(draw, p.strip(), f_desc, max_text_width)
            all_lines.extend(wrapped)
    
    line_h = 24
    text_h = len(all_lines) * line_h
    card_h = max(86, 38 + text_h + 10)
    
    # Background card
    draw_card(draw, [x1, y, x2, y + card_h], fill=(255, 255, 255), outline=(228, 233, 240), radius=10, width=1)
    
    # Bullet title
    draw.text((x1 + 18, y + 10), "✔", font=f_title, fill=TEXT_MAIN)
    draw.text((x1 + 44, y + 10), b_title, font=f_title, fill=TEXT_MAIN)
    
    # Text lines
    ty = y + 36
    for line in all_lines:
        draw.text((x1 + 44, ty), line, font=f_desc, fill=TEXT_BODY)
        ty += line_h
        
    return card_h + 12

# ==============================================================================
# SLIDE 1: TRANG TIÊU ĐỀ
# ==============================================================================
def make_slide_1():
    img, draw = create_base()

    # Outer decorative frame
    draw.rounded_rectangle([60, 60, WIDTH - 60, HEIGHT - 60], radius=20, fill=None, outline=CARD_BORDER, width=2)

    # Top Tag
    f_badge = get_font(FONT_BOLD, 16)
    badge_text = "BÁO CÁO CHUYÊN ĐỀ • KHO THÔNG MINH (SMART WAREHOUSE)"
    bbox = draw.textbbox((0, 0), badge_text, font=f_badge)
    bw = bbox[2] - bbox[0] + 32
    bh = bbox[3] - bbox[1] + 16
    draw.rounded_rectangle([120, 130, 120 + bw, 130 + bh], radius=8, fill=BADGE_BG)
    draw.text((120 + 16, 130 + 7), badge_text, font=f_badge, fill=BADGE_FG)

    # Main Big Title
    f_title = get_font(FONT_BOLD, 52)
    draw.text((120, 220), "2. CẤU TRÚC VÀ NGUYÊN LÝ HOẠT ĐỘNG", font=f_title, fill=TEXT_MAIN)
    draw.text((120, 295), "CỦA HỆ THỐNG AS/RS", font=f_title, fill=TEXT_MAIN)

    # Subtitle
    f_sub = get_font(FONT_REG, 24)
    draw.text((120, 395), "Automated Storage and Retrieval System (Hệ thống lưu trữ và truy xuất tự động)", font=f_sub, fill=TEXT_MUTED)

    # Divider line
    draw.line([(120, 460), (WIDTH - 120, 460)], fill=ACCENT_LINE, width=2)

    # 3 Summary Pillar Cards
    card_w = (WIDTH - 240 - 60) // 3
    pillars = [
        ("2.1. CÁC THÀNH PHẦN CHÍNH", "5 CẤU PHẦN CỐT LÕI", [
            "• Giá đỡ (Racks)",
            "• Hệ thống Stacker (Cần trục)",
            "• Hệ thống truyền tải (Conveyor/AGV)",
            "• Hệ thống điều khiển (PLC)",
            "• Phần mềm quản lý kho (WMS)"
        ]),
        ("2.2. NGUYÊN LÝ HOẠT ĐỘNG", "5 BƯỚC KHÉP KÍN", [
            "• Bước 1: Nhập hàng & Gắn mã định danh",
            "• Bước 2: Phân tích & Xác định vị trí",
            "• Bước 3: Vận chuyển & Lưu trữ tự động",
            "• Bước 4: Quản lý vị trí & Tồn kho real-time",
            "• Bước 5: Truy xuất hàng tự động"
        ]),
        ("THÔNG TIN TRÌNH BÀY", "PHẦN CỦA LY", [
            "• Người thực hiện: Ly",
            "• Chủ đề: Thẻ nội dung phần 2",
            "• Định dạng: Trình chiếu tối giản",
            "• Nguồn dữ liệu: ITG Technology & VTI Solutions",
            "• Mục tiêu: Nắm vững cấu trúc & vận hành"
        ])
    ]

    for idx, (cat, title, items) in enumerate(pillars):
        x1 = 120 + idx * (card_w + 30)
        y1 = 510
        x2 = x1 + card_w
        y2 = 890
        draw_card(draw, [x1, y1, x2, y2], fill=CARD_BG, outline=CARD_BORDER, radius=16)

        # Header of card
        draw.rounded_rectangle([x1, y1, x2, y1 + 65], radius=16, fill=(241, 245, 249))
        draw.rectangle([x1, y1 + 50, x2, y1 + 65], fill=(241, 245, 249))
        draw.line([(x1, y1 + 65), (x2, y1 + 65)], fill=CARD_BORDER, width=2)

        f_c1 = get_font(FONT_BOLD, 14)
        draw.text((x1 + 24, y1 + 14), cat, font=f_c1, fill=TEXT_MUTED)

        f_c2 = get_font(FONT_BOLD, 18)
        draw.text((x1 + 24, y1 + 34), title, font=f_c2, fill=TEXT_MAIN)

        # Items
        f_item = get_font(FONT_REG, 18)
        curr_y = y1 + 90
        for item in items:
            draw.text((x1 + 24, curr_y), item, font=f_item, fill=TEXT_BODY)
            curr_y += 36

    # Bottom footer tag
    f_bot = get_font(FONT_REG, 16)
    draw.text((120, 950), "Báo cáo nội dung chuyên đề Kho hàng thông minh • Bộ môn Tự động hóa & Logistics", font=f_bot, fill=TEXT_MUTED)

    img.save(os.path.join(OUTPUT_DIR, "Slide_01_Tieu_de_Tong_quan.png"))
    print("Slide 1 generated.")

# ==============================================================================
# SLIDE 2: 2.1 TỔNG QUAN 5 THÀNH PHẦN
# ==============================================================================
def make_slide_2():
    img, draw = create_base()
    draw_header(draw, "2. CẤU TRÚC HỆ THỐNG AS/RS", "2.1. CÁC THÀNH PHẦN CHÍNH CỦA MỘT HỆ THỐNG AS/RS", 
                "Về cơ bản, hệ thống AS/RS được cấu tạo từ 5 thành phần chính phối hợp nhịp nhàng giữa cơ khí, điều khiển và phần mềm")
    draw_footer(draw, 2)

    # Top highlight quote card
    draw_card(draw, [90, 215, WIDTH - 90, 290], fill=(241, 245, 249), outline=CARD_BORDER, radius=12)
    f_quote = get_font(FONT_BOLD, 20)
    quote_text = "5 THÀNH PHẦN CỐT LÕI:  (1) Giá đỡ   •   (2) Hệ thống Stacker   •   (3) Hệ thống truyền tải   •   (4) Hệ thống điều khiển   •   (5) Hệ thống WMS"
    draw.text((120, 238), quote_text, font=f_quote, fill=TEXT_MAIN)

    # 5 Vertical Column Cards
    col_w = (WIDTH - 180 - (4 * 20)) // 5
    cols = [
        ("01", "GIÁ ĐỠ", "(Rack System)", "Hệ thống kệ chứa hàng", [
            "Trang bị các giá đỡ pallet & giá đỡ ổ đĩa chịu tải trọng lớn.",
            "Tận dụng tối đa chiều cao nhà kho (lên đến 40m).",
            "Tích hợp cùng băng tải bốc xếp theo lệnh máy tính."
        ]),
        ("02", "STACKER", "(Stacker Crane)", "Cần trục xếp dỡ đa trục", [
            "Ổ đĩa chuyển đổi tần số vector mượt mà, chính xác.",
            "Bộ mã hóa (Encoder) định vị chuẩn từng milimet.",
            "Trang bị đầy đủ thiết bị an toàn cơ - điện tử nghiêm ngặt."
        ]),
        ("03", "TRUYỀN TẢI", "(Conveying System)", "Luân chuyển hàng hóa", [
            "Bố trí ở khu vực giao nhận và tiếp nhận cửa kho.",
            "Hỗ trợ vận chuyển qua xe nâng, băng tải con lăn/xích.",
            "Kết hợp thang máy công nghiệp đưa hàng lên cao."
        ]),
        ("04", "ĐIỀU KHIỂN", "(Control System)", "Cầu nối hiện trường", [
            "Thu thập & kết nối dữ liệu thực tế tại kho vận.",
            "Gửi thông tin về WMS qua bộ điều khiển PLC.",
            "Phối hợp điều phối băng tải ngoại tuyến nhịp nhàng."
        ]),
        ("05", "HỆ THỐNG WMS", "(Warehouse Software)", "Bộ não quản lý thông minh", [
            "Cấu trúc mạng sao, máy chủ mạng & máy chủ RF.",
            "Máy tính quản lý, giám sát giao diện trực quan 24/7.",
            "Trạm gốc RF và thiết bị đầu cuối RF cho kho vào/ra."
        ])
    ]

    for idx, (num, title, en_title, tag, points) in enumerate(cols):
        x1 = 90 + idx * (col_w + 20)
        y1 = 315
        x2 = x1 + col_w
        y2 = 980

        draw_card(draw, [x1, y1, x2, y2], fill=CARD_BG, outline=CARD_BORDER, radius=14)

        # Header of column
        draw.rounded_rectangle([x1, y1, x2, y1 + 125], radius=14, fill=(255, 255, 255), outline=CARD_BORDER, width=2)
        draw.rectangle([x1, y1 + 110, x2, y1 + 125], fill=(255, 255, 255))
        draw.line([(x1, y1 + 125), (x2, y1 + 125)], fill=CARD_BORDER, width=2)

        # Number badge
        f_num = get_font(FONT_BOLD, 28)
        draw.text((x1 + 18, y1 + 14), num, font=f_num, fill=TEXT_MAIN)

        f_t = get_font(FONT_BOLD, 19)
        draw.text((x1 + 18, y1 + 50), title, font=f_t, fill=TEXT_MAIN)

        f_sub = get_font(FONT_REG, 14)
        draw.text((x1 + 18, y1 + 75), en_title, font=f_sub, fill=TEXT_MUTED)

        f_tag = get_font(FONT_BOLD, 12)
        draw.text((x1 + 18, y1 + 97), f"• {tag}", font=f_tag, fill=(71, 85, 105))

        # Points
        f_p = get_font(FONT_REG, 15)
        curr_y = y1 + 145
        for pt in points:
            draw.text((x1 + 16, curr_y), "▪", font=f_p, fill=TEXT_MAIN)
            lines = wrap_text(draw, pt, f_p, col_w - 44)
            for line in lines:
                draw.text((x1 + 32, curr_y), line, font=f_p, fill=TEXT_BODY)
                curr_y += 22
            curr_y += 14

    img.save(os.path.join(OUTPUT_DIR, "Slide_02_Tong_quan_5_Thanh_phan.png"))
    print("Slide 2 generated.")

# ==============================================================================
# SLIDE 3: CHI TIẾT THÀNH PHẦN 1 & 2 (GIÁ ĐỠ & STACKER)
# ==============================================================================
def make_slide_3():
    img, draw = create_base()
    draw_header(draw, "2.1. CÁC THÀNH PHẦN CHÍNH (PHẦN 1)", "CHI TIẾT: GIÁ ĐỠ VÀ HỆ THỐNG STACKER CRANE",
                "Phân tích chuyên sâu 2 thành phần cơ khí và thiết bị chấp hành chịu tải trọng lớn nhất trong kho AS/RS")
    draw_footer(draw, 3)

    card_w = (WIDTH - 180 - 40) // 2
    cards = [
        ("THÀNH PHẦN 1", "HỆ THỐNG GIÁ ĐỠ (RACK SYSTEM)", "Hạ tầng chịu tải và lưu trữ hàng hóa mật độ cao", [
            ("Trang bị giá đỡ chuyên dụng", "Hệ thống kệ AS/RS được thiết kế và trang bị các giá đỡ pallet cũng như giá đỡ ổ đĩa chuyên dụng có khả năng tải hàng hóa với công suất lớn, độ bền cơ học cao."),
            ("Tận dụng không gian thẳng đứng", "Khác với kho truyền thống, khung giàn kệ AS/RS có thể vươn cao tới 30 - 40 mét, giúp khai thác triệt để thể tích không gian kho và tiết kiệm đến 70% diện tích mặt bằng."),
            ("Tích hợp đồng bộ cùng băng tải", "Các băng tải ngoại vi được thiết kế đồng bộ ngay tại chân kệ để thực hiện các thao tác bốc dỡ, đưa hàng vào ô chứa hoàn toàn theo chỉ dẫn từ máy tính trung tâm."),
            ("Tiêu chuẩn an toàn kết cấu", "Hệ thống kết cấu thép được tính toán chống rung lắc khi cần trục Stacker tăng tốc và đảm bảo an toàn tuyệt đối trước tải trọng hàng nghìn tấn.")
        ]),
        ("THÀNH PHẦN 2", "HỆ THỐNG STACKER (CẦN TRỤC XẾP CHỒNG)", "Thiết bị chấp hành tự động truy xuất hàng đa trục", [
            ("Ổ đĩa chuyển đổi tần số vector", "Sử dụng các ổ đĩa điều khiển tần số vector tiên tiến, giúp động cơ nâng hạ và di chuyển Stacker tăng giảm tốc cực kỳ êm ái, giảm hao mòn cơ khí và tiết kiệm điện năng."),
            ("Bộ mã hóa vị trí (Encoder)", "Trang bị bộ mã hóa điều khiển vị trí độ phân giải cao, giúp định vị chính xác tọa độ từng ô kệ theo 3 chiều không gian (dài, rộng, cao) với sai số chỉ tính bằng milimét."),
            ("Hệ thống an toàn cơ khí & điện tử", "Tích hợp đồng bộ thiết bị an toàn cơ khí (chốt hãm, chống rơi tự do) cùng thiết bị an toàn điện tử (cảm biến quang, giới hạn hành trình, nút dừng khẩn cấp E-stop)."),
            ("Vận hành liên tục 24/7", "Thay thế hoàn toàn xe nâng truyền thống, Stacker hoạt động bền bỉ, tốc độ cao mà không bị suy giảm năng suất do mệt mỏi hay phụ thuộc con người.")
        ])
    ]

    for idx, (badge, title, subtitle, bullets) in enumerate(cards):
        x1 = 90 + idx * (card_w + 40)
        y1 = 215
        x2 = x1 + card_w
        y2 = 980

        draw_card(draw, [x1, y1, x2, y2], fill=CARD_BG, outline=CARD_BORDER, radius=16)

        # Header Card Box
        draw.rounded_rectangle([x1, y1, x2, y1 + 105], radius=16, fill=(255, 255, 255), outline=CARD_BORDER, width=2)
        draw.rectangle([x1, y1 + 85, x2, y1 + 105], fill=(255, 255, 255))
        draw.line([(x1, y1 + 105), (x2, y1 + 105)], fill=CARD_BORDER, width=2)

        # Badge
        f_b = get_font(FONT_BOLD, 13)
        draw.rounded_rectangle([x1 + 24, y1 + 16, x1 + 160, y1 + 40], radius=6, fill=BADGE_BG)
        draw.text((x1 + 34, y1 + 20), badge, font=f_b, fill=BADGE_FG)

        # Title
        f_t = get_font(FONT_BOLD, 22)
        draw.text((x1 + 24, y1 + 48), title, font=f_t, fill=TEXT_MAIN)

        f_sub = get_font(FONT_REG, 15)
        draw.text((x1 + 24, y1 + 78), subtitle, font=f_sub, fill=TEXT_MUTED)

        # Bullets with dynamic height
        curr_y = y1 + 125
        f_bt = get_font(FONT_BOLD, 18)
        f_bd = get_font(FONT_REG, 16)
        max_tw = card_w - 76

        for b_title, b_desc in bullets:
            consumed = draw_bullet_card(draw, x1 + 20, curr_y, x2 - 20, b_title, b_desc, f_bt, f_bd, max_tw)
            curr_y += consumed

    img.save(os.path.join(OUTPUT_DIR, "Slide_03_Gia_do_va_Stacker.png"))
    print("Slide 3 generated.")

# ==============================================================================
# SLIDE 4: CHI TIẾT THÀNH PHẦN 3, 4 & 5 (TRUYỀN TẢI, ĐIỀU KHIỂN & WMS)
# ==============================================================================
def make_slide_4():
    img, draw = create_base()
    draw_header(draw, "2.1. CÁC THÀNH PHẦN CHÍNH (PHẦN 2)", "CHI TIẾT: HỆ THỐNG TRUYỀN TẢI, ĐIỀU KHIỂN VÀ PHẦN MỀM WMS",
                "Hạ tầng vận chuyển liên kết, mạng điều khiển hiện trường và bộ não quản trị dữ liệu kho thông minh")
    draw_footer(draw, 4)

    card_w = (WIDTH - 180 - (2 * 30)) // 3
    cards = [
        ("THÀNH PHẦN 3", "HỆ THỐNG TRUYỀN TẢI", "Conveying & Transfer System", [
            ("Vị trí bố trí", "Được lắp đặt ở gần khu vực cửa kho, các hành lang giao nhận và kết nối trực tiếp với chân giàn kệ AS/RS."),
            ("Phương tiện vận chuyển", "Hỗ trợ luân chuyển hàng hóa tự động thông qua xe nâng, hệ thống băng tải con lăn, băng tải xích công nghiệp."),
            ("Tích hợp thang máy", "Kết hợp nhịp nhàng với hệ thống thang máy chuyên dụng để vận chuyển hàng hóa lên xuống giữa các tầng sàn."),
            ("Dòng chảy liên tục", "Đảm bảo hàng hóa từ khâu tiếp nhận đến vị trí lưu kho luôn được luân chuyển mượt mà, không bị nghẽn mạch.")
        ]),
        ("THÀNH PHẦN 4", "HỆ THỐNG ĐIỀU KHIỂN", "PLC & Automation Control", [
            ("Kết nối dữ liệu thực tế", "Cho phép thu thập và kết nối toàn bộ dữ liệu trạng thái thực tế tại hiện trường khu vực kho vận theo thời gian thực."),
            ("Truyền thông tin về WMS", "Chuyển giao dữ liệu hai chiều về hệ thống phần mềm quản lý kho thông minh (WMS) chính xác và tức thời."),
            ("Bộ điều khiển chuyên dụng", "Sử dụng các bộ điều khiển logic lập trình (PLC) công nghiệp cùng hệ thống băng tải ngoại tuyến tin cậy."),
            ("Độ trễ cực thấp", "Xử lý tức thì các tín hiệu cảm biến định vị, kiểm tra tải trọng và kích thước pallet trước khi đưa vào kệ.")
        ]),
        ("THÀNH PHẦN 5", "HỆ THỐNG PHẦN MỀM WMS", "Warehouse Management System", [
            ("Cấu trúc mạng sao", "Hệ thống quản lý kho thông minh được thiết kế theo cấu trúc mạng sao (Star Network) tối ưu tính bảo mật và ổn định."),
            ("Hệ thống máy chủ", "Trang bị đầy đủ máy chủ mạng (Network Server) và máy chủ RF chuyên dụng phục vụ giao tiếp vô tuyến."),
            ("Giám sát & Quản trị", "Hệ thống máy tính giám sát trực quan cho phép theo dõi mọi luồng xuất nhập, trạng thái từng ô kệ 24/7."),
            ("Trạm gốc & Thiết bị RF", "Bao gồm các trạm gốc RF (Base Stations) và thiết bị đầu cuối cầm tay (RF Terminals) kiểm soát hàng vào/ra.")
        ])
    ]

    for idx, (badge, title, en_title, points) in enumerate(cards):
        x1 = 90 + idx * (card_w + 30)
        y1 = 215
        x2 = x1 + card_w
        y2 = 980

        draw_card(draw, [x1, y1, x2, y2], fill=CARD_BG, outline=CARD_BORDER, radius=16)

        # Header Card Box
        draw.rounded_rectangle([x1, y1, x2, y1 + 105], radius=16, fill=(255, 255, 255), outline=CARD_BORDER, width=2)
        draw.rectangle([x1, y1 + 85, x2, y1 + 105], fill=(255, 255, 255))
        draw.line([(x1, y1 + 105), (x2, y1 + 105)], fill=CARD_BORDER, width=2)

        # Badge
        f_b = get_font(FONT_BOLD, 13)
        draw.rounded_rectangle([x1 + 20, y1 + 16, x1 + 145, y1 + 40], radius=6, fill=BADGE_BG)
        draw.text((x1 + 30, y1 + 20), badge, font=f_b, fill=BADGE_FG)

        # Title
        f_t = get_font(FONT_BOLD, 20)
        draw.text((x1 + 20, y1 + 48), title, font=f_t, fill=TEXT_MAIN)

        f_sub = get_font(FONT_REG, 14)
        draw.text((x1 + 20, y1 + 76), en_title, font=f_sub, fill=TEXT_MUTED)

        # Bullets
        curr_y = y1 + 125
        f_bt = get_font(FONT_BOLD, 17)
        f_bd = get_font(FONT_REG, 15)
        max_tw = card_w - 60

        for b_title, b_desc in points:
            consumed = draw_bullet_card(draw, x1 + 16, curr_y, x2 - 16, b_title, b_desc, f_bt, f_bd, max_tw)
            curr_y += consumed

    img.save(os.path.join(OUTPUT_DIR, "Slide_04_Truyen_tai_Dieu_khien_WMS.png"))
    print("Slide 4 generated.")

# ==============================================================================
# SLIDE 5: 2.2 TỔNG QUAN NGUYÊN LÝ HOẠT ĐỘNG (SƠ ĐỒ 5 BƯỚC)
# ==============================================================================
def make_slide_5():
    img, draw = create_base()
    draw_header(draw, "2. NGUYÊN LÝ HOẠT ĐỘNG", "2.2. NGUYÊN LÝ HOẠT ĐỘNG CỦA HỆ THỐNG KHO AS/RS",
                "Chuỗi quy trình 5 bước tích hợp khép kín giữa phần cứng và phần mềm, xử lý nhanh chóng từ lúc nhập đến lúc xuất kho")
    draw_footer(draw, 5)

    # Core principle banner
    draw_card(draw, [90, 215, WIDTH - 90, 305], fill=(241, 245, 249), outline=CARD_BORDER, radius=14)
    f_p_title = get_font(FONT_BOLD, 18)
    f_p_body = get_font(FONT_REG, 17)
    draw.text((120, 230), "NGUYÊN LÝ HOẠT ĐỘNG CỐT LÕI:", font=f_p_title, fill=TEXT_MAIN)
    desc = "Tách biệt hoàn toàn giữa không gian lưu trữ và khu vực thao tác của con người. Khi có lệnh xuất/nhập, hệ thống tự động điều khiển thiết bị di chuyển chính xác đến ô kệ tương ứng, tối ưu hóa thời gian và đạt độ chính xác gần như tuyệt đối."
    lines = wrap_text(draw, desc, f_p_body, WIDTH - 260)
    y_t = 258
    for l in lines:
        draw.text((120, y_t), l, font=f_p_body, fill=TEXT_BODY)
        y_t += 24

    # 5 Process Steps Horizontal Cards
    card_w = (WIDTH - 180 - (4 * 20)) // 5
    steps = [
        ("BƯỚC 1", "NHẬP HÀNG & GẮN MÃ", [
            "Hàng hóa đặt lên pallet hoặc thùng tiêu chuẩn.",
            "Gắn mã định danh: Barcode, QR code hoặc RFID.",
            "Băng chuyền tự động đưa hàng từ điểm nhập vào kho."
        ]),
        ("BƯỚC 2", "XÁC ĐỊNH VỊ TRÍ LƯU TRỮ", [
            "Phần mềm WMS phân tích đa tiêu chí.",
            "Đánh giá kích thước, tải trọng, tần suất xuất nhập.",
            "Quyết định vị trí tối ưu, tận dụng tối đa chiều cao kho."
        ]),
        ("BƯỚC 3", "VẬN CHUYỂN & LƯU TỰ ĐỘNG", [
            "Cần trục Stacker Crane / Robot nhận lệnh từ WMS.",
            "Di chuyển theo 3 trục: Ngang, Dọc và Thẳng đứng.",
            "Đưa hàng vào ô kệ chỉ định với sai số cực thấp."
        ]),
        ("BƯỚC 4", "QUẢN LÝ VỊ TRÍ & TỒN KHO", [
            "WMS cập nhật dữ liệu kho theo thời gian thực.",
            "Ghi nhận vị trí chính xác, số lượng và thời gian nhập.",
            "Kiểm soát tồn kho trực quan, loại bỏ kiểm kho thủ công."
        ]),
        ("BƯỚC 5", "TRUY XUẤT HÀNG TỰ ĐỘNG", [
            "WMS nhận lệnh sản xuất hoặc đơn xuất hàng.",
            "Robot tự động lấy đúng loại hàng, đúng số lượng.",
            "Băng chuyền đưa hàng ra khu vực xuất đóng gói."
        ])
    ]

    for idx, (step_num, step_title, points) in enumerate(steps):
        x1 = 90 + idx * (card_w + 20)
        y1 = 330
        x2 = x1 + card_w
        y2 = 860

        draw_card(draw, [x1, y1, x2, y2], fill=CARD_BG, outline=CARD_BORDER, radius=14)

        # Header Box of step
        draw.rounded_rectangle([x1, y1, x2, y1 + 105], radius=14, fill=(255, 255, 255), outline=CARD_BORDER, width=2)
        draw.rectangle([x1, y1 + 85, x2, y1 + 105], fill=(255, 255, 255))
        draw.line([(x1, y1 + 105), (x2, y1 + 105)], fill=CARD_BORDER, width=2)

        # Step badge
        f_sb = get_font(FONT_BOLD, 14)
        draw.rounded_rectangle([x1 + 16, y1 + 14, x1 + 95, y1 + 38], radius=6, fill=BADGE_BG)
        draw.text((x1 + 24, y1 + 18), step_num, font=f_sb, fill=BADGE_FG)

        # Title
        f_st = get_font(FONT_BOLD, 17)
        lines_t = wrap_text(draw, step_title, f_st, card_w - 32)
        curr_yt = y1 + 48
        for lt in lines_t:
            draw.text((x1 + 16, curr_yt), lt, font=f_st, fill=TEXT_MAIN)
            curr_yt += 23

        # Bullet points
        f_pt = get_font(FONT_REG, 15)
        curr_y = y1 + 130
        for p in points:
            draw.text((x1 + 16, curr_y), "▪", font=f_pt, fill=TEXT_MAIN)
            p_lines = wrap_text(draw, p, f_pt, card_w - 44)
            for pl in p_lines:
                draw.text((x1 + 32, curr_y), pl, font=f_pt, fill=TEXT_BODY)
                curr_y += 22
            curr_y += 12

    # Bottom summary tags
    draw_card(draw, [90, 885, WIDTH - 90, 970], fill=(255, 255, 255), outline=CARD_BORDER, radius=12)
    f_val_t = get_font(FONT_BOLD, 18)
    f_val_d = get_font(FONT_REG, 16)
    draw.text((120, 905), "LỢI THẾ VƯỢT TRỘI:", font=f_val_t, fill=TEXT_MAIN)
    val_text = "Tốc độ xử lý nhanh chóng 24/7   |   Độ chính xác tiệm cận tuyệt đối   |   Giảm 80% rủi ro tai nạn lao động & hư hỏng hàng hóa"
    draw.text((120, 935), val_text, font=f_val_d, fill=TEXT_MUTED)

    img.save(os.path.join(OUTPUT_DIR, "Slide_05_Nguyen_ly_5_buoc_Tong_quan.png"))
    print("Slide 5 generated.")

# ==============================================================================
# SLIDE 6: CHI TIẾT BƯỚC 1 & 2 (NHẬP HÀNG & XÁC ĐỊNH VỊ TRÍ)
# ==============================================================================
def make_slide_6():
    img, draw = create_base()
    draw_header(draw, "2.2. NGUYÊN LÝ HOẠT ĐỘNG (GIAI ĐOẠN ĐẦU VÀO)", "BƯỚC 1 & BƯỚC 2: TIẾP NHẬN, ĐỊNH DANH VÀ TỐI ƯU VỊ TRÍ LƯU TRỮ",
                "Khởi tạo dòng hàng: Chuẩn hóa nhận diện vật lý và thuật toán phân tích vị trí thông minh của WMS")
    draw_footer(draw, 6)

    card_w = (WIDTH - 180 - 40) // 2
    cards = [
        ("BƯỚC 1", "NHẬP HÀNG VÀ GẮN MÃ ĐỊNH DANH", "Số hóa kiện hàng và tiếp nhận tự động tại cửa kho", [
            ("Chuẩn hóa đơn vị chứa hàng", "Hàng hóa khi được đưa vào kho sẽ được đặt ngay ngắn lên pallet, thùng chứa (tote) hoặc khay chứa tiêu chuẩn để phù hợp với thông số của giá đỡ và cánh tay robot."),
            ("Gắn mã nhận diện thông minh", "Mỗi đơn vị hàng được gắn mã định danh duy nhất (Barcode, mã QR hoặc chip RFID). Đây là chìa khóa để toàn bộ hệ sinh thái AS/RS 'nhận biết', truy vết và giám sát."),
            ("Đồng bộ dữ liệu tức thời vào WMS", "Thông tin về lô hàng, số lượng, quy cách sau khi quét mã sẽ được nhập tức thì vào cơ sở dữ liệu của phần mềm quản lý kho WMS."),
            ("Vận chuyển tự động tại khu tiếp nhận", "Tại khu vực tiếp nhận, hệ thống băng chuyền tự động vận chuyển hàng từ cửa nhập vào khu lưu trữ, loại bỏ hoàn toàn việc nhân sự phải bốc xếp thủ công như kho truyền thống.")
        ]),
        ("BƯỚC 2", "XÁC ĐỊNH VỊ TRÍ LƯU TRỮ TỐI ƯU", "Thuật toán WMS tính toán tọa độ lưu kho hoàn hảo", [
            ("Phân tích đa tiêu chí hàng hóa", "Trước khi hàng được cất vào kệ, phần mềm WMS phân tích dữ liệu đa chiều: Chủng loại hàng hóa, tính chất bảo quản, kích thước hình học và tải trọng kiện hàng."),
            ("Đánh giá tần suất xuất nhập (Velocity)", "WMS tự động phân loại hàng quay vòng nhanh (Fast-moving) để bố trí ở các tầng kệ thấp, gần cửa xuất; hàng lưu kho dài ngày được đưa lên cao hoặc vào sâu bên trong."),
            ("Kiểm tra sức chứa ô kệ thời gian thực", "Hệ thống tự động rà soát bản đồ kho số hóa, xác định các ô kệ còn trống phù hợp với tải trọng và kích thước của kiện hàng cần nhập."),
            ("Tối ưu hóa không gian & thời gian", "Quyết định vị trí tối ưu giúp tận dụng tối đa chiều cao kho, giảm tải hành trình cho Stacker và rút ngắn tối đa thời gian lấy hàng sau này.")
        ])
    ]

    for idx, (badge, title, subtitle, bullets) in enumerate(cards):
        x1 = 90 + idx * (card_w + 40)
        y1 = 215
        x2 = x1 + card_w
        y2 = 980

        draw_card(draw, [x1, y1, x2, y2], fill=CARD_BG, outline=CARD_BORDER, radius=16)

        # Header Card Box
        draw.rounded_rectangle([x1, y1, x2, y1 + 105], radius=16, fill=(255, 255, 255), outline=CARD_BORDER, width=2)
        draw.rectangle([x1, y1 + 85, x2, y1 + 105], fill=(255, 255, 255))
        draw.line([(x1, y1 + 105), (x2, y1 + 105)], fill=CARD_BORDER, width=2)

        # Badge
        f_b = get_font(FONT_BOLD, 13)
        draw.rounded_rectangle([x1 + 24, y1 + 16, x1 + 120, y1 + 40], radius=6, fill=BADGE_BG)
        draw.text((x1 + 34, y1 + 20), badge, font=f_b, fill=BADGE_FG)

        # Title
        f_t = get_font(FONT_BOLD, 22)
        draw.text((x1 + 24, y1 + 48), title, font=f_t, fill=TEXT_MAIN)

        f_sub = get_font(FONT_REG, 15)
        draw.text((x1 + 24, y1 + 78), subtitle, font=f_sub, fill=TEXT_MUTED)

        # Bullets
        curr_y = y1 + 125
        f_bt = get_font(FONT_BOLD, 18)
        f_bd = get_font(FONT_REG, 16)
        max_tw = card_w - 76

        for b_title, b_desc in bullets:
            consumed = draw_bullet_card(draw, x1 + 20, curr_y, x2 - 20, b_title, b_desc, f_bt, f_bd, max_tw)
            curr_y += consumed

    img.save(os.path.join(OUTPUT_DIR, "Slide_06_Buoc_1_va_Buoc_2.png"))
    print("Slide 6 generated.")

# ==============================================================================
# SLIDE 7: CHI TIẾT BƯỚC 3 & 4 (VẬN CHUYỂN LƯU TRỮ & QUẢN LÝ TỒN KHO)
# ==============================================================================
def make_slide_7():
    img, draw = create_base()
    draw_header(draw, "2.2. NGUYÊN LÝ HOẠT ĐỘNG (LƯU TRỮ & GIÁM SÁT)", "BƯỚC 3 & BƯỚC 4: VẬN CHUYỂN TỰ ĐỘNG VÀ QUẢN LÝ TỒN KHO THỜI GIAN THỰC",
                "Thiết bị chấp hành tự động cất hàng vào kệ chính xác và WMS đồng bộ dữ liệu tức thời")
    draw_footer(draw, 7)

    card_w = (WIDTH - 180 - 40) // 2
    cards = [
        ("BƯỚC 3", "VẬN CHUYỂN VÀ LƯU TRỮ TỰ ĐỘNG", "Thiết bị Stacker / Robot đưa hàng vào ô kệ chuẩn xác", [
            ("Kích hoạt lệnh từ WMS", "Sau khi WMS xác định tọa độ lưu trữ tối ưu, lệnh điều khiển được gửi xuống hệ thống điều khiển PLC để kích hoạt cần trục Stacker Crane hoặc robot kho."),
            ("Chuyển động đa trục linh hoạt", "Stacker di chuyển đồng thời theo 3 trục không gian: Trục ngang (dọc theo hành lang kệ), Trục thẳng đứng (nâng hạ theo chiều cao), Trục dọc (vươn tay gắp vào sâu trong ô kệ)."),
            ("Độ chính xác cực cao", "Thiết bị đưa hàng chuẩn xác vào đúng ô kệ đã được chỉ định với sai số cực thấp, không xảy ra va chạm hay cong vênh pallet."),
            ("An toàn và bảo vệ hàng hóa", "Toàn bộ quá trình diễn ra tự động 100%, không cần con người vào sâu trong khu vực kệ cao, triệt tiêu rủi ro tai nạn lao động và hư hại hàng hóa.")
        ]),
        ("BƯỚC 4", "QUẢN LÝ VỊ TRÍ VÀ TỒN KHO REAL-TIME", "Minh bạch dữ liệu kho và kiểm soát 24/7 trên phần mềm", [
            ("Cập nhật dữ liệu thời gian thực", "Ngay khi hàng được đặt an toàn vào ô kệ, hệ thống cảm biến xác nhận và WMS lập tức cập nhật dữ liệu kho theo thời gian thực (real-time)."),
            ("Thông tin số hóa chi tiết", "Dữ liệu được số hóa toàn diện bao gồm: Vị trí chính xác (Dãy, Cột, Tầng), số lượng tồn kho từng SKU, số lô sản xuất và thời gian nhập kho chi tiết."),
            ("Nắm bắt tồn kho chính xác tuyệt đối", "Nhờ đó, ban quản trị doanh nghiệp luôn biết chính xác trong kho đang có gì, ở đâu, tình trạng tồn trữ ra sao vào bất kỳ thời điểm nào."),
            ("Loại bỏ kiểm kho thủ công", "Doanh nghiệp không còn phải tốn thời gian kiểm kê định kỳ thủ công, không bị thất thoát hàng hóa và không phụ thuộc vào trí nhớ cá nhân của thủ kho.")
        ])
    ]

    for idx, (badge, title, subtitle, bullets) in enumerate(cards):
        x1 = 90 + idx * (card_w + 40)
        y1 = 215
        x2 = x1 + card_w
        y2 = 980

        draw_card(draw, [x1, y1, x2, y2], fill=CARD_BG, outline=CARD_BORDER, radius=16)

        # Header Card Box
        draw.rounded_rectangle([x1, y1, x2, y1 + 105], radius=16, fill=(255, 255, 255), outline=CARD_BORDER, width=2)
        draw.rectangle([x1, y1 + 85, x2, y1 + 105], fill=(255, 255, 255))
        draw.line([(x1, y1 + 105), (x2, y1 + 105)], fill=CARD_BORDER, width=2)

        # Badge
        f_b = get_font(FONT_BOLD, 13)
        draw.rounded_rectangle([x1 + 24, y1 + 16, x1 + 120, y1 + 40], radius=6, fill=BADGE_BG)
        draw.text((x1 + 34, y1 + 20), badge, font=f_b, fill=BADGE_FG)

        # Title
        f_t = get_font(FONT_BOLD, 22)
        draw.text((x1 + 24, y1 + 48), title, font=f_t, fill=TEXT_MAIN)

        f_sub = get_font(FONT_REG, 15)
        draw.text((x1 + 24, y1 + 78), subtitle, font=f_sub, fill=TEXT_MUTED)

        # Bullets
        curr_y = y1 + 125
        f_bt = get_font(FONT_BOLD, 18)
        f_bd = get_font(FONT_REG, 16)
        max_tw = card_w - 76

        for b_title, b_desc in bullets:
            consumed = draw_bullet_card(draw, x1 + 20, curr_y, x2 - 20, b_title, b_desc, f_bt, f_bd, max_tw)
            curr_y += consumed

    img.save(os.path.join(OUTPUT_DIR, "Slide_07_Buoc_3_va_Buoc_4.png"))
    print("Slide 7 generated.")

# ==============================================================================
# SLIDE 8: CHI TIẾT BƯỚC 5 & TỔNG KẾT VẬN HÀNH
# ==============================================================================
def make_slide_8():
    img, draw = create_base()
    draw_header(draw, "2.2. NGUYÊN LÝ HOẠT ĐỘNG (ĐẦU RA & TỔNG KẾT)", "BƯỚC 5: TRUY XUẤT TỰ ĐỘNG VÀ GIÁ TRỊ VẬN HÀNH CỦA AS/RS",
                "Hoàn tất chu trình xuất kho nhanh chóng và tổng hợp các giá trị đột phá của kho tự động thông minh")
    draw_footer(draw, 8)

    card_w = (WIDTH - 180 - 40) // 2
    cards = [
        ("BƯỚC 5", "TRUY XUẤT HÀNG TỰ ĐỘNG (RETRIEVAL)", "Xuất hàng chính xác, liên tục theo lệnh từ WMS", [
            ("Tiếp nhận lệnh sản xuất / xuất bán", "Khi có đơn hàng xuất bán hoặc yêu cầu cấp phát vật tư cho sản xuất, WMS gửi tín hiệu tọa độ đến hệ thống điều khiển AS/RS."),
            ("Tự động định vị & lấy hàng", "Robot hoặc cần trục Stacker tự động di chuyển đến chính xác vị trí ô kệ chứa hàng, dùng cơ cấu lấy đúng loại hàng và đúng số lượng yêu cầu."),
            ("Đưa hàng ra khu vực xuất đóng gói", "Kiện hàng được đưa ra ngoài và chuyển tiếp lên hệ thống băng chuyền tự động để đi thẳng tới khu vực đóng gói hoặc bốc xếp lên xe tải."),
            ("Vận hành liên tục, không sai sót", "Toàn bộ quy trình diễn ra nhanh chóng, liên tục 24/7 và gần như loại bỏ hoàn toàn khả năng xảy ra nhầm lẫn đơn hàng.")
        ]),
        ("TỔNG KẾT", "GIÁ TRỊ CỐT LÕI CỦA HỆ THỐNG AS/RS", "Lợi ích vượt trội so với kho truyền thống", [
            ("Tối ưu diện tích sàn (60 - 80%)", "Khai thác tối đa chiều cao nhà xưởng và thu hẹp lối đi xe nâng, giúp tăng sức chứa lên gấp 3 đến 5 lần trên cùng diện tích."),
            ("Tốc độ & Hiệu suất 24/7", "Xử lý hàng hóa nhanh chóng, ổn định cả ngày lẫn đêm, giải quyết triệt để nút thắt cổ chai vào các mùa cao điểm logistics."),
            ("Chính xác tiệm cận 100%", "Định vị bằng phần mềm WMS và mã RFID/Barcode giúp triệt tiêu thất thoát, sai lệch số lượng hoặc nhầm vị trí hàng."),
            ("Tiết kiệm chi phí & An toàn tối đa", "Cắt giảm mạnh chi phí nhân công bốc dỡ trực tiếp và loại bỏ các vụ tai nạn lao động nghiêm trọng trong khu vực kệ cao.")
        ])
    ]

    for idx, (badge, title, subtitle, bullets) in enumerate(cards):
        x1 = 90 + idx * (card_w + 40)
        y1 = 215
        x2 = x1 + card_w
        y2 = 980

        draw_card(draw, [x1, y1, x2, y2], fill=CARD_BG, outline=CARD_BORDER, radius=16)

        # Header Card Box
        draw.rounded_rectangle([x1, y1, x2, y1 + 105], radius=16, fill=(255, 255, 255), outline=CARD_BORDER, width=2)
        draw.rectangle([x1, y1 + 85, x2, y1 + 105], fill=(255, 255, 255))
        draw.line([(x1, y1 + 105), (x2, y1 + 105)], fill=CARD_BORDER, width=2)

        # Badge
        f_b = get_font(FONT_BOLD, 13)
        draw.rounded_rectangle([x1 + 24, y1 + 16, x1 + 130, y1 + 40], radius=6, fill=BADGE_BG)
        draw.text((x1 + 34, y1 + 20), badge, font=f_b, fill=BADGE_FG)

        # Title
        f_t = get_font(FONT_BOLD, 22)
        draw.text((x1 + 24, y1 + 48), title, font=f_t, fill=TEXT_MAIN)

        f_sub = get_font(FONT_REG, 15)
        draw.text((x1 + 24, y1 + 78), subtitle, font=f_sub, fill=TEXT_MUTED)

        # Bullets
        curr_y = y1 + 125
        f_bt = get_font(FONT_BOLD, 18)
        f_bd = get_font(FONT_REG, 16)
        max_tw = card_w - 76

        for b_title, b_desc in bullets:
            consumed = draw_bullet_card(draw, x1 + 20, curr_y, x2 - 20, b_title, b_desc, f_bt, f_bd, max_tw)
            curr_y += consumed

    img.save(os.path.join(OUTPUT_DIR, "Slide_08_Buoc_5_va_Tong_ket.png"))
    print("Slide 8 generated.")

if __name__ == "__main__":
    print("Starting generation of 8 slides for Ly's section...")
    make_slide_1()
    make_slide_2()
    make_slide_3()
    make_slide_4()
    make_slide_5()
    make_slide_6()
    make_slide_7()
    make_slide_8()
    print("ALL 8 SLIDES GENERATED SUCCESSFULLY IN:", OUTPUT_DIR)

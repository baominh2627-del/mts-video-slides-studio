# -*- coding: utf-8 -*-
"""
Video Generator: Phương trình Van der Waals cho khí thực
- Độ phân giải: 1024 x 576 (Chuẩn 16:9, khớp 100% video mẫu)
- Tốc độ khung hình: 30 FPS
- Branding: MTSEducation (watermark góc trên trái & góc dưới phải)
- Giọng đọc: vi-VN-NamMinhNeural (chuẩn Bắc ngữ điệu khoa học)
- Nhạc nền: Ambient science lo-fi pad êm dịu
- Phụ đề: Chữ vàng viền đen, căn giữa dưới màn hình, đồng bộ giọng đọc
"""

import os
import sys
import json
import math
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

sys.stdout.reconfigure(encoding='utf-8')

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
BUILD_DIR = r"C:\Users\DELL\Documents\CODE\DU_AN\video_build"
OUTPUT_MP4 = r"C:\Users\DELL\Documents\CODE\DU_AN\PHUONG_TRINH_VAN_DER_WAALS_MTSEducation.mp4"
TIMELINE_JSON = os.path.join(BUILD_DIR, "timeline.json")
AUDIO_MASTER = os.path.join(BUILD_DIR, "audio_master.wav")
PORTRAIT_IMG = os.path.join(BUILD_DIR, "vanderwaals.jpg")

WIDTH = 1024
HEIGHT = 576
FPS = 30

# Load Fonts
FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_REG = "C:/Windows/Fonts/segoeui.ttf"
FONT_ITALIC = "C:/Windows/Fonts/segoeuii.ttf"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

f_brand = get_font(FONT_BOLD, 22)
f_brand_sub = get_font(FONT_BOLD, 15)
f_badge = get_font(FONT_BOLD, 13)
f_header_title = get_font(FONT_BOLD, 20)
f_card_title = get_font(FONT_BOLD, 16)
f_body = get_font(FONT_REG, 14)
f_body_b = get_font(FONT_BOLD, 14)
f_body_sm = get_font(FONT_REG, 13)
f_body_sm_b = get_font(FONT_BOLD, 13)
f_math_xl = get_font(FONT_BOLD, 30)
f_math_lg = get_font(FONT_BOLD, 24)
f_math_md = get_font(FONT_BOLD, 19)
f_sub = get_font(FONT_BOLD, 22)

# Colors
BG_DARK = (15, 20, 30)
CARD_BG = (22, 29, 44)
CARD_BORDER = (45, 55, 78)
CYAN_ACCENT = (56, 189, 248)
GREEN_ACCENT = (74, 222, 128)
RED_ACCENT = (248, 113, 113)
GOLD_ACCENT = (250, 204, 21)
AMBER_ACCENT = (251, 146, 60)
PURPLE_ACCENT = (192, 132, 252)

# Load portrait image if exists
portrait_pil = None
if os.path.exists(PORTRAIT_IMG):
    try:
        p_raw = Image.open(PORTRAIT_IMG).convert("RGB")
        portrait_pil = p_raw.resize((150, 180), Image.Resampling.LANCZOS)
    except Exception as e:
        print("Portrait load error:", e)

# Load Timeline
with open(TIMELINE_JSON, "r", encoding="utf-8") as f:
    timeline_data = json.load(f)

TOTAL_DURATION = timeline_data["total_duration"]
TOTAL_FRAMES = int(TOTAL_DURATION * FPS)
CLIPS = timeline_data["timeline"]

def get_current_subtitle(t):
    for c in CLIPS:
        if c["start"] <= t <= c["end"]:
            return c["text"]
    return ""

def draw_header_watermark(draw, scene_badge, title_text="PHƯƠNG TRÌNH VAN DER WAALS"):
    # Brand Top-Left (MTSEducation)
    draw.text((32, 22), "MTSEducation", font=f_brand, fill=(0, 0, 0))
    draw.text((30, 20), "MTSEducation", font=f_brand, fill=(255, 255, 255))
    
    # Secondary watermark bottom right
    draw.text((WIDTH - 120, HEIGHT - 25), "MTSEducation", font=f_brand_sub, fill=(130, 145, 170))
    
    # Header Center Badge
    badge_w = 460
    badge_x = (WIDTH - badge_w) // 2
    # Outer glow
    draw.rounded_rectangle([badge_x - 1, 12, badge_x + badge_w + 1, 52], radius=10, fill=(180, 30, 30))
    draw.rounded_rectangle([badge_x, 13, badge_x + badge_w, 51], radius=9, fill=(220, 38, 38))
    
    bbox_t = draw.textbbox((0, 0), title_text, font=f_header_title)
    tw = bbox_t[2] - bbox_t[0]
    draw.text((badge_x + (badge_w - tw) // 2, 20), title_text, font=f_header_title, fill=(255, 255, 255))
    
    # Scene sub-badge (left side below MTSEducation)
    if scene_badge:
        bbox_sb = draw.textbbox((0, 0), scene_badge, font=f_badge)
        sb_w = bbox_sb[2] - bbox_sb[0] + 16
        draw.rounded_rectangle([30, 52, 30 + sb_w, 74], radius=5, fill=(30, 41, 59), outline=(71, 85, 105), width=1)
        draw.text((38, 55), scene_badge, font=f_badge, fill=CYAN_ACCENT)

def draw_subtitle(draw, text):
    if not text:
        return
    text = text.upper()
    bbox = draw.textbbox((0, 0), text, font=f_sub)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    
    # If text is too wide for one line, wrap it
    max_w = WIDTH - 60
    lines = [text]
    if w > max_w:
        words = text.split()
        mid = len(words) // 2
        lines = [" ".join(words[:mid]), " ".join(words[mid:])]
        
    line_h = 28
    total_h = len(lines) * line_h
    start_y = HEIGHT - 55 - (total_h - line_h)
    
    for l_idx, line in enumerate(lines):
        l_bbox = draw.textbbox((0, 0), line, font=f_sub)
        lw = l_bbox[2] - l_bbox[0]
        x = (WIDTH - lw) // 2
        y = start_y + l_idx * line_h
        
        # Semi-transparent dark backing strip
        draw.rounded_rectangle([x - 14, y - 4, x + lw + 14, y + line_h - 2], radius=6, fill=(10, 10, 15))
        
        # Black outline
        for ox in [-2, -1, 0, 1, 2]:
            for oy in [-2, -1, 0, 1, 2]:
                if ox != 0 or oy != 0:
                    draw.text((x + ox, y + oy), line, font=f_sub, fill=(0, 0, 0))
        # Bright Yellow Fill
        draw.text((x, y), line, font=f_sub, fill=(255, 235, 50))

# ----------------- SCENE RENDERERS -----------------

def render_frame_scene1(t, sub_text):
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(img)
    draw_header_watermark(draw, "PHẦN 1: MÔ HÌNH KHÍ")
    
    # Left Card: Ideal Gas
    draw.rounded_rectangle([45, 90, 495, 485], radius=14, fill=CARD_BG, outline=CYAN_ACCENT, width=2)
    draw.rounded_rectangle([65, 105, 475, 140], radius=8, fill=(14, 50, 75))
    draw.text((150, 112), "1. MÔ HÌNH KHÍ LÝ TƯỞNG", font=f_card_title, fill=CYAN_ACCENT)
    
    # Simulation box
    draw.rounded_rectangle([65, 155, 475, 335], radius=10, fill=(10, 15, 25), outline=(30, 45, 65), width=1)
    np.random.seed(42)
    for p_i in range(24):
        px = 80 + int((np.sin(t * 1.5 + p_i * 1.2) * 0.5 + 0.5) * 360)
        py = 170 + int((np.cos(t * 1.8 + p_i * 0.9) * 0.5 + 0.5) * 140)
        draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=CYAN_ACCENT, outline=(255, 255, 255))
    draw.text((185, 235), "P · V = n · R · T", font=f_math_md, fill=(255, 255, 255))
    
    draw.text((68, 355), "• Phân tử coi như CHẤT ĐIỂM (thể tích V = 0)", font=f_body_b, fill=GREEN_ACCENT)
    draw.text((68, 385), "• Hoàn toàn KHÔNG CÓ LỰC HÚT giữa các phân tử", font=f_body_b, fill=GREEN_ACCENT)
    draw.text((68, 415), "• Va chạm hoàn toàn đàn hồi với thành bình", font=f_body, fill=(200, 210, 230))
    draw.text((68, 445), "-> Chỉ đúng ở ÁP SUẤT THẤP & NHIỆT ĐỘ CAO", font=f_body_b, fill=GOLD_ACCENT)
    
    # Right Card: Real Gas
    draw.rounded_rectangle([525, 90, 975, 485], radius=14, fill=CARD_BG, outline=RED_ACCENT, width=2)
    draw.rounded_rectangle([545, 105, 955, 140], radius=8, fill=(75, 25, 30))
    draw.text((645, 112), "2. MÔ HÌNH KHÍ THỰC TẾ", font=f_card_title, fill=RED_ACCENT)
    
    # Simulation box
    draw.rounded_rectangle([545, 155, 955, 335], radius=10, fill=(10, 15, 25), outline=(55, 30, 35), width=1)
    np.random.seed(101)
    pts = []
    for p_i in range(12):
        px = 575 + int((np.sin(t * 0.9 + p_i * 1.5) * 0.5 + 0.5) * 340)
        py = 175 + int((np.cos(t * 1.1 + p_i * 1.1) * 0.5 + 0.5) * 130)
        pts.append((px, py))
    for i in range(len(pts)):
        for j in range(i+1, len(pts)):
            dist = math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1])
            if dist < 85:
                draw.line([pts[i], pts[j]], fill=(180, 50, 60), width=1)
    for px, py in pts:
        draw.ellipse([px - 10, py - 10, px + 10, py + 10], fill=(220, 70, 70), outline=(255, 180, 180), width=2)
    draw.text((660, 235), "P · V ≠ n · R · T", font=f_math_md, fill=(255, 180, 180))
    
    draw.text((548, 355), "• Phân tử có KÍCH THƯỚC HỮU HẠN (bán kính r > 0)", font=f_body_b, fill=RED_ACCENT)
    draw.text((548, 385), "• Tồn tại LỰC HÚT LIÊN PHÂN TỬ Van der Waals", font=f_body_b, fill=RED_ACCENT)
    draw.text((548, 415), "• Các phân tử cản trở lẫn nhau khi chuyển động", font=f_body, fill=(230, 200, 200))
    draw.text((548, 445), "⚠ SAI LỆCH CỰC LỚN Ở ÁP SUẤT CAO & NHIỆT ĐỘ THẤP!", font=f_body_b, fill=AMBER_ACCENT)
    
    draw_subtitle(draw, sub_text)
    return img

def render_frame_scene2(t, sub_text):
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(img)
    draw_header_watermark(draw, "PHẦN 2: THỂ TÍCH RIÊNG (b)")
    
    # Left Card: Physical Mechanism of Excluded Volume
    draw.rounded_rectangle([45, 90, 505, 485], radius=14, fill=CARD_BG, outline=CARD_BORDER, width=2)
    draw.rounded_rectangle([65, 105, 485, 140], radius=8, fill=(18, 40, 65))
    draw.text((105, 112), "BẢN CHẤT THỂ TÍCH LOẠI TRỪ (EXCLUDED VOLUME)", font=f_card_title, fill=CYAN_ACCENT)
    
    # Schematic Container & Two colliding spheres
    draw.rounded_rectangle([65, 155, 485, 360], radius=10, fill=(10, 15, 25), outline=(40, 60, 90), width=1)
    
    # Central sphere 1
    c1x, c1y = 220, 255
    r = 26
    # Dotted exclusion circle radius 2r = 52
    draw.ellipse([c1x - 2*r, c1y - 2*r, c1x + 2*r, c1y + 2*r], fill=(30, 70, 50), outline=GREEN_ACCENT, width=2)
    # Sphere 1
    draw.ellipse([c1x - r, c1y - r, c1x + r, c1y + r], fill=(40, 140, 200), outline=(200, 230, 255), width=2)
    draw.text((c1x - 12, c1y - 10), "Hạt 1", font=f_body_sm_b, fill=(255, 255, 255))
    
    # Orbiting / Approaching sphere 2
    ang = t * 1.2
    c2x = int(c1x + 2 * r * math.cos(ang))
    c2y = int(c1y + 2 * r * math.sin(ang))
    draw.ellipse([c2x - r, c2y - r, c2x + r, c2y + r], fill=(220, 90, 60), outline=(255, 200, 180), width=2)
    draw.text((c2x - 12, c2y - 10), "Hạt 2", font=f_body_sm_b, fill=(255, 255, 255))
    
    # Connecting distance line
    draw.line([(c1x, c1y), (c2x, c2y)], fill=GOLD_ACCENT, width=2)
    draw.text((345, 195), "Khoảng cách tâm = 2r", font=f_body_sm_b, fill=GOLD_ACCENT)
    draw.text((345, 230), "V_loại trừ = 8 · v0", font=f_body_sm_b, fill=GREEN_ACCENT)
    draw.text((345, 260), "Bình quân 1 hạt: 4 · v0", font=f_body_sm, fill=(200, 215, 230))
    draw.text((345, 290), "1 mol khí: b = 4 · NA · v0", font=f_body_sm_b, fill=CYAN_ACCENT)
    
    # Summary note below schematic
    draw.text((70, 385), "• Phân tử không phải chất điểm, mà chiếm không gian riêng.", font=f_body, fill=(220, 230, 245))
    draw.text((70, 415), "• Mỗi phân tử loại trừ một quả cầu bán kính 2r xung quanh nó.", font=f_body, fill=(220, 230, 245))
    draw.text((70, 445), "• Hằng số b đặc trưng cho thể tích chiếm chỗ của 1 mol hạt.", font=f_body_b, fill=GREEN_ACCENT)
    
    # Right Card: The Formula Transformation
    draw.rounded_rectangle([525, 90, 975, 485], radius=14, fill=CARD_BG, outline=GREEN_ACCENT, width=2)
    draw.rounded_rectangle([545, 105, 955, 140], radius=8, fill=(20, 60, 40))
    draw.text((615, 112), "CÔNG THỨC HIỆU CHỈNH THỂ TÍCH", font=f_card_title, fill=GREEN_ACCENT)
    
    draw.text((550, 165), "Tổng thể tích bình chứa:", font=f_body, fill=(180, 195, 215))
    draw.text((750, 165), "V", font=f_math_md, fill=CYAN_ACCENT)
    
    draw.text((550, 205), "Thể tích bị n mol phân tử chiếm chỗ:", font=f_body, fill=(180, 195, 215))
    draw.text((820, 205), "n · b", font=f_math_md, fill=RED_ACCENT)
    
    draw.text((550, 245), "Thể tích tự do thực sự để chuyển động:", font=f_body_b, fill=(255, 255, 255))
    
    # Glowing Formula Box
    draw.rounded_rectangle([550, 280, 950, 360], radius=12, fill=(12, 45, 30), outline=GREEN_ACCENT, width=2)
    draw.text((620, 300), "V_tự do  =  V  -  n · b", font=f_math_xl, fill=GREEN_ACCENT)
    
    draw.text((550, 385), "Thay thế vào định luật khí lý tưởng P · V = nRT:", font=f_body, fill=(200, 215, 235))
    draw.rounded_rectangle([550, 415, 950, 465], radius=10, fill=(18, 30, 48), outline=(60, 80, 110), width=1)
    draw.text((625, 427), "P · ( V  -  n · b )  =  n · R · T", font=f_math_lg, fill=GOLD_ACCENT)
    
    draw_subtitle(draw, sub_text)
    return img

def render_frame_scene3(t, sub_text):
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(img)
    draw_header_watermark(draw, "PHẦN 3: LỰC TƯƠNG TÁC (a)")
    
    # Left Card: Pressure Deficit Mechanism
    draw.rounded_rectangle([45, 90, 505, 485], radius=14, fill=CARD_BG, outline=CARD_BORDER, width=2)
    draw.rounded_rectangle([65, 105, 485, 140], radius=8, fill=(45, 30, 60))
    draw.text((115, 112), "CƠ CHẾ LỰC HÚT VÀ SỰ SỤT GIẢM ÁP SUẤT", font=f_card_title, fill=PURPLE_ACCENT)
    
    # Canvas box
    draw.rounded_rectangle([65, 155, 485, 350], radius=10, fill=(10, 15, 25), outline=(40, 60, 90), width=1)
    
    # Case 1: Inside the gas
    draw.text((80, 165), "A. Phân tử ở sâu trong lòng khối khí:", font=f_body_sm_b, fill=CYAN_ACCENT)
    ix, iy = 150, 235
    # Radial arrows
    for deg in range(0, 360, 45):
        rad = math.radians(deg)
        ax = int(ix + 35 * math.cos(rad))
        ay = int(iy + 35 * math.sin(rad))
        draw.line([(ix, iy), (ax, ay)], fill=(90, 140, 200), width=2)
    draw.ellipse([ix - 12, iy - 12, ix + 12, iy + 12], fill=CYAN_ACCENT, outline=(255, 255, 255), width=2)
    draw.text((205, 225), "Σ F = 0 (Lực hút cân bằng)", font=f_body_b, fill=GREEN_ACCENT)
    
    # Case 2: Near the wall
    draw.text((80, 280), "B. Phân tử tiến sát đến thành bình:", font=f_body_sm_b, fill=RED_ACCENT)
    # Container Wall on the right edge of this sub-box
    wx = 465
    draw.line([(wx, 280), (wx, 345)], fill=(200, 200, 200), width=6)
    draw.text((wx - 35, 325), "Thành", font=f_body_sm, fill=(160, 160, 160))
    
    # Near wall molecule
    nx, ny = 425, 310
    # Velocity arrow forward
    draw.line([(nx, ny), (nx + 28, ny)], fill=CYAN_ACCENT, width=3)
    # Reverse attraction arrows backward!
    for dy in [-25, 0, 25]:
        draw.line([(nx, ny), (nx - 55, ny + dy)], fill=RED_ACCENT, width=3)
    draw.ellipse([nx - 11, ny - 11, nx + 11, ny + 11], fill=(240, 80, 80), outline=(255, 255, 255), width=2)
    draw.text((85, 310), "-> Bị hút kéo lùi lại!", font=f_body_b, fill=RED_ACCENT)
    
    draw.text((70, 375), "• Khi va chạm thành bình, phân tử bị lớp khí phía sau kéo lại.", font=f_body, fill=(220, 230, 245))
    draw.text((70, 405), "• Vận tốc & động lượng va đập bị giảm -> Áp suất P_thực < P_lý tưởng.", font=f_body_b, fill=AMBER_ACCENT)
    draw.text((70, 435), "• Cần bù thêm một lượng ÁP SUẤT NỘI (Pi) do lực tương tác.", font=f_body_b, fill=GOLD_ACCENT)
    
    # Right Card: Cohesion Pressure & Formula
    draw.rounded_rectangle([525, 90, 975, 485], radius=14, fill=CARD_BG, outline=AMBER_ACCENT, width=2)
    draw.rounded_rectangle([545, 105, 955, 140], radius=8, fill=(60, 35, 15))
    draw.text((615, 112), "CÔNG THỨC HIỆU CHỈNH ÁP SUẤT", font=f_card_title, fill=AMBER_ACCENT)
    
    draw.text((550, 160), "Lực hút kéo lùi tỷ lệ với:", font=f_body, fill=(180, 195, 215))
    draw.text((550, 185), "• Mật độ hạt ở thành bình:  (n / V)", font=f_body_b, fill=CYAN_ACCENT)
    draw.text((550, 210), "• Mật độ hạt kéo phía sau:   (n / V)", font=f_body_b, fill=CYAN_ACCENT)
    draw.text((550, 240), "-> Lực hút tỷ lệ bình phương: (n / V)²  =  n² / V²", font=f_body_b, fill=GOLD_ACCENT)
    
    # Glowing Formula Box: Internal Pressure
    draw.rounded_rectangle([550, 275, 950, 355], radius=12, fill=(45, 25, 10), outline=AMBER_ACCENT, width=2)
    draw.text((590, 290), "Áp suất nội:   Pi  =  a · n² / V²", font=f_math_lg, fill=AMBER_ACCENT)
    draw.text((590, 325), "(a: Hằng số đo độ mạnh lực hút liên phân tử)", font=f_body_sm, fill=(220, 180, 150))
    
    draw.text((550, 380), "Áp suất lý tưởng đưa vào phương trình:", font=f_body, fill=(200, 215, 235))
    draw.rounded_rectangle([550, 410, 950, 465], radius=10, fill=(18, 30, 48), outline=(60, 80, 110), width=1)
    draw.text((605, 425), "P_lý tưởng  =  P  +  ( a · n² / V² )", font=f_math_lg, fill=GREEN_ACCENT)
    
    draw_subtitle(draw, sub_text)
    return img

def render_frame_scene4(t, sub_text):
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(img)
    draw_header_watermark(draw, "PHẦN 4: PHƯƠNG TRÌNH KINH ĐIỂN")
    
    # Top Card: Master Equation
    draw.rounded_rectangle([45, 88, 975, 230], radius=14, fill=CARD_BG, outline=GOLD_ACCENT, width=2)
    draw.rounded_rectangle([65, 98, 955, 126], radius=6, fill=(50, 40, 10))
    draw.text((365, 102), "PHƯƠNG TRÌNH TRẠNG THÁI VAN DER WAALS", font=f_badge, fill=GOLD_ACCENT)
    
    # Master Equation text without overlaps
    eq_y = 138
    draw.text((120, eq_y), "(  P  +  ", font=f_math_xl, fill=(255, 255, 255))
    draw.text((230, eq_y), "a · n² / V²", font=f_math_xl, fill=AMBER_ACCENT)
    draw.text((400, eq_y), "  ) · (  V  -  ", font=f_math_xl, fill=(255, 255, 255))
    draw.text((580, eq_y), "n · b", font=f_math_xl, fill=GREEN_ACCENT)
    draw.text((665, eq_y), "  )  =  n · R · T", font=f_math_xl, fill=(255, 255, 255))
    
    # 3 Badges below
    draw.rounded_rectangle([130, 185, 385, 215], radius=6, fill=(50, 30, 15), outline=AMBER_ACCENT, width=1)
    draw.text((145, 192), "Áp suất hiệu chỉnh (+Pi)", font=f_body_sm_b, fill=AMBER_ACCENT)
    
    draw.rounded_rectangle([440, 185, 680, 215], radius=6, fill=(15, 45, 25), outline=GREEN_ACCENT, width=1)
    draw.text((460, 192), "Thể tích tự do (V - nb)", font=f_body_sm_b, fill=GREEN_ACCENT)
    
    draw.rounded_rectangle([735, 185, 920, 215], radius=6, fill=(15, 35, 55), outline=CYAN_ACCENT, width=1)
    draw.text((755, 192), "Nhiệt động học (nRT)", font=f_body_sm_b, fill=CYAN_ACCENT)
    
    # Bottom Card: Data Table
    draw.rounded_rectangle([45, 242, 975, 485], radius=14, fill=CARD_BG, outline=CARD_BORDER, width=2)
    draw.rounded_rectangle([65, 252, 955, 280], radius=6, fill=(20, 30, 50))
    draw.text((330, 256), "BẢNG TRA CỨU HẰNG SỐ a & b CỦA MỘT SỐ KHÍ THỰC", font=f_card_title, fill=CYAN_ACCENT)
    
    # Table headers
    headers = [("Chất khí", 70), ("a (L²·bar / mol²)", 260), ("b (L / mol)", 470), ("Ý nghĩa & Đặc điểm vật lý", 640)]
    for h_txt, hx in headers:
        draw.text((hx, 290), h_txt, font=f_body_b, fill=GOLD_ACCENT)
    draw.line([(65, 312), (955, 312)], fill=(50, 65, 90), width=1)
    
    # Table rows
    rows = [
        ("Helium (He)", "0.034", "0.0237", "Phân tử siêu nhỏ, tương tác cực yếu (gần lý tưởng nhất)", GREEN_ACCENT),
        ("Hydro (H2)", "0.244", "0.0266", "Khối lượng rất nhẹ, thể tích riêng nhỏ", CYAN_ACCENT),
        ("Oxy (O2)", "1.360", "0.0318", "Khí phổ biến, kích thước và lực hút trung bình", (220, 230, 240)),
        ("Cacbonic (CO2)", "3.590", "0.0427", "Phân tử lớn, lực hút mạnh, dễ bị hóa lỏng", AMBER_ACCENT),
        ("Hơi nước (H2O)", "5.460", "0.0305", "Liên kết hydro cực mạnh -> Hằng số a rất lớn!", RED_ACCENT),
    ]
    
    ry = 322
    for r_gas, r_a, r_b, r_desc, r_col in rows:
        draw.text((70, ry), r_gas, font=f_body_b, fill=r_col)
        draw.text((290, ry), r_a, font=f_body, fill=(255, 255, 255))
        draw.text((490, ry), r_b, font=f_body, fill=(255, 255, 255))
        draw.text((640, ry), r_desc, font=f_body_sm, fill=(200, 215, 235))
        ry += 30
        draw.line([(65, ry - 4), (955, ry - 4)], fill=(30, 42, 60), width=1)
        
    draw_subtitle(draw, sub_text)
    return img

def render_frame_scene5(t, sub_text):
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(img)
    draw_header_watermark(draw, "PHẦN 5: ĐẲNG NHIỆT & TỚI HẠN")
    
    # Left Card: P-V Isotherms Diagram
    draw.rounded_rectangle([45, 90, 565, 485], radius=14, fill=CARD_BG, outline=CARD_BORDER, width=2)
    draw.rounded_rectangle([65, 105, 545, 140], radius=8, fill=(15, 40, 55))
    draw.text((120, 112), "ĐỒ THỊ ĐẲNG NHIỆT P - V CỦA VAN DER WAALS", font=f_card_title, fill=CYAN_ACCENT)
    
    # Coordinate system (P vertical, V horizontal)
    ox, oy = 110, 420
    draw.line([(ox, oy), (ox, 160)], fill=(200, 210, 230), width=2) # P axis
    draw.line([(ox, oy), (ox + 420, oy)], fill=(200, 210, 230), width=2) # V axis
    draw.text((ox - 30, 160), "P", font=f_math_md, fill=GOLD_ACCENT)
    draw.text((ox + 410, oy + 8), "V", font=f_math_md, fill=GOLD_ACCENT)
    
    # Physical Isotherms: P decreases as V increases!
    # Curve 1: T > Tc (Supercritical gas: smooth downward curve, Cyan)
    pts1 = []
    for vx in range(40, 410, 8):
        py_val = 165 + (vx / 410.0) ** 0.5 * 180
        pts1.append((ox + vx, int(py_val)))
    draw.line(pts1, fill=CYAN_ACCENT, width=2)
    draw.text((ox + 310, 315), "T > Tc (Khí)", font=f_body_sm_b, fill=CYAN_ACCENT)
    
    # Curve 2: T = Tc (Critical Isotherm with horizontal inflection at K, Gold)
    pts2 = []
    for vx in range(35, 410, 8):
        # S-shape / inflection around vx = 170, py = 260
        delta = (vx - 170) / 90.0
        py_val = 260 + (delta ** 3) * 12 + delta * 25
        pts2.append((ox + vx, int(min(max(py_val, 175), 415))))
    draw.line(pts2, fill=GOLD_ACCENT, width=3)
    
    # Critical Point K
    kx, ky = ox + 170, 260
    draw.ellipse([kx - 6, ky - 6, kx + 6, ky + 6], fill=RED_ACCENT, outline=(255, 255, 255), width=2)
    draw.text((kx + 10, ky - 20), "Điểm tới hạn K", font=f_body_sm_b, fill=RED_ACCENT)
    draw.text((ox + 310, 385), "T = Tc", font=f_body_sm_b, fill=GOLD_ACCENT)
    
    # Curve 3: T < Tc (Subcritical: liquid branch -> horizontal coexistence -> vapor branch)
    pts3_liquid = [(ox + 40, 180), (ox + 70, 250), (ox + 95, 345)]
    pts3_tie = [(ox + 95, 345), (ox + 290, 345)] # Maxwell plateau (Lỏng - Hơi cân bằng)
    pts3_vapor = [(ox + 290, 345), (ox + 340, 380), (ox + 405, 410)]
    draw.line(pts3_liquid, fill=(240, 90, 90), width=2)
    draw.line(pts3_tie, fill=AMBER_ACCENT, width=4)
    draw.line(pts3_vapor, fill=(240, 90, 90), width=2)
    draw.text((ox + 120, 355), "Vùng Lỏng - Hơi bão hòa", font=f_body_sm_b, fill=AMBER_ACCENT)
    draw.text((ox + 70, 400), "T < Tc", font=f_body_sm, fill=(240, 90, 90))
    
    # Critical Formulas box below
    draw.text((70, 445), "Thông số tới hạn:  Vc = 3b  |  Pc = a / (27b²)  |  Tc = 8a / (27Rb)", font=f_body_sm_b, fill=GOLD_ACCENT)
    
    # Right Panel: Van der Waals Portrait & Nobel Prize / Outro
    draw.rounded_rectangle([585, 90, 975, 485], radius=14, fill=CARD_BG, outline=GOLD_ACCENT, width=2)
    
    # If in outro (t > 180s), show big subscribe callout
    if t > 180.0:
        draw.rounded_rectangle([605, 105, 955, 140], radius=8, fill=(70, 20, 20))
        draw.text((675, 112), "CẢM ƠN CÁC BẠN ĐÃ THEO DÕI!", font=f_card_title, fill=(255, 255, 255))
        
        # Big Channel Logo
        draw.rounded_rectangle([630, 165, 930, 320], radius=16, fill=(15, 23, 42), outline=CYAN_ACCENT, width=2)
        draw.text((670, 200), "MTSEducation", font=f_math_xl, fill=(255, 255, 255))
        draw.text((655, 255), "Học Khoa Học & Vật Lý Trực Quan", font=f_body_b, fill=CYAN_ACCENT)
        
        draw.rounded_rectangle([650, 345, 910, 400], radius=10, fill=(220, 38, 38))
        draw.text((680, 360), "[!] LIKE & ĐĂNG KÝ KÊNH", font=f_math_md, fill=(255, 255, 255))
        
        draw.text((630, 430), "Chúc các bạn học tập tốt và thành công!", font=f_body, fill=(200, 215, 235))
    else:
        draw.rounded_rectangle([605, 105, 955, 140], radius=8, fill=(30, 45, 70))
        draw.text((660, 112), "JOHANNES D. VAN DER WAALS", font=f_card_title, fill=CYAN_ACCENT)
        
        # Portrait paste
        if portrait_pil:
            px = 705
            py = 155
            # Paste portrait with subtle gold frame
            draw.rounded_rectangle([px - 4, py - 4, px + 154, py + 184], radius=10, fill=(40, 50, 70), outline=GOLD_ACCENT, width=2)
            img.paste(portrait_pil, (px, py))
            
        draw.text((680, 350), "1837 – 1923  (Hà Lan)", font=f_body_b, fill=(220, 230, 245))
        
        draw.rounded_rectangle([615, 380, 945, 460], radius=10, fill=(45, 35, 10), outline=GOLD_ACCENT, width=1)
        draw.text((675, 390), "[NOBEL VẬT LÝ NĂM 1910]", font=f_body_b, fill=GOLD_ACCENT)
        draw.text((635, 415), "Vinh danh công trình phương trình trạng thái", font=f_body_sm, fill=(255, 255, 255))
        draw.text((645, 435), "của chất khí và hiện tượng hóa lỏng.", font=f_body_sm, fill=(200, 215, 235))
        
    draw_subtitle(draw, sub_text)
    return img

def render_frame(frame_idx):
    t = frame_idx / FPS
    sub = get_current_subtitle(t)
    
    # Route to appropriate scene
    if t < 31.74:
        return render_frame_scene1(t, sub)
    elif t < 69.98:
        return render_frame_scene2(t, sub)
    elif t < 115.28:
        return render_frame_scene3(t, sub)
    elif t < 157.18:
        return render_frame_scene4(t, sub)
    else:
        return render_frame_scene5(t, sub)

def main():
    print(f"Starting video render...")
    print(f"Total Duration: {TOTAL_DURATION:.2f}s | FPS: {FPS} | Total Frames: {TOTAL_FRAMES}")
    print(f"Output: {OUTPUT_MP4}")
    
    # Launch ffmpeg process reading raw RGB24 frames from stdin
    temp_video = os.path.join(BUILD_DIR, "video_stream.mp4")
    
    cmd = [
        FFMPEG, "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        temp_video
    ]
    
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    
    print_interval = FPS * 10 # every 10 seconds of video
    for f_idx in range(TOTAL_FRAMES):
        frame_img = render_frame(f_idx)
        raw_bytes = frame_img.tobytes()
        proc.stdin.write(raw_bytes)
        
        if f_idx % print_interval == 0:
            pct = (f_idx / TOTAL_FRAMES) * 100
            print(f"Render progress: {f_idx}/{TOTAL_FRAMES} frames ({pct:.1f}%) | Time: {f_idx/FPS:.1f}s / {TOTAL_DURATION:.1f}s", flush=True)
            
    proc.stdin.close()
    stderr_out = proc.stderr.read().decode('utf-8', errors='ignore')
    proc.wait()
    
    if proc.returncode != 0:
        print("FFmpeg encoding error:", stderr_out)
        return
        
    print("Video track encoded successfully! Now muxing with master audio...")
    
    # Mux video with audio_master.wav
    mux_cmd = [
        FFMPEG, "-y",
        "-i", temp_video,
        "-i", AUDIO_MASTER,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        OUTPUT_MP4
    ]
    subprocess.run(mux_cmd, check=True)
    
    size_mb = os.path.getsize(OUTPUT_MP4) / (1024 * 1024)
    print(f"\n==========================================")
    print(f"🎉 FINAL VIDEO CREATED SUCCESSFULLY!")
    print(f"Path: {OUTPUT_MP4}")
    print(f"Size: {size_mb:.2f} MB | Duration: {TOTAL_DURATION:.2f}s ({TOTAL_DURATION/60:.2f} mins)")
    print(f"==========================================")

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
import os
import sys
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8')

WIDTH = 1024
HEIGHT = 576

# Fonts
FONT_TITLE = "C:/Windows/Fonts/segoeuib.ttf"
FONT_SUB = "C:/Windows/Fonts/ARIALNB.TTF"
FONT_BODY = "C:/Windows/Fonts/segoeui.ttf"
FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_ITALIC = "C:/Windows/Fonts/segoeuii.ttf"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

f_brand = get_font(FONT_BOLD, 22)
f_brand_sub = get_font(FONT_SUB, 15)
f_badge = get_font(FONT_BOLD, 14)
f_title = get_font(FONT_BOLD, 20)
f_card_title = get_font(FONT_BOLD, 17)
f_body = get_font(FONT_BODY, 14)
f_body_b = get_font(FONT_BOLD, 14)
f_math_lg = get_font(FONT_BOLD, 28)
f_math_md = get_font(FONT_BOLD, 20)
f_sub = get_font(FONT_SUB, 24)

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

def draw_header_watermark(draw, scene_badge, title_text="PHƯƠNG TRÌNH VAN DER WAALS"):
    # Brand Top-Left (MTSEducation)
    draw.text((32, 22), "MTSEducation", font=f_brand, fill=(0, 0, 0))
    draw.text((30, 20), "MTSEducation", font=f_brand, fill=(255, 255, 255))
    
    # Secondary tiny watermark bottom right
    draw.text((WIDTH - 120, HEIGHT - 25), "MTSEducation", font=f_brand_sub, fill=(120, 130, 150))
    
    # Header Center Badge
    badge_w = 460
    badge_x = (WIDTH - badge_w) // 2
    # Outer glow
    draw.rounded_rectangle([badge_x - 1, 12, badge_x + badge_w + 1, 52], radius=10, fill=(180, 30, 30))
    draw.rounded_rectangle([badge_x, 13, badge_x + badge_w, 51], radius=9, fill=(220, 38, 38))
    
    bbox_t = draw.textbbox((0, 0), title_text, font=f_title)
    tw = bbox_t[2] - bbox_t[0]
    draw.text((badge_x + (badge_w - tw) // 2, 20), title_text, font=f_title, fill=(255, 255, 255))
    
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
    
    x = (WIDTH - w) // 2
    y = HEIGHT - 65
    
    # Semi-transparent dark backing strip
    draw.rounded_rectangle([x - 18, y - 6, x + w + 18, y + h + 8], radius=8, fill=(10, 10, 15))
    
    # Black outline
    outline_color = (0, 0, 0)
    for ox in [-2, -1, 0, 1, 2]:
        for oy in [-2, -1, 0, 1, 2]:
            if ox != 0 or oy != 0:
                draw.text((x + ox, y + oy), text, font=f_sub, fill=outline_color)
    # Bright Yellow Fill
    draw.text((x, y), text, font=f_sub, fill=(255, 235, 50))

# Test rendering Scene 1 frame
def render_scene_1(t=10.0, sub_text=""):
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(img)
    draw_header_watermark(draw, "PHẦN 1: MÔ HÌNH KHÍ")
    
    # Left Card: Ideal Gas
    draw.rounded_rectangle([45, 90, 495, 480], radius=14, fill=CARD_BG, outline=CYAN_ACCENT, width=2)
    # Header badge inside left card
    draw.rounded_rectangle([65, 105, 475, 140], radius=8, fill=(14, 50, 75))
    draw.text((150, 112), "1. MÔ HÌNH KHÍ LÝ TƯỞNG", font=f_card_title, fill=CYAN_ACCENT)
    
    # Simulation sub-box
    draw.rounded_rectangle([65, 155, 475, 335], radius=10, fill=(10, 15, 25), outline=(30, 45, 65), width=1)
    # Draw point particles
    np.random.seed(42)
    for p_i in range(24):
        px = 80 + int((np.sin(t * 1.5 + p_i * 1.2) * 0.5 + 0.5) * 360)
        py = 170 + int((np.cos(t * 1.8 + p_i * 0.9) * 0.5 + 0.5) * 140)
        draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=CYAN_ACCENT, outline=(255, 255, 255))
    draw.text((185, 235), "P · V = n · R · T", font=f_math_md, fill=(255, 255, 255))
    
    # Bullet points
    draw.text((68, 355), "✓ Phân tử coi như CHẤT ĐIỂM (thể tích V = 0)", font=f_body_b, fill=GREEN_ACCENT)
    draw.text((68, 385), "✓ Hoàn toàn KHÔNG CÓ LỰC HÚT giữa các phân tử", font=f_body_b, fill=GREEN_ACCENT)
    draw.text((68, 415), "✓ Va chạm hoàn toàn đàn hồi với thành bình", font=f_body, fill=(200, 210, 230))
    draw.text((68, 445), "➜ Chỉ đúng ở ÁP SUẤT RẤT THẤP & NHIỆT ĐỘ CAO", font=f_body_b, fill=GOLD_ACCENT)
    
    # Right Card: Real Gas
    draw.rounded_rectangle([525, 90, 975, 480], radius=14, fill=CARD_BG, outline=RED_ACCENT, width=2)
    draw.rounded_rectangle([545, 105, 955, 140], radius=8, fill=(75, 25, 30))
    draw.text((645, 112), "2. MÔ HÌNH KHÍ THỰC TẾ", font=f_card_title, fill=RED_ACCENT)
    
    # Simulation sub-box
    draw.rounded_rectangle([545, 155, 955, 335], radius=10, fill=(10, 15, 25), outline=(55, 30, 35), width=1)
    # Draw real gas finite-size molecules with attraction lines
    np.random.seed(101)
    pts = []
    for p_i in range(12):
        px = 575 + int((np.sin(t * 0.9 + p_i * 1.5) * 0.5 + 0.5) * 340)
        py = 175 + int((np.cos(t * 1.1 + p_i * 1.1) * 0.5 + 0.5) * 130)
        pts.append((px, py))
    # Draw attraction lines between nearby pairs
    for i in range(len(pts)):
        for j in range(i+1, len(pts)):
            dist = math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1])
            if dist < 85:
                draw.line([pts[i], pts[j]], fill=(180, 50, 60), width=1)
    for px, py in pts:
        draw.ellipse([px - 10, py - 10, px + 10, py + 10], fill=(220, 70, 70), outline=(255, 180, 180), width=2)
    draw.text((660, 235), "P · V ≠ n · R · T", font=f_math_md, fill=(255, 180, 180))
    
    # Bullet points
    draw.text((548, 355), "✕ Phân tử có KÍCH THƯỚC HỮU HẠN (bán kính r > 0)", font=f_body_b, fill=RED_ACCENT)
    draw.text((548, 385), "✕ Tồn tại LỰC HÚT LIÊN PHÂN TỬ Van der Waals", font=f_body_b, fill=RED_ACCENT)
    draw.text((548, 415), "✕ Các phân tử cản trở lẫn nhau khi chuyển động", font=f_body, fill=(230, 200, 200))
    draw.text((548, 445), "⚠ SAI LỆCH RẤT LỚN KHI ÁP SUẤT CAO & NHIỆT ĐỘ THẤP!", font=f_body_b, fill=AMBER_ACCENT)
    
    draw_subtitle(draw, sub_text)
    return img

os.makedirs(r"C:\Users\DELL\Documents\CODE\DU_AN\video_build\test_frames", exist_ok=True)
img1 = render_scene_1(5.0, "TRONG CHƯƠNG TRÌNH VẬT LÝ, PHƯƠNG TRÌNH KHÍ LÝ TƯỞNG ĐÃ VÔ CÙNG QUEN THUỘC")
img1.save(r"C:\Users\DELL\Documents\CODE\DU_AN\video_build\test_frames\scene1_preview.jpg", quality=95)
print("Saved scene1_preview.jpg")

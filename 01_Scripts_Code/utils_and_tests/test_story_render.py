# -*- coding: utf-8 -*-
import os
import sys
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8')

WIDTH = 1024
HEIGHT = 576

FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_REG = "C:/Windows/Fonts/segoeui.ttf"

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
f_math_xl = get_font(FONT_BOLD, 28)
f_math_lg = get_font(FONT_BOLD, 22)
f_math_md = get_font(FONT_BOLD, 18)
f_sub = get_font(FONT_BOLD, 22)

# Colors
BG_DARK = (13, 17, 28)
CARD_BG = (20, 27, 42)
CARD_BORDER = (45, 58, 85)
CYAN_ACCENT = (56, 189, 248)
GREEN_ACCENT = (74, 222, 128)
RED_ACCENT = (248, 113, 113)
GOLD_ACCENT = (250, 204, 21)
AMBER_ACCENT = (251, 146, 60)
PURPLE_ACCENT = (192, 132, 252)

# Load real assets
REAL_DIR = r"C:\Users\DELL\Documents\CODE\DU_AN\real_assets"

# Cutout of Van der Waals
vdw_cutout = Image.open(os.path.join(REAL_DIR, "vdw_presenter.png")).convert("RGBA")
# Real Andrews Isotherm
img_andrews = Image.open(os.path.join(REAL_DIR, "Carbon_dioxide_isotherms.png")).convert("RGB")
# Real Lennard-Jones graph
img_lj = Image.open(os.path.join(REAL_DIR, "Graph_of_Lennard-Jones_potential.png")).convert("RGB")
# Real Van der Waals force illustration
img_vdw_force = Image.open(os.path.join(REAL_DIR, "Force_de_van_de_Waals.png")).convert("RGB")
# Real Compressibility Factor
img_z = Image.open(os.path.join(REAL_DIR, "Compressibility_factor.jpg")).convert("RGB")
# Real Nobel Medal
img_nobel = Image.open(os.path.join(REAL_DIR, "nobel_thumb.jpg")).convert("RGB")

def draw_header_watermark(draw, scene_badge, title_text="PHƯƠNG TRÌNH VAN DER WAALS"):
    # Brand Top-Left (MTSEducation)
    draw.text((32, 22), "MTSEducation", font=f_brand, fill=(0, 0, 0))
    draw.text((30, 20), "MTSEducation", font=f_brand, fill=(255, 255, 255))
    
    # Secondary watermark bottom right
    draw.text((WIDTH - 120, HEIGHT - 25), "MTSEducation", font=f_brand_sub, fill=(130, 145, 170))
    
    # Header Center Badge
    badge_w = 460
    badge_x = (WIDTH - badge_w) // 2
    draw.rounded_rectangle([badge_x - 1, 12, badge_x + badge_w + 1, 52], radius=10, fill=(180, 30, 30))
    draw.rounded_rectangle([badge_x, 13, badge_x + badge_w, 51], radius=9, fill=(220, 38, 38))
    
    bbox_t = draw.textbbox((0, 0), title_text, font=f_header_title)
    tw = bbox_t[2] - bbox_t[0]
    draw.text((badge_x + (badge_w - tw) // 2, 20), title_text, font=f_header_title, fill=(255, 255, 255))
    
    # Scene sub-badge
    if scene_badge:
        bbox_sb = draw.textbbox((0, 0), scene_badge, font=f_badge)
        sb_w = bbox_sb[2] - bbox_sb[0] + 16
        draw.rounded_rectangle([30, 52, 30 + sb_w, 74], radius=5, fill=(30, 41, 59), outline=(71, 85, 105), width=1)
        draw.text((38, 55), scene_badge, font=f_badge, fill=CYAN_ACCENT)

def draw_subtitle(draw, text):
    if not text:
        return
    text = text.upper()
    max_w = WIDTH - 60
    lines = [text]
    bbox = draw.textbbox((0, 0), text, font=f_sub)
    if (bbox[2] - bbox[0]) > max_w:
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
        
        draw.rounded_rectangle([x - 14, y - 4, x + lw + 14, y + line_h - 2], radius=6, fill=(10, 10, 15))
        for ox in [-2, -1, 0, 1, 2]:
            for oy in [-2, -1, 0, 1, 2]:
                if ox != 0 or oy != 0:
                    draw.text((x + ox, y + oy), line, font=f_sub, fill=(0, 0, 0))
        draw.text((x, y), line, font=f_sub, fill=(255, 235, 50))

def draw_van_der_waals_pointer(img, draw, target_point, scale=0.32, pos=(750, 190)):
    """
    Renders the real Van der Waals cutout and draws his golden pointer stick
    pointing directly at target_point (tx, ty).
    """
    # Scale Van der Waals cutout
    pw = int(vdw_cutout.width * scale)
    ph = int(vdw_cutout.height * scale)
    vdw_scaled = vdw_cutout.resize((pw, ph), Image.Resampling.LANCZOS)
    
    # Hand origin roughly on chest/shoulder
    hx = pos[0] + int(pw * 0.32)
    hy = pos[1] + int(ph * 0.65)
    
    # Paste presenter
    img.paste(vdw_scaled, pos, vdw_scaled)
    
    # Name Tag under presenter
    draw.rounded_rectangle([pos[0] + 10, pos[1] + ph - 25, pos[0] + pw - 10, pos[1] + ph + 2], radius=5, fill=(15, 23, 42), outline=GOLD_ACCENT, width=1)
    draw.text((pos[0] + 25, pos[1] + ph - 22), "J. D. van der Waals", font=f_body_sm_b, fill=(255, 255, 255))
    
    # Pointer Stick (Golden rod extending from hand to target)
    tx, ty = target_point
    draw.line([(hx, hy), (tx, ty)], fill=GOLD_ACCENT, width=4)
    # Glowing tip
    draw.ellipse([tx - 6, ty - 6, tx + 6, ty + 6], fill=(255, 255, 255), outline=RED_ACCENT, width=2)
    # Laser / focus pulse ring
    draw.ellipse([tx - 12, ty - 12, tx + 12, ty + 12], outline=RED_ACCENT, width=2)

# Test rendering Scene 1 (The Real Gas Dilemma & Real Z Compressibility Chart)
def render_test_scene1():
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(img)
    draw_header_watermark(draw, "PHẦN 1: NGHỊCH LÝ KHÍ THỰC")
    
    # Left Card: Real Scientific Diagram (Compressibility Factor Z)
    draw.rounded_rectangle([45, 90, 520, 485], radius=14, fill=CARD_BG, outline=CARD_BORDER, width=2)
    draw.rounded_rectangle([65, 105, 500, 140], radius=8, fill=(18, 40, 65))
    draw.text((110, 112), "SỰ SAI LỆCH CỦA KHÍ THỰC (HỆ SỐ Z)", font=f_card_title, fill=CYAN_ACCENT)
    
    # Paste Real Diagram: Compressibility_factor
    z_w, z_h = 210, 310
    z_scaled = img_z.resize((z_w, z_h), Image.Resampling.LANCZOS)
    draw.rounded_rectangle([65, 155, 65 + z_w + 4, 155 + z_h + 4], radius=8, fill=(255, 255, 255), outline=CYAN_ACCENT, width=2)
    img.paste(z_scaled, (67, 157))
    
    # Annotations next to real diagram
    draw.text((295, 175), "• Khí lý tưởng: Z = 1", font=f_body_b, fill=GREEN_ACCENT)
    draw.text((295, 200), "  (Không kích thước, không lực hút)", font=f_body_sm, fill=(200, 215, 235))
    
    draw.text((295, 255), "• Áp suất vừa: Z < 1", font=f_body_b, fill=RED_ACCENT)
    draw.text((295, 280), "  -> Lực hút chiếm ưu thế", font=f_body_sm, fill=(240, 180, 180))
    
    draw.text((295, 345), "• Áp suất cao: Z > 1", font=f_body_b, fill=AMBER_ACCENT)
    draw.text((295, 370), "  -> Thể tích phân tử cản trở", font=f_body_sm, fill=(255, 220, 180))
    
    draw.text((70, 480 - 15), "[!] Định luật PV = nRT thất bại khi áp suất tăng cao!", font=f_body_sm_b, fill=GOLD_ACCENT)
    
    # Right Side: Van der Waals steps in and points!
    draw.rounded_rectangle([545, 90, 975, 485], radius=14, fill=CARD_BG, outline=GOLD_ACCENT, width=2)
    draw.rounded_rectangle([565, 105, 955, 140], radius=8, fill=(50, 35, 15))
    draw.text((610, 112), "NHÀ VẬT LÝ VÀO CUỘC (NĂM 1873)", font=f_card_title, fill=GOLD_ACCENT)
    
    draw.text((565, 155), "Johannes Diderik van der Waals phát hiện:", font=f_body, fill=(220, 230, 245))
    draw.text((565, 180), "1. Phân tử có kích thước thật -> Cần trừ b", font=f_body_b, fill=GREEN_ACCENT)
    draw.text((565, 205), "2. Giữa các hạt có lực hút -> Cần bù áp suất a", font=f_body_b, fill=AMBER_ACCENT)
    
    # Van der Waals pointer pointing to the Z < 1 strong interaction zone!
    target = (280, 285)
    draw_van_der_waals_pointer(img, draw, target, scale=0.36, pos=(670, 225))
    
    draw_subtitle(draw, "NHƯNG Ở ĐIỀU KIỆN ÁP SUẤT CAO, KHÍ THỰC BỘC LỘ SAI LỆCH RẤT LỚN SO VỚI LÝ THUYẾT!")
    img.save(r"C:\Users\DELL\Documents\CODE\DU_AN\real_assets\test_scene1_story.jpg", quality=95)
    print("Saved test_scene1_story.jpg!")

render_test_scene1()

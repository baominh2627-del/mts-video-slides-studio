# -*- coding: utf-8 -*-
import os
import sys
import math
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8')

WIDTH = 1312
HEIGHT = 1199

FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_REG = "C:/Windows/Fonts/segoeui.ttf"
FONT_ITALIC = "C:/Windows/Fonts/segoeuii.ttf"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

f_tag = get_font(FONT_BOLD, 38)
f_title_sub = get_font(FONT_BOLD, 85)
f_title_main = get_font(FONT_BOLD, 125)
f_math_lg = get_font(FONT_BOLD, 36)
f_math_md = get_font(FONT_BOLD, 30)
f_math_sm = get_font(FONT_BOLD, 26)
f_name = get_font(FONT_BOLD, 28)
f_brand = get_font(FONT_BOLD, 32)
f_brand_sub = get_font(FONT_BOLD, 20)

# Create pastel gradient background (clean light cyan / lilac)
img = Image.new("RGB", (WIDTH, HEIGHT), (255, 255, 255))
draw = ImageDraw.Draw(img)

# Soft gradient
for y in range(HEIGHT):
    factor_y = y / HEIGHT
    # Top: very faint soft cyan (245, 250, 255) -> Bottom: very faint soft purple/pink (248, 245, 255)
    r = int(245 + 5 * factor_y)
    g = int(248 - 5 * factor_y)
    b = int(255)
    draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

# Subtle decorative pastel blobs in background
# Top right soft cyan blob
draw.ellipse([WIDTH - 380, -80, WIDTH + 150, 420], fill=(230, 245, 255))
# Bottom left soft violet blob
draw.ellipse([-100, HEIGHT - 350, 400, HEIGHT + 150], fill=(245, 235, 255))

# Top-Left Tag: - Nhiệt động lực học -
tag_text = "- Nhiệt động lực học -"
draw.text((80, 55), tag_text, font=f_tag, fill=(45, 110, 230))
# Doodle lines next to tag
draw.line([(55, 52), (40, 45)], fill=(45, 110, 230), width=4)
draw.line([(55, 75), (35, 80)], fill=(45, 110, 230), width=4)

# Top-Right Doodle: Molecular cluster field lines
center_doodle = (WIDTH - 150, 110)
for r_i in [25, 45, 65]:
    draw.ellipse([center_doodle[0] - r_i, center_doodle[1] - r_i, center_doodle[0] + r_i, center_doodle[1] + r_i], outline=(100, 150, 245), width=3)
draw.ellipse([center_doodle[0] - 12, center_doodle[1] - 12, center_doodle[0] + 12, center_doodle[1] + 12], fill=(45, 110, 230))

# Main Title:
# Line 1: "Phương trình"
draw.text((260, 160), "Phương trình", font=f_title_sub, fill=(15, 30, 65))

# Brush stroke highlight behind "Van der Waals"
brush_x = 180
brush_y = 295
brush_w = 950
brush_h = 145
draw.rounded_rectangle([brush_x, brush_y, brush_x + brush_w, brush_y + brush_h], radius=35, fill=(195, 225, 255))

# Line 2: "Van der Waals"
draw.text((205, 290), "Van der Waals", font=f_title_main, fill=(10, 20, 50))

# Left Side: System of Equations
eq_x = 120
eq_y = 510

# Big Curly Bracket "{"
bracket_x = eq_x - 40
draw.line([(bracket_x, eq_y), (bracket_x, eq_y + 115)], fill=(15, 30, 65), width=5)
draw.line([(bracket_x - 15, eq_y + 115), (bracket_x, eq_y + 115)], fill=(15, 30, 65), width=5)
draw.line([(bracket_x, eq_y + 115), (bracket_x, eq_y + 230)], fill=(15, 30, 65), width=5)

# Equation 1: (P + a/V^2)(V - b) = RT
draw.text((eq_x, eq_y), "( P + a / V² ) · ( V - b ) = R · T", font=f_math_lg, fill=(15, 30, 65))

# Equation 2: Pc = a / (27 b^2)
draw.text((eq_x, eq_y + 65), "Pc = a / ( 27 · b² )", font=f_math_md, fill=(15, 30, 65))

# Equation 3: Vc = 3b
draw.text((eq_x, eq_y + 125), "Vc = 3 · b", font=f_math_md, fill=(15, 30, 65))

# Equation 4: Tc = 8a / (27 R b)
draw.text((eq_x, eq_y + 185), "Tc = 8 · a / ( 27 · R · b )", font=f_math_md, fill=(15, 30, 65))

# Bottom Left Illustration: Cute molecular diagram & P-V curve
draw.rounded_rectangle([100, 800, 560, 1080], radius=20, fill=(255, 255, 255), outline=(210, 225, 245), width=3)
# Sub-title
draw.text((140, 820), "Mô hình Khí thực & Điểm tới hạn", font=f_math_sm, fill=(45, 110, 230))

# Two attracting spheres
s1x, s1y = 220, 930
s2x, s2y = 440, 930
sr = 45
# Exclusion zone
draw.ellipse([s1x - sr*1.5, s1y - sr*1.5, s1x + sr*1.5, s1y + sr*1.5], fill=(235, 245, 255), outline=(100, 160, 250), width=2)
# Sphere 1
draw.ellipse([s1x - sr, s1y - sr, s1x + sr, s1y + sr], fill=(59, 130, 246), outline=(30, 64, 175), width=3)
draw.text((s1x - 14, s1y - 15), "b", font=f_math_md, fill=(255, 255, 255))

# Sphere 2
draw.ellipse([s2x - sr, s2y - sr, s2x + sr, s2y + sr], fill=(239, 68, 68), outline=(185, 28, 28), width=3)
draw.text((s2x - 14, s2y - 15), "a", font=f_math_md, fill=(255, 255, 255))

# Attraction arrows pointing to each other
draw.line([(s1x + sr + 8, s1y), (s2x - sr - 8, s1y)], fill=(220, 38, 38), width=4)
# Arrowheads
draw.polygon([(s1x + sr + 18, s1y - 8), (s1x + sr + 8, s1y), (s1x + sr + 18, s1y + 8)], fill=(220, 38, 38))
draw.polygon([(s2x - sr - 18, s1y - 8), (s2x - sr - 8, s1y), (s2x - sr - 18, s1y + 8)], fill=(220, 38, 38))
draw.text((285, 895), "Lực hút a", font=f_name, fill=(220, 38, 38))
draw.text((160, 1010), "Thể tích riêng b  +  Lực hút a/V²", font=f_math_sm, fill=(15, 30, 65))

# Right Side: Portrait of Johannes Diderik van der Waals
portrait_path = r"C:\Users\DELL\Documents\CODE\DU_AN\video_build\vanderwaals.jpg"
if os.path.exists(portrait_path):
    p_img = Image.open(portrait_path).convert("RGBA")
    # Resize portrait to nice size
    pw, ph = 480, 560
    p_resized = p_img.resize((pw, ph), Image.Resampling.LANCZOS)
    
    # Create soft oval mask
    mask = Image.new("L", (pw, ph), 0)
    d_mask = ImageDraw.Draw(mask)
    d_mask.ellipse([10, 10, pw - 10, ph - 10], fill=255)
    
    # Soften mask edges with gaussian blur
    from PIL import ImageFilter
    mask = mask.filter(ImageFilter.GaussianBlur(12))
    
    pos_x = WIDTH - 580
    pos_y = 510
    
    # Decorative backing circle
    draw.ellipse([pos_x - 15, pos_y - 15, pos_x + pw + 15, pos_y + ph + 15], fill=(225, 240, 255), outline=(180, 210, 245), width=3)
    
    img.paste(p_resized, (pos_x, pos_y), mask)
    
    # Label: Johannes Clerk Maxwell style -> "Johannes D. van der Waals"
    label_x = WIDTH - 430
    label_y = 460
    draw.text((label_x, label_y), "Johannes D. van der Waals", font=f_name, fill=(15, 30, 65))
    # Curved arrow pointing to portrait
    draw.arc([label_x + 140, label_y + 35, label_x + 190, label_y + 85], start=180, end=320, fill=(45, 110, 230), width=3)

# Bottom-Right Watermark / Channel Badge: MTSEducation
draw.rounded_rectangle([WIDTH - 360, HEIGHT - 95, WIDTH - 50, HEIGHT - 35], radius=15, fill=(15, 23, 42))
draw.text((WIDTH - 335, HEIGHT - 85), "MTSEducation", font=f_brand, fill=(255, 255, 255))

# Save cover image
out1 = r"C:\Users\DELL\Documents\CODE\DU_AN\ẢNH BÌA TT_PHƯƠNG TRÌNH VAN DER WAALS.png"
out2 = r"C:\Users\DELL\Documents\Downloads\ẢNH BÌA TT_PHƯƠNG TRÌNH VAN DER WAALS.png"
img.save(out1, quality=95)
img.save(out2, quality=95)
print("Saved cover image to both locations successfully!")

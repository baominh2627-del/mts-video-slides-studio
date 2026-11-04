import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# 1. Base image from video (e.g. frame_5s or frame_60s where lattice is beautiful)
base_bgr = cv2.imread(r'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\frame_5s.jpg')
# Clean seam in base image
c_left = base_bgr[15:140, 66].astype(float)
c_right = base_bgr[15:140, 84].astype(float)
for x in range(67, 84):
    alpha = (x - 66) / (84.0 - 66.0)
    base_bgr[15:140, x] = np.clip(c_left * (1.0 - alpha) + c_right * alpha, 0, 255).astype(np.uint8)

# Resize to 1080x1920
base_1080 = cv2.resize(base_bgr, (1080, 1920), interpolation=cv2.INTER_CUBIC)

# Convert to PIL
im_base = Image.fromarray(cv2.cvtColor(base_1080, cv2.COLOR_BGR2RGB))

# Apply subtle dark vignette overlay for readability while keeping the 3D lattice visible
vignette = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
v_draw = ImageDraw.Draw(vignette)

# Gradient dark overlays at top and bottom
for y in range(1920):
    # Top gradient
    if y < 450:
        a = int(220 * (1.0 - y / 450.0))
        v_draw.line([(0, y), (1080, y)], fill=(10, 15, 29, a))
    # Bottom gradient
    elif y > 1150:
        a = int(240 * ((y - 1150) / (1920 - 1150)))
        v_draw.line([(0, y), (1080, y)], fill=(10, 15, 29, a))

im_comp = Image.alpha_composite(im_base.convert('RGBA'), vignette)

draw = ImageDraw.Draw(im_comp)

# Fonts
font_bold = r'C:\Windows\Fonts\segoeuib.ttf'
font_reg = r'C:\Windows\Fonts\segoeui.ttf'

f_cat = ImageFont.truetype(font_bold, 28)
f_title_big = ImageFont.truetype(font_bold, 86)
f_hook = ImageFont.truetype(font_bold, 32)
f_hook_sub = ImageFont.truetype(font_bold, 26)
f_formula = ImageFont.truetype(font_bold, 54)
f_formula_sub = ImageFont.truetype(font_reg, 24)
f_brand = ImageFont.truetype(font_bold, 36)

# Helper function to draw centered text with deep glow/shadow
def draw_centered_text(y, text, font, fill_color, shadow_color=(0, 0, 0, 220), shadow_offset=4):
    tw = draw.textlength(text, font=font)
    x = (1080 - tw) // 2
    if shadow_color:
        for dx, dy in [(-shadow_offset, 0), (shadow_offset, 0), (0, -shadow_offset), (0, shadow_offset), 
                      (shadow_offset, shadow_offset), (-shadow_offset, shadow_offset)]:
            draw.text((x + dx, y + dy), text, font=font, fill=shadow_color)
    draw.text((x, y), text, font=font, fill=fill_color)
    return tw

# 1. Top Channel & Subject Badge
# Box: [x: 180, y: 160, w: 720, h: 70]
badge_w, badge_h = 760, 72
bx = (1080 - badge_w) // 2
by = 160
draw.rounded_rectangle([bx, by, bx + badge_w, by + badge_h], radius=36, fill=(15, 23, 42, 230), outline=(56, 189, 248, 255), width=2)
# Cyan dot
draw.ellipse([bx + 26, by + 26, bx + 46, by + 46], fill=(56, 189, 248, 255))
# Text
header_str = "VẬT LÝ 12  ·  MTSEducation"
hw = draw.textlength(header_str, font=f_cat)
draw.text((bx + (badge_w - hw) // 2 + 15, by + 18), header_str, font=f_cat, fill=(255, 255, 255))

# 2. Eye-Catching Hook Pill
hook_w, hook_h = 720, 58
hx = (1080 - hook_w) // 2
hy = 265
draw.rounded_rectangle([hx, hy, hx + hook_w, hy + hook_h], radius=16, fill=(239, 68, 68, 240)) # Vibrant coral red badge
hook_str = "⚡ 3 KHÁI NIỆM DỄ NHẦM LẪN NHẤT ⚡"
hkw = draw.textlength(hook_str, font=f_hook_sub)
draw.text((hx + (hook_w - hkw) // 2, hy + 13), hook_str, font=f_hook_sub, fill=(255, 255, 255))

# 3. Big Titles (placed below the 3D lattice in the video frame, y ≈ 1120)
# Notice in original video: "NHIỆT LƯỢNG", "NHIỆT NĂNG", "NỘI NĂNG" are below the lattice!
# Let's inspect coordinates so they match perfectly
draw_centered_text(1080, "NHIỆT LƯỢNG", f_title_big, (250, 204, 21))   # Glowing Gold
draw_centered_text(1185, "NHIỆT NĂNG", f_title_big, (251, 146, 60))    # Vibrant Orange
draw_centered_text(1290, "NỘI NĂNG", f_title_big, (56, 189, 248))      # Electric Cyan

# 4. Sub-hook: "Hiểu đúng bản chất — Chinh phục điểm 9+ Vật Lý"
sh_text = "Hiểu đúng bản chất — Chinh phục điểm 9+"
draw_centered_text(1415, sh_text, ImageFont.truetype(font_reg, 32), (226, 232, 240))

# 5. Core Formula Glass Card: ΔU = A + Q
cw, ch = 740, 160
cx = (1080 - cw) // 2
cy = 1490
draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=24, fill=(15, 23, 42, 230), outline=(56, 189, 248, 220), width=2)

form_title = "NGUYÊN LÍ I NHIỆT ĐỘNG LỰC HỌC"
fw = draw.textlength(form_title, font=ImageFont.truetype(font_bold, 22))
draw.text((cx + (cw - fw) // 2, cy + 20), form_title, font=ImageFont.truetype(font_bold, 22), fill=(148, 163, 184))

form_eq = "ΔU = A + Q"
few = draw.textlength(form_eq, font=ImageFont.truetype(font_bold, 60))
draw.text((cx + (cw - few) // 2, cy + 58), form_eq, font=ImageFont.truetype(font_bold, 60), fill=(255, 255, 255))

# 6. Bottom Creator Tag
bot_text = "Kênh kiến thức trực quan: MTSEducation"
bw = draw.textlength(bot_text, font=ImageFont.truetype(font_bold, 26))
draw.text(((1080 - bw) // 2, 1720), bot_text, font=ImageFont.truetype(font_bold, 26), fill=(56, 189, 248))

im_final = im_comp.convert('RGB')
im_final.save(r'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\test_cover_v1.jpg', quality=95)
print('Saved test_cover_v1.jpg')

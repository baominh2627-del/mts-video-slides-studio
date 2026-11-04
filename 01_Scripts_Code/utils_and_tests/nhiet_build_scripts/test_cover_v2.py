import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Load frame_5s (which has the gorgeous 3D lattice in the top half)
base = cv2.imread(r'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\frame_5s.jpg')

# Clean seam on top left
c_left = base[15:140, 66].astype(float)
c_right = base[15:140, 84].astype(float)
for x in range(67, 84):
    alpha = (x - 66) / (84.0 - 66.0)
    base[15:140, x] = np.clip(c_left * (1.0 - alpha) + c_right * alpha, 0, 255).astype(np.uint8)

# Resize to 1080x1920
base_1080 = cv2.resize(base, (1080, 1920), interpolation=cv2.INTER_CUBIC)
im = Image.fromarray(cv2.cvtColor(base_1080, cv2.COLOR_BGR2RGB))
draw = ImageDraw.Draw(im)

# Notice: In 1080x1920, the 3D lattice is at y: [350, 1100]
# Below y = 1100, the old text in frame_5s was located!
# Let's paint a smooth deep navy backdrop from y = 1080 downwards to completely cover old text!
# And top gradient above y = 340 to cover old top text ("VẬT LÝ 12 · NHIỆT HỌC")!

# Top cover: y = 0 to 350
top_overlay = Image.new('RGBA', (1080, 350), (10, 15, 29, 255))
# Bottom cover: y = 1080 to 1920
bot_overlay = Image.new('RGBA', (1080, 1920 - 1080), (10, 15, 29, 255))

im.paste(top_overlay, (0, 0))
im.paste(bot_overlay, (0, 1080))

# Smooth transition gradients so there are no hard cuts
draw = ImageDraw.Draw(im)
# Top transition
for y in range(300, 370):
    alpha = int(255 * (1.0 - (y - 300) / 70.0))
    draw.line([(0, y), (1080, y)], fill=(10, 15, 29, alpha))

# Bottom transition
for y in range(1040, 1100):
    alpha = int(255 * ((y - 1040) / 60.0))
    draw.line([(0, y), (1080, y)], fill=(10, 15, 29, alpha))

# Now let's draw the clean typography!
font_bold = r'C:\Windows\Fonts\segoeuib.ttf'
font_reg = r'C:\Windows\Fonts\segoeui.ttf'

f_cat = ImageFont.truetype(font_bold, 30)
f_hook = ImageFont.truetype(font_bold, 28)
f_title_big = ImageFont.truetype(font_bold, 92)
f_sub = ImageFont.truetype(font_reg, 32)
f_formula_h = ImageFont.truetype(font_bold, 24)
f_formula_eq = ImageFont.truetype(font_bold, 64)
f_brand = ImageFont.truetype(font_bold, 28)

# 1. Header Badge: [x: 180, y: 140, w: 720, h: 74]
bw, bh = 720, 74
bx = (1080 - bw) // 2
by = 130
draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=37, fill=(18, 26, 47), outline=(56, 189, 248), width=2)
# Cyan dot
draw.ellipse([bx + 30, by + 27, bx + 50, by + 47], fill=(56, 189, 248))
# Text
h_text = "VẬT LÝ 12  ·  MTSEducation"
hw = draw.textlength(h_text, font=f_cat)
draw.text((bx + (bw - hw) // 2 + 15, by + 18), h_text, font=f_cat, fill=(255, 255, 255))

# 2. Viral Catchy Hook Tag
hk_w, hk_h = 700, 56
hk_x = (1080 - hk_w) // 2
hk_y = 230
draw.rounded_rectangle([hk_x, hk_y, hk_x + hk_w, hk_y + hk_h], radius=16, fill=(239, 68, 68))
hk_text = "3 KHÁI NIỆM HAY BỊ NHẦM LẪN NHẤT"
hkw = draw.textlength(hk_text, font=f_hook)
draw.text((hk_x + (hk_w - hkw) // 2, hk_y + 11), hk_text, font=f_hook, fill=(255, 255, 255))

# 3. Main Titles (Centered, Big, Impactful)
def draw_title(y, text, fill_col):
    tw = draw.textlength(text, font=f_title_big)
    x = (1080 - tw) // 2
    # shadow
    for dx, dy in [(-3,0),(3,0),(0,-3),(0,3),(3,3),(-3,3)]:
        draw.text((x + dx, y + dy), text, font=f_title_big, fill=(0, 0, 0))
    draw.text((x, y), text, font=f_title_big, fill=fill_col)

draw_title(1110, "NHIỆT LƯỢNG", (250, 204, 21))   # Yellow Gold
draw_title(1220, "NHIỆT NĂNG", (251, 146, 60))    # Sunset Orange
draw_title(1330, "NỘI NĂNG", (56, 189, 248))      # Cyan Blue

# 4. Subtitle
sub_text = "Hiểu đúng bản chất — Chinh phục điểm 9+"
sw = draw.textlength(sub_text, font=f_sub)
draw.text(((1080 - sw) // 2, 1460), sub_text, font=f_sub, fill=(203, 213, 225))

# 5. Equation Card: Delta U = A + Q
cw, ch = 760, 160
cx = (1080 - cw) // 2
cy = 1530
draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=24, fill=(18, 26, 47), outline=(56, 189, 248), width=2)

eq_title = "NGUYÊN LÍ I NHIỆT ĐỘNG LỰC HỌC"
etw = draw.textlength(eq_title, font=f_formula_h)
draw.text((cx + (cw - etw) // 2, cy + 22), eq_title, font=f_formula_h, fill=(148, 163, 184))

eq_val = "ΔU = A + Q"
eqw = draw.textlength(eq_val, font=f_formula_eq)
draw.text((cx + (cw - eqw) // 2, cy + 62), eq_val, font=f_formula_eq, fill=(255, 255, 255))

# 6. Bottom Brand Footer
ft_text = "Học Vật Lý Dễ Dàng Cùng MTSEducation"
ftw = draw.textlength(ft_text, font=f_brand)
draw.text(((1080 - ftw) // 2, 1740), ft_text, font=f_brand, fill=(56, 189, 248))

im.save(r'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\test_cover_v2.jpg', quality=95)
print('Saved test_cover_v2.jpg')

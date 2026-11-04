import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Load frame where D chambers and spiral are displayed (e.g. frame_99pct_234.9s or frame_0pct)
base = cv2.imread(r'C:\Users\DELL\Documents\CODE\DU_AN\fdown_build\frame_99pct_234.9s.jpg')

# Clean top-left logo and bottom text from base
base[35:125, 35:135] = base[20:35, 35:135].mean(axis=(0,1))
base[955:992, 40:536] = base[935:950, 40:536].mean(axis=(0,1))

# Resize to 1080x1920
base_1080 = cv2.resize(base, (1080, 1920), interpolation=cv2.INTER_CUBIC)
im = Image.fromarray(cv2.cvtColor(base_1080, cv2.COLOR_BGR2RGB))

# In 1080x1920, the D chamber illustration is in the upper-middle area (y: 350 to 950)
# Below y = 1000 in frame_99pct was "HỌC VẬT LÝ HAY MỖI NGÀY / THẢ TIM..."
# We cover y: 1000 to 1920 with a smooth dark backdrop for our clean typography & formula cards!
# And top y: 0 to 320 for header badge!

top_overlay = Image.new('RGBA', (1080, 320), (10, 15, 29, 255))
bot_overlay = Image.new('RGBA', (1080, 1920 - 1000), (10, 15, 29, 255))
im.paste(top_overlay, (0, 0))
im.paste(bot_overlay, (0, 1000))

draw = ImageDraw.Draw(im)
# Gradient transitions
for y in range(270, 340):
    alpha = int(255 * (1.0 - (y - 270) / 70.0))
    draw.line([(0, y), (1080, y)], fill=(10, 15, 29, alpha))

for y in range(960, 1020):
    alpha = int(255 * ((y - 960) / 60.0))
    draw.line([(0, y), (1080, y)], fill=(10, 15, 29, alpha))

# Fonts
font_bold = r'C:\Windows\Fonts\segoeuib.ttf'
font_reg = r'C:\Windows\Fonts\segoeui.ttf'

f_cat = ImageFont.truetype(font_bold, 30)
f_hook = ImageFont.truetype(font_bold, 28)
f_title_big = ImageFont.truetype(font_bold, 92)
f_sub = ImageFont.truetype(font_reg, 32)
f_formula_h = ImageFont.truetype(font_bold, 24)
f_formula_eq = ImageFont.truetype(font_bold, 50)
f_brand = ImageFont.truetype(font_bold, 28)

# 1. Header Badge: [x: 180, y: 130, w: 720, h: 74]
bw, bh = 720, 74
bx = (1080 - bw) // 2
by = 130
draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=37, fill=(18, 26, 47), outline=(56, 189, 248), width=2)
draw.ellipse([bx + 30, by + 27, bx + 50, by + 47], fill=(56, 189, 248))
h_text = "VẬT LÝ 12  ·  MTSEducation"
hw = draw.textlength(h_text, font=f_cat)
draw.text((bx + (bw - hw) // 2 + 15, by + 18), h_text, font=f_cat, fill=(255, 255, 255))

# 2. Viral Catchy Hook Tag
hk_w, hk_h = 700, 56
hk_x = (1080 - hk_w) // 2
hk_y = 230
draw.rounded_rectangle([hk_x, hk_y, hk_x + hk_w, hk_y + hk_h], radius=16, fill=(239, 68, 68))
hk_text = "DẠNG BÀI TRỌNG TÂM · ĐÚNG / SAI"
hkw = draw.textlength(hk_text, font=f_hook)
draw.text((hk_x + (hk_w - hkw) // 2, hk_y + 11), hk_text, font=f_hook, fill=(255, 255, 255))

# 3. Main Big Titles (Centered, Color-Coded)
def draw_title(y, text, fill_col):
    tw = draw.textlength(text, font=f_title_big)
    x = (1080 - tw) // 2
    for dx, dy in [(-3,0),(3,0),(0,-3),(0,3),(3,3),(-3,3)]:
        draw.text((x + dx, y + dy), text, font=f_title_big, fill=(0, 0, 0))
    draw.text((x, y), text, font=f_title_big, fill=fill_col)

draw_title(1040, "MÁY GIA TỐC", (250, 204, 21))   # Yellow Gold
draw_title(1150, "CYCLOTRON", (56, 189, 248))     # Cyan Blue
draw_title(1260, "HẠT DEUTERON", (251, 146, 60))  # Sunset Orange

# 4. Subtitle
sub_text = "Nguyên lý tăng tốc hạt trong điện trường & từ trường"
sw = draw.textlength(sub_text, font=f_sub)
draw.text(((1080 - sw) // 2, 1385), sub_text, font=f_sub, fill=(203, 213, 225))

# 5. Core Formula Card: Wd = n.qU & R = mv / qB
cw, ch = 800, 190
cx = (1080 - cw) // 2
cy = 1460
draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=24, fill=(18, 26, 47), outline=(56, 189, 248), width=2)

eq_title = "CÔNG THỨC CỐT LÕI CYCLOTRON"
etw = draw.textlength(eq_title, font=f_formula_h)
draw.text((cx + (cw - etw) // 2, cy + 20), eq_title, font=f_formula_h, fill=(148, 163, 184))

eq_val1 = "A = qU   ·   Wđ = n · qU"
eqw1 = draw.textlength(eq_val1, font=f_formula_eq)
draw.text((cx + (cw - eqw1) // 2, cy + 62), eq_val1, font=f_formula_eq, fill=(255, 255, 255))

eq_val2 = "Bán kính cực đại:  R = m·v / (q·B)"
eqw2 = draw.textlength(eq_val2, font=ImageFont.truetype(font_bold, 30))
draw.text((cx + (cw - eqw2) // 2, cy + 130), eq_val2, font=ImageFont.truetype(font_bold, 30), fill=(56, 189, 248))

# 6. Bottom Brand Footer
ft_text = "Học Vật Lý Dễ Dàng Cùng MTSEducation"
ftw = draw.textlength(ft_text, font=f_brand)
draw.text(((1080 - ftw) // 2, 1720), ft_text, font=f_brand, fill=(56, 189, 248))

im.save(r'C:\Users\DELL\Documents\CODE\DU_AN\fdown_build\test_cover_cyclotron.jpg', quality=95)
print("Saved test_cover_cyclotron.jpg")

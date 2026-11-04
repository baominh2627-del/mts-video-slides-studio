import os, sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
draw = ImageDraw.Draw(overlay)

# 1. Top-left badge: MTSEducation
badge_font = ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf', 30)
badge_text = "MTSEducation"
bbox = badge_font.getbbox(badge_text)
bw = bbox[2] - bbox[0] + 46
bh = bbox[3] - bbox[1] + 24
bx, by = 40, 60

# Dark rounded badge with cyan dot & border
draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=18, fill=(15, 23, 42, 220), outline=(56, 189, 248, 255), width=2)
# Cyan glow dot
draw.ellipse([bx + 14, by + 13, bx + 26, by + 25], fill=(56, 189, 248, 255))
draw.text((bx + 34, by + 9), badge_text, fill=(255, 255, 255, 255), font=badge_font)

# 2. Main subtitle text:
# "-Web luyện đề ĐGNL, TSA, THPT"
# "Hoàn Toàn MIỄN PHÍ !!!!! 😳😳"
font_path = r'C:\Windows\Fonts\arialbd.ttf'
font_size = 50
font = ImageFont.truetype(font_path, font_size)

line1 = "-Web luyện đề ĐGNL, TSA, THPT"
line2_text = "Hoàn Toàn MIỄN PHÍ !!!!! "
emojis = "😳😳"

emoji_font = ImageFont.truetype(r'C:\Windows\Fonts\seguiemj.ttf', font_size - 4)

b1 = font.getbbox(line1)
w1 = b1[2] - b1[0]
h1 = b1[3] - b1[1]

b2 = font.getbbox(line2_text)
w2_txt = b2[2] - b2[0]
b_em = emoji_font.getbbox(emojis)
w_em = b_em[2] - b_em[0]
w2_total = w2_txt + w_em

# Center of text at Y = 1530
y_center = 1530
y1 = y_center - h1 - 15
x1 = (W - w1) // 2

# Draw stroke for Line 1
stroke_w = 4
for dx in range(-stroke_w, stroke_w + 1):
    for dy in range(-stroke_w, stroke_w + 1):
        if dx*dx + dy*dy <= stroke_w*stroke_w:
            draw.text((x1 + dx, y1 + dy), line1, font=font, fill=(0, 0, 0, 255))
draw.text((x1, y1), line1, font=font, fill=(255, 255, 255, 255))

# Underline Line 1
ul1_y = y1 + h1 + 12
draw.line([(x1 - 4, ul1_y), (x1 + w1 + 4, ul1_y)], fill=(0, 0, 0, 255), width=6)
draw.line([(x1 - 2, ul1_y), (x1 + w1 + 2, ul1_y)], fill=(255, 255, 255, 255), width=3)

# Line 2
y2 = y1 + h1 + 38
x2 = (W - w2_total) // 2

for dx in range(-stroke_w, stroke_w + 1):
    for dy in range(-stroke_w, stroke_w + 1):
        if dx*dx + dy*dy <= stroke_w*stroke_w:
            draw.text((x2 + dx, y2 + dy), line2_text, font=font, fill=(0, 0, 0, 255))
draw.text((x2, y2), line2_text, font=font, fill=(255, 255, 255, 255))

# Underline Line 2
ul2_y = y2 + h1 + 12
draw.line([(x2 - 4, ul2_y), (x2 + w2_txt + 4, ul2_y)], fill=(0, 0, 0, 255), width=6)
draw.line([(x2 - 2, ul2_y), (x2 + w2_txt + 2, ul2_y)], fill=(255, 255, 255, 255), width=3)

# Draw Emojis
draw.text((x2 + w2_txt, y2 - 2), emojis, font=emoji_font, fill=(255, 255, 255, 255), embedded_color=True)

out_overlay = r'C:\Users\DELL\Documents\CODE\DU_AN\full_overlay_1026.png'
overlay.save(out_overlay)
print("Saved full overlay to:", out_overlay)

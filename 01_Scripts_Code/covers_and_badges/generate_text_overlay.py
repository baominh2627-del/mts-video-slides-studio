import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont

# Text from draft_content.json:
# "text": "Web luyện đề ĐGNL, TSA, THPT\nHoàn Toàn MIỄN PHÍ !!!!!\U0001faea\U0001faea"
# In CapCut UI: "Web luyện đề ĐGNL, TSA, THPT\nHoàn Toàn MIỄN PHÍ !!!!!😳😳"

W, H = 1080, 1920
txt_img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
draw = ImageDraw.Draw(txt_img)

font_path = r'C:\Windows\Fonts\arialbd.ttf'
font_size = 46
font = ImageFont.truetype(font_path, font_size)

line1 = "Web luyện đề ĐGNL, TSA, THPT"
line2 = "Hoàn Toàn MIỄN PHÍ !!!!! 😳😳"

# Let's measure text sizes
b1 = font.getbbox(line1)
w1 = b1[2] - b1[0]
h1 = b1[3] - b1[1]

# Position based on CapCut transform: x = -0.0696, y = -0.2836
# In CapCut 1080x1920:
# center is 540, 960
# x_center = 540 + (-0.0696 * 540) = 502
# y_center = 960 - (-0.2836 * 960) = 1232
center_x = int(540 + (-0.0696 * 540))
center_y = int(960 - (-0.2836 * 960))

# Line 1 position
x1 = center_x - w1 // 2
y1 = center_y - 45

# Draw outline (stroke) for Line 1
stroke_w = 4
for dx in range(-stroke_w, stroke_w + 1):
    for dy in range(-stroke_w, stroke_w + 1):
        if dx*dx + dy*dy <= stroke_w*stroke_w:
            draw.text((x1 + dx, y1 + dy), line1, font=font, fill=(0, 0, 0, 255))
# Main text Line 1
draw.text((x1, y1), line1, font=font, fill=(255, 255, 255, 255))
# Underline Line 1
draw.line([(x1, y1 + h1 + 10), (x1 + w1, y1 + h1 + 10)], fill=(255, 255, 255, 255), width=3)
draw.line([(x1 - 1, y1 + h1 + 10 + 2), (x1 + w1 + 1, y1 + h1 + 10 + 2)], fill=(0, 0, 0, 255), width=1)

# Line 2: "Hoàn Toàn MIỄN PHÍ !!!!!" + emojis
# Let's draw text part and emoji part
line2_text = "Hoàn Toàn MIỄN PHÍ !!!!! "
b2 = font.getbbox(line2_text)
w2_text = b2[2] - b2[0]

# Emoji font
emoji_font_path = r'C:\Windows\Fonts\seguiemj.ttf'
emoji_font = ImageFont.truetype(emoji_font_path, font_size - 4)
emojis = "😳😳"
b_em = emoji_font.getbbox(emojis)
w_em = b_em[2] - b_em[0]

w2_total = w2_text + w_em
x2 = center_x - w2_total // 2
y2 = y1 + h1 + 35

# Stroke Line 2
for dx in range(-stroke_w, stroke_w + 1):
    for dy in range(-stroke_w, stroke_w + 1):
        if dx*dx + dy*dy <= stroke_w*stroke_w:
            draw.text((x2 + dx, y2 + dy), line2_text, font=font, fill=(0, 0, 0, 255))
draw.text((x2, y2), line2_text, font=font, fill=(255, 255, 255, 255))

# Underline Line 2 (under text part)
draw.line([(x2, y2 + h1 + 10), (x2 + w2_text, y2 + h1 + 10)], fill=(255, 255, 255, 255), width=3)

# Draw Emojis
draw.text((x2 + w2_text, y2), emojis, font=emoji_font, fill=(255, 255, 255, 255), embedded_color=True)

# Save overlay
overlay_path = r'c:\Users\DELL\Documents\CODE\DU_AN\text_overlay_1026.png'
txt_img.save(overlay_path)
print("Saved text overlay to:", overlay_path)

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

im = cv2.imread(r'C:\Users\DELL\Documents\CODE\DU_AN\fdown_build\frame_30pct_71.2s.jpg')

# 1. Clean top-left logo area: x: 35 to 135, y: 35 to 125
# Background color in top corner is dark navy (around [10, 10, 15])
# Let's fill the logo box with background color and slight vertical gradient
tl_bg = im[20:35, 35:135].mean(axis=(0,1))
im[35:125, 35:135] = tl_bg

# 2. Clean bottom text area: x: 40 to 536, y: 955 to 992
bot_bg = im[935:950, 40:536].mean(axis=(0,1))
im[955:992, 40:536] = bot_bg

# Resize to 1080x1920
im_1080 = cv2.resize(im, (1080, 1920), interpolation=cv2.INTER_CUBIC)
im_pil = Image.fromarray(cv2.cvtColor(im_1080, cv2.COLOR_BGR2RGB)).convert('RGBA')

overlay = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
draw = ImageDraw.Draw(overlay)

font_bold = r'C:\Windows\Fonts\segoeuib.ttf'

# Watermark badge
draw.rounded_rectangle([40, 48, 330, 114], radius=16, fill=(15, 23, 42, 230), outline=(56, 189, 248, 240), width=2)
draw.ellipse([60, 71, 76, 87], fill=(56, 189, 248, 255))
draw.text((88, 60), 'MTSEducation', font=ImageFont.truetype(font_bold, 28), fill=(255, 255, 255, 255))

# Bottom footer badge:
bw, bh = 600, 56
bx = (1080 - bw) // 2
by = 1795
draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=28, fill=(15, 23, 42, 230), outline=(56, 189, 248, 200), width=2)
draw.ellipse([bx + 24, by + 20, bx + 40, by + 36], fill=(56, 189, 248, 255))
bot_text = "MTSEducation  ·  Vật Lý Trực Quan"
btw = draw.textlength(bot_text, font=ImageFont.truetype(font_bold, 24))
draw.text((bx + (bw - btw) // 2 + 10, by + 12), bot_text, font=ImageFont.truetype(font_bold, 24), fill=(255, 255, 255, 255))

result = Image.alpha_composite(im_pil, overlay).convert('RGB')
result.save(r'C:\Users\DELL\Documents\CODE\DU_AN\fdown_build\test_overlay_clean.jpg', quality=95)
print("Saved test_overlay_clean.jpg")

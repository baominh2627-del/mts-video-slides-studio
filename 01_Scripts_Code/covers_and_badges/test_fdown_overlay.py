import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

im = cv2.imread(r'C:\Users\DELL\Documents\CODE\DU_AN\fdown_build\test_inpainted.jpg')

# Resize to 1080x1920
im_1080 = cv2.resize(im, (1080, 1920), interpolation=cv2.INTER_CUBIC)
im_pil = Image.fromarray(cv2.cvtColor(im_1080, cv2.COLOR_BGR2RGB)).convert('RGBA')

overlay = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
draw = ImageDraw.Draw(overlay)

font_bold = r'C:\Windows\Fonts\segoeuib.ttf'
font_reg = r'C:\Windows\Fonts\segoeui.ttf'

# 1. Top-left Watermark Pill: [40, 48, 330, 114]
draw.rounded_rectangle([40, 48, 330, 114], radius=16, fill=(15, 23, 42, 220), outline=(56, 189, 248, 240), width=2)
draw.ellipse([60, 71, 76, 87], fill=(56, 189, 248, 255))
draw.text((88, 60), 'MTSEducation', font=ImageFont.truetype(font_bold, 28), fill=(255, 255, 255, 255))

# 2. Bottom Branded Footer Pill: centered around y = 1800 (960 * 1.875)
bw, bh = 580, 54
bx = (1080 - bw) // 2
by = 1795
draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=27, fill=(15, 23, 42, 200), outline=(56, 189, 248, 180), width=1)
draw.ellipse([bx + 20, by + 19, bx + 36, by + 35], fill=(56, 189, 248, 255))
bot_text = "MTSEducation  ·  Vật Lý Trực Quan"
btw = draw.textlength(bot_text, font=ImageFont.truetype(font_bold, 24))
draw.text((bx + (bw - btw) // 2 + 10, by + 11), bot_text, font=ImageFont.truetype(font_bold, 24), fill=(255, 255, 255, 240))

result = Image.alpha_composite(im_pil, overlay).convert('RGB')
result.save(r'C:\Users\DELL\Documents\CODE\DU_AN\fdown_build\test_overlay_1080.jpg', quality=95)
print("Saved test_overlay_1080.jpg")

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Load outro frame
frame = cv2.imread(r'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\check_outro_160.0s.jpg')

# 1. Inpaint seam
c_left = frame[15:140, 66].astype(float)
c_right = frame[15:140, 84].astype(float)
for x in range(67, 84):
    alpha = (x - 66) / (84.0 - 66.0)
    frame[15:140, x] = np.clip(c_left * (1.0 - alpha) + c_right * alpha, 0, 255).astype(np.uint8)

# 2. Resize to 1080x1920
frame_1080 = cv2.resize(frame, (1080, 1920), interpolation=cv2.INTER_CUBIC)
pil_img = Image.fromarray(cv2.cvtColor(frame_1080, cv2.COLOR_BGR2RGB)).convert('RGBA')

overlay = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
draw = ImageDraw.Draw(overlay)

font_bold = r'C:\Windows\Fonts\segoeuib.ttf'
font_reg = r'C:\Windows\Fonts\segoeui.ttf'

f_logo = ImageFont.truetype(font_bold, 46)
f_sub = ImageFont.truetype(font_bold, 22)
f_tag = ImageFont.truetype(font_reg, 21)

# Watermark badge
draw.rounded_rectangle([40, 48, 330, 114], radius=16, fill=(15, 23, 42, 220), outline=(56, 189, 248, 240), width=2)
draw.ellipse([60, 71, 76, 87], fill=(56, 189, 248, 255))
draw.text((88, 60), 'MTSEducation', font=ImageFont.truetype(font_bold, 28), fill=(255, 255, 255, 255))

# Outro card: bw = 506, bh = 218, bx = 287, by = 368
bw, bh = 506, 218
bx = (1080 - bw) // 2
by = 368

draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=24, fill=(13, 20, 36, 255), outline=(56, 189, 248, 255), width=3)
# Inner accent pill
draw.rounded_rectangle([bx + 20, by + 18, bx + bw - 20, by + 98], radius=16, fill=(30, 41, 59, 255))

# MTSEducation text centered in pill
tw = draw.textlength('MTSEducation', font=f_logo)
draw.text((bx + (bw - tw) // 2, by + 28), 'MTSEducation', font=f_logo, fill=(255, 255, 255))

# Subtitles
sw1 = draw.textlength('VẬT LÝ & KHOA HỌC TRỰC QUAN', font=f_sub)
draw.text((bx + (bw - sw1) // 2, by + 116), 'VẬT LÝ & KHOA HỌC TRỰC QUAN', font=f_sub, fill=(56, 189, 248))

sw2 = draw.textlength('Follow để học giỏi Vật Lý!', font=f_tag)
draw.text((bx + (bw - sw2) // 2, by + 156), 'Follow để học giỏi Vật Lý!', font=f_tag, fill=(203, 213, 225))

result = Image.alpha_composite(pil_img, overlay).convert('RGB')
result.save(r'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\test_1080_outro.jpg', quality=95)
print('Saved test_1080_outro.jpg')

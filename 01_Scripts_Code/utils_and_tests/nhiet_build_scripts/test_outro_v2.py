import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

im = Image.open(r'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\check_outro_160.0s.jpg')
draw = ImageDraw.Draw(im)

font_bold = r'C:\Windows\Fonts\segoeuib.ttf'
font_reg = r'C:\Windows\Fonts\segoeui.ttf'

f_logo = ImageFont.truetype(font_bold, 25)
f_sub = ImageFont.truetype(font_bold, 12)
f_tag = ImageFont.truetype(font_reg, 12)

# Card dimensions covering y: 195 to 312
bw, bh = 270, 116
bx = (576 - bw) // 2
by = 196

# Outer Card with dark navy background, subtle cyan glow border
draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=14, fill=(13, 20, 36), outline=(56, 189, 248), width=2)

# Top badge header pill
draw.rounded_rectangle([bx + 12, by + 10, bx + bw - 12, by + 52], radius=8, fill=(30, 41, 59))

# Channel Name
draw.text((bx + 38, by + 17), 'MTSEducation', font=f_logo, fill=(255, 255, 255))

# Subtitles
draw.text((bx + 26, by + 62), 'VẬT LÝ & KHOA HỌC TRỰC QUAN', font=f_sub, fill=(56, 189, 248))
draw.text((bx + 42, by + 84), 'Follow để học giỏi Vật Lý!', font=f_tag, fill=(203, 213, 225))

im.save(r'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\test_outro_mts_v2.jpg', quality=95)
print('Saved test_outro_mts_v2.jpg successfully')

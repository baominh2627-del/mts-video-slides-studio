import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# 1. Pre-render top-left watermark patch: [40, 48, 330, 114]
# Box size: w = 290, h = 66
w_w, w_h = 290, 66
w_img = Image.new('RGBA', (w_w, w_h), (0, 0, 0, 0))
w_draw = ImageDraw.Draw(w_img)

font_bold = r'C:\Windows\Fonts\segoeuib.ttf'
font_brand = ImageFont.truetype(font_bold, 28)

w_draw.rounded_rectangle([0, 0, w_w, w_h], radius=16, fill=(15, 23, 42, 220), outline=(56, 189, 248, 240), width=2)
w_draw.ellipse([20, 23, 36, 39], fill=(56, 189, 248, 255))
w_draw.text((48, 12), 'MTSEducation', font=font_brand, fill=(255, 255, 255, 255))

w_np = np.array(w_img)
w_bgr = cv2.cvtColor(w_np[:, :, :3], cv2.COLOR_RGB2BGR)
w_alpha = (w_np[:, :, 3].astype(float) / 255.0)[:, :, np.newaxis]

# 2. Pre-render outro card patch: bw = 506, bh = 218
o_w, o_h = 506, 218
o_img = Image.new('RGBA', (o_w, o_h), (0, 0, 0, 0))
o_draw = ImageDraw.Draw(o_img)

f_logo = ImageFont.truetype(font_bold, 46)
f_sub = ImageFont.truetype(font_bold, 22)
f_tag = ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf', 21)

o_draw.rounded_rectangle([0, 0, o_w, o_h], radius=24, fill=(13, 20, 36, 255), outline=(56, 189, 248, 255), width=3)
o_draw.rounded_rectangle([20, 18, o_w - 20, 98], radius=16, fill=(30, 41, 59, 255))

tw = o_draw.textlength('MTSEducation', font=f_logo)
o_draw.text(((o_w - tw) // 2, 28), 'MTSEducation', font=f_logo, fill=(255, 255, 255))

sw1 = o_draw.textlength('VẬT LÝ & KHOA HỌC TRỰC QUAN', font=f_sub)
o_draw.text(((o_w - sw1) // 2, 116), 'VẬT LÝ & KHOA HỌC TRỰC QUAN', font=f_sub, fill=(56, 189, 248))

sw2 = o_draw.textlength('Follow để học giỏi Vật Lý!', font=f_tag)
o_draw.text(((o_w - sw2) // 2, 156), 'Follow để học giỏi Vật Lý!', font=f_tag, fill=(203, 213, 225))

o_np = np.array(o_img)
o_bgr = cv2.cvtColor(o_np[:, :, :3], cv2.COLOR_RGB2BGR)
o_alpha = (o_np[:, :, 3].astype(float) / 255.0)[:, :, np.newaxis]

print(f'Watermark patch shape: {w_bgr.shape}, Outro patch shape: {o_bgr.shape}')

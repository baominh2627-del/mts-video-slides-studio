import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# 1. Pre-render patches
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

# Test on frame 4800 (outro)
cap = cv2.VideoCapture(r'C:\Users\DELL\Documents\Downloads\NHIỆT LƯỢNG, NỘI NĂNG, NHIỆT NĂNG.mp4')
cap.set(cv2.CAP_PROP_POS_FRAMES, 4800)
ret, frame = cap.read()
cap.release()

# Inpaint seam
c_left = frame[15:140, 66].astype(float)
c_right = frame[15:140, 84].astype(float)
for x in range(67, 84):
    alpha = (x - 66) / (84.0 - 66.0)
    frame[15:140, x] = np.clip(c_left * (1.0 - alpha) + c_right * alpha, 0, 255).astype(np.uint8)

frame_1080 = cv2.resize(frame, (1080, 1920), interpolation=cv2.INTER_CUBIC)

# Blend watermark
roi_w = frame_1080[48:114, 40:330]
frame_1080[48:114, 40:330] = np.clip(roi_w.astype(float) * (1.0 - w_alpha) + w_bgr.astype(float) * w_alpha, 0, 255).astype(np.uint8)

# Blend outro
roi_o = frame_1080[368:586, 287:793]
frame_1080[368:586, 287:793] = np.clip(roi_o.astype(float) * (1.0 - o_alpha) + o_bgr.astype(float) * o_alpha, 0, 255).astype(np.uint8)

cv2.imwrite(r'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\test_frame_4800_final.jpg', frame_1080)
print('Saved test_frame_4800_final.jpg')

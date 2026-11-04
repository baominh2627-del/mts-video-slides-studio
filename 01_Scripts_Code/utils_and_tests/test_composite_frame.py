# -*- coding: utf-8 -*-
import os
import sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8')

W, H = 1080, 1920
font_arial_bold = r"C:\Windows\Fonts\arialbd.ttf"
font_tahoma_bold = r"C:\Windows\Fonts\tahomabd.ttf"

f_badge = ImageFont.truetype(font_tahoma_bold, 32)
f_title = ImageFont.truetype(font_arial_bold, 54)
f_subtitle = ImageFont.truetype(font_tahoma_bold, 34)
f_caption = ImageFont.truetype(font_arial_bold, 42)
f_cta_bold = ImageFont.truetype(font_arial_bold, 36)
f_cta_sub = ImageFont.truetype(font_tahoma_bold, 28)
f_addr = ImageFont.truetype(font_tahoma_bold, 22)

# Create background
bg = np.zeros((H, W, 3), dtype=np.uint8)
# Vertical dark tech gradient
for y in range(H):
    ratio = y / H
    r = int(8 + 10 * ratio)
    g = int(12 + 15 * ratio)
    b = int(24 + 30 * ratio)
    bg[y, :] = (b, g, r)  # BGR

# Load a sample frame from scene_2.mp4
cap = cv2.VideoCapture(r"C:\Users\DELL\Documents\CODE\DU_AN\web_records\scene_2.mp4")
ret, web_frame = cap.read()
cap.release()

if ret:
    # Resize web frame to 1000x562
    web_w, web_h = 1000, 562
    web_resized = cv2.resize(web_frame, (web_w, web_h), interpolation=cv2.INTER_CUBIC)
    
    # Position of browser mockup
    bx = 40
    by = 480
    header_h = 44
    
    # Draw browser header in BGR
    cv2.rectangle(bg, (bx, by), (bx + web_w, by + header_h), (45, 36, 28), -1)
    # 3 traffic lights
    cv2.circle(bg, (bx + 25, by + 22), 8, (86, 95, 255), -1)   # Red
    cv2.circle(bg, (bx + 50, by + 22), 8, (46, 189, 255), -1)  # Yellow
    cv2.circle(bg, (bx + 75, by + 22), 8, (63, 201, 39), -1)   # Green
    
    # Address bar
    cv2.rectangle(bg, (bx + 120, by + 8), (bx + web_w - 40, by + header_h - 8), (25, 20, 16), -1)
    
    # Put web frame
    bg[by + header_h : by + header_h + web_h, bx : bx + web_w] = web_resized
    
    # Outer border
    cv2.rectangle(bg, (bx - 2, by - 2), (bx + web_w + 2, by + header_h + web_h + 2), (255, 180, 50), 3)

# Convert to PIL for text drawing
img_pil = Image.fromarray(cv2.cvtColor(bg, cv2.COLOR_BGR2RGB))
draw = ImageDraw.Draw(img_pil)

# Helper for text with outline
def draw_text_stroke(draw, pos, text, font, fill, stroke_fill=(0, 0, 0), stroke_w=4):
    x, y = pos
    draw.text((x, y), text, font=font, fill=fill, stroke_width=stroke_w, stroke_fill=stroke_fill)

# Top Watermark
draw.text((45, 40), "MTS Education ✦", font=f_badge, fill=(255, 255, 255))
draw.text((W - 380, 40), "HOTLINE: 0372 336 302", font=f_addr, fill=(200, 225, 255))

# Scene Badge
badge_text = "📚 KHO ĐỀ TN THPT 2025-2026"
bb = draw.textbbox((0, 0), badge_text, font=f_badge)
bw = bb[2] - bb[0] + 40
bx = (W - bw) // 2
draw.rounded_rectangle([bx, 110, bx + bw, 165], radius=15, fill=(30, 45, 90), outline=(59, 130, 246), width=2)
draw.text((bx + 20, 118), badge_text, font=f_badge, fill=(255, 255, 255))

# Main Title
title_text = "TOÁN · LÝ · HÓA · SỬ · ANH"
tb = draw.textbbox((0, 0), title_text, font=f_title)
tw = tb[2] - tb[0]
draw_text_stroke(draw, ((W - tw) // 2, 190), title_text, font=f_title, fill=(255, 234, 0), stroke_w=6)

# Subtitle under title
sub_text = "🎯 CHUẨN 100% CẤU TRÚC BỘ GIÁO DỤC"
sb = draw.textbbox((0, 0), sub_text, font=f_subtitle)
draw_text_stroke(draw, ((W - (sb[2] - sb[0])) // 2, 270), sub_text, font=f_subtitle, fill=(0, 242, 254), stroke_w=4)

# Browser Address Bar text
draw.text((bx + 145, 492), "🔒 https://mtsedu.vercel.app/#physics", font=f_addr, fill=(180, 200, 230))

# Subtitle Card
cap_box = [60, 1150, W - 60, 1300]
draw.rounded_rectangle(cap_box, radius=20, fill=(15, 23, 42), outline=(255, 255, 255), width=2)
c1 = "Kho đề thi thử tốt nghiệp THPT chuẩn 100%:"
c2 = "Toán bứt phá · Vật lý trực quan · Hóa chuyên sâu!"
b1 = draw.textbbox((0, 0), c1, font=f_caption)
b2 = draw.textbbox((0, 0), c2, font=f_caption)
draw_text_stroke(draw, ((W - (b1[2] - b1[0])) // 2, 1170), c1, font=f_caption, fill=(255, 255, 255), stroke_w=3)
draw_text_stroke(draw, ((W - (b2[2] - b2[0])) // 2, 1230), c2, font=f_caption, fill=(255, 234, 0), stroke_w=3)

# Bottom Sticky CTA Banner
cta_box = [40, 1680, W - 40, 1860]
draw.rounded_rectangle(cta_box, radius=24, fill=(18, 25, 45), outline=(255, 215, 0), width=3)
cta1 = "🎁 MIỄN PHÍ 100% CHO 2K11, 2K10 & ĐẶC BIỆT 2K9!"
cta2 = "🌐 MTSEDU.VERCEL.APP  |  📞 ZALO: 0372 336 302"
b_cta1 = draw.textbbox((0, 0), cta1, font=f_cta_bold)
b_cta2 = draw.textbbox((0, 0), cta2, font=f_cta_sub)
draw_text_stroke(draw, ((W - (b_cta1[2] - b_cta1[0])) // 2, 1715), cta1, font=f_cta_bold, fill=(255, 220, 0), stroke_w=4)
draw_text_stroke(draw, ((W - (b_cta2[2] - b_cta2[0])) // 2, 1785), cta2, font=f_cta_sub, fill=(255, 255, 255), stroke_w=2)

# Save test frame
res_bgr = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
cv2.imwrite("test_preview_frame.jpg", res_bgr)
print("Preview frame saved to test_preview_frame.jpg")

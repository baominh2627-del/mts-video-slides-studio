# -*- coding: utf-8 -*-
import os
import sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8')

W, H = 1080, 1920

# Fonts
font_bold = "C:/Windows/Fonts/segoeuib.ttf" if os.path.exists("C:/Windows/Fonts/segoeuib.ttf") else "C:/Windows/Fonts/arialbd.ttf"
font_reg = "C:/Windows/Fonts/segoeui.ttf" if os.path.exists("C:/Windows/Fonts/segoeui.ttf") else "C:/Windows/Fonts/arial.ttf"
font_tahoma = "C:/Windows/Fonts/tahomabd.ttf"

f_wm = ImageFont.truetype(font_bold, 30)
f_badge = ImageFont.truetype(font_bold, 30)
f_title = ImageFont.truetype(font_bold, 54)
f_subtitle = ImageFont.truetype(font_bold, 34)
f_caption = ImageFont.truetype(font_bold, 40)
f_feature = ImageFont.truetype(font_bold, 26)
f_cta_bold = ImageFont.truetype(font_bold, 36)
f_cta_sub = ImageFont.truetype(font_bold, 28)
f_addr = ImageFont.truetype(font_bold, 22)

# 1. Base Pastel Background
# White background (#FFFFFF) with subtle watercolor washes:
# Top-left sky blue (#D9F0FF), Top-right lavender (#E8DCFF), Bottom-left pink (#FFD9F0)
bg = Image.new("RGBA", (W, H), (255, 255, 255, 255))
wash = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d_wash = ImageDraw.Draw(wash)

# Soft watercolor blobs
# Top-Left Sky Blue blob
d_wash.ellipse([-150, -100, 600, 500], fill=(217, 240, 255, 140))
# Top-Right Lavender blob
d_wash.ellipse([W - 500, -120, W + 200, 550], fill=(232, 220, 255, 130))
# Center-Right Pastel Pink blob
d_wash.ellipse([W - 350, 700, W + 150, 1200], fill=(255, 217, 240, 110))
# Bottom-Left Pastel Cyan blob
d_wash.ellipse([-120, H - 650, 450, H + 100], fill=(191, 232, 255, 130))
# Bottom-Right Soft Pink/Lavender
d_wash.ellipse([W - 400, H - 450, W + 150, H + 100], fill=(255, 225, 245, 120))

bg = Image.alpha_composite(bg, wash)
draw = ImageDraw.Draw(bg)

# Draw cute background doodle lines and sparkles
# Decorative stars/sparkles
def draw_sparkle(draw, cx, cy, size, color):
    draw.line([(cx - size, cy), (cx + size, cy)], fill=color, width=3)
    draw.line([(cx, cy - size), (cx, cy + size)], fill=color, width=3)
    draw.line([(cx - size//2, cy - size//2), (cx + size//2, cy + size//2)], fill=color, width=2)
    draw.line([(cx - size//2, cy + size//2), (cx + size//2, cy - size//2)], fill=color, width=2)

draw_sparkle(draw, 100, 220, 18, (66, 107, 255))
draw_sparkle(draw, W - 110, 200, 22, (255, 120, 180))
draw_sparkle(draw, 80, 1360, 16, (66, 107, 255))
draw_sparkle(draw, W - 90, 1380, 20, (255, 180, 50))

# Doodle curved lines
draw.arc([W - 180, 280, W - 60, 400], start=180, end=320, fill=(66, 107, 255), width=3)
draw.arc([60, 360, 180, 480], start=0, end=140, fill=(255, 140, 180), width=3)

# 2. Browser Mockup (Clean Light/Pastel Paper style)
cap = cv2.VideoCapture(r"C:\Users\DELL\Documents\CODE\DU_AN\web_records\scene_2.mp4")
ret, web_frame = cap.read()
cap.release()

bx = 40
by = 440
base_w, base_h = 1000, 680
header_h = 46

# Soft drop shadow behind browser window
shadow_pad = 12
draw.rounded_rectangle([bx - shadow_pad, by - shadow_pad, bx + base_w + shadow_pad, by + base_h + shadow_pad],
                       radius=30, fill=(210, 230, 255, 120))

# Window body
draw.rounded_rectangle([bx, by, bx + base_w, by + base_h], radius=24, fill=(255, 255, 255), outline=(66, 107, 255), width=3)

# Window Header
draw.rounded_rectangle([bx, by, bx + base_w, by + header_h + 10], radius=24, fill=(234, 244, 255))
draw.rectangle([bx, by + 20, bx + base_w, by + header_h], fill=(234, 244, 255))
draw.line([(bx, by + header_h), (bx + base_w, by + header_h)], fill=(191, 232, 255), width=2)

# 3 cute dots
draw.ellipse([bx + 25, by + 16, bx + 39, by + 30], fill=(255, 107, 107)) # Coral
draw.ellipse([bx + 48, by + 16, bx + 62, by + 30], fill=(255, 209, 102)) # Amber
draw.ellipse([bx + 71, by + 16, bx + 85, by + 30], fill=(6, 214, 160))  # Mint

# Address bar
addr_x = bx + 110
addr_w = base_w - 140
draw.rounded_rectangle([addr_x, by + 8, addr_x + addr_w, by + header_h - 8], radius=14, fill=(255, 255, 255), outline=(191, 232, 255), width=2)
draw.text((addr_x + 18, by + 11), "🔒 https://mtsedu.vercel.app/#physics", font=f_addr, fill=(16, 40, 92))

# Put web content into PIL image
if ret:
    web_content_h = base_h - header_h
    web_resized = cv2.resize(web_frame, (base_w, web_content_h), interpolation=cv2.INTER_AREA)
    web_pil = Image.fromarray(cv2.cvtColor(web_resized, cv2.COLOR_BGR2RGB))
    bg.paste(web_pil, (bx, by + header_h))

# Redraw border to keep edges crisp
draw.rounded_rectangle([bx, by, bx + base_w, by + base_h], radius=24, outline=(66, 107, 255), width=3)

# 3. Top Watermark
draw.text((45, 38), "MTS Education ✦", font=f_wm, fill=(16, 40, 92))
# Draw cute underline
draw.line([(45, 75), (280, 75)], fill=(66, 107, 255), width=3)

# Hotline pill
draw.rounded_rectangle([W - 390, 32, W - 45, 82], radius=18, fill=(255, 255, 255), outline=(191, 232, 255), width=2)
draw.text((W - 370, 44), "HOTLINE: 0372 336 302", font=f_addr, fill=(16, 40, 92))

# 4. Scene Badge
badge_txt = "📚 KHO ĐỀ TN THPT 2025-2026 ✨"
bb = draw.textbbox((0, 0), badge_txt, font=f_badge)
bw = bb[2] - bb[0] + 50
bx_badge = (W - bw) // 2
draw.rounded_rectangle([bx_badge, 105, bx_badge + bw, 162], radius=20, fill=(217, 240, 255), outline=(66, 107, 255), width=2)
draw.text((bx_badge + 25, 115), badge_txt, font=f_badge, fill=(16, 40, 92))

# 5. Main Title with soft pastel highlight brush
title_txt = "TOÁN · LÝ · HÓA · SỬ · ANH"
tb = draw.textbbox((0, 0), title_txt, font=f_title)
tw = tb[2] - tb[0]
title_x = (W - tw) // 2
# Pastel yellow/cyan brush behind title
draw.rounded_rectangle([title_x - 15, 192, title_x + tw + 15, 256], radius=16, fill=(255, 242, 175, 180))
draw.text((title_x, 190), title_txt, font=f_title, fill=(16, 40, 92))

# Subtitle
sub_txt = "🎯 Chuẩn 100% Ma Trận Đề Bộ GD&ĐT"
sb = draw.textbbox((0, 0), sub_txt, font=f_subtitle)
sub_x = (W - (sb[2] - sb[0])) // 2
draw.text((sub_x, 275), sub_txt, font=f_subtitle, fill=(66, 107, 255))

# 6. Dynamic Subtitle Card (Paper Note Style)
cap_box = [50, 1165, W - 50, 1295]
# Soft shadow
draw.rounded_rectangle([cap_box[0] - 6, cap_box[1] - 6, cap_box[2] + 6, cap_box[3] + 6], radius=24, fill=(215, 235, 255, 100))
draw.rounded_rectangle(cap_box, radius=20, fill=(255, 255, 255), outline=(66, 107, 255), width=2)
c_text = "Toán bứt phá · Vật lý trực quan · Hóa chuyên sâu!"
cb = draw.textbbox((0, 0), c_text, font=f_caption)
draw.text(((W - (cb[2] - cb[0])) // 2, 1205), c_text, font=f_caption, fill=(16, 40, 92))

# 7. 3 Floating Feature Badges
features = [
    ("⚡ Bấm Giờ Thật", (191, 232, 255)),
    ("💯 Chấm Điểm Ngay", (167, 243, 208)),
    ("📖 Giải Chi Tiết", (255, 217, 240))
]
pill_w = 300
pill_gap = 25
start_px = (W - (3 * pill_w + 2 * pill_gap)) // 2
for fi, (ftxt, fbg) in enumerate(features):
    px = start_px + fi * (pill_w + pill_gap)
    draw.rounded_rectangle([px, 1325, px + pill_w, 1385], radius=16, fill=(255, 255, 255), outline=(66, 107, 255), width=2)
    # Interior soft tint
    draw.rounded_rectangle([px + 3, 1328, px + pill_w - 3, 1382], radius=14, fill=fbg)
    fb = draw.textbbox((0, 0), ftxt, font=f_feature)
    draw.text((px + (pill_w - (fb[2] - fb[0])) // 2, 1342), ftxt, font=f_feature, fill=(16, 40, 92))

# 8. Bottom Sticky CTA Banner (Paper Card with Cobalt & Pastel Borders)
cta_box = [40, 1420, W - 40, 1870]
# Soft shadow
draw.rounded_rectangle([cta_box[0] - 8, cta_box[1] - 8, cta_box[2] + 8, cta_box[3] + 8], radius=30, fill=(210, 230, 255, 120))
draw.rounded_rectangle(cta_box, radius=24, fill=(255, 255, 255), outline=(66, 107, 255), width=3)

# Top pastel accent bar inside card
draw.rounded_rectangle([cta_box[0] + 3, cta_box[1] + 3, cta_box[2] - 3, cta_box[1] + 120], radius=22, fill=(255, 217, 240))
draw.rectangle([cta_box[0] + 3, cta_box[1] + 50, cta_box[2] - 3, cta_box[1] + 120], fill=(255, 217, 240))

t1 = "🎁 HOÀN TOÀN MIỄN PHÍ 100%!"
t2 = "DÀNH CHO HỌC SINH 2K11, 2K10 & ĐẶC BIỆT 2K9"
t3 = "🌐 Website: MTSEDU.VERCEL.APP"
t4 = "📞 Hotline & Zalo: 0372 336 302"

b_t1 = draw.textbbox((0, 0), t1, font=f_cta_bold)
b_t2 = draw.textbbox((0, 0), t2, font=f_cta_sub)
b_t3 = draw.textbbox((0, 0), t3, font=f_cta_bold)
b_t4 = draw.textbbox((0, 0), t4, font=f_cta_bold)

draw.text(((W - (b_t1[2] - b_t1[0])) // 2, 1445), t1, font=f_cta_bold, fill=(225, 29, 72)) # Coral red
draw.text(((W - (b_t2[2] - b_t2[0])) // 2, 1500), t2, font=f_cta_sub, fill=(16, 40, 92))

# Divider line with cute doodle dots
draw.line([(80, 1580), (W - 80, 1580)], fill=(191, 232, 255), width=2)

draw.text(((W - (b_t3[2] - b_t3[0])) // 2, 1615), t3, font=f_cta_bold, fill=(66, 107, 255))
draw.text(((W - (b_t4[2] - b_t4[0])) // 2, 1690), t4, font=f_cta_bold, fill=(16, 40, 92))

# Big CTA Button
btn_y = 1765
btn_w = 880
btn_h = 74
btn_x = (W - btn_w) // 2
draw.rounded_rectangle([btn_x, btn_y, btn_x + btn_w, btn_y + btn_h], radius=20, fill=(66, 107, 255), outline=(191, 232, 255), width=2)
btn_text = "👉 TRUY CẬP NGAY ĐỂ NHẬN TÀI KHOẢN VIP 👈"
bb = draw.textbbox((0, 0), btn_text, font=f_cta_sub)
draw.text((btn_x + (btn_w - (bb[2] - bb[0])) // 2, btn_y + 20), btn_text, font=f_cta_sub, fill=(255, 255, 255))

bg.convert("RGB").save("test_pastel_preview.jpg")
print("Saved test_pastel_preview.jpg successfully!")

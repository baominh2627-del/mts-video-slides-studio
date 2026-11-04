import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
cover = Image.new('RGB', (W, H), (10, 15, 29))
draw = ImageDraw.Draw(cover)

# Background subtle dark tech gradient
for y in range(H):
    r = int(10 + (20 - 10) * (y / H))
    g = int(15 + (25 - 15) * (y / H))
    b = int(29 + (55 - 29) * (y / H))
    draw.line([(0, y), (W, y)], fill=(r, g, b))

# Load a clean illustrative frame from demo_2 (e.g. at frame 10s showing the website UI)
frame = cv2.imread(r'c:\Users\DELL\Documents\CODE\DU_AN\demo_2_frame10s.jpg')
# Resize frame to fit nicely
frame_w = 1000
frame_h = int(frame.shape[0] * (frame_w / frame.shape[1]))
# Cap frame height to 700
if frame_h > 720:
    frame_h = 720
frame_resized = cv2.resize(frame, (frame_w, frame_h), interpolation=cv2.INTER_LANCZOS4)
frame_pil = Image.fromarray(cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB))

# Frame position in middle
frame_x = (W - frame_w) // 2
frame_y = 560

# Border & shadow around frame
border_box = [frame_x - 4, frame_y - 4, frame_x + frame_w + 4, frame_y + frame_h + 4]
draw.rounded_rectangle(border_box, radius=18, fill=(24, 32, 54), outline=(56, 189, 248), width=3)
cover.paste(frame_pil, (frame_x, frame_y))

# Fonts
font_path_bold = r'C:\Windows\Fonts\arialbd.ttf'
font_path_reg = r'C:\Windows\Fonts\arial.ttf'
font_segoe_b = r'C:\Windows\Fonts\segoeuib.ttf'

font_badge = ImageFont.truetype(font_path_bold, 28)
font_title = ImageFont.truetype(font_path_bold, 58)
font_sub = ImageFont.truetype(font_path_bold, 34)
font_card_title = ImageFont.truetype(font_path_bold, 30)
font_pill = ImageFont.truetype(font_path_bold, 26)
font_footer = ImageFont.truetype(font_path_bold, 28)

# Top badge
badge_text = "MTSEducation · NỀN TẢNG ÔN THI TRỰC TUYẾN"
bbox = font_badge.getbbox(badge_text)
bw = bbox[2] - bbox[0] + 48
bh = bbox[3] - bbox[1] + 24
bx = (W - bw) // 2
by = 120
draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=24, fill=(30, 41, 59), outline=(56, 189, 248), width=2)
# Cyan dot
draw.ellipse([bx + 16, by + 14, bx + 28, by + 26], fill=(56, 189, 248))
draw.text((bx + 38, by + 10), badge_text, fill=(255, 255, 255), font=font_badge)

# Main Title: WEB LUYỆN ĐỀ MIỄN PHÍ
title_text = "WEB LUYỆN ĐỀ"
tbbox = font_title.getbbox(title_text)
tx = (W - (tbbox[2] - tbbox[0])) // 2
ty = 230
for off in [(-2,-2), (2,2), (-2,2), (2,-2), (0,3)]:
    draw.text((tx + off[0], ty + off[1]), title_text, fill=(2, 132, 199), font=font_title)
draw.text((tx, ty), title_text, fill=(56, 189, 248), font=font_title)

# Subtitle: ĐGNL · TSA · THPT
sub_text = "ĐGNL - TSA - THPT QUỐC GIA"
sbbox = font_sub.getbbox(sub_text)
sx = (W - (sbbox[2] - sbbox[0])) // 2
sy = 330
draw.text((sx, sy), sub_text, fill=(251, 191, 36), font=font_sub)

# Tagline pill: "HOÀN TOÀN MIỄN PHÍ 100%"
tag_text = "🔥 HOÀN TOÀN MIỄN PHÍ 100% - CHẤM ĐIỂM TỰ ĐỘNG 🔥"
tag_font = ImageFont.truetype(font_path_bold, 24)
tg_bbox = tag_font.getbbox(tag_text)
tw = tg_bbox[2] - tg_bbox[0] + 36
th = tg_bbox[3] - tg_bbox[1] + 16
tx_pill = (W - tw) // 2
ty_pill = 410
draw.rounded_rectangle([tx_pill, ty_pill, tx_pill + tw, ty_pill + th], radius=16, fill=(15, 23, 42), outline=(245, 158, 11), width=2)
draw.text((tx_pill + 18, ty_pill + 8), tag_text, fill=(253, 230, 138), font=tag_font)

# Feature Card 1: Kho đề chuẩn cấu trúc mới
card1_y = frame_y + frame_h + 50
card_w = 980
card_x = (W - card_w) // 2
draw.rounded_rectangle([card_x, card1_y, card_x + card_w, card1_y + 130], radius=20, fill=(15, 23, 42), outline=(56, 189, 248), width=2)
draw.text((card_x + 30, card1_y + 20), "📚 Đầy đủ kỳ thi ĐHQG Hà Nội, TP.HCM & Bách Khoa", fill=(255, 255, 255), font=font_card_title)
draw.text((card_x + 30, card1_y + 70), "Thi trực tuyến bấm giờ như thi thật + Lời giải chi tiết", fill=(148, 163, 184), font=font_pill)

# Feature Card 2: Luyện đề mọi lúc mọi nơi
card2_y = card1_y + 155
draw.rounded_rectangle([card_x, card2_y, card_x + card_w, card2_y + 130], radius=20, fill=(15, 23, 42), outline=(245, 158, 11), width=2)
draw.text((card_x + 30, card2_y + 20), "⚡ Trải nghiệm mượt mà trên cả Điện thoại & Máy tính", fill=(253, 230, 138), font=font_card_title)
draw.text((card_x + 30, card2_y + 70), "Phân tích điểm mạnh, điểm yếu theo từng chuyên đề", fill=(203, 213, 225), font=font_pill)

# Bottom footer badge
ft_text = "Theo dõi MTSEducation để nhận tài liệu & đề thi mới nhất!"
ft_bbox = font_footer.getbbox(ft_text)
ft_x = (W - (ft_bbox[2] - ft_bbox[0])) // 2
ft_y = 1790
draw.text((ft_x, ft_y), ft_text, fill=(203, 213, 225), font=font_footer)

out_dl = r'C:\Users\DELL\Documents\Downloads\ẢNH BÌA TIKTOK_DEMO WEB.png'
out_ws = r'c:\Users\DELL\Documents\CODE\DU_AN\ẢNH BÌA TIKTOK_DEMO WEB.png'
cover.save(out_dl)
cover.save(out_ws)
print("Saved cover")

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
cover = Image.new('RGB', (W, H), (10, 15, 29))
draw = ImageDraw.Draw(cover)

# Background subtle dark tech gradient
for y in range(H):
    r = int(10 + (22 - 10) * (y / H))
    g = int(15 + (26 - 15) * (y / H))
    b = int(29 + (50 - 29) * (y / H))
    draw.line([(0, y), (W, y)], fill=(r, g, b))

# Load illustrative frame from video (e.g. at 60s showing the prism diagram)
frame = cv2.imread(r'c:\Users\DELL\Documents\CODE\DU_AN\chitiet_60s.jpg')
frame_w = 980
frame_h = int(frame.shape[0] * (frame_w / frame.shape[1]))
if frame_h > 720:
    frame_h = 720
frame_resized = cv2.resize(frame, (frame_w, frame_h), interpolation=cv2.INTER_LANCZOS4)
frame_pil = Image.fromarray(cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB))

# Frame position in middle
frame_x = (W - frame_w) // 2
frame_y = 520

border_box = [frame_x - 4, frame_y - 4, frame_x + frame_w + 4, frame_y + frame_h + 4]
draw.rounded_rectangle(border_box, radius=18, fill=(24, 32, 54), outline=(56, 189, 248), width=3)
cover.paste(frame_pil, (frame_x, frame_y))

# Fonts
font_path_bold = r'C:\Windows\Fonts\arialbd.ttf'
font_segoe_b = r'C:\Windows\Fonts\segoeuib.ttf'

font_badge = ImageFont.truetype(font_path_bold, 28)
font_title = ImageFont.truetype(font_path_bold, 58)
font_sub = ImageFont.truetype(font_path_bold, 34)
font_card_title = ImageFont.truetype(font_path_bold, 30)
font_formula = ImageFont.truetype(font_segoe_b, 40)
font_formula_sub = ImageFont.truetype(font_path_bold, 24)
font_footer = ImageFont.truetype(font_path_bold, 28)

# Top badge with official logo
logo_pil = Image.open('c:/Users/DELL/Documents/CODE/DU_AN/favicon_transparent.png')
logo_icon = logo_pil.resize((48, 48), Image.LANCZOS)

badge_text = "MTSEducation · VẬT LÝ NÂNG CAO"
bbox = font_badge.getbbox(badge_text)
bw = bbox[2] - bbox[0] + 48 + 36
bh = 68
bx = (W - bw) // 2
by = 110
draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=24, fill=(30, 41, 59), outline=(56, 189, 248), width=2)
# Paste official logo
cover.paste(logo_icon, (bx + 16, by + 10), logo_icon)
draw.text((bx + 72, by + 16), badge_text, fill=(255, 255, 255), font=font_badge)

# Main Title: GIẢI CHI TIẾT CÂU 16
title_text = "GIẢI CHI TIẾT CÂU 16"
tbbox = font_title.getbbox(title_text)
tx = (W - (tbbox[2] - tbbox[0])) // 2
ty = 220
for off in [(-2,-2), (2,2), (-2,2), (2,-2), (0,3)]:
    draw.text((tx + off[0], ty + off[1]), title_text, fill=(2, 132, 199), font=font_title)
draw.text((tx, ty), title_text, fill=(56, 189, 248), font=font_title)

# Subtitle: CÂN BẰNG NHIỆT LĂNG TRỤ TAM GIÁC
sub_text = "CÂN BẰNG NHIỆT TRONG LĂNG TRỤ"
sbbox = font_sub.getbbox(sub_text)
sx = (W - (sbbox[2] - sbbox[0])) // 2
sy = 315
draw.text((sx, sy), sub_text, fill=(251, 191, 36), font=font_sub)

# Tagline pill: "PHƯƠNG PHÁP VI PHÂN & MẸO TRỌNG TÂM"
tag_text = "⚡ TÍCH PHÂN TÍNH t₀ & MẸO GIẢI NHANH 10 GIÂY ⚡"
tag_font = ImageFont.truetype(font_path_bold, 24)
tg_bbox = tag_font.getbbox(tag_text)
tw = tg_bbox[2] - tg_bbox[0] + 36
th = tg_bbox[3] - tg_bbox[1] + 16
tx_pill = (W - tw) // 2
ty_pill = 390
draw.rounded_rectangle([tx_pill, ty_pill, tx_pill + tw, ty_pill + th], radius=16, fill=(15, 23, 42), outline=(245, 158, 11), width=2)
draw.text((tx_pill + 18, ty_pill + 8), tag_text, fill=(253, 230, 138), font=tag_font)

# Feature Card 1: Công thức bản chất
card1_y = frame_y + frame_h + 40
card_w = 980
card_x = (W - card_w) // 2
draw.rounded_rectangle([card_x, card1_y, card_x + card_w, card1_y + 150], radius=20, fill=(15, 23, 42), outline=(56, 189, 248), width=2)
draw.text((card_x + 30, card1_y + 18), "Bản chất: Trung bình nhiệt độ theo khối lượng", fill=(148, 163, 184), font=font_card_title)
draw.text((card_x + 30, card1_y + 68), "t₀  =  ∫ t dm / ∫ dm  =  5kH² / (½ kH²)  =  10°C", fill=(255, 255, 255), font=font_formula)

# Feature Card 2: Mẹo giải nhanh trọng tâm
card2_y = card1_y + 175
draw.rounded_rectangle([card_x, card2_y, card_x + card_w, card2_y + 150], radius=20, fill=(15, 23, 42), outline=(245, 158, 11), width=2)
draw.text((card_x + 30, card2_y + 18), "Mẹo giải nhanh 10 giây (Trọng tâm tam giác):", fill=(253, 230, 138), font=font_card_title)
draw.text((card_x + 30, card2_y + 68), "h_G = 2H/3  ⇒  t₀ = 4 + 9 · (2/3)  =  10°C", fill=(251, 191, 36), font=font_formula)
draw.text((card_x + 30, card2_y + 118), "✓ Áp dụng chuẩn cho mọi dạng bình khi t(h) bậc nhất!", fill=(203, 213, 225), font=font_formula_sub)

# Bottom footer badge
ft_text = "Lưu lại và follow MTSEducation để xem thêm bài giảng hay!"
ft_bbox = font_footer.getbbox(ft_text)
ft_x = (W - (ft_bbox[2] - ft_bbox[0])) // 2
ft_y = 1795
draw.text((ft_x, ft_y), ft_text, fill=(203, 213, 225), font=font_footer)

out_dl = r'C:\Users\DELL\Documents\Downloads\ẢNH BÌA TIKTOK_GIẢI CÂU 16.png'
out_ws = r'c:\Users\DELL\Documents\CODE\DU_AN\ẢNH BÌA TIKTOK_GIẢI CÂU 16.png'
cover.save(out_dl)
cover.save(out_ws)
print("Saved updated cover with official logo!")

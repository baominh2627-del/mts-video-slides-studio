import cv2, os, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8')

W, H = 1080, 1920
cover = Image.new('RGB', (W, H), (10, 15, 29))
draw = ImageDraw.Draw(cover)

# Background subtle dark tech gradient
for y in range(H):
    r = int(10 + (22 - 10) * (y / H))
    g = int(15 + (26 - 15) * (y / H))
    b = int(29 + (50 - 29) * (y / H))
    draw.line([(0, y), (W, y)], fill=(r, g, b))

# Load illustrative frame from Video 2
frame_path = r'c:\Users\DELL\Documents\CODE\DU_AN\final_v2_172s.jpg'
frame = cv2.imread(frame_path)
frame_w = 980
frame_h = int(frame.shape[0] * (frame_w / frame.shape[1]))
if frame_h > 740:
    frame_h = 740
frame_resized = cv2.resize(frame, (frame_w, frame_h), interpolation=cv2.INTER_LANCZOS4)
frame_pil = Image.fromarray(cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB))

# Frame position in middle
frame_x = (W - frame_w) // 2
frame_y = 510

border_box = [frame_x - 4, frame_y - 4, frame_x + frame_w + 4, frame_y + frame_h + 4]
draw.rounded_rectangle(border_box, radius=20, fill=(24, 32, 54), outline=(56, 189, 248), width=3)
cover.paste(frame_pil, (frame_x, frame_y))

# Fonts
font_path_bold = r'C:\Windows\Fonts\arialbd.ttf'
font_segoe_b = r'C:\Windows\Fonts\segoeuib.ttf'

font_badge = ImageFont.truetype(font_path_bold, 28)
font_title = ImageFont.truetype(font_path_bold, 54)
font_sub = ImageFont.truetype(font_path_bold, 32)
font_tag = ImageFont.truetype(font_path_bold, 24)
font_card_title = ImageFont.truetype(font_path_bold, 30)
font_formula = ImageFont.truetype(font_segoe_b, 38)
font_formula_sub = ImageFont.truetype(font_path_bold, 24)
font_footer = ImageFont.truetype(font_path_bold, 28)

def draw_vector_bolt(d, cx, cy, color=(251, 191, 36)):
    bolt = [(cx + 2, cy - 10), (cx - 6, cy + 1), (cx, cy + 1), (cx - 3, cy + 11), (cx + 6, cy - 1), (cx, cy - 1)]
    d.polygon(bolt, fill=color)

def draw_vector_check(d, cx, cy, color=(52, 211, 153)):
    d.line([(cx - 7, cy), (cx - 2, cy + 6), (cx + 7, cy - 6)], fill=color, width=3)

# Top badge with official logo
logo_pil = Image.open('c:/Users/DELL/Documents/CODE/DU_AN/favicon_transparent.png')
logo_icon = logo_pil.resize((48, 48), Image.LANCZOS)

badge_text = "MTSEducation · BẢN ĐẶC BIỆT (VIDEO 2)"
bbox = font_badge.getbbox(badge_text)
bw = bbox[2] - bbox[0] + 48 + 36
bh = 68
bx = (W - bw) // 2
by = 100
draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=24, fill=(30, 41, 59), outline=(56, 189, 248), width=2)
cover.paste(logo_icon, (bx + 16, by + 10), logo_icon)
draw.text((bx + 72, by + 16), badge_text, fill=(255, 255, 255), font=font_badge)

# Main Title: CÂN BẰNG NHIỆT · CÂU 16
title_text = "CÂN BẰNG NHIỆT · CÂU 16"
tbbox = font_title.getbbox(title_text)
tx = (W - (tbbox[2] - tbbox[0])) // 2
ty = 210
for off in [(-2,-2), (2,2), (-2,2), (2,-2), (0,3)]:
    draw.text((tx + off[0], ty + off[1]), title_text, fill=(2, 132, 199), font=font_title)
draw.text((tx, ty), title_text, fill=(56, 189, 248), font=font_title)

# Subtitle: BÌNH LĂNG TRỤ TAM GIÁC
sub_text = "HIỆU ỨNG TRỰC QUAN · DỄ HIỂU · GẦN GŨI"
sbbox = font_sub.getbbox(sub_text)
sx = (W - (sbbox[2] - sbbox[0])) // 2
sy = 305
draw.text((sx, sy), sub_text, fill=(251, 191, 36), font=font_sub)

# Tagline pill with vector lightning bolts on both sides
tag_text = "ĐẦY ĐỦ MINH HỌA TỪNG BƯỚC & MẸO GIẢI NHANH 10S"
tg_bbox = font_tag.getbbox(tag_text)
tw = tg_bbox[2] - tg_bbox[0] + 80
th = tg_bbox[3] - tg_bbox[1] + 20
tx_pill = (W - tw) // 2
ty_pill = 380
draw.rounded_rectangle([tx_pill, ty_pill, tx_pill + tw, ty_pill + th], radius=16, fill=(15, 23, 42), outline=(245, 158, 11), width=2)
# Left bolt
draw_vector_bolt(draw, tx_pill + 22, ty_pill + th // 2)
# Right bolt
draw_vector_bolt(draw, tx_pill + tw - 22, ty_pill + th // 2)
# Text
draw.text((tx_pill + 40, ty_pill + 9), tag_text, fill=(253, 230, 138), font=font_tag)

# Feature Card 1: Bản chất tích phân
card1_y = frame_y + frame_h + 35
card_w = 980
card_x = (W - card_w) // 2
draw.rounded_rectangle([card_x, card1_y, card_x + card_w, card1_y + 145], radius=20, fill=(15, 23, 42), outline=(56, 189, 248), width=2)
draw.text((card_x + 30, card1_y + 16), "Bản chất: Trung bình nhiệt độ theo khối lượng", fill=(148, 163, 184), font=font_card_title)
draw.text((card_x + 30, card1_y + 64), "t₀  =  ∫ t dm / ∫ dm  =  5kH² / (½ kH²)  =  10°C", fill=(255, 255, 255), font=font_formula)

# Feature Card 2: Mẹo giải nhanh trọng tâm
card2_y = card1_y + 168
draw.rounded_rectangle([card_x, card2_y, card_x + card_w, card2_y + 145], radius=20, fill=(15, 23, 42), outline=(245, 158, 11), width=2)
draw.text((card_x + 30, card2_y + 16), "Mẹo giải nhanh 10 giây (Trọng tâm tam giác):", fill=(253, 230, 138), font=font_card_title)
draw.text((card_x + 30, card2_y + 64), "h_G = ⅔ H   ==>   t₀ = 4 + 9 · (⅔)  =  10°C", fill=(251, 191, 36), font=font_formula)
# Vector checkmark
draw_vector_check(draw, card_x + 40, card2_y + 126)
draw.text((card_x + 56, card2_y + 112), "Áp dụng chuẩn xác cho mọi dạng bình khi t(h) bậc nhất!", fill=(203, 213, 225), font=font_formula_sub)

# Bottom footer badge
ft_text = "Lưu lại và follow MTSEducation để xem thêm bài giảng hay!"
ft_bbox = font_footer.getbbox(ft_text)
ft_x = (W - (ft_bbox[2] - ft_bbox[0])) // 2
ft_y = 1810
draw.text((ft_x, ft_y), ft_text, fill=(203, 213, 225), font=font_footer)

out_dl = r'C:\Users\DELL\Documents\Downloads\ẢNH BÌA TIKTOK_GIẢI CÂU 16_VIDEO 2.png'
out_ws = r'c:\Users\DELL\Documents\CODE\DU_AN\ẢNH BÌA TIKTOK_GIẢI CÂU 16_VIDEO 2.png'
cover.save(out_dl)
cover.save(out_ws)
print("Updated Video 2 TikTok cover with vector icons!")

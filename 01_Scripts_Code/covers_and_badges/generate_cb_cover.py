import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Canvas vertical 1080x1920
W, H = 1080, 1920
cover = Image.new('RGB', (W, H), (10, 14, 26))
draw = ImageDraw.Draw(cover)

# Background subtle gradient
for y in range(H):
    r = int(10 + (25 - 10) * (y / H))
    g = int(14 + (20 - 14) * (y / H))
    b = int(26 + (45 - 26) * (y / H))
    draw.line([(0, y), (W, y)], fill=(r, g, b))

# Load illustrative frame from video
frame = cv2.imread(r'c:\Users\DELL\Documents\CODE\DU_AN\cb_frame_20s.jpg')
# Resize frame to fit nicely horizontally in 1080 width with margin
# Frame is 1920x1080 (16:9). At width 1000, height is ~562
frame_w = 1020
frame_h = int(1080 * (frame_w / 1920))
frame_resized = cv2.resize(frame, (frame_w, frame_h), interpolation=cv2.INTER_LANCZOS4)
frame_pil = Image.fromarray(cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB))

# Frame position in middle
frame_x = (W - frame_w) // 2
frame_y = 520

# Draw border & shadow around frame
border_box = [frame_x - 4, frame_y - 4, frame_x + frame_w + 4, frame_y + frame_h + 4]
draw.rounded_rectangle(border_box, radius=16, fill=(24, 32, 54), outline=(56, 189, 248), width=3)
cover.paste(frame_pil, (frame_x, frame_y))

# Fonts
font_path_bold = r'C:\Windows\Fonts\arialbd.ttf'
font_path_reg = r'C:\Windows\Fonts\arial.ttf'
font_segoe_b = r'C:\Windows\Fonts\segoeuib.ttf'

font_badge = ImageFont.truetype(font_path_bold, 28)
font_title = ImageFont.truetype(font_path_bold, 64)
font_sub = ImageFont.truetype(font_path_bold, 32)
font_card_title = ImageFont.truetype(font_path_bold, 32)
font_formula = ImageFont.truetype(font_segoe_b, 42)
font_formula_sub = ImageFont.truetype(font_path_reg, 24)
font_footer = ImageFont.truetype(font_path_bold, 30)

# Top badge
badge_text = "MTSEducation · VẬT LÝ TRỰC QUAN"
bbox = font_badge.getbbox(badge_text)
bw = bbox[2] - bbox[0] + 48
bh = bbox[3] - bbox[1] + 24
bx = (W - bw) // 2
by = 120
draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=24, fill=(30, 41, 59), outline=(56, 189, 248), width=2)
# Cyan dot
draw.ellipse([bx + 16, by + 14, bx + 28, by + 26], fill=(56, 189, 248))
draw.text((bx + 38, by + 10), badge_text, fill=(255, 255, 255), font=font_badge)

# Main Title: CÂN BẰNG NHIỆT
title_text = "CÂN BẰNG NHIỆT"
tbbox = font_title.getbbox(title_text)
tx = (W - (tbbox[2] - tbbox[0])) // 2
ty = 230
# Glowing text shadow
for off in [(-2,-2), (2,2), (-2,2), (2,-2), (0,3)]:
    draw.text((tx + off[0], ty + off[1]), title_text, fill=(180, 83, 9), font=font_title)
draw.text((tx, ty), title_text, fill=(251, 191, 36), font=font_title)

# Subtitle: NGUYÊN LÝ & PHƯƠNG TRÌNH
sub_text = "NGUYÊN LÝ & PHƯƠNG TRÌNH TRỌNG TÂM"
sbbox = font_sub.getbbox(sub_text)
sx = (W - (sbbox[2] - sbbox[0])) // 2
sy = 330
draw.text((sx, sy), sub_text, fill=(226, 232, 240), font=font_sub)

# Tagline pill: "Lý Thuyết & Thí Nghiệm Trực Quan"
tag_text = "⚡ ĐỊNH LUẬT BẢO TOÀN NĂNG LƯỢNG NHIỆT ⚡"
tag_font = ImageFont.truetype(font_path_bold, 24)
tg_bbox = tag_font.getbbox(tag_text)
tw = tg_bbox[2] - tg_bbox[0] + 36
th = tg_bbox[3] - tg_bbox[1] + 16
tx_pill = (W - tw) // 2
ty_pill = 395
draw.rounded_rectangle([tx_pill, ty_pill, tx_pill + tw, ty_pill + th], radius=16, fill=(15, 23, 42), outline=(245, 158, 11), width=2)
draw.text((tx_pill + 18, ty_pill + 8), tag_text, fill=(253, 230, 138), font=tag_font)

# Formula Card 1: Q_tỏa = Q_thu
card1_y = frame_y + frame_h + 50
card_w = 1000
card_x = (W - card_w) // 2
draw.rounded_rectangle([card_x, card1_y, card_x + card_w, card1_y + 160], radius=20, fill=(15, 23, 42), outline=(56, 189, 248), width=2)
draw.text((card_x + 30, card1_y + 20), "Phương Trình Cân Bằng Nhiệt:", fill=(148, 163, 184), font=font_card_title)
draw.text((card_x + 30, card1_y + 75), "Q_tỏa  =  Q_thu", fill=(255, 255, 255), font=font_formula)
draw.text((card_x + 550, card1_y + 85), "(Nhiệt độ cuối cân bằng: t_cb)", fill=(56, 189, 248), font=font_formula_sub)

# Formula Card 2: Q = m . c . Δt
card2_y = card1_y + 185
draw.rounded_rectangle([card_x, card2_y, card_x + card_w, card2_y + 160], radius=20, fill=(15, 23, 42), outline=(245, 158, 11), width=2)
draw.text((card_x + 30, card2_y + 20), "Công Thức Tính Nhiệt Lượng:", fill=(148, 163, 184), font=font_card_title)
draw.text((card_x + 30, card2_y + 75), "Q  =  m · c · Δt", fill=(253, 230, 138), font=font_formula)
draw.text((card_x + 530, card2_y + 85), "(Δt = |t_cuối - t_đầu|)", fill=(245, 158, 11), font=font_formula_sub)

# Bottom footer badge
ft_text = "Học Vật Lý Dễ Hiểu Cùng MTSEducation"
ft_bbox = font_footer.getbbox(ft_text)
ft_x = (W - (ft_bbox[2] - ft_bbox[0])) // 2
ft_y = 1790
draw.text((ft_x, ft_y), ft_text, fill=(203, 213, 225), font=font_footer)

out_dl = r'C:\Users\DELL\Documents\Downloads\ẢNH BÌA TIKTOK_CÂN BẰNG NHIỆT.png'
out_ws = r'c:\Users\DELL\Documents\CODE\DU_AN\ẢNH BÌA TIKTOK_CÂN BẰNG NHIỆT.png'
cover.save(out_dl)
cover.save(out_ws)
print("Saved TikTok cover to:", out_dl)

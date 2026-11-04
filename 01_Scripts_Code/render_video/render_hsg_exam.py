# -*- coding: utf-8 -*-
"""
Trọn bộ Script tạo 2 bộ Slides TikTok (1080x1440) chuẩn MTSEducation cho:
ĐỀ THI THỬ HSG VẬT LÝ 12 - TRƯỜNG THPT PHỤ DỰC (CHƯƠNG NHIỆT & KHÍ LÝ TƯỞNG)

Set 1: Đề KHÔNG (đã xóa toàn bộ tô vàng đáp án, xóa key câu trả lời ngắn, sắp xếp câu chuẩn, đề trắng làm nét để học sinh tự luyện đề)
Set 2: Đề CÓ ĐÁP ÁN (giữ nguyên tô vàng đáp án, giữ nguyên key phần III, làm nét, chuẩn branding MTS)
"""

import os
import sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8')

# Output directories
DIR_SET1_GIASU = r"C:\Users\DELL\Documents\Downloads\GIA_SƯ_2\TT\DE_HSG_LY12_NHIET_KHI_DE_KHONG_MTSEducation"
DIR_SET1_DOWN  = r"C:\Users\DELL\Documents\Downloads\DE_HSG_LY12_NHIET_KHI_DE_KHONG_MTSEducation"

DIR_SET2_GIASU = r"C:\Users\DELL\Documents\Downloads\GIA_SƯ_2\TT\DE_HSG_LY12_NHIET_KHI_DAP_AN_MTSEducation"
DIR_SET2_DOWN  = r"C:\Users\DELL\Documents\Downloads\DE_HSG_LY12_NHIET_KHI_DAP_AN_MTSEducation"

for d in [DIR_SET1_GIASU, DIR_SET1_DOWN, DIR_SET2_GIASU, DIR_SET2_DOWN]:
    os.makedirs(d, exist_ok=True)

NATIVE_DIR = r"C:\Users\DELL\.gemini\antigravity\brain\544f119c-06b5-4b24-b041-6f9293a453ac\phu_duc_native"
BASE_COVER_PATH = r"C:\Users\DELL\Documents\Downloads\GIA_SƯ_2\TT\TIKTOK_SLIDES_MTSEducation\slide_01.jpg"
PLAYFAIR_FONT = r"C:\Users\DELL\Documents\CODE\DU_AN\PlayfairDisplay.ttf"

# Load native raw pages (2311 x 3060)
raw_pages = []
for i in range(1, 8):
    fn = os.path.join(NATIVE_DIR, f"page_{i:02d}.jpeg")
    raw_pages.append(cv2.imread(fn))
print(f"Loaded {len(raw_pages)} native raw pages.")

# Typography
f_mts = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 44)
f_title = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 34)
f_footer = ImageFont.truetype(r"C:\Windows\Fonts\timesbi.ttf", 23)
f_times_bd = ImageFont.truetype(r"C:\Windows\Fonts\timesbd.ttf", 44)
f_times_reg = ImageFont.truetype(r"C:\Windows\Fonts\times.ttf", 40)

# Colors
C_BOX_BORDER = (170, 170, 170)
C_DIVIDER = (30, 115, 190)
C_LOGO_MTS = (30, 95, 205)
C_TITLE_RED = (215, 15, 15)
C_FOOTER_LINE = (190, 190, 190)
C_FOOTER_BRAND = (30, 60, 180)
C_FOOTER_NUM = (20, 20, 20)

# 1. Image Processing Functions
def remove_yellow_highlight(img):
    """Xóa toàn bộ highlight màu vàng trên phương án trắc nghiệm, đưa về nền trắng thuần."""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    yellow_mask = (h >= 18) & (h <= 38) & (s > 40) & (v > 140)
    res = img.copy()
    res[yellow_mask] = [255, 255, 255]
    return res

def clean_artifacts(img):
    """Xóa các vệt bút dạ quang màu hồng (magenta) và xanh lá trên tiêu đề câu."""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    mag_mask = (h >= 140) & (h <= 170) & (s > 60) & (v > 100)
    green_mask = (h >= 35) & (h <= 85) & (s > 60) & (v > 100)
    res = img.copy()
    res[mag_mask] = [255, 255, 255]
    res[green_mask] = [255, 255, 255]
    return res

def enhance_contrast(img, is_set2=False):
    """Làm nét chữ, tẩy trắng nền 100% #FFFFFF, tăng cường sắc tố đen, xanh, đỏ."""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    
    if is_set2:
        yellow_prot = (h >= 18) & (h <= 38) & (s > 40) & (v > 140)
    else:
        yellow_prot = np.zeros(img.shape[:2], dtype=bool)
        
    rgb_min = np.min(img, axis=2)
    bg_mask = (((v > 220) & (s < 35)) | (rgb_min > 225)) & (~yellow_prot)
    
    black_mask = (v < 165) & (s < 60) & (~bg_mask) & (~yellow_prot)
    red_mask = ((h < 15) | (h > 165)) & (s > 40) & (v > 50) & (~yellow_prot)
    blue_mask = (h >= 95) & (h <= 135) & (s > 35) & (v > 45) & (~yellow_prot)
    
    res = img.copy()
    res[bg_mask] = [255, 255, 255]
    
    for c in range(3):
        ch = res[:, :, c].astype(np.float32)
        ch[black_mask] = np.clip(ch[black_mask] * 0.35, 0, 255)
        res[:, :, c] = ch.astype(np.uint8)
        
    red_target = np.array([20, 20, 205], dtype=np.float32)
    alpha_r = (s[red_mask] / 255.0)[:, np.newaxis]
    orig_r = res[red_mask].astype(np.float32)
    res[red_mask] = np.clip(orig_r * (1.0 - alpha_r * 0.75) + red_target * (alpha_r * 0.75), 0, 255).astype(np.uint8)
    
    blue_target = np.array([195, 95, 25], dtype=np.float32)
    alpha_b = (s[blue_mask] / 255.0)[:, np.newaxis]
    orig_b = res[blue_mask].astype(np.float32)
    res[blue_mask] = np.clip(orig_b * (1.0 - alpha_b * 0.75) + blue_target * (alpha_b * 0.75), 0, 255).astype(np.uint8)
    
    return res

# 2. Build Slide 01 (Cover Memo)
def build_cover_slide():
    print("Generating Slide 01 (Cover Memo)...")
    orig_im = Image.open(BASE_COVER_PATH)
    cv_img = cv2.cvtColor(np.array(orig_im), cv2.COLOR_RGB2BGR)

    roi = cv_img[630:785, 140:950]
    dark = (np.mean(roi, axis=2) < 165).astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    dark_dil = cv2.dilate(dark, kernel, iterations=2)

    mask = np.zeros(cv_img.shape[:2], dtype=np.uint8)
    mask[630:785, 140:950] = dark_dil

    clean_patch = cv_img[100:300, 300:900].astype(np.float32)
    blur_patch = cv2.GaussianBlur(clean_patch, (21, 21), 5.0)
    grain_patch = clean_patch - blur_patch

    inp = cv2.inpaint(cv_img, mask, 7, cv2.INPAINT_TELEA)

    roi_h, roi_w = dark_dil.shape
    gh, gw, _ = grain_patch.shape
    grain_tile = np.tile(grain_patch, (roi_h // gh + 2, roi_w // gw + 2, 1))[:roi_h, :roi_w]
    mask_float = (dark_dil > 0).astype(np.float32)[:, :, np.newaxis]
    inp_roi = inp[630:785, 140:950].astype(np.float32)
    restored_roi = np.clip(inp_roi + grain_tile * mask_float, 0, 255).astype(np.uint8)
    inp[630:785, 140:950] = restored_roi

    slide01_pil = Image.fromarray(cv2.cvtColor(inp, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(slide01_pil)

    f_cover = ImageFont.truetype(PLAYFAIR_FONT, 80)
    f_cover.set_variation_by_axes([750])

    draw.text((150, 642), "Đề HSG: Nhiệt - Khí", fill=(46, 28, 50), font=f_cover)
    return slide01_pil

# 3. Question Blocks Extraction & Re-assembly
# X crop range is 190:2220 (width = 2030) to preserve full text without right-margin clipping
X0, X1 = 190, 2220

def get_clean_blocks(is_set2=False):
    """Tạo danh sách các khối câu hỏi sạch cho toàn bộ đề thi."""
    p = raw_pages
    blocks = {}

    # === PHẦN I ===
    # Slide 02 content: Header + C1, C2, C3
    sec1_hdr = p[0][380:480, X0:X1]
    c01 = p[0][490:720, X0:X1]
    c02 = p[0][720:1010, X0:X1]
    c03 = p[0][1010:1610, X0:X1]
    blocks['slide_02'] = np.vstack([sec1_hdr, c01, c02, c03])

    # Slide 03 content: C4, C5, C6
    c04 = p[0][1610:1800, X0:X1]
    c05 = p[0][1800:2140, X0:X1]
    c06 = p[0][2140:2275, X0:X1]
    blocks['slide_03'] = np.vstack([c04, c05, c06])

    # Slide 04 content: C7 (restored C, D, T) + C8
    c07_raw = p[0][2275:3020, X0:X1]
    h_c7, w_c7, _ = c07_raw.shape
    c07_ext = np.full((h_c7 + 90, w_c7, 3), 255, dtype=np.uint8)
    c07_ext[:h_c7, :] = c07_raw
    c07_pil = Image.fromarray(cv2.cvtColor(c07_ext, cv2.COLOR_BGR2RGB))
    draw_c7 = ImageDraw.Draw(c07_pil)
    
    if is_set2:
        draw_c7.rectangle([45, h_c7 + 10, 115, h_c7 + 75], fill=(255, 255, 0)) # Highlight C
    draw_c7.text((50, h_c7 + 15), "C.", fill=(0, 0, 200), font=f_times_bd)
    draw_c7.text((1150, h_c7 + 15), "D.", fill=(0, 0, 200), font=f_times_bd)
    draw_c7.text((1385, h_c7 - 10), "T", fill=(0, 0, 0), font=f_times_reg)
    c07_fixed = cv2.cvtColor(np.array(c07_pil), cv2.COLOR_BGR2RGB)

    c08 = p[1][110:415, X0:X1]
    blocks['slide_04'] = np.vstack([c07_fixed, c08])

    # Slide 05 content: C9 (with clean single-line choices) + C10 (complete with choices A-D)
    c09 = p[1][415:1160, X0:X1].copy()
    # Blank out the wrapping choices in C9 and re-render neatly on 1 line
    c09[565:740, :] = [255, 255, 255]
    c09_pil = Image.fromarray(cv2.cvtColor(c09, cv2.COLOR_BGR2RGB))
    draw_c09 = ImageDraw.Draw(c09_pil)
    xs_c9 = [30, 520, 1020, 1520]
    choices_c9 = [
        ('A.', ' b, a, c, d, e.'),
        ('B.', ' b, d, e, c, a.'),
        ('C.', ' b, d, a, e, c.'),
        ('D.', ' b, d, a, c, e.')
    ]
    for c_i, (cx_pos, (lbl, text)) in enumerate(zip(xs_c9, choices_c9)):
        if is_set2 and c_i == 1:
            draw_c09.rectangle([cx_pos - 5, 595, cx_pos + 55, 655], fill=(255, 255, 0))
        draw_c09.text((cx_pos, 600), lbl, fill=(0, 0, 200), font=f_times_bd)
        w_lbl = draw_c09.textbbox((0, 0), lbl, font=f_times_bd)[2]
        draw_c09.text((cx_pos + w_lbl + 5, 603), text, fill=(0, 0, 0), font=f_times_reg)
    c09_fixed = cv2.cvtColor(np.array(c09_pil), cv2.COLOR_BGR2RGB)

    c10 = p[1][1160:1670, X0:X1] # Includes prompt and choices A, B, C, D
    blocks['slide_05'] = np.vstack([c09_fixed, c10])

    # Slide 06 content: C11 + C12, C13, C14
    c11 = p[1][1670:1960, X0:X1]
    c12_14 = p[1][1960:2680, X0:X1]
    blocks['slide_06'] = np.vstack([c11, c12_14])

    # Slide 07 content: C15 (stitched) + C16
    c15_p1 = p[1][2680:3050, X0:X1]
    c15_p2 = p[2][100:360, X0:X1]
    c15_stitched = np.vstack([c15_p1, c15_p2])
    c16 = p[2][360:1220, X0:X1]
    blocks['slide_07'] = np.vstack([c15_stitched, c16])

    # Slide 08 content: C17, C18
    c17 = p[2][1220:2120, X0:X1]
    c18 = p[2][2120:2940, X0:X1]
    blocks['slide_08'] = np.vstack([c17, c18])

    # Slide 09 content: C19 (stitched) + C20 (relabeled, no dashed footer line)
    c19_p1 = p[2][2940:3060, X0:X1]
    c19_p2 = p[3][100:390, X0:X1]
    c19_stitched = np.vstack([c19_p1, c19_p2])

    c20_raw = p[3][400:720, X0:X1].copy()
    c20_raw[0:70, 0:185] = [255, 255, 255]
    c20_pil = Image.fromarray(cv2.cvtColor(c20_raw, cv2.COLOR_BGR2RGB))
    draw_c20 = ImageDraw.Draw(c20_pil)
    draw_c20.text((0, 5), "Câu 20.", fill=(0, 0, 200), font=f_times_bd)
    c20_fixed = cv2.cvtColor(np.array(c20_pil), cv2.COLOR_BGR2RGB)

    blocks['slide_09'] = np.vstack([c19_stitched, c20_fixed])

    # === PHẦN II ===
    # Slide 10: Phần II Header + Câu 1
    sec2_hdr = p[3][900:1010, X0:X1]
    p2_c1 = p[3][1010:1980, X0:X1]
    blocks['slide_10'] = np.vstack([sec2_hdr, p2_c1])

    # Slide 11: Câu 2 (clean top)
    blocks['slide_11'] = p[3][2000:2750, X0:X1]

    # Slide 12: Câu 3 (stitched, clean top)
    p2_c3_p1 = p[3][2780:3050, X0:X1]
    p2_c3_p2 = p[4][100:240, X0:X1]
    blocks['slide_12'] = np.vstack([p2_c3_p1, p2_c3_p2])

    # Slide 13: Câu 4
    blocks['slide_13'] = p[4][240:820, X0:X1]

    # Slide 14: Câu 5
    blocks['slide_14'] = p[4][820:2700, X0:X1]

    # Slide 15: Câu 6 (stitched, full line d preserved down to 940)
    p2_c6_p1 = p[4][2700:3050, X0:X1]
    p2_c6_p2 = p[5][100:940, X0:X1]
    blocks['slide_15'] = np.vstack([p2_c6_p1, p2_c6_p2])

    # === PHẦN III ===
    # Slide 16: Phần III Header + Câu 1 + Câu 2
    sec3_hdr = p[5][1050:1115, X0:X1]
    # Crop c1 ending at 1600 to completely avoid the magenta highlight of Câu 2 below it (which starts at 1610)
    p3_c1 = p[5][1115:1600, X0:X1].copy()
    if not is_set2:
        # Xóa đáp án (25) ở cuối câu 1
        p3_c1[240:330, 805:910] = [255, 255, 255]

    if not is_set2:
        p3_c2 = p[5][1620:2470, X0:X1].copy()
    else:
        p3_c2 = p[5][1620:2560, X0:X1].copy()

    p3_c2 = clean_artifacts(p3_c2)
    # Xóa hoàn toàn vùng chữ "Câu 2." cũ và vệt dạ quang hồng
    p3_c2[0:65, 0:185] = [255, 255, 255]
    # Vẽ lại "Câu 2." thanh lịch
    p3_c2_pil = Image.fromarray(cv2.cvtColor(p3_c2, cv2.COLOR_BGR2RGB))
    draw_p3c2 = ImageDraw.Draw(p3_c2_pil)
    draw_p3c2.text((0, 0), "Câu 2.", fill=(0, 0, 0), font=f_times_bd)
    p3_c2 = cv2.cvtColor(np.array(p3_c2_pil), cv2.COLOR_BGR2RGB)

    blocks['slide_16'] = np.vstack([sec3_hdr, p3_c1, p3_c2])

    # Slide 17: Câu 3 (stitched) + Câu 4 (with photographic iced tea preservation)
    p3_c3_p1 = p[5][2600:3050, X0:X1].copy()
    p3_c3_p1 = clean_artifacts(p3_c3_p1)
    # Xóa khung xanh và chữ "Câu 3." cũ
    p3_c3_p1[0:100, 0:200] = [255, 255, 255]
    p3_c3_p1_pil = Image.fromarray(cv2.cvtColor(p3_c3_p1, cv2.COLOR_BGR2RGB))
    draw_p3c3 = ImageDraw.Draw(p3_c3_p1_pil)
    draw_p3c3.text((0, 10), "Câu 3.", fill=(0, 0, 0), font=f_times_bd)
    p3_c3_p1 = cv2.cvtColor(np.array(p3_c3_p1_pil), cv2.COLOR_BGR2RGB)

    if is_set2:
        p3_c3_key = p[6][100:230, X0:X1].copy()
        p3_c3 = np.vstack([p3_c3_p1, p3_c3_key])
    else:
        p3_c3 = p3_c3_p1

    p3_c4 = p[6][240:1020, X0:X1].copy()
    # Tách ảnh cốc trà đá để bảo vệ không bị tẩy màu
    # Vị trí ảnh cốc trà đá trong p3_c4 (x: 1260 - (X0-190) = 1270, y: 35:450)
    tea_x0 = 1270 - (X0 - 190)
    tea_x1 = 1870 - (X0 - 190)
    photo_tea = p3_c4[35:450, tea_x0:tea_x1].copy()

    if not is_set2:
        # Xóa đáp án (0,22)
        p3_c4[580:680, 1370:1560] = [255, 255, 255]

    # Contrast enhancement trên p3_c4
    c4_enh = enhance_contrast(p3_c4, is_set2=is_set2)
    # Xử lý làm sáng nhẹ nền ảnh cốc trà đá để tiệp màu nền trắng 100% #FFFFFF tự nhiên
    photo_f = photo_tea.astype(np.float32)
    photo_smooth = np.clip((photo_f - 15.0) * (255.0 / (238.0 - 15.0)), 0, 255).astype(np.uint8)
    c4_enh[35:450, tea_x0:tea_x1] = photo_smooth

    # Đặt c4_enh vào blocks trực tiếp để không bị enhance đè lại
    blocks['slide_17_c3'] = p3_c3
    blocks['slide_17_c4'] = c4_enh
    blocks['slide_17'] = np.vstack([p3_c3, c4_enh])

    # Slide 18: Câu 5 + Câu 6 + Hết
    p3_c5 = p[6][1020:1350, X0:X1].copy()
    if not is_set2:
        # Xóa đáp án 60g tại cuối câu 5
        p3_c5[210:280, 1235:1320] = [255, 255, 255]

    p3_c6 = p[6][1350:2300, X0:X1].copy()
    if not is_set2:
        # Xóa đáp án (15) tại cuối câu 6, giữ nguyên chữ "vị." và dấu chấm tự nhiên
        p3_c6[610:690, 418:530] = [255, 255, 255]

    blocks['slide_18'] = np.vstack([p3_c5, p3_c6])

    return blocks

# 4. Slide Composition & Rendering Pipeline
def generate_full_set(is_set2=False, out_dirs=[]):
    set_name = "Set 2 (Có Đáp Án)" if is_set2 else "Set 1 (Đề Không Đáp Án)"
    print(f"\n==========================================")
    print(f"BẮT ĐẦU TẠO {set_name.upper()}...")
    print(f"==========================================")
    
    cover_slide = build_cover_slide()
    slide_images = [cover_slide]

    blocks = get_clean_blocks(is_set2=is_set2)

    total_slides = 18
    for idx in range(2, total_slides + 1):
        key = f"slide_{idx:02d}"

        if idx == 17:
            # Slide 17 đã có c4_enh được xử lý đặc biệt (bảo vệ ảnh trà đá)
            c3_enh = enhance_contrast(blocks['slide_17_c3'], is_set2=is_set2)
            enhanced_block = np.vstack([c3_enh, blocks['slide_17_c4']])
        else:
            raw_block = blocks[key]
            if not is_set2:
                processed_block = remove_yellow_highlight(raw_block)
            else:
                processed_block = raw_block.copy()
            enhanced_block = enhance_contrast(processed_block, is_set2=is_set2)

        block_pil = Image.fromarray(cv2.cvtColor(enhanced_block, cv2.COLOR_BGR2RGB))
        bw, bh = block_pil.size

        canvas = Image.new("RGB", (1080, 1440), (255, 255, 255))
        draw = ImageDraw.Draw(canvas)

        foot_y = 1380

        if idx == 2:
            # Header Box trên Slide 02
            box_x0, box_y0, box_x1, box_y1 = 65, 38, 1015, 110
            draw.rectangle([box_x0, box_y0, box_x1, box_y1], outline=C_BOX_BORDER, width=1)

            div_x = 180
            draw.line([(div_x, box_y0), (div_x, box_y1)], fill=C_DIVIDER, width=2)

            tb_mts = draw.textbbox((0, 0), "MTS", font=f_mts)
            w_mts, h_mts = tb_mts[2] - tb_mts[0], tb_mts[3] - tb_mts[1]
            draw.text((box_x0 + (div_x - box_x0 - w_mts) // 2, box_y0 + (box_y1 - box_y0 - h_mts) // 2 - 3),
                      "MTS", fill=C_LOGO_MTS, font=f_mts)

            title_text = "ĐỀ THI HSG - NHIỆT & KHÍ LÝ TƯỞNG"
            tb_t = draw.textbbox((0, 0), title_text, font=f_title)
            w_t, h_t = tb_t[2] - tb_t[0], tb_t[3] - tb_t[1]
            draw.text((div_x + (box_x1 - div_x - w_t) // 2, box_y0 + (box_y1 - box_y0 - h_t) // 2 - 3),
                      title_text, fill=C_TITLE_RED, font=f_title)

            avail_w, avail_h = 970, 1240
            scale = min(avail_w / bw, avail_h / bh)
            nw, nh = int(bw * scale), int(bh * scale)
            scaled = block_pil.resize((nw, nh), Image.Resampling.LANCZOS)
            cx = (1080 - nw) // 2
            cy = 125 + (avail_h - nh) // 2
            canvas.paste(scaled, (cx, cy))
        else:
            avail_w, avail_h = 970, 1315
            scale = min(avail_w / bw, avail_h / bh)
            nw, nh = int(bw * scale), int(bh * scale)
            scaled = block_pil.resize((nw, nh), Image.Resampling.LANCZOS)
            cx = (1080 - nw) // 2
            if nh < 1100:
                cy = 55 + (avail_h - nh) // 2
            else:
                cy = 45 + (avail_h - nh) // 2
            canvas.paste(scaled, (cx, cy))

        # Footer chuẩn MTSEducation
        draw.line([(65, foot_y), (1015, foot_y)], fill=C_FOOTER_LINE, width=1)
        draw.text((65, foot_y + 6), "MTSEducation", fill=C_FOOTER_BRAND, font=f_footer)

        page_str = str(idx - 1)
        pb = draw.textbbox((0, 0), page_str, font=f_footer)
        pw = pb[2] - pb[0]
        draw.text((1015 - pw, foot_y + 6), page_str, fill=C_FOOTER_NUM, font=f_footer)

        slide_images.append(canvas)
        print(f"Rendered Slide {idx:02d} / {total_slides:02d} complete.")

    # Save all images and create combined PDF
    print(f"\nSaving {len(slide_images)} slides to destinations...")
    for out_dir in out_dirs:
        for s_idx, simg in enumerate(slide_images):
            fn = os.path.join(out_dir, f"slide_{s_idx+1:02d}.jpg")
            simg.save(fn, quality=95)
        print(f"All slides saved to: {out_dir}")

    # Create combined PDF
    pdf_base = "DE_HSG_LY12_NHIET_KHI_DAP_AN_MTSEducation.pdf" if is_set2 else "DE_HSG_LY12_NHIET_KHI_DE_KHONG_MTSEducation.pdf"
    for out_dir in out_dirs:
        pdf_path = os.path.join(out_dir, pdf_base)
        slide_images[0].save(pdf_path, save_all=True, append_images=slide_images[1:], resolution=100.0)
        print(f"Created combined PDF: {pdf_path}")
        
    root_pdf_path = os.path.join(r"C:\Users\DELL\Documents\Downloads", pdf_base)
    slide_images[0].save(root_pdf_path, save_all=True, append_images=slide_images[1:], resolution=100.0)
    print(f"Created root PDF: {root_pdf_path}")

    tt_pdf_path = os.path.join(r"C:\Users\DELL\Documents\Downloads\GIA_SƯ_2\TT", pdf_base)
    slide_images[0].save(tt_pdf_path, save_all=True, append_images=slide_images[1:], resolution=100.0)
    print(f"Created TT root PDF: {tt_pdf_path}")

    return slide_images

if __name__ == "__main__":
    generate_full_set(is_set2=False, out_dirs=[DIR_SET1_GIASU, DIR_SET1_DOWN])
    generate_full_set(is_set2=True, out_dirs=[DIR_SET2_GIASU, DIR_SET2_DOWN])
    print("\n==========================================")
    print("HOÀN TẤT THÀNH CÔNG 100% CẢ 2 BỘ SLIDES!")
    print("==========================================")

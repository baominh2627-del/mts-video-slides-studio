# -*- coding: utf-8 -*-
r"""
Script chuyển đổi Đề thi 'DỰ ĐOÁN ĐỀ GKI_LÝ 12.pdf' thành bộ TikTok Slides 1080x1440
chuẩn giao diện MTSEducation.

Lưu trữ DUY NHẤT tại:
C:\Users\DELL\Documents\Downloads\GIA_SƯ_2\TT\TIKTOK_SLIDES_MTSEducation
"""

import os
import sys
import glob
import fitz
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8')

# 1. Paths
PDF_PATH = r"C:\Users\DELL\Documents\Downloads\DỰ ĐOÁN ĐỀ GKI_LÝ 12.pdf"
if not os.path.exists(PDF_PATH):
    # Try finding via glob if unicode path issue
    found = glob.glob(r"C:\Users\DELL\Documents\Downloads\*GKI*.pdf")
    if found:
        PDF_PATH = found[0]

BASE_COVER_PATH = r"C:\Users\DELL\Documents\CODE\DU_AN\tiktok_slides_raw\slide_01.jpg"
PLAYFAIR_FONT = r"C:\Users\DELL\Documents\CODE\DU_AN\PlayfairDisplay.ttf"

# Target Directory - ONLY ONE PLACE!
TARGET_DIR = r"C:\Users\DELL\Documents\Downloads\GIA_SƯ_2\TT\TIKTOK_SLIDES_MTSEducation"
os.makedirs(TARGET_DIR, exist_ok=True)

# 2. Typography & Colors
f_mts = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 44)
f_title = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 34)
f_footer = ImageFont.truetype(r"C:\Windows\Fonts\timesbi.ttf", 23)

C_BOX_BORDER = (170, 170, 170)
C_DIVIDER = (30, 115, 190)
C_LOGO_MTS = (30, 95, 205)
C_TITLE_RED = (215, 15, 15)
C_FOOTER_LINE = (190, 190, 190)
C_FOOTER_BRAND = (30, 60, 180)
C_FOOTER_NUM = (20, 20, 20)

# 3. Build Slide 01: Cover Memo Card
def build_cover_slide():
    print("Generating Slide 01 (Cover Memo)...")
    orig_im = Image.open(BASE_COVER_PATH)
    cv_img = cv2.cvtColor(np.array(orig_im), cv2.COLOR_RGB2BGR)

    # Inpaint entire text area on memo card (500:850, 130:950)
    roi = cv_img[500:850, 130:950]
    dark = (np.mean(roi, axis=2) < 170).astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    dark_dil = cv2.dilate(dark, kernel, iterations=2)

    mask = np.zeros(cv_img.shape[:2], dtype=np.uint8)
    mask[500:850, 130:950] = dark_dil

    clean_patch = cv_img[100:300, 300:900].astype(np.float32)
    blur_patch = cv2.GaussianBlur(clean_patch, (21, 21), 5.0)
    grain_patch = clean_patch - blur_patch

    inp = cv2.inpaint(cv_img, mask, 7, cv2.INPAINT_TELEA)

    roi_h, roi_w = dark_dil.shape
    gh, gw, _ = grain_patch.shape
    grain_tile = np.tile(grain_patch, (roi_h // gh + 2, roi_w // gw + 2, 1))[:roi_h, :roi_w]
    mask_float = (dark_dil > 0).astype(np.float32)[:, :, np.newaxis]
    inp_roi = inp[500:850, 130:950].astype(np.float32)
    restored_roi = np.clip(inp_roi + grain_tile * mask_float, 0, 255).astype(np.uint8)
    inp[500:850, 130:950] = restored_roi

    slide01_pil = Image.fromarray(cv2.cvtColor(inp, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(slide01_pil)

    f_tag = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 28)
    f_main = ImageFont.truetype(PLAYFAIR_FONT, 70)
    f_sub = ImageFont.truetype(r"C:\Windows\Fonts\timesbd.ttf", 36)
    f_brand = ImageFont.truetype(r"C:\Windows\Fonts\timesbi.ttf", 28)

    # Tagline
    draw.text((150, 520), "DỰ ĐOÁN ĐỀ THI GIỮA KÌ I", fill=(180, 50, 50), font=f_tag)

    # Main Title
    draw.text((150, 575), "VẬT LÍ 12", fill=(35, 25, 45), font=f_main)

    # Subtitle
    draw.text((150, 680), "Chuyên đề: Vật lí nhiệt & Khí lí tưởng", fill=(60, 45, 75), font=f_sub)

    # Brand / Channel
    draw.text((150, 755), "Biên soạn & Thiết kế: MTSEducation", fill=(30, 95, 205), font=f_brand)

    return slide01_pil

# 4. Process and Render Exam Content Slides
def render_exam_slides():
    doc = fitz.open(PDF_PATH)
    print(f"Loaded PDF: {PDF_PATH} ({len(doc)} pages)")

    slides = []
    # Add Cover Slide as Slide 01
    cover_slide = build_cover_slide()
    slides.append(cover_slide)

    zoom = 3.0  # Ultra-crisp vector rendering
    mat = fitz.Matrix(zoom, zoom)

    foot_y = 1380

    for p_idx in range(len(doc)):
        page = doc[p_idx]
        pix = page.get_pixmap(matrix=mat)
        page_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        page_cv = cv2.cvtColor(np.array(page_img), cv2.COLOR_RGB2BGR)

        # Detect ink boundaries
        ink = (page_cv < 220).any(axis=2)
        row_counts = ink.sum(axis=1)

        # Content y_max: remove original PDF footer at the bottom (y > 780 pt)
        content_y_max = np.where(row_counts[:int(780 * zoom)] > 10)[0][-1] + 15

        if p_idx == 0:
            # Page 1: Start at PHẦN I (y ≈ 120 pt = 360 px in zoom 3.0)
            content_y_min = int(120 * zoom)
            ink_sub = np.where(row_counts[content_y_min:content_y_min + 120] > 10)[0]
            if len(ink_sub):
                content_y_min = content_y_min + ink_sub[0] - 10
        else:
            content_y_min = int(45 * zoom)
            ink_sub = np.where(row_counts[content_y_min:content_y_min + 150] > 10)[0]
            if len(ink_sub):
                content_y_min = content_y_min + ink_sub[0] - 10

        # Detect x boundaries
        col_counts = ink[content_y_min:content_y_max, :].sum(axis=0)
        xs = np.where(col_counts > 5)[0]
        x_min = max(0, xs[0] - 15)
        x_max = min(pix.width, xs[-1] + 15)

        cropped_block = page_img.crop((x_min, content_y_min, x_max, content_y_max))
        bw, bh = cropped_block.size

        # Create 1080x1440 canvas
        canvas = Image.new("RGB", (1080, 1440), (255, 255, 255))
        draw = ImageDraw.Draw(canvas)

        if p_idx == 0:
            # Slide 02 Header Box
            box_x0, box_y0, box_x1, box_y1 = 65, 38, 1015, 110
            draw.rectangle([box_x0, box_y0, box_x1, box_y1], outline=C_BOX_BORDER, width=1)
            div_x = 180
            draw.line([(div_x, box_y0), (div_x, box_y1)], fill=C_DIVIDER, width=2)

            tb_mts = draw.textbbox((0, 0), "MTS", font=f_mts)
            w_mts, h_mts = tb_mts[2] - tb_mts[0], tb_mts[3] - tb_mts[1]
            draw.text((box_x0 + (div_x - box_x0 - w_mts) // 2, box_y0 + (box_y1 - box_y0 - h_mts) // 2 - 3),
                      "MTS", fill=C_LOGO_MTS, font=f_mts)

            title_text = "DỰ ĐOÁN ĐỀ GKI - VẬT LÍ 12"
            tb_t = draw.textbbox((0, 0), title_text, font=f_title)
            w_t, h_t = tb_t[2] - tb_t[0], tb_t[3] - tb_t[1]
            draw.text((div_x + (box_x1 - div_x - w_t) // 2, box_y0 + (box_y1 - box_y0 - h_t) // 2 - 3),
                      title_text, fill=C_TITLE_RED, font=f_title)

            avail_w, avail_h = 970, 1240
            scale = min(avail_w / bw, avail_h / bh)
            nw, nh = int(bw * scale), int(bh * scale)
            scaled = cropped_block.resize((nw, nh), Image.Resampling.LANCZOS)
            cx = (1080 - nw) // 2
            cy = 135 + (avail_h - nh) // 2
            canvas.paste(scaled, (cx, cy))
        else:
            # Slides 03 to 08
            avail_w, avail_h = 970, 1315
            scale = min(avail_w / bw, avail_h / bh)
            nw, nh = int(bw * scale), int(bh * scale)
            scaled = cropped_block.resize((nw, nh), Image.Resampling.LANCZOS)
            cx = (1080 - nw) // 2
            if nh < 1100:
                cy = 55 + (avail_h - nh) // 2
            else:
                cy = 45 + (avail_h - nh) // 2
            canvas.paste(scaled, (cx, cy))

        # MTSEducation Footer
        draw.line([(65, foot_y), (1015, foot_y)], fill=C_FOOTER_LINE, width=1)
        draw.text((65, foot_y + 6), "MTSEducation", fill=C_FOOTER_BRAND, font=f_footer)

        page_str = str(p_idx + 1)
        pb = draw.textbbox((0, 0), page_str, font=f_footer)
        pw = pb[2] - pb[0]
        draw.text((1015 - pw, foot_y + 6), page_str, fill=C_FOOTER_NUM, font=f_footer)

        slides.append(canvas)
        print(f"Slide {p_idx + 2:02d} rendered complete (Page {p_idx + 1}).")

    return slides

# 5. Main Execution: Save strictly to TARGET_DIR
if __name__ == "__main__":
    print(f"Starting slide generation for: {PDF_PATH}")
    print(f"Destination folder (ONLY ONE): {TARGET_DIR}")

    slides = render_exam_slides()
    print(f"\nTotal slides generated: {len(slides)}")

    for idx, slide_img in enumerate(slides):
        out_fn = os.path.join(TARGET_DIR, f"slide_{idx + 1:02d}.jpg")
        # Save high quality JPEG
        slide_img.save(out_fn, quality=98)
        print(f"Saved: {out_fn}")

    print("\n==========================================")
    print("HOÀN TẤT THÀNH CÔNG! ĐÃ LƯU TẤT CẢ 8 SLIDES VÀO 1 NƠI DUY NHẤT:")
    print(TARGET_DIR)
    print("==========================================")

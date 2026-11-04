# -*- coding: utf-8 -*-
r"""
Script chuyển đổi Đề thi thành bộ ảnh TikTok Slides (1080x1440)
- Header Box Slide 02: Ảnh avatar Conan trắng đen (B&W) thay cho chữ "Hóa chất" / "MTS".
- Footer: "Hóa chất" cùng số trang.
- Bìa Memo: "Biên soạn & Thiết kế: Hóa chất".
- Thư mục lưu trữ:
  C:\Users\DELL\Documents\Downloads\GIA_SƯ_2\TT\ĐỀ 50 CÂU_ Dạng Nhúng Vật Liên Tiếp Và Dãy Số
"""

import os
import sys
import fitz
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8')

# Brand & Avatar Configuration
BRAND_NAME = "Hóa chất"
CONAN_SRC = r"C:\Users\DELL\.gemini\antigravity\brain\835e6faf-41ce-4061-8bb6-9ca9efc0ff6c\.user_uploaded\media_1793421482919_25456a2b.png"

# 1. Paths
PDF_PATH = r"C:\Users\DELL\Documents\Downloads\ĐỀ 50 CÂU_ Dạng Nhúng Vật Liên Tiếp Và Dãy Số.pdf"
if not os.path.exists(PDF_PATH):
    for f in os.listdir(r"C:\Users\DELL\Documents\Downloads"):
        if "50" in f and "Dãy Số" in f and f.endswith(".pdf"):
            PDF_PATH = os.path.join(r"C:\Users\DELL\Documents\Downloads", f)
            break

pdf_basename = os.path.splitext(os.path.basename(PDF_PATH))[0]
BASE_TT_DIR = r"C:\Users\DELL\Documents\Downloads\GIA_SƯ_2\TT"
TARGET_DIR = os.path.join(BASE_TT_DIR, pdf_basename)
os.makedirs(TARGET_DIR, exist_ok=True)

LEGACY_DIR = os.path.join(BASE_TT_DIR, "TIKTOK_SLIDES_MTSEducation")
os.makedirs(LEGACY_DIR, exist_ok=True)

BASE_COVER_PATH = r"C:\Users\DELL\Documents\CODE\DU_AN\tiktok_slides_raw\slide_01.jpg"
PLAYFAIR_FONT = r"C:\Users\DELL\Documents\CODE\DU_AN\PlayfairDisplay.ttf"

# 2. Typography & Colors
f_title = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 31)
f_footer = ImageFont.truetype(r"C:\Windows\Fonts\timesbi.ttf", 25)

C_BOX_BORDER = (170, 170, 170)
C_DIVIDER = (30, 115, 190)
C_BRAND_BLUE = (30, 95, 205)
C_TITLE_RED = (215, 15, 15)
C_FOOTER_LINE = (190, 190, 190)
C_FOOTER_BRAND = (30, 60, 180)
C_FOOTER_NUM = (20, 20, 20)

# 3. Process Conan Avatar to High-Quality B&W
def get_conan_bw_avatar(target_size=70):
    im_conan = cv2.imread(CONAN_SRC)
    if im_conan is None:
        raise FileNotFoundError(f"Cannot load Conan image from {CONAN_SRC}")

    # Inpaint copyright watermark at bottom right (rows 420:442, cols 330:444)
    mask = np.zeros(im_conan.shape[:2], dtype=np.uint8)
    roi = im_conan[420:442, 330:444]
    bright = (roi > 150).all(axis=2).astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    bright_dil = cv2.dilate(bright, kernel, iterations=1)
    mask[420:442, 330:444] = bright_dil
    inp = cv2.inpaint(im_conan, mask, 3, cv2.INPAINT_TELEA)

    # Grayscale & contrast enhancement
    gray = cv2.cvtColor(inp, cv2.COLOR_BGR2GRAY)
    p2, p98 = np.percentile(gray, (1, 99))
    gray_stretch = np.clip((gray - p2) * 255.0 / (p98 - p2), 0, 255).astype(np.uint8)
    conan_pil = Image.fromarray(gray_stretch).convert("RGB")
    avatar = conan_pil.resize((target_size, target_size), Image.Resampling.LANCZOS)
    return avatar

# 4. Build Slide 01: Cover Memo Card
def build_cover_slide():
    print(f"Generating Slide 01 (Cover Memo) - Brand: {BRAND_NAME}...")
    orig_im = Image.open(BASE_COVER_PATH)
    cv_img = cv2.cvtColor(np.array(orig_im), cv2.COLOR_RGB2BGR)

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

    f_tag = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 26)
    f_main = ImageFont.truetype(PLAYFAIR_FONT, 60)
    f_sub = ImageFont.truetype(r"C:\Windows\Fonts\timesbd.ttf", 33)
    f_brand = ImageFont.truetype(r"C:\Windows\Fonts\timesbi.ttf", 28)

    draw.text((150, 520), "CHUYÊN ĐỀ VẬT LÍ NÂNG CAO", fill=(180, 50, 50), font=f_tag)
    draw.text((150, 570), "50 BÀI TOÁN NHÚNG NHIỆT", fill=(35, 25, 45), font=f_main)
    draw.text((150, 675), "Nhúng Vật Liên Tiếp & Phương Pháp Dãy Số", fill=(60, 45, 75), font=f_sub)
    draw.text((150, 755), f"Biên soạn & Thiết kế: {BRAND_NAME}", fill=C_BRAND_BLUE, font=f_brand)

    return slide01_pil

# 5. Process and Render Exam Content Slides
def render_exam_slides():
    doc = fitz.open(PDF_PATH)
    print(f"Loaded PDF: {PDF_PATH} ({len(doc)} pages)")
    print(f"Target folder: {TARGET_DIR}")

    slides = []
    # Add Cover Slide as Slide 01
    cover_slide = build_cover_slide()
    slides.append(cover_slide)

    conan_avatar = get_conan_bw_avatar(target_size=70)

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

        # Content y_max: remove original PDF footer at the bottom (y > 780 pt = 2340 px)
        content_y_max = np.where(row_counts[:int(780 * zoom)] > 10)[0][-1] + 15

        if p_idx == 0:
            # Page 1: Start at DẠNG 1 (y ≈ 100 pt = 300 px in zoom 3.0)
            content_y_min = int(100 * zoom)
            ink_sub = np.where(row_counts[content_y_min:content_y_min + 100] > 10)[0]
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
            # Slide 02 Header Box with Conan B&W Avatar
            box_x0, box_y0, box_x1, box_y1 = 65, 38, 1015, 110
            draw.rectangle([box_x0, box_y0, box_x1, box_y1], outline=C_BOX_BORDER, width=1)
            
            # Divider line forming square avatar compartment [65..137] (72x72 px)
            div_x = 137
            draw.line([(div_x, box_y0), (div_x, box_y1)], fill=C_DIVIDER, width=2)

            # Paste Conan B&W Avatar (70x70) cleanly inside [66, 39]
            canvas.paste(conan_avatar, (box_x0 + 1, box_y0 + 1))

            # Right topic title
            title_text = "50 CÂU: NHÚNG VẬT LIÊN TIẾP & DÃY SỐ"
            tb_t = draw.textbbox((0, 0), title_text, font=f_title)
            w_t, h_t = tb_t[2] - tb_t[0], tb_t[3] - tb_t[1]
            draw.text((div_x + (box_x1 - div_x - w_t) // 2, box_y0 + (box_y1 - box_y0 - h_t) // 2 - 3),
                      title_text, fill=C_TITLE_RED, font=f_title)

            avail_w, avail_h = 970, 1240
            scale = min(avail_w / bw, avail_h / bh)
            nw, nh = int(bw * scale), int(bh * scale)
            scaled = cropped_block.resize((nw, nh), Image.Resampling.LANCZOS)
            cx = (1080 - nw) // 2
            cy = 130 + (avail_h - nh) // 2
            canvas.paste(scaled, (cx, cy))
        elif p_idx == len(doc) - 1:
            # Last page (Page 8): short content, top-align naturally
            avail_w, avail_h = 970, 1315
            scale = min(avail_w / bw, avail_h / bh)
            nw, nh = int(bw * scale), int(bh * scale)
            scaled = cropped_block.resize((nw, nh), Image.Resampling.LANCZOS)
            cx = (1080 - nw) // 2
            cy = 120
            canvas.paste(scaled, (cx, cy))
        else:
            # Slides 03 to 08
            avail_w, avail_h = 970, 1315
            scale = min(avail_w / bw, avail_h / bh)
            nw, nh = int(bw * scale), int(bh * scale)
            scaled = cropped_block.resize((nw, nh), Image.Resampling.LANCZOS)
            cx = (1080 - nw) // 2
            if nh < 1150:
                cy = 55 + (avail_h - nh) // 2
            else:
                cy = 45 + (avail_h - nh) // 2
            canvas.paste(scaled, (cx, cy))

        # Footer with "Hóa chất" branding
        draw.line([(65, foot_y), (1015, foot_y)], fill=C_FOOTER_LINE, width=1)
        draw.text((65, foot_y + 6), BRAND_NAME, fill=C_FOOTER_BRAND, font=f_footer)

        page_str = str(p_idx + 1)
        pb = draw.textbbox((0, 0), page_str, font=f_footer)
        pw = pb[2] - pb[0]
        draw.text((1015 - pw, foot_y + 6), page_str, fill=C_FOOTER_NUM, font=f_footer)

        slides.append(canvas)
        print(f"Slide {p_idx + 2:02d} rendered complete (Page {p_idx + 1}).")

    return slides

# 6. Main Execution: Save to TARGET_DIR and LEGACY_DIR
if __name__ == "__main__":
    print(f"Starting slide generation for: {PDF_PATH}")
    print(f"Primary output directory: {TARGET_DIR}")

    slides = render_exam_slides()
    print(f"\nTotal slides generated: {len(slides)}")

    for dest_dir in [TARGET_DIR, LEGACY_DIR]:
        for idx, slide_img in enumerate(slides):
            out_fn = os.path.join(dest_dir, f"slide_{idx + 1:02d}.jpg")
            slide_img.save(out_fn, quality=98)
        print(f"Saved all 9 slides to: {dest_dir}")

    print("\n==========================================")
    print("HOÀN TẤT THÀNH CÔNG! ĐÃ THAY Ô THƯƠNG HIỆU BẰNG AVATAR CONAN TRẮNG ĐEN:")
    print(TARGET_DIR)
    print("==========================================")

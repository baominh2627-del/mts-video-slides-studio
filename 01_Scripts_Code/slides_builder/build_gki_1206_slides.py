# -*- coding: utf-8 -*-
r"""
Script chuyển đổi Đề thi 'ĐỀ GHKI_LÝ 12_THPT NGÔ THÌ NHẬM_MÃ ĐỀ 1206.pdf'
thành bộ ảnh TikTok Slides (1080x1440) theo chuẩn script "Hóa chất":
- Slide 01 (Bìa Memo): "Biên soạn & Thiết kế: Hóa chất"
- Slide 02 (Trang 1): Header Box với Avatar Conan trắng đen (B&W) + Tiêu đề đỏ
- Slide 02..06: Footer "Hóa chất" + Số trang
- Lưu DUY NHẤT tại 1 nơi, tên ngắn gọn dễ hiểu:
  C:\Users\DELL\Documents\Downloads\GIA_SƯ_2\TT\ĐỀ GKI 1206
"""

import os
import sys
import shutil
import pymupdf as fitz
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8')

# Brand & Avatar Configuration
BRAND_NAME = "Hóa chất"
CONAN_SRC = r"C:\Users\DELL\.gemini\antigravity\brain\835e6faf-41ce-4061-8bb6-9ca9efc0ff6c\.user_uploaded\media_1793421482919_25456a2b.png"
BASE_COVER_PATH = r"C:\Users\DELL\Documents\CODE\DU_AN\tiktok_slides_raw\slide_01.jpg"
PLAYFAIR_FONT = r"C:\Users\DELL\Documents\CODE\DU_AN\PlayfairDisplay.ttf"

# Find input PDF (handles any rename containing 1206)
DOWNLOADS_DIR = r"C:\Users\DELL\Documents\Downloads"
PDF_PATH = None
for fname in os.listdir(DOWNLOADS_DIR):
    if "1206" in fname and fname.lower().endswith(".pdf"):
        PDF_PATH = os.path.join(DOWNLOADS_DIR, fname)
        break

if not PDF_PATH or not os.path.exists(PDF_PATH):
    raise FileNotFoundError("Không tìm thấy file PDF Mã đề 1206 trong Downloads!")

# ONLY ONE TARGET DIRECTORY matching user's requested name
OLD_DIR = r"C:\Users\DELL\Documents\Downloads\GIA_SƯ_2\TT\ĐỀ GKI 1206"
if os.path.exists(OLD_DIR):
    shutil.rmtree(OLD_DIR)

TARGET_DIR = r"C:\Users\DELL\Documents\Downloads\GIA_SƯ_2\TT\ĐỀ GHKI_LÝ 12_THPT NGÔ THÌ NHẬM_MÃ ĐỀ 1206"
os.makedirs(TARGET_DIR, exist_ok=True)

# Typography & Colors
f_title = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 29)
f_footer = ImageFont.truetype(r"C:\Windows\Fonts\timesbi.ttf", 25)

C_BOX_BORDER = (170, 170, 170)
C_DIVIDER = (30, 115, 190)
C_BRAND_BLUE = (30, 95, 205)
C_TITLE_RED = (215, 15, 15)
C_FOOTER_LINE = (190, 190, 190)
C_FOOTER_BRAND = (30, 60, 180)
C_FOOTER_NUM = (20, 20, 20)


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


def build_cover_slide(lines_4):
    print("Generating Slide 01 (Cover Memo) with Playfair Display Bold...")
    orig_im = Image.open(BASE_COVER_PATH)
    cv_img = cv2.cvtColor(np.array(orig_im), cv2.COLOR_RGB2BGR)

    # Cleanly remove original 4 lines of text (480:1100, 140:950) without blotches
    y0_roi, y1_roi = 480, 1100
    x0_roi, x1_roi = 140, 950
    roi = cv_img[y0_roi:y1_roi, x0_roi:x1_roi].astype(np.float32)

    # Blur slightly to ignore fine halftone dots when detecting dark text strokes
    roi_smooth = cv2.GaussianBlur(roi, (7, 7), 2.0)
    dark = (np.mean(roi_smooth, axis=2) < 190).astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (19, 19))
    mask = cv2.dilate(dark, kernel, iterations=1)

    # Feather mask for seamless blending
    mask_f = cv2.GaussianBlur(mask.astype(np.float32) / 255.0, (21, 21), 6.0)[:, :, np.newaxis]
    valid_w = 1.0 - (mask > 0).astype(np.float32)[:, :, np.newaxis]

    # Normalized convolution to interpolate smooth paper color across thick strokes
    num = cv2.GaussianBlur(roi * valid_w, (151, 151), 50.0)
    den = cv2.GaussianBlur(valid_w, (151, 151), 50.0)[:, :, np.newaxis] + 1e-5
    smooth_bg = num / den

    # Extract authentic paper halftone grain from strictly clean area (340:475, 260:900)
    clean_patch = cv_img[340:475, 260:900].astype(np.float32)
    blur_patch = cv2.GaussianBlur(clean_patch, (31, 31), 8.0)
    grain_patch = clean_patch - blur_patch

    roi_h, roi_w = mask.shape
    gh, gw, _ = grain_patch.shape
    grain_tile = np.tile(grain_patch, (roi_h // gh + 2, roi_w // gw + 2, 1))[:roi_h, :roi_w]

    restored_roi = roi * (1.0 - mask_f) + (smooth_bg + grain_tile) * mask_f
    cv_img[y0_roi:y1_roi, x0_roi:x1_roi] = np.clip(restored_roi, 0, 255).astype(np.uint8)

    slide01_pil = Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(slide01_pil)

    # Exact font from right image: PlayfairDisplay Bold (weight=750, size=98), color=(52, 37, 58)
    f_cover = ImageFont.truetype(PLAYFAIR_FONT, 98)
    f_cover.set_variation_by_axes([750])
    c_text = (52, 37, 58)

    start_x = 165
    start_y = 485
    line_gap = 152

    for i, line_txt in enumerate(lines_4):
        draw.text((start_x, start_y + i * line_gap), line_txt, fill=c_text, font=f_cover)

    return slide01_pil


def render_exam_slides():
    doc = fitz.open(PDF_PATH)
    print(f"Loaded PDF: {PDF_PATH} ({len(doc)} pages)")
    print(f"Target folder (ONLY ONE): {TARGET_DIR}")

    slides = []
    cover_slide = build_cover_slide([
        "Đề GHKI Lý 12",
        "Trường THPT",
        "Ngô Thì Nhậm",
        "Mã đề 1206",
    ])
    slides.append(cover_slide)

    conan_avatar = get_conan_bw_avatar(target_size=70)

    zoom = 3.0  # Ultra-crisp rendering
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

        # Content y_max: remove original PDF footer line (at y=783 pt) & footer text (at y=796 pt)
        max_allowed_y = int(781.5 * zoom)
        content_y_max = min(max_allowed_y, np.where(row_counts[:max_allowed_y] > 10)[0][-1] + 12)

        if p_idx == 0:
            # Page 1: Skip school header and horizontal line at y=157.5 pt, start at PHẦN I (y=160 pt)
            min_allowed_y = int(159.0 * zoom)
            content_y_min = min_allowed_y
            ink_sub = np.where(row_counts[content_y_min:content_y_min + 100] > 10)[0]
            if len(ink_sub):
                content_y_min = max(min_allowed_y, content_y_min + ink_sub[0] - 8)
        else:
            content_y_min = int(45 * zoom)
            ink_sub = np.where(row_counts[content_y_min:content_y_min + 150] > 10)[0]
            if len(ink_sub):
                content_y_min = content_y_min + ink_sub[0] - 10

        # Detect x boundaries across the page
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

            div_x = 137
            draw.line([(div_x, box_y0), (div_x, box_y1)], fill=C_DIVIDER, width=2)

            canvas.paste(conan_avatar, (box_x0 + 1, box_y0 + 1))

            title_text = "ĐỀ GHKI LÝ 12 - THPT NGÔ THÌ NHẬM - MÃ ĐỀ 1206"
            tb_t = draw.textbbox((0, 0), title_text, font=f_title)
            w_t, h_t = tb_t[2] - tb_t[0], tb_t[3] - tb_t[1]
            draw.text(
                (div_x + (box_x1 - div_x - w_t) // 2, box_y0 + (box_y1 - box_y0 - h_t) // 2 - 3),
                title_text,
                fill=C_TITLE_RED,
                font=f_title,
            )

            avail_w, avail_h = 970, 1240
            scale = min(avail_w / bw, avail_h / bh)
            nw, nh = int(bw * scale), int(bh * scale)
            scaled = cropped_block.resize((nw, nh), Image.Resampling.LANCZOS)
            cx = (1080 - nw) // 2
            cy = 130 + (avail_h - nh) // 2
            canvas.paste(scaled, (cx, cy))
        elif p_idx == len(doc) - 1:
            # Last page (Page 5): short content, top-align naturally
            avail_w, avail_h = 970, 1315
            scale = min(avail_w / bw, avail_h / bh)
            nw, nh = int(bw * scale), int(bh * scale)
            scaled = cropped_block.resize((nw, nh), Image.Resampling.LANCZOS)
            cx = (1080 - nw) // 2
            cy = 120
            canvas.paste(scaled, (cx, cy))
        else:
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


if __name__ == "__main__":
    slides = render_exam_slides()
    for idx, slide_img in enumerate(slides):
        out_fn = os.path.join(TARGET_DIR, f"slide_{idx + 1:02d}.jpg")
        slide_img.save(out_fn, quality=98)
        print(f"Saved: {out_fn}")

    print("\nHOÀN TẤT! Đã lưu duy nhất tại:", TARGET_DIR)

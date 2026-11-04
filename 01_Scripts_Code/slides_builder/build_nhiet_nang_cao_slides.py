# -*- coding: utf-8 -*-
import os
import sys
import shutil
import cv2
import numpy as np
from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r"C:\Users\DELL\Documents\CODE\DU_AN")
sys.path.insert(0, r"C:\Users\DELL\.gemini\antigravity\brain\7fc5fdf5-08a9-49a1-9425-2e94645c4b7e\scratch")

import build_gki_1206_slides as b
import generate_v2 as g2

SINGLE_DIR = r"C:\Users\DELL\Documents\Downloads\GIA_SƯ_2\TT\NHIỆT NÂNG CAO"
if os.path.exists(SINGLE_DIR):
    shutil.rmtree(SINGLE_DIR)
os.makedirs(SINGLE_DIR, exist_ok=True)

# Clean up any duplicate folders created by g2 import
for d in g2.DEST_DIRS:
    if os.path.exists(d):
        shutil.rmtree(d)

# Also remove old v1 PDF in Downloads if present
for f in os.listdir(r"C:\Users\DELL\Documents\Downloads"):
    if "Viết Tay" in f and f.endswith(".pdf"):
        try:
            os.remove(os.path.join(r"C:\Users\DELL\Documents\Downloads", f))
        except Exception:
            pass

slides = []
slides.append(b.build_cover_slide([
    "Giải chi tiết",
    "Bài tập Nhiệt",
    "Nâng cao",
    "Vật Lí 12",
]))
conan_avatar = b.get_conan_bw_avatar(target_size=70)
zoom = g2.zoom
foot_y = 1380

for p_idx, proc in enumerate(g2.processors):
    page_img = proc()
    page_cv = cv2.cvtColor(np.array(page_img), cv2.COLOR_RGB2BGR)
    ink = (page_cv < 235).any(axis=2)
    row_counts = ink.sum(axis=1)
    max_y = int(790 * zoom)
    content_y_max = min(max_y, np.where(row_counts[:max_y] > 5)[0][-1] + 15)
    min_y = int(80 * zoom) if p_idx == 0 else int(42 * zoom)
    ink_sub = np.where(row_counts[min_y:min_y + 150] > 5)[0]
    content_y_min = max(min_y, min_y + ink_sub[0] - 8) if len(ink_sub) else min_y
    col_counts = ink[content_y_min:content_y_max, :].sum(axis=0)
    xs = np.where(col_counts > 5)[0]
    x_min, x_max = max(0, xs[0] - 15), min(page_img.width, xs[-1] + 15)
    cropped = page_img.crop((x_min, content_y_min, x_max, content_y_max))
    bw, bh = cropped.size
    canvas = Image.new("RGB", (1080, 1440), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    if p_idx == 0:
        box_x0, box_y0, box_x1, box_y1 = 65, 38, 1015, 110
        draw.rectangle([box_x0, box_y0, box_x1, box_y1], outline=b.C_BOX_BORDER, width=1)
        div_x = 137
        draw.line([(div_x, box_y0), (div_x, box_y1)], fill=b.C_DIVIDER, width=2)
        canvas.paste(conan_avatar, (box_x0 + 1, box_y0 + 1))
        title_text = "GIẢI CHI TIẾT BÀI TẬP NHIỆT NÂNG CAO"
        tb_t = draw.textbbox((0, 0), title_text, font=b.f_title)
        w_t, h_t = tb_t[2] - tb_t[0], tb_t[3] - tb_t[1]
        draw.text((div_x + (box_x1 - div_x - w_t) // 2, box_y0 + (box_y1 - box_y0 - h_t) // 2 - 3), title_text, fill=b.C_TITLE_RED, font=b.f_title)
        avail_w, avail_h = 970, 1240
        scale = min(avail_w / bw, avail_h / bh)
        nw, nh = int(bw * scale), int(bh * scale)
        scaled = cropped.resize((nw, nh), Image.Resampling.LANCZOS)
        canvas.paste(scaled, ((1080 - nw) // 2, 130 + (avail_h - nh) // 2))
    else:
        avail_w, avail_h = 970, 1315
        scale = min(avail_w / bw, avail_h / bh)
        nw, nh = int(bw * scale), int(bh * scale)
        scaled = cropped.resize((nw, nh), Image.Resampling.LANCZOS)
        cy = 100 if p_idx == len(g2.processors) - 1 and nh < 1000 else 50 + (avail_h - nh) // 2
        canvas.paste(scaled, ((1080 - nw) // 2, cy))
    draw.line([(65, foot_y), (1015, foot_y)], fill=b.C_FOOTER_LINE, width=1)
    draw.text((65, foot_y + 6), b.BRAND_NAME, fill=b.C_FOOTER_BRAND, font=b.f_footer)
    page_str = str(p_idx + 1)
    pb = draw.textbbox((0, 0), page_str, font=b.f_footer)
    draw.text((1015 - (pb[2] - pb[0]), foot_y + 6), page_str, fill=b.C_FOOTER_NUM, font=b.f_footer)
    slides.append(canvas)

for idx, s in enumerate(slides):
    out_fn = os.path.join(SINGLE_DIR, f"slide_{idx+1:02d}.jpg")
    s.save(out_fn, quality=98)
    print("Saved:", out_fn)

print("DONE:", SINGLE_DIR)

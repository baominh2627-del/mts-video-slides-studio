# -*- coding: utf-8 -*-
import os
import sys
import time
import shutil
import subprocess
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

FFMPEG = r'C:\Users\DELL\AppData\Local\Programs\Python\Python313\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
SOURCE_VIDEO = r'C:\Users\DELL\Documents\Downloads\FDown.vn_Tai_video_Facebook_720p (HD)_3e54.mp4'
VOCALS_AUDIO = r'C:\Users\DELL\.gemini\antigravity\brain\544f119c-06b5-4b24-b041-6f9293a453ac\scratch\full_sep\vocals.wav'

OUT_DIR_WS = r'C:\Users\DELL\Documents\CODE\DU_AN'
OUT_DIR_DL = r'C:\Users\DELL\Documents\Downloads'

OUT_VERT_WS = os.path.join(OUT_DIR_WS, 'CÂN BẰNG NHIỆT_MTSEducation_TikTok_1080.mp4')
OUT_LAND_WS = os.path.join(OUT_DIR_WS, 'CÂN BẰNG NHIỆT_MTSEducation_1080p.mp4')

FONT_BOLD = r'C:\Windows\Fonts\segoeuib.ttf'
FONT_REG = r'C:\Windows\Fonts\segoeui.ttf'

print(f"Reading source video: {SOURCE_VIDEO}")
cap = cv2.VideoCapture(SOURCE_VIDEO)
fps = cap.get(cv2.CAP_PROP_FPS)
if fps <= 0: fps = 30.0
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
src_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
src_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
duration = total_frames / fps
print(f"Source info: {src_w}x{src_h} @ {fps} FPS, {total_frames} frames ({duration:.2f}s)")
cap.release()

# -------------------------------------------------------------
# WATERMARK CLEANING FUNCTION
# -------------------------------------------------------------
bg_ref = np.array([216, 229, 239], dtype=np.uint8)

# Pre-calculate feather weights for wood grain patch in Scene 1 & 3
_patch_w, _patch_h = 200, 17
_feather = 10
_alpha = np.ones((_patch_h, _patch_w), dtype=np.float32)
for _i in range(_feather):
    _alpha[:, _i] = _i / _feather
    _alpha[:, -1 - _i] = _i / _feather
_alpha_3d = _alpha[:, :, None]

def clean_frame(f):
    # In Scene 2 (Cream paper with graph & formulas), ROI [675:692, 600:700] is cream paper (mean > 190)
    # In Scene 1 & 3 (Physics lab illustration on wood table), it is dark wood engraving lines (mean < 170)
    is_scene_2 = f[675:692, 600:700].mean() > 190
    if is_scene_2:
        # Scene 2: Remove diagonal watermark '@dohoangtumath' across the cream background
        roi = f[160:680, 350:750]
        diff = np.abs(roi.astype(int) - bg_ref.astype(int)).max(axis=2)
        wm_mask = (diff >= 1) & (diff <= 35)
        roi[wm_mask] = bg_ref
        f[160:680, 350:750] = roi
    else:
        # Scene 1 & 3: Feathered wood grain patch seamlessly covers '@dohoangtumath' at bottom
        patch_left = f[678:695, 338:538]
        patch_feathered = (patch_left * _alpha_3d + f[678:695, 538:738] * (1.0 - _alpha_3d)).astype(np.uint8)
        f[678:695, 538:738] = patch_feathered
    return f

# -------------------------------------------------------------
# 1. RENDER VERTICAL TIKTOK VIDEO (1080 x 1920)
# -------------------------------------------------------------
print("\n" + "="*50)
print(">>> STAGE 1: RENDERING VERTICAL TIKTOK VIDEO (1080x1920)")
print("="*50)

VERT_W, VERT_H = 1080, 1920

# Pre-render static background & decorations for Vertical TikTok format
template_im = Image.new('RGB', (VERT_W, VERT_H), (10, 15, 29))
t_draw = ImageDraw.Draw(template_im)

# Subtle ambient light in center
for r in range(400, 100, -15):
    alpha = int(22 * (1.0 - r / 400.0))
    t_draw.ellipse([VERT_W//2 - r, 780 - r, VERT_W//2 + r, 780 + r], fill=(18, 38, 70))

# Fonts
f_badge = ImageFont.truetype(FONT_BOLD, 28)
f_hook = ImageFont.truetype(FONT_BOLD, 36)
f_card_h = ImageFont.truetype(FONT_BOLD, 24)
f_card_eq = ImageFont.truetype(FONT_BOLD, 38)
f_card_ans = ImageFont.truetype(FONT_BOLD, 32)
f_brand_bot = ImageFont.truetype(FONT_BOLD, 26)

# Header Badge
bw, bh = 600, 68
bx = (VERT_W - bw) // 2
t_draw.rounded_rectangle([bx, 150, bx + bw, 150 + bh], radius=34, fill=(18, 26, 47), outline=(56, 189, 248), width=2)
t_draw.ellipse([bx + 26, 150 + 24, bx + 44, 150 + 42], fill=(56, 189, 248))
h_txt = 'VẬT LÝ 12  ·  MTSEducation'
hw = t_draw.textlength(h_txt, font=f_badge)
t_draw.text((bx + (bw - hw) // 2 + 12, 150 + 16), h_txt, font=f_badge, fill=(255, 255, 255))

# Title
t_text = 'BÀI TOÁN CÂN BẰNG NHIỆT'
tw = t_draw.textlength(t_text, font=f_hook)
t_draw.text(((VERT_W - tw) // 2, 260), t_text, font=f_hook, fill=(250, 204, 21))

t_sub = 'LÊN 90°C CẦN MẤY QUẢ CẦU?'
tsw = t_draw.textlength(t_sub, font=f_hook)
t_draw.text(((VERT_W - tsw) // 2, 330), t_sub, font=f_hook, fill=(56, 189, 248))

# Bottom Formula Card
cw, ch = 840, 180
cx = (VERT_W - cw) // 2
cy = 1170
t_draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=24, fill=(18, 26, 47), outline=(56, 189, 248), width=2)

eq_title = 'PHƯƠNG TRÌNH CÂN BẰNG NHIỆT'
etw = t_draw.textlength(eq_title, font=f_card_h)
t_draw.text((cx + (cw - etw) // 2, cy + 18), eq_title, font=f_card_h, fill=(148, 163, 184))

eq_val1 = 'Q_tỏa = Q_thu    ->    m1c1 = 3mc'
eqw1 = t_draw.textlength(eq_val1, font=f_card_eq)
t_draw.text((cx + (cw - eqw1) // 2, cy + 58), eq_val1, font=f_card_eq, fill=(255, 255, 255))

eq_val2 = '10n · mc = 3mc · 70    ->    ĐÁP ÁN: 21 QUẢ'
eqw2 = t_draw.textlength(eq_val2, font=f_card_ans)
t_draw.text((cx + (cw - eqw2) // 2, cy + 118), eq_val2, font=f_card_ans, fill=(56, 189, 248))

# Footer
ft_text = 'MTSEducation  ·  Vật Lý Trực Quan'
ftw = t_draw.textlength(ft_text, font=f_brand_bot)
t_draw.text(((VERT_W - ftw) // 2, 1750), ft_text, font=f_brand_bot, fill=(56, 189, 248))

template_bgr = cv2.cvtColor(np.array(template_im), cv2.COLOR_RGB2BGR)

# Target animation positioning inside 1080x1920
anim_w = 1000
anim_h = int(src_h * (anim_w / src_w)) # 562 px
anim_x = (VERT_W - anim_w) // 2
anim_y = 520

# Add neon cyan border to template_bgr around the animation slot
cv2.rectangle(template_bgr, (anim_x - 3, anim_y - 3), (anim_x + anim_w + 3, anim_y + anim_h + 3), (248, 189, 56), 3)

# Start FFmpeg process for Vertical video
cmd_vert = [
    FFMPEG, '-y',
    '-f', 'rawvideo',
    '-vcodec', 'rawvideo',
    '-s', f'{VERT_W}x{VERT_H}',
    '-pix_fmt', 'bgr24',
    '-r', f'{fps}',
    '-i', '-',
    '-i', VOCALS_AUDIO,
    '-map', '0:v',
    '-map', '1:a',
    '-c:v', 'libx264',
    '-preset', 'fast',
    '-crf', '18',
    '-pix_fmt', 'yuv420p',
    '-c:a', 'aac',
    '-b:a', '192k',
    '-shortest',
    OUT_VERT_WS
]

log_vert = open(r'C:\Users\DELL\Documents\CODE\DU_AN\ffmpeg_vert.log', 'w', encoding='utf-8')
proc_vert = subprocess.Popen(cmd_vert, stdin=subprocess.PIPE, stderr=log_vert)

cap = cv2.VideoCapture(SOURCE_VIDEO)
frame_idx = 0
t0 = time.time()

while True:
    ret, frame = cap.read()
    if not ret: break

    # Clean watermarks
    frame = clean_frame(frame)

    # Scale animation to 1000x562
    frame_scaled = cv2.resize(frame, (anim_w, anim_h), interpolation=cv2.INTER_CUBIC)

    # Compose into template canvas
    canvas = template_bgr.copy()
    canvas[anim_y:anim_y+anim_h, anim_x:anim_x+anim_w] = frame_scaled

    # Pipe to FFmpeg
    proc_vert.stdin.write(canvas.tobytes())

    frame_idx += 1
    if frame_idx % 500 == 0 or frame_idx == total_frames:
        elapsed = time.time() - t0
        cur_fps = frame_idx / elapsed if elapsed > 0 else 0
        pct = (frame_idx / total_frames) * 100
        eta = (total_frames - frame_idx) / cur_fps if cur_fps > 0 else 0
        print(f"Vertical: {frame_idx}/{total_frames} ({pct:.1f}%) | {cur_fps:.1f} fps | ETA: {eta:.1f}s")

cap.release()
proc_vert.stdin.close()
proc_vert.wait()
log_vert.close()
print(f"Vertical video render completed in {time.time() - t0:.2f}s!")

# -------------------------------------------------------------
# 2. RENDER LANDSCAPE FULL HD VIDEO (1920 x 1080)
# -------------------------------------------------------------
print("\n" + "="*50)
print(">>> STAGE 2: RENDERING LANDSCAPE 1080P VIDEO (1920x1080)")
print("="*50)

LAND_W, LAND_H = 1920, 1080

# Pre-render Landscape Watermark Badge (310x70)
w_img = Image.new('RGBA', (310, 70), (0, 0, 0, 0))
w_draw = ImageDraw.Draw(w_img)
font_brand = ImageFont.truetype(FONT_BOLD, 30)
w_draw.rounded_rectangle([0, 0, 310, 70], radius=18, fill=(15, 23, 42, 230), outline=(56, 189, 248, 240), width=2)
w_draw.ellipse([22, 24, 40, 42], fill=(56, 189, 248, 255))
w_draw.text((54, 14), 'MTSEducation', font=font_brand, fill=(255, 255, 255, 255))

w_np = np.array(w_img)
w_bgr = cv2.cvtColor(w_np[:, :, :3], cv2.COLOR_RGB2BGR)
w_alpha = (w_np[:, :, 3].astype(float) / 255.0)[:, :, np.newaxis]

cmd_land = [
    FFMPEG, '-y',
    '-f', 'rawvideo',
    '-vcodec', 'rawvideo',
    '-s', f'{LAND_W}x{LAND_H}',
    '-pix_fmt', 'bgr24',
    '-r', f'{fps}',
    '-i', '-',
    '-i', VOCALS_AUDIO,
    '-map', '0:v',
    '-map', '1:a',
    '-c:v', 'libx264',
    '-preset', 'fast',
    '-crf', '18',
    '-pix_fmt', 'yuv420p',
    '-c:a', 'aac',
    '-b:a', '192k',
    '-shortest',
    OUT_LAND_WS
]

log_land = open(r'C:\Users\DELL\Documents\CODE\DU_AN\ffmpeg_land.log', 'w', encoding='utf-8')
proc_land = subprocess.Popen(cmd_land, stdin=subprocess.PIPE, stderr=log_land)

cap = cv2.VideoCapture(SOURCE_VIDEO)
frame_idx = 0
t0 = time.time()

while True:
    ret, frame = cap.read()
    if not ret: break

    # Clean watermarks
    frame = clean_frame(frame)

    # Scale to 1920x1080 Full HD
    frame_1080p = cv2.resize(frame, (LAND_W, LAND_H), interpolation=cv2.INTER_CUBIC)

    # Blend top-left MTSEducation badge: y: 35..105, x: 40..350
    roi_b = frame_1080p[35:105, 40:350]
    frame_1080p[35:105, 40:350] = np.clip(roi_b.astype(float) * (1.0 - w_alpha) + w_bgr.astype(float) * w_alpha, 0, 255).astype(np.uint8)

    # Pipe to FFmpeg
    proc_land.stdin.write(frame_1080p.tobytes())

    frame_idx += 1
    if frame_idx % 500 == 0 or frame_idx == total_frames:
        elapsed = time.time() - t0
        cur_fps = frame_idx / elapsed if elapsed > 0 else 0
        pct = (frame_idx / total_frames) * 100
        eta = (total_frames - frame_idx) / cur_fps if cur_fps > 0 else 0
        print(f"Landscape: {frame_idx}/{total_frames} ({pct:.1f}%) | {cur_fps:.1f} fps | ETA: {eta:.1f}s")

cap.release()
proc_land.stdin.close()
proc_land.wait()
log_land.close()
print(f"Landscape video render completed in {time.time() - t0:.2f}s!")

# -------------------------------------------------------------
# 3. COPY OUTPUTS TO DOWNLOADS WITH COMPATIBILITY NAMES
# -------------------------------------------------------------
print("\n" + "="*50)
print(">>> STAGE 3: COPYING DELIVERABLES TO TARGET FOLDERS")
print("="*50)

# Vertical TikTok Deliverables
shutil.copy2(OUT_VERT_WS, os.path.join(OUT_DIR_DL, 'CÂN BẰNG NHIỆT_MTSEducation_TikTok_1080.mp4'))
shutil.copy2(OUT_VERT_WS, os.path.join(OUT_DIR_DL, 'CÂN BẰNG NHIỆT_MTSEducation.mp4'))
shutil.copy2(OUT_VERT_WS, os.path.join(OUT_DIR_DL, 'FDown.vn_Tai_video_Facebook_720p (HD)_3e54_MTSEducation.mp4'))

# Landscape 1080p Deliverables
shutil.copy2(OUT_LAND_WS, os.path.join(OUT_DIR_DL, 'CÂN BẰNG NHIỆT_MTSEducation_1080p.mp4'))

print("All deliverables copied successfully to Downloads!")

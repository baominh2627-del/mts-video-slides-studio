import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import time
import shutil
import subprocess
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SOURCE_VIDEO = r'C:\Users\DELL\Documents\Downloads\NHIỆT LƯỢNG, NỘI NĂNG, NHIỆT NĂNG.mp4'
OUTPUT_WORKSPACE = r'C:\Users\DELL\Documents\CODE\DU_AN\NHIỆT LƯỢNG, NỘI NĂNG, NHIỆT NĂNG_MTSEducation.mp4'
OUTPUT_DOWNLOADS = r'C:\Users\DELL\Documents\Downloads\NHIỆT LƯỢNG, NỘI NĂNG, NHIỆT NĂNG_MTSEducation.mp4'

FFMPEG_PATH = r'C:\Users\DELL\AppData\Local\Programs\Python\Python313\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'

print(f"Opening input video: {SOURCE_VIDEO}")
cap = cv2.VideoCapture(SOURCE_VIDEO)
fps = cap.get(cv2.CAP_PROP_FPS)
if fps <= 0:
    fps = 30.0
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
src_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
src_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
duration = total_frames / fps

print(f"Source: {src_w}x{src_h} @ {fps:.2f} FPS | Total frames: {total_frames} ({duration:.2f}s)")

# Target dimensions
OUT_W, OUT_H = 1080, 1920

# 1. Pre-render Top-Left Watermark Patch: [40, 48, 330, 114]
w_w, w_h = 290, 66
w_img = Image.new('RGBA', (w_w, w_h), (0, 0, 0, 0))
w_draw = ImageDraw.Draw(w_img)
font_bold = r'C:\Windows\Fonts\segoeuib.ttf'
font_brand = ImageFont.truetype(font_bold, 28)

w_draw.rounded_rectangle([0, 0, w_w, w_h], radius=16, fill=(15, 23, 42, 220), outline=(56, 189, 248, 240), width=2)
w_draw.ellipse([20, 23, 36, 39], fill=(56, 189, 248, 255))
w_draw.text((48, 12), 'MTSEducation', font=font_brand, fill=(255, 255, 255, 255))

w_np = np.array(w_img)
w_bgr = cv2.cvtColor(w_np[:, :, :3], cv2.COLOR_RGB2BGR)
w_alpha = (w_np[:, :, 3].astype(float) / 255.0)[:, :, np.newaxis]

# 2. Pre-render Outro Replacement Card Patch: bw = 506, bh = 218
o_w, o_h = 506, 218
o_img = Image.new('RGBA', (o_w, o_h), (0, 0, 0, 0))
o_draw = ImageDraw.Draw(o_img)
f_logo = ImageFont.truetype(font_bold, 46)
f_sub = ImageFont.truetype(font_bold, 22)
f_tag = ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf', 21)

o_draw.rounded_rectangle([0, 0, o_w, o_h], radius=24, fill=(13, 20, 36, 255), outline=(56, 189, 248, 255), width=3)
o_draw.rounded_rectangle([20, 18, o_w - 20, 98], radius=16, fill=(30, 41, 59, 255))

tw = o_draw.textlength('MTSEducation', font=f_logo)
o_draw.text(((o_w - tw) // 2, 28), 'MTSEducation', font=f_logo, fill=(255, 255, 255))

sw1 = o_draw.textlength('VẬT LÝ & KHOA HỌC TRỰC QUAN', font=f_sub)
o_draw.text(((o_w - sw1) // 2, 116), 'VẬT LÝ & KHOA HỌC TRỰC QUAN', font=f_sub, fill=(56, 189, 248))

sw2 = o_draw.textlength('Follow để học giỏi Vật Lý!', font=f_tag)
o_draw.text(((o_w - sw2) // 2, 156), 'Follow để học giỏi Vật Lý!', font=f_tag, fill=(203, 213, 225))

o_np = np.array(o_img)
o_bgr = cv2.cvtColor(o_np[:, :, :3], cv2.COLOR_RGB2BGR)
o_alpha = (o_np[:, :, 3].astype(float) / 255.0)[:, :, np.newaxis]

# Outro cut frame threshold (from frame 4766 onwards)
OUTRO_START_FRAME = 4766

# Start FFmpeg subprocess
cmd = [
    FFMPEG_PATH,
    '-y',
    '-f', 'rawvideo',
    '-vcodec', 'rawvideo',
    '-s', f'{OUT_W}x{OUT_H}',
    '-pix_fmt', 'bgr24',
    '-r', f'{fps}',
    '-i', '-',
    '-i', SOURCE_VIDEO,
    '-map', '0:v',
    '-map', '1:a',
    '-c:v', 'libx264',
    '-preset', 'fast',
    '-crf', '17',
    '-pix_fmt', 'yuv420p',
    '-c:a', 'copy',
    '-shortest',
    OUTPUT_WORKSPACE
]

print("Starting FFmpeg encoder...")
proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

t0 = time.time()
frame_idx = 0

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 1. Inpaint seam in 576x1024
        c_left = frame[15:140, 66].astype(float)
        c_right = frame[15:140, 84].astype(float)
        for x in range(67, 84):
            alpha = (x - 66) / 18.0
            frame[15:140, x] = np.clip(c_left * (1.0 - alpha) + c_right * alpha, 0, 255).astype(np.uint8)

        # 2. Resize to 1080x1920
        frame_1080 = cv2.resize(frame, (OUT_W, OUT_H), interpolation=cv2.INTER_CUBIC)

        # 3. Blend watermark patch
        roi_w = frame_1080[48:114, 40:330]
        frame_1080[48:114, 40:330] = np.clip(roi_w.astype(float) * (1.0 - w_alpha) + w_bgr.astype(float) * w_alpha, 0, 255).astype(np.uint8)

        # 4. Blend outro replacement card if in outro screen
        if frame_idx >= OUTRO_START_FRAME:
            roi_o = frame_1080[368:586, 287:793]
            frame_1080[368:586, 287:793] = np.clip(roi_o.astype(float) * (1.0 - o_alpha) + o_bgr.astype(float) * o_alpha, 0, 255).astype(np.uint8)

        # 5. Write frame to FFmpeg stdin
        proc.stdin.write(frame_1080.tobytes())

        frame_idx += 1
        if frame_idx % 500 == 0 or frame_idx == total_frames:
            elapsed = time.time() - t0
            cur_fps = frame_idx / elapsed if elapsed > 0 else 0
            pct = (frame_idx / total_frames) * 100
            eta = (total_frames - frame_idx) / cur_fps if cur_fps > 0 else 0
            print(f"Progress: {frame_idx}/{total_frames} ({pct:.1f}%) | {cur_fps:.1f} fps | ETA: {eta:.1f}s")

    cap.release()
    proc.stdin.close()
    print("Waiting for FFmpeg to finalize encoding...")
    proc.wait()
    _, stderr = proc.communicate()
    print("FFmpeg encoding completed successfully!")

except Exception as e:
    print(f"Error during rendering: {e}")
    if proc.stdin:
        proc.stdin.close()
    proc.kill()
    cap.release()
    sys.exit(1)

# Copy to Downloads
if os.path.exists(OUTPUT_WORKSPACE):
    size_mb = os.path.getsize(OUTPUT_WORKSPACE) / (1024 * 1024)
    print(f"Rendered file size: {size_mb:.2f} MB")
    print(f"Copying to Downloads: {OUTPUT_DOWNLOADS}...")
    shutil.copy(OUTPUT_WORKSPACE, OUTPUT_DOWNLOADS)
    print("File successfully copied to Downloads!")
else:
    print("ERROR: Output file was not created!")
    sys.exit(1)

print(f"ALL DONE in {time.time() - t0:.2f}s!")

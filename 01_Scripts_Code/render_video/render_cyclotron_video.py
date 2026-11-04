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

SOURCE_VIDEO = r'C:\Users\DELL\Documents\Downloads\FDown.vn_TikTok_Video_Downloader_3387.mp4'
OUT_WORKSPACE = r'C:\Users\DELL\Documents\CODE\DU_AN\MÁY GIA TỐC CYCLOTRON_MTSEducation.mp4'
OUT_DOWNLOADS_1 = r'C:\Users\DELL\Documents\Downloads\MÁY GIA TỐC CYCLOTRON_MTSEducation.mp4'
OUT_DOWNLOADS_2 = r'C:\Users\DELL\Documents\Downloads\FDown.vn_TikTok_Video_Downloader_3387_MTSEducation.mp4'

FFMPEG = r'C:\Users\DELL\AppData\Local\Programs\Python\Python313\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'

OUT_W, OUT_H = 1080, 1920

print(f"Opening source video: {SOURCE_VIDEO}")
cap = cv2.VideoCapture(SOURCE_VIDEO)
fps = cap.get(cv2.CAP_PROP_FPS)
if fps <= 0: fps = 30.0
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
src_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
src_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
duration = total_frames / fps
print(f"Source info: {src_w}x{src_h} @ {fps} FPS, {total_frames} frames ({duration:.2f}s)")

# 1. Pre-render 1080p Watermark Patch (290x66)
w_w, w_h = 290, 66
w_img = Image.new('RGBA', (w_w, w_h), (0, 0, 0, 0))
w_draw = ImageDraw.Draw(w_img)
font_bold = r'C:\Windows\Fonts\segoeuib.ttf'
font_brand = ImageFont.truetype(font_bold, 28)
w_draw.rounded_rectangle([0, 0, w_w, w_h], radius=16, fill=(15, 23, 42, 230), outline=(56, 189, 248, 240), width=2)
w_draw.ellipse([20, 23, 36, 39], fill=(56, 189, 248, 255))
w_draw.text((48, 12), 'MTSEducation', font=font_brand, fill=(255, 255, 255, 255))
w_np = np.array(w_img)
w_bgr = cv2.cvtColor(w_np[:, :, :3], cv2.COLOR_RGB2BGR)
w_alpha = (w_np[:, :, 3].astype(float) / 255.0)[:, :, np.newaxis]

# 2. Pre-render 1080p Bottom Footer Patch (600x56)
b_w, b_h = 600, 56
b_img = Image.new('RGBA', (b_w, b_h), (0, 0, 0, 0))
b_draw = ImageDraw.Draw(b_img)
b_draw.rounded_rectangle([0, 0, b_w, b_h], radius=28, fill=(15, 23, 42, 230), outline=(56, 189, 248, 200), width=2)
b_draw.ellipse([24, 20, 40, 36], fill=(56, 189, 248, 255))
bot_text = "MTSEducation  ·  Vật Lý Trực Quan"
btw = b_draw.textlength(bot_text, font=ImageFont.truetype(font_bold, 24))
b_draw.text(((b_w - btw) // 2 + 10, 12), bot_text, font=ImageFont.truetype(font_bold, 24), fill=(255, 255, 255, 255))
b_np = np.array(b_img)
b_bgr = cv2.cvtColor(b_np[:, :, :3], cv2.COLOR_RGB2BGR)
b_alpha = (b_np[:, :, 3].astype(float) / 255.0)[:, :, np.newaxis]

# Start FFmpeg subprocess
log_file = open(r'C:\Users\DELL\Documents\CODE\DU_AN\ffmpeg_cyclotron.log', 'w', encoding='utf-8')
ffmpeg_cmd = [
    FFMPEG, '-y',
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
    OUT_WORKSPACE
]

print("Starting FFmpeg encoder...")
proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=log_file)

t0 = time.time()
frame_idx = 0

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 1. Clean top-left logo area: x: 35 to 135, y: 35 to 125
        tl_bg = frame[20:35, 35:135].mean(axis=(0, 1))
        frame[35:125, 35:135] = tl_bg

        # 2. Clean bottom text area: x: 40 to 536, y: 955 to 992
        bot_bg = frame[935:950, 40:536].mean(axis=(0, 1))
        frame[955:992, 40:536] = bot_bg

        # 3. Resize to 1080x1920
        frame_1080 = cv2.resize(frame, (OUT_W, OUT_H), interpolation=cv2.INTER_CUBIC)

        # 4. Blend top-left watermark patch: y: 48..114, x: 40..330
        roi_w = frame_1080[48:114, 40:330]
        frame_1080[48:114, 40:330] = np.clip(roi_w.astype(float) * (1.0 - w_alpha) + w_bgr.astype(float) * w_alpha, 0, 255).astype(np.uint8)

        # 5. Blend bottom footer patch: y: 1795..1851, x: 240..840
        roi_b = frame_1080[1795:1851, 240:840]
        frame_1080[1795:1851, 240:840] = np.clip(roi_b.astype(float) * (1.0 - b_alpha) + b_bgr.astype(float) * b_alpha, 0, 255).astype(np.uint8)

        # 6. Pipe frame to FFmpeg
        proc.stdin.write(frame_1080.tobytes())

        frame_idx += 1
        if frame_idx % 600 == 0 or frame_idx == total_frames:
            elapsed = time.time() - t0
            cur_fps = frame_idx / elapsed if elapsed > 0 else 0
            pct = (frame_idx / total_frames) * 100
            eta = (total_frames - frame_idx) / cur_fps if cur_fps > 0 else 0
            print(f"Progress: {frame_idx}/{total_frames} ({pct:.1f}%) | Speed: {cur_fps:.1f} fps | ETA: {eta:.1f}s")

    cap.release()
    proc.stdin.close()
    print("Waiting for FFmpeg to finalize encoding...")
    proc.wait()
    log_file.close()

except Exception as e:
    print(f"Error during render: {e}")
    if proc.stdin: proc.stdin.close()
    proc.kill()
    cap.release()
    log_file.close()
    sys.exit(1)

# Copy to target files
if os.path.exists(OUT_WORKSPACE):
    size_mb = os.path.getsize(OUT_WORKSPACE) / (1024 * 1024)
    print(f"Rendered video size: {size_mb:.2f} MB")
    print(f"Copying to: {OUT_DOWNLOADS_1}")
    shutil.copy(OUT_WORKSPACE, OUT_DOWNLOADS_1)
    print(f"Copying to: {OUT_DOWNLOADS_2}")
    shutil.copy(OUT_WORKSPACE, OUT_DOWNLOADS_2)
    print("ALL DONE SUCCESSFULLY!")
else:
    print("ERROR: Output file not created!")
    sys.exit(1)

# -*- coding: utf-8 -*-
import os
import sys
import time
import shutil
import subprocess
import cv2
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

FFMPEG = r'C:\Users\DELL\AppData\Local\Programs\Python\Python313\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
INPUT_VIDEO = r'C:\Users\DELL\Documents\Downloads\MÁY GIA TỐC CYCLOTRON.mp4'
OUT_VIDEO = r'C:\Users\DELL\Documents\CODE\DU_AN\MÁY GIA TỐC CYCLOTRON_CLEANED.mp4'

print(f"Reading input video: {INPUT_VIDEO}")
cap = cv2.VideoCapture(INPUT_VIDEO)
fps = cap.get(cv2.CAP_PROP_FPS)
if fps <= 0: fps = 30.0
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
duration = total_frames / fps
print(f"Input info: {w}x{h} @ {fps} FPS, {total_frames} frames ({duration:.2f}s)")

# Extract clean background patch from frame 1860 (just before banner appears at 1862)
cap.set(cv2.CAP_PROP_POS_FRAMES, 1860)
ret, f_ref = cap.read()
if not ret:
    print("Error reading frame 1860!")
    sys.exit(1)

# Clean slate background patch
patch_y1, patch_y2 = 1025, 1325
patch_x1, patch_x2 = 145, 935
patch = f_ref[patch_y1:patch_y2, patch_x1:patch_x2].copy()

# Vertical feathering (8 pixels on top and bottom) to ensure 100% invisible edge blending
ph, pw = patch.shape[:2]
feather = 8
alpha = np.ones((ph, pw), dtype=np.float32)
for i in range(feather):
    alpha[i, :] = i / feather
    alpha[-1 - i, :] = i / feather
alpha_3d = alpha[:, :, None]

# Reset capture to start
cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

# Start FFmpeg subprocess
log_file = open(r'C:\Users\DELL\Documents\CODE\DU_AN\ffmpeg_banner.log', 'w', encoding='utf-8')
ffmpeg_cmd = [
    FFMPEG, '-y',
    '-f', 'rawvideo',
    '-vcodec', 'rawvideo',
    '-s', f'{w}x{h}',
    '-pix_fmt', 'bgr24',
    '-r', f'{fps}',
    '-i', '-',
    '-i', INPUT_VIDEO,
    '-map', '0:v',
    '-map', '1:a',
    '-c:v', 'libx264',
    '-preset', 'fast',
    '-crf', '17',
    '-pix_fmt', 'yuv420p',
    '-c:a', 'copy',
    '-shortest',
    OUT_VIDEO
]

print("Starting FFmpeg encoder...")
proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=log_file)

t0 = time.time()
frame_idx = 0

BANNER_START = 1862
BANNER_END = 2222

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Remove banner if in banner range
        if BANNER_START <= frame_idx <= BANNER_END:
            orig_roi = frame[patch_y1:patch_y2, patch_x1:patch_x2].astype(float)
            blended = orig_roi * (1.0 - alpha_3d) + patch.astype(float) * alpha_3d
            frame[patch_y1:patch_y2, patch_x1:patch_x2] = np.clip(blended, 0, 255).astype(np.uint8)

        # Pipe frame to FFmpeg
        proc.stdin.write(frame.tobytes())

        frame_idx += 1
        if frame_idx % 1000 == 0 or frame_idx == total_frames:
            elapsed = time.time() - t0
            cur_fps = frame_idx / elapsed if elapsed > 0 else 0
            pct = (frame_idx / total_frames) * 100
            eta = (total_frames - frame_idx) / cur_fps if cur_fps > 0 else 0
            print(f"Progress: {frame_idx}/{total_frames} ({pct:.1f}%) | {cur_fps:.1f} fps | ETA: {eta:.1f}s")

    cap.release()
    proc.stdin.close()
    print("Waiting for FFmpeg to finalize encoding...")
    proc.wait()
    log_file.close()
    print(f"Render completed in {time.time() - t0:.2f}s!")

except Exception as e:
    print(f"Error during render: {e}")
    if proc.stdin: proc.stdin.close()
    proc.kill()
    cap.release()
    log_file.close()
    sys.exit(1)

# Check output file
if os.path.exists(OUT_VIDEO):
    size_mb = os.path.getsize(OUT_VIDEO) / (1024 * 1024)
    print(f"Rendered video size: {size_mb:.2f} MB")
    
    # Target destination copies
    targets = [
        r'C:\Users\DELL\Documents\Downloads\MÁY GIA TỐC CYCLOTRON.mp4',
        r'C:\Users\DELL\Documents\Downloads\MÁY GIA TỐC CYCLOTRON_CHỈNH SỬA.mp4',
        r'C:\Users\DELL\Documents\Downloads\MÁY GIA TỐC CYCLOTRON_MTSEducation.mp4',
        r'C:\Users\DELL\Documents\CODE\DU_AN\MÁY GIA TỐC CYCLOTRON_CHỈNH SỬA_1080p.mp4',
        r'C:\Users\DELL\Documents\CODE\DU_AN\MÁY GIA TỐC CYCLOTRON_MTSEducation.mp4'
    ]
    
    for t_path in targets:
        print(f"Copying to: {t_path}")
        shutil.copy2(OUT_VIDEO, t_path)
        
    print("ALL TARGETS UPDATED SUCCESSFULLY!")
else:
    print("ERROR: Output file not found!")
    sys.exit(1)

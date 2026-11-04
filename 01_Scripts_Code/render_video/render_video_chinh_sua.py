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

SOURCE_VIDEO = r'C:\Users\DELL\Documents\Downloads\NHIỆT LƯỢNG, NỘI NĂNG, NHIỆT NĂNG.mp4'
BGM_MUSIC = r'C:\Users\DELL\Documents\Downloads\Van_Huann_vhremixx_mashup_violin.mp3'
MIXED_AUDIO = r'C:\Users\DELL\Documents\CODE\DU_AN\mixed_audio_1024.wav'

OUTPUT_WORKSPACE = r'C:\Users\DELL\Documents\CODE\DU_AN\VIDEO CHỈNH SỬA.mp4'
OUTPUT_DOWNLOADS = r'C:\Users\DELL\Documents\Downloads\VIDEO CHỈNH SỬA.mp4'

FFMPEG = r'C:\Users\DELL\AppData\Local\Programs\Python\Python313\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'

SPEED = 1.35  # Matching CapCut's 1.35x speed
OUT_W, OUT_H = 1080, 1920
FPS = 30.0

print(f"Step 1: Generating mixed audio (Speed: {SPEED}x, BGM: Violin remix)...")
# 1. Generate mixed audio: voice atempo=1.35, volume=1.3; bgm volume=0.45; duration=121.43s
audio_cmd = [
    FFMPEG, '-y',
    '-i', SOURCE_VIDEO,
    '-stream_loop', '2', '-i', BGM_MUSIC,
    '-filter_complex',
    f'[0:a]atempo={SPEED},volume=1.3[voice];'
    '[1:a]volume=0.45[bgm];'
    '[voice][bgm]amix=inputs=2:duration=first:dropout_transition=2[outa]',
    '-map', '[outa]',
    '-t', '121.433',
    MIXED_AUDIO
]
res = subprocess.run(audio_cmd, capture_output=True, text=True)
if res.returncode != 0:
    print("Audio mixing failed:", res.stderr)
    sys.exit(1)
print(f"Mixed audio ready: {os.path.getsize(MIXED_AUDIO)/(1024*1024):.2f} MB")

# Step 2: Pre-render overlays at 1080p
print("Step 2: Pre-rendering 1080p watermark and outro branding patches...")
font_bold = r'C:\Windows\Fonts\segoeuib.ttf'
font_reg = r'C:\Windows\Fonts\segoeui.ttf'

# Watermark badge: [40, 48, 330, 114] -> size 290x66
w_w, w_h = 290, 66
w_img = Image.new('RGBA', (w_w, w_h), (0, 0, 0, 0))
w_draw = ImageDraw.Draw(w_img)
font_brand = ImageFont.truetype(font_bold, 28)
w_draw.rounded_rectangle([0, 0, w_w, w_h], radius=16, fill=(15, 23, 42, 220), outline=(56, 189, 248, 240), width=2)
w_draw.ellipse([20, 23, 36, 39], fill=(56, 189, 248, 255))
w_draw.text((48, 12), 'MTSEducation', font=font_brand, fill=(255, 255, 255, 255))
w_np = np.array(w_img)
w_bgr = cv2.cvtColor(w_np[:, :, :3], cv2.COLOR_RGB2BGR)
w_alpha = (w_np[:, :, 3].astype(float) / 255.0)[:, :, np.newaxis]

# Outro card: size 506x218
o_w, o_h = 506, 218
o_img = Image.new('RGBA', (o_w, o_h), (0, 0, 0, 0))
o_draw = ImageDraw.Draw(o_img)
f_logo = ImageFont.truetype(font_bold, 46)
f_sub = ImageFont.truetype(font_bold, 22)
f_tag = ImageFont.truetype(font_reg, 21)
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

# Step 3: Open video and calculate frame count
cap = cv2.VideoCapture(SOURCE_VIDEO)
total_src_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
total_out_frames = int(total_src_frames / SPEED)
print(f"Total source frames: {total_src_frames} -> Output frames: {total_out_frames} ({total_out_frames / FPS:.2f}s)")

# Outro threshold in source video: frame 4766
OUTRO_SRC_FRAME = 4766

# Start FFmpeg process
log_file = open(r'C:\Users\DELL\Documents\CODE\DU_AN\ffmpeg_render.log', 'w', encoding='utf-8')
ffmpeg_cmd = [
    FFMPEG, '-y',
    '-f', 'rawvideo',
    '-vcodec', 'rawvideo',
    '-s', f'{OUT_W}x{OUT_H}',
    '-pix_fmt', 'bgr24',
    '-r', f'{FPS}',
    '-i', '-',
    '-i', MIXED_AUDIO,
    '-map', '0:v',
    '-map', '1:a',
    '-c:v', 'libx264',
    '-preset', 'fast',
    '-crf', '17',
    '-pix_fmt', 'yuv420p',
    '-c:a', 'aac',
    '-b:a', '192k',
    '-shortest',
    OUTPUT_WORKSPACE
]

print("Step 4: Starting FFmpeg encoding pipeline...")
proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=log_file)

t0 = time.time()
cur_src_idx = -1
cached_frame = None

for out_idx in range(total_out_frames):
    target_src_idx = min(int(out_idx * SPEED), total_src_frames - 1)
    
    # Advance source frames
    while cur_src_idx < target_src_idx:
        ret, src_frame = cap.read()
        cur_src_idx += 1
        if not ret:
            break
        cached_frame = src_frame

    if cached_frame is None:
        break

    frame = cached_frame.copy()

    # 1. Inpaint top-left seam in 576x1024
    c_left = frame[15:140, 66].astype(float)
    c_right = frame[15:140, 84].astype(float)
    for x in range(67, 84):
        alpha = (x - 66) / 18.0
        frame[15:140, x] = np.clip(c_left * (1.0 - alpha) + c_right * alpha, 0, 255).astype(np.uint8)

    # 2. Resize to 1080x1920
    frame_1080 = cv2.resize(frame, (OUT_W, OUT_H), interpolation=cv2.INTER_CUBIC)

    # 3. Watermark badge
    roi_w = frame_1080[48:114, 40:330]
    frame_1080[48:114, 40:330] = np.clip(roi_w.astype(float) * (1.0 - w_alpha) + w_bgr.astype(float) * w_alpha, 0, 255).astype(np.uint8)

    # 4. Outro replacement card
    if target_src_idx >= OUTRO_SRC_FRAME:
        roi_o = frame_1080[368:586, 287:793]
        frame_1080[368:586, 287:793] = np.clip(roi_o.astype(float) * (1.0 - o_alpha) + o_bgr.astype(float) * o_alpha, 0, 255).astype(np.uint8)

    # 5. Write to FFmpeg stdin
    proc.stdin.write(frame_1080.tobytes())

    if out_idx % 400 == 0 or out_idx == total_out_frames - 1:
        elapsed = time.time() - t0
        cur_fps = (out_idx + 1) / elapsed if elapsed > 0 else 0
        pct = ((out_idx + 1) / total_out_frames) * 100
        eta = (total_out_frames - (out_idx + 1)) / cur_fps if cur_fps > 0 else 0
        print(f"Render progress: {out_idx + 1}/{total_out_frames} ({pct:.1f}%) | Speed: {cur_fps:.1f} fps | ETA: {eta:.1f}s")

cap.release()
proc.stdin.close()
print("Finalizing video encoding...")
proc.wait()
log_file.close()

if os.path.exists(OUTPUT_WORKSPACE):
    size_mb = os.path.getsize(OUTPUT_WORKSPACE) / (1024 * 1024)
    print(f"Video rendered successfully! Size: {size_mb:.2f} MB")
    print(f"Copying to Downloads: {OUTPUT_DOWNLOADS}...")
    shutil.copy(OUTPUT_WORKSPACE, OUTPUT_DOWNLOADS)
    print(f"DONE! Output available at: {OUTPUT_DOWNLOADS}")
else:
    print("ERROR: Output file not created!")
    sys.exit(1)

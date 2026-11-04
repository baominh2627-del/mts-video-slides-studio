import os
import sys
import time
import subprocess
import cv2
import numpy as np
import shutil

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

SRC_VIDEO = r"C:\Users\DELL\Documents\Downloads\GIA_SƯ_2\TT\VIDEO CHỈNH SỬA_CÂN BẰNG NHIỆT.mp4"
TEMP_OUTPUT = r"c:\Users\DELL\Documents\CODE\DU_AN\temp_rendered_white.mp4"
DST_OUTPUT_1 = r"C:\Users\DELL\Documents\Downloads\GIA_SƯ_2\TT\VIDEO CHỈNH SỬA_CÂN BẰNG NHIỆT_NỀN TRẮNG.mp4"
DST_OUTPUT_2 = r"C:\Users\DELL\Documents\Downloads\VIDEO CHỈNH SỬA_CÂN BẰNG NHIỆT_NỀN TRẮNG.mp4"
DST_OUTPUT_3 = r"C:\Users\DELL\Documents\Downloads\GIA_SƯ_2\TT\CÂN BẰNG NHIỆT_MTSEducation_1080p_NỀN TRẮNG.mp4"

FFMPEG_EXE = r"C:\Users\DELL\AppData\Local\Programs\Python\Python313\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"

print(f"=== INITIALIZING WHITE THEME RENDERER (PERFECT DYNAMIC PIPELINE) ===")
print(f"Source video: {SRC_VIDEO}")

# 1. Precompute Colorlevels LUT
lut_b = np.clip((np.arange(256).astype(float) - 10.2) / (181.05 - 10.2) * 255.0, 0, 255).astype(np.uint8)
lut_g = np.clip((np.arange(256).astype(float) - 10.2) / (191.25 - 10.2) * 255.0, 0, 255).astype(np.uint8)
lut_r = np.clip((np.arange(256).astype(float) - 10.2) / (201.45 - 10.2) * 255.0, 0, 255).astype(np.uint8)
lut = np.dstack([lut_b, lut_g, lut_r])

# 2. Kernel definitions
k_v21 = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 21))
k_col = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
k3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

# 3. Precompute Blue Color Table for Beaker Water
y_coords = np.arange(665, 965)
depth_arr = np.clip((y_coords - 675) / (945.0 - 675.0), 0.0, 1.0)
b_col = (245 * (1 - depth_arr) + 225 * depth_arr).astype(np.float32)
g_col = (195 * (1 - depth_arr) + 140 * depth_arr).astype(np.float32)
r_col = (45 * (1 - depth_arr) + 10 * depth_arr).astype(np.float32)
blue_color_table = np.stack([b_col, g_col, r_col], axis=-1)[:, None, :] # shape (300, 1, 3)

# 4. Precompute Scene 1b Bottom Water Gradient
s1b_depth = np.linspace(0.0, 1.0, 100, dtype=np.float32)[:, None, None]
s1b_blue = np.array([240, 180, 20], dtype=np.float32)
s1b_alpha = s1b_depth * 0.45

def process_frame(img, t_sec):
    h, w, c = img.shape
    
    # 1. White remap via LUT (fast ~5ms)
    white = cv2.LUT(img, lut)
    
    # Scene 2 (26.83s to 60.33s): Math slide has pure white background, no stripes
    if 26.83 <= t_sec < 60.33:
        return white

    gray = cv2.cvtColor(white, cv2.COLOR_BGR2GRAY)
    
    # 2. Base clean background via vertical dilation + thresholding at 120
    v_clean = cv2.dilate(white, k_v21)
    v_gray = cv2.cvtColor(v_clean, cv2.COLOR_BGR2GRAY)
    clean_bg = v_clean.copy()
    clean_bg[v_gray > 120] = [255, 255, 255]
    
    # 3. Dynamic Foreground Protection Mask (NO hardcoded apparatus rectangles!)
    fg_mask = np.zeros((h, w), dtype=bool)
    
    # Outer double border
    fg_mask[18:40, 18:1902] = True
    fg_mask[1040:1062, 18:1902] = True
    fg_mask[18:1062, 18:40] = True
    fg_mask[18:1062, 1880:1902] = True
    
    # Top-left badge
    fg_mask[20:105, 20:380] = True
    
    # Red features: glowing spheres, arrows, red numbers, tongs claws around spheres
    is_red = (white[:,:,2].astype(int) - white[:,:,0].astype(int) > 30) & \
             (white[:,:,2].astype(int) - white[:,:,1].astype(int) > 18)
    is_red_dilated = cv2.dilate(is_red.astype(np.uint8), k_col).astype(bool)
    fg_mask[is_red_dilated] = True
    
    # Dynamic detection of callout boxes & question card
    white_fill = (gray > 245).astype(np.uint8)
    eroded = cv2.erode(white_fill, k3)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(eroded)
    
    for i in range(1, num_labels):
        bx, by, bw, bh, area = stats[i]
        if bx < 15 or by < 15 or bx + bw > w - 15 or by + bh > h - 15:
            continue
        if bw > 850 or bh > 350:
            continue
        if bh >= 12 and bw >= 20 and area >= 300:
            pad = 4
            y1 = max(0, by - pad)
            y2 = min(h, by + bh + pad)
            x1 = max(0, bx - pad)
            x2 = min(w, bx + bw + pad)
            fg_mask[y1:y2, x1:x2] = True
            
    # Subtitle detection: only protect if subtitle card is active
    sub_sample = img[820:900, 600:1300]
    if (sub_sample < 40).mean() > 0.15:
        fg_mask[815:915, 480:1440] = True
        
    # 4. Compose output
    out = clean_bg.copy()
    out[fg_mask] = white[fg_mask]
    
    # Pure white border margins
    out[:18, :] = [255, 255, 255]
    out[1062:, :] = [255, 255, 255]
    out[:, :18] = [255, 255, 255]
    out[:, 1902:] = [255, 255, 255]
    
    # 5. Water Tinting
    if t_sec < 12.5 or t_sec >= 60.33:
        # Scene 1 & Scene 3: Wide shot with full beaker
        # Dynamically detect beaker left and right walls
        left_cands = np.where(gray[750, 880:1050] < 80)[0] + 880
        right_cands = np.where(gray[750, 1380:1520] < 80)[0] + 1380
        b_left = left_cands.min() if len(left_cands) > 0 else 940
        b_right = right_cands.max() if len(right_cands) > 0 else 1480
        cx = (b_left + b_right) / 2.0
        rx = (b_right - b_left) / 2.0
        
        x1 = max(0, int(cx - rx))
        x2 = min(w, int(cx + rx))
        if x2 > x1:
            xs = np.arange(x1, x2)
            dx_norm = ((xs - cx) / float(rx))**2
            valid_dx = (dx_norm <= 1.0)
            
            w_mask_roi = np.zeros((300, x2 - x1), dtype=np.float32)
            men_y = 675 + 15 * (1.0 - dx_norm)
            bot_y = 945 + 15 * (1.0 - dx_norm)
            for row_idx, y_val in enumerate(y_coords):
                in_water = valid_dx & (y_val >= men_y) & (y_val <= bot_y)
                w_mask_roi[row_idx, in_water] = 1.0
            w_mask_roi = cv2.GaussianBlur(w_mask_roi, (13, 13), 0)
            
            orig_roi = out[665:965, x1:x2, :].astype(np.float32)
            tint_roi = orig_roi * (blue_color_table / 255.0)
            tint_roi = np.clip(tint_roi * 1.1 + blue_color_table * 0.15, 0, 255)
            alpha_roi = w_mask_roi[:, :, None] * 0.65
            out[665:965, x1:x2, :] = (orig_roi * (1.0 - alpha_roi) + tint_roi * alpha_roi).astype(np.uint8)
            
    elif 12.5 <= t_sec < 26.83:
        # Scene 1b: Zoomed shot of thermometer column
        roi = out[940:1040, 560:1450, :].astype(np.float32)
        out[940:1040, 560:1450, :] = (roi * (1.0 - s1b_alpha) + roi * (s1b_blue / 255.0) * s1b_alpha).astype(np.uint8)
        
    return out

def main():
    cap = cv2.VideoCapture(SRC_VIDEO)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print(f"Video Info: {w}x{h} @ {fps} FPS, Total Frames: {total_frames} ({total_frames/fps:.2f}s)")

    if os.path.exists(TEMP_OUTPUT):
        try: os.remove(TEMP_OUTPUT)
        except: pass

    ffmpeg_cmd = [
        FFMPEG_EXE,
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{w}x{h}",
        "-pix_fmt", "bgr24",
        "-r", str(fps),
        "-i", "-",
        "-i", SRC_VIDEO,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "16",
        "-pix_fmt", "yuv420p",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:a", "copy",
        TEMP_OUTPUT
    ]

    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    start_time = time.time()
    print("Starting frame processing loop...")

    frame_idx = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            t_sec = frame_idx / fps
            
            processed = process_frame(frame, t_sec)
            proc.stdin.write(processed.tobytes())
            
            frame_idx += 1
            if frame_idx % 150 == 0 or frame_idx == total_frames:
                elapsed = time.time() - start_time
                fps_proc = frame_idx / elapsed if elapsed > 0 else 0
                eta = (total_frames - frame_idx) / fps_proc if fps_proc > 0 else 0
                print(f"Progress: frame {frame_idx}/{total_frames} ({frame_idx/total_frames*100:.1f}%) | "
                      f"Speed: {fps_proc:.1f} fps | Elapsed: {elapsed:.1f}s | ETA: {eta:.1f}s")
    except Exception as e:
        print(f"Error during processing: {e}")
        proc.kill()
        cap.release()
        sys.exit(1)

    cap.release()
    proc.stdin.close()
    stderr_output = proc.stderr.read().decode('utf-8', errors='ignore')
    proc.wait()

    if proc.returncode != 0:
        print(f"FFmpeg failed with return code {proc.returncode}:\n{stderr_output}")
        sys.exit(1)

    total_elapsed = time.time() - start_time
    print(f"Render completed successfully in {total_elapsed:.1f}s!")

    # Copy to all destinations
    print(f"Saving output to: {DST_OUTPUT_1}")
    shutil.copyfile(TEMP_OUTPUT, DST_OUTPUT_1)

    print(f"Saving backup to: {DST_OUTPUT_2}")
    shutil.copyfile(TEMP_OUTPUT, DST_OUTPUT_2)

    print(f"Updating copy: {DST_OUTPUT_3}")
    shutil.copyfile(TEMP_OUTPUT, DST_OUTPUT_3)

    if os.path.exists(TEMP_OUTPUT):
        try: os.remove(TEMP_OUTPUT)
        except: pass

    print("=== ALL OUTPUTS SUCCESSFULLY SAVED ===")

if __name__ == '__main__':
    main()

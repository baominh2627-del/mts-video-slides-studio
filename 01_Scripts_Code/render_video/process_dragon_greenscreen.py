import os
import subprocess
import cv2
import numpy as np

FFMPEG_EXE = r"C:\Users\DELL\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-essentials_build\bin\ffmpeg.exe"
if not os.path.exists(FFMPEG_EXE):
    FFMPEG_EXE = "ffmpeg"

OUT_DIR = r"c:\Users\DELL\Documents\CODE\DU_AN\02_San_Pham_Hoan_Chinh\Video_Rong_Nhay"
RAW_VID = os.path.join(OUT_DIR, "dragon_greenscreen_raw.mp4")
SCRATCH_DIR = r"C:\Users\DELL\.gemini\antigravity\brain\2d7fd8bc-e0e7-4a3a-b3c8-15e0f46cfe2b\scratch"
os.makedirs(SCRATCH_DIR, exist_ok=True)

# Tight crop box around the dancing dragon across all 310 frames (even dimensions: 1040x824)
CROP_X1, CROP_X2 = 0, 1040
CROP_Y1, CROP_Y2 = 530, 1354
CROP_W = CROP_X2 - CROP_X1
CROP_H = CROP_Y2 - CROP_Y1


def extract_dragon_rgba(bgr_crop: np.ndarray) -> np.ndarray:
    """
    Remove green screen (BGR ~ [11, 255, 21]) cleanly with smooth anti-aliased alpha,
    zero green halo on the black outline, and 100% protection for the dragon's yellow-green eyes.
    """
    b = bgr_crop[:, :, 0].astype(np.float32)
    g = bgr_crop[:, :, 1].astype(np.float32)
    r = bgr_crop[:, :, 2].astype(np.float32)

    # Pure background green has G ~ 255, R ~ 21, B ~ 11.
    # Dragon's yellow-green eyes have high R (R > 130), whereas green screen & its edge spill on black outline have R <= 35.
    # Measure how close each pixel is to the green screen line from (0,0,0) to (11,255,21):
    # Specifically, green excess over red and blue:
    green_excess = g - np.maximum(r * 1.35, b * 1.35)

    # Candidate background mask (pure green region)
    sure_bg = ((g > 210) & (r < 60) & (b < 60)).astype(np.uint8)

    # Flood-fill / connected components from the border so interior regions (like eyes) are never touched
    h, w = sure_bg.shape
    num_labels, labels = cv2.connectedComponents(sure_bg)
    border_labels = set(labels[0, :]).union(set(labels[h - 1, :])).union(set(labels[:, 0])).union(set(labels[:, w - 1]))
    border_labels.discard(0)
    exterior_bg = np.isin(labels, list(border_labels)).astype(np.uint8)

    # Dilate exterior_bg slightly (3px) to cover the anti-aliased transition zone on the outer black outline
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    transition_zone = cv2.dilate(exterior_bg, kernel, iterations=1) > 0

    # Compute smooth alpha in the transition zone based on green_excess
    # For pure green (green_excess >= 210) -> alpha = 0
    # For black outline (green_excess <= 25) -> alpha = 255
    alpha_float = np.ones((h, w), dtype=np.float32)
    t_alpha = 1.0 - np.clip((green_excess - 25.0) / (205.0 - 25.0), 0.0, 1.0)
    alpha_float[transition_zone] = t_alpha[transition_zone]
    alpha_float[exterior_bg > 0] = 0.0

    # De-spill green from semi-transparent edge pixels (where the dragon's black outline touches the green screen)
    # Any pixel in transition_zone had background [11, 255, 21] mixed with black [0, 0, 0]:
    bg_weight = 1.0 - alpha_float
    clean_b = np.clip(b - bg_weight * 11.0, 0, 255)
    clean_g = np.clip(g - bg_weight * 255.0, 0, 255)
    clean_r = np.clip(r - bg_weight * 21.0, 0, 255)

    # Extra de-spill for any remaining green tint on the outer contour
    edge_mask = transition_zone & (alpha_float > 0.0) & (alpha_float < 0.99)
    max_rb = np.maximum(clean_r, clean_b)
    clean_g[edge_mask] = np.minimum(clean_g[edge_mask], max_rb[edge_mask])

    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    rgba[:, :, 0] = clean_b.astype(np.uint8)
    rgba[:, :, 1] = clean_g.astype(np.uint8)
    rgba[:, :, 2] = clean_r.astype(np.uint8)
    rgba[:, :, 3] = (alpha_float * 255.0).astype(np.uint8)
    return rgba


def main():
    cap = cv2.VideoCapture(RAW_VID)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frames_rgba = []
    frames_cropped_green = []

    idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        crop = frame[CROP_Y1:CROP_Y2, CROP_X1:CROP_X2]
        rgba = extract_dragon_rgba(crop)
        frames_rgba.append(rgba)
        frames_cropped_green.append(crop)

        if idx in (0, 77, 155):
            # Save a preview on a checkerboard + dark blue background to verify quality
            yy, xx = np.indices((CROP_H, CROP_W))
            checker = (((xx // 24) + (yy // 24)) % 2) * 40 + 30
            bg = np.stack([checker + 30, checker + 10, checker], axis=-1).astype(np.float32)
            a = (rgba[:, :, 3:4].astype(np.float32)) / 255.0
            comp = (rgba[:, :, :3].astype(np.float32) * a + bg * (1.0 - a)).astype(np.uint8)
            cv2.imwrite(os.path.join(SCRATCH_DIR, f"preview_keyed_{idx}.png"), comp)
            cv2.imwrite(os.path.join(SCRATCH_DIR, f"rgba_frame_{idx}.png"), rgba)
        idx += 1
    cap.release()
    print(f"Processed {len(frames_rgba)} frames ({CROP_W}x{CROP_H} @ {fps} fps).")

    # Save raw BGRA frames via pipe to FFmpeg to produce:
    # 1. rong_nhay_trong_suot.mov (QuickTime qtrle / PNG in MOV with RGBA alpha + audio, supported by CapCut/Premiere/AE)
    mov_path = os.path.join(OUT_DIR, "rong_nhay_trong_suot.mov")
    cmd_mov = [
        FFMPEG_EXE, "-y",
        "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{CROP_W}x{CROP_H}", "-r", str(fps), "-i", "-",
        "-i", RAW_VID,
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "png", "-c:a", "aac", "-b:a", "192k", "-shortest",
        mov_path
    ]
    p_mov = subprocess.Popen(cmd_mov, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    for f in frames_rgba:
        p_mov.stdin.write(f.tobytes())
    p_mov.stdin.close()
    p_mov.wait()
    print("Saved transparent MOV:", mov_path, os.path.getsize(mov_path))

    # 2. rong_nhay_trong_suot.webm (VP9 with Alpha channel + Audio)
    webm_path = os.path.join(OUT_DIR, "rong_nhay_trong_suot.webm")
    cmd_webm = [
        FFMPEG_EXE, "-y",
        "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{CROP_W}x{CROP_H}", "-r", str(fps), "-i", "-",
        "-i", RAW_VID,
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "2M", "-auto-alt-ref", "0",
        "-c:a", "libopus", "-shortest",
        webm_path
    ]
    p_webm = subprocess.Popen(cmd_webm, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    for f in frames_rgba:
        p_webm.stdin.write(f.tobytes())
    p_webm.stdin.close()
    p_webm.wait()
    print("Saved transparent WebM:", webm_path, os.path.getsize(webm_path))

    # 3. rong_nhay_trong_suot.gif (Animated transparent GIF sticker)
    gif_path = os.path.join(OUT_DIR, "rong_nhay_trong_suot.gif")
    cmd_gif = [
        FFMPEG_EXE, "-y",
        "-i", mov_path,
        "-vf", "fps=20,scale=520:-1:flags=lanczos,split[s0][s1];[s0]palettegen=reserve_transparent=1[p];[s1][p]paletteuse=alpha_threshold=128",
        gif_path
    ]
    subprocess.run(cmd_gif, stderr=subprocess.DEVNULL, check=True)
    print("Saved transparent GIF:", gif_path, os.path.getsize(gif_path))

    # 4. rong_nhay_nen_den.mp4 (Cropped MP4 with green removed -> pure black background + audio, for Blend Mode / Screen or quick preview)
    black_mp4_path = os.path.join(OUT_DIR, "rong_nhay_nen_den.mp4")
    cmd_black = [
        FFMPEG_EXE, "-y",
        "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{CROP_W}x{CROP_H}", "-r", str(fps), "-i", "-",
        "-i", RAW_VID,
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "aac", "-b:a", "192k", "-shortest",
        black_mp4_path
    ]
    p_black = subprocess.Popen(cmd_black, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    for f in frames_rgba:
        a = (f[:, :, 3:4].astype(np.float32)) / 255.0
        bgr_on_black = (f[:, :, :3].astype(np.float32) * a).astype(np.uint8)
        p_black.stdin.write(bgr_on_black.tobytes())
    p_black.stdin.close()
    p_black.wait()
    print("Saved black-bg MP4:", black_mp4_path, os.path.getsize(black_mp4_path))

    # 5. rong_nhay_phong_xanh_da_crop.mp4 (Cropped tightly around dragon with pure green background + audio)
    crop_green_path = os.path.join(OUT_DIR, "rong_nhay_phong_xanh_da_crop.mp4")
    cmd_green = [
        FFMPEG_EXE, "-y",
        "-i", RAW_VID,
        "-vf", f"crop={CROP_W}:{CROP_H}:{CROP_X1}:{CROP_Y1}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "copy",
        crop_green_path
    ]
    subprocess.run(cmd_green, stderr=subprocess.DEVNULL, check=True)
    print("Saved cropped green-screen MP4:", crop_green_path, os.path.getsize(crop_green_path))


if __name__ == "__main__":
    main()

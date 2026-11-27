# -*- coding: utf-8 -*-
"""
Ghép Intro BM chính thức vào đầu buổi học + Đóng dấu (Watermark) mờ BM BẢO MINH
trực tiếp ở góc bảng viết OneNote xuyên suốt video bài giảng, xuất chuẩn Full HD 1920x1080.

Có thể tái sử dụng cho mọi buổi học tiếp theo:
    py -3.13 01_Scripts_Code/render_video/ghep_intro_va_watermark_bm.py -i "duong_dan_buoi_hoc.mp4"
"""

import argparse
import os
import sys
import time
import subprocess
import cv2
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

BASE_DIR = r"C:\Users\DELL\Documents\CODE\DU_AN"
DEFAULT_INTRO = os.path.join(
    BASE_DIR, "02_San_Pham_Hoan_Chinh", "Video_Intro_BM", "BM_Intro_ChinhThuc_NhacRieng_1080p60.mp4"
)
WATERMARK_ASSET = os.path.join(
    BASE_DIR, "03_Tai_Nguyen_Goc", "Logo_Va_Font", "bm_baominh_watermark_crop_1080p.png"
)


def ensure_watermark_asset():
    if os.path.exists(WATERMARK_ASSET) and os.path.getsize(WATERMARK_ASSET) > 1000:
        return WATERMARK_ASSET

    dl = r"C:\Users\DELL\Documents\Downloads"
    candidates = [
        os.path.join(dl, f)
        for f in os.listdir(dl)
        if f.lower().startswith("logo bm") and "không" not in f.lower() and f.lower().endswith(".png")
    ]
    if candidates:
        src = cv2.imread(candidates[0])
        rgb = cv2.cvtColor(src, cv2.COLOR_BGR2RGB).astype(np.float32)
        interior = (rgb[:, :, 0] - rgb[:, :, 1]) > 110
        brand_rgb = np.median(rgb[interior], axis=0)
        alpha = np.clip((254.0 - rgb[:, :, 1]) / (254.0 - brand_rgb[1]), 0.0, 1.0)
        alpha = np.clip((alpha - 0.05) / 0.90, 0.0, 1.0)
        ys, xs = np.where(alpha > 0.03)
        crop_a = alpha[ys.min() : ys.max() + 1, xs.min() : xs.max() + 1]
    else:
        fallback = os.path.join(BASE_DIR, "03_Tai_Nguyen_Goc", "Logo_Va_Font", "bm_logo_transparent.png")
        rgba_fb = cv2.imread(fallback, cv2.IMREAD_UNCHANGED)
        crop_a = rgba_fb[:, :, 3].astype(np.float32) / 255.0
        brand_rgb = [247.0, 79.0, 141.0]

    wm_w = 210
    wm_h = int(round(crop_a.shape[0] * (wm_w / crop_a.shape[1])))
    wm_a = cv2.resize(crop_a, (wm_w, wm_h), interpolation=cv2.INTER_AREA)

    opacity = 0.20  # 20% subtle stationery watermark on OneNote board
    wm_rgba = np.zeros((wm_h, wm_w, 4), dtype=np.uint8)
    wm_rgba[:, :, 0] = int(brand_rgb[2])
    wm_rgba[:, :, 1] = int(brand_rgb[1])
    wm_rgba[:, :, 2] = int(brand_rgb[0])
    wm_rgba[:, :, 3] = np.clip(wm_a * opacity * 255.0, 0, 255).astype(np.uint8)

    os.makedirs(os.path.dirname(WATERMARK_ASSET), exist_ok=True)
    cv2.imwrite(WATERMARK_ASSET, wm_rgba)
    return WATERMARK_ASSET


def render_lesson_with_intro_and_watermark(input_mp4, output_mp4, intro_mp4=DEFAULT_INTRO, wm_x=1198, wm_y=778):
    wm_png = ensure_watermark_asset()
    print(f"[Input Lesson] {input_mp4}")
    print(f"[Input Intro]  {intro_mp4}")
    print(f"[Watermark]    {wm_png} at ({wm_x}, {wm_y})")
    print(f"[Output MP4]   {output_mp4}")

    filter_complex = (
        "[0:v]fps=30,scale=1920:1080:flags=bicubic,setsar=1,format=yuv420p[v0];"
        "[0:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,volume=0.85[a0];"
        "[1:v]fps=30,scale=1920:1080:flags=bicubic,setsar=1[v1s];"
        f"[v1s][2:v]overlay={wm_x}:{wm_y}:eof_action=repeat,fade=t=in:st=0:d=0.28,format=yuv420p[v1];"
        "[1:a]aresample=48000:async=1000,aformat=sample_fmts=fltp:channel_layouts=stereo[a1];"
        "[v0][a0][v1][a1]concat=n=2:v=1:a=1[vout][aout]"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-reinit_filter", "0",
        "-i", intro_mp4,
        "-i", input_mp4,
        "-i", wm_png,
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "[aout]",
        "-c:v", "libx264",
        "-profile:v", "high",
        "-crf", "18",
        "-preset", "veryfast",
        "-tune", "stillimage",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        "-stats_period", "30",
        output_mp4,
    ]

    t0 = time.time()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
    for line in proc.stdout:
        line_s = line.strip()
        if "time=" in line_s or "Error" in line_s or "muxing overhead" in line_s:
            print(line_s, flush=True)

    ret = proc.wait()
    if ret != 0:
        raise RuntimeError(f"FFmpeg exited with code {ret}")

    elapsed = time.time() - t0
    mb = os.path.getsize(output_mp4) / (1024 * 1024)
    print(f"\n[SUCCESS] Exported Full HD 1080p video in {elapsed/60:.1f} minutes! Size: {mb:.1f} MB")
    print(f"[Path] {output_mp4}")


if __name__ == "__main__":
    dl_dir = r"C:\Users\DELL\Documents\Downloads"
    default_in = next(
        (os.path.join(dl_dir, f) for f in os.listdir(dl_dir) if "22_11" in f and f.lower().endswith(".mp4") and "_FULL_BM" not in f),
        None,
    )

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", default=default_in, help="Đường dẫn video buổi học gốc")
    parser.add_argument("-o", "--output", default=None, help="Đường dẫn xuất file hoàn chỉnh")
    args = parser.parse_args()

    if not args.input or not os.path.exists(args.input):
        raise FileNotFoundError("Không tìm thấy file video buổi học đầu vào!")

    if args.output is None:
        base_no_ext = os.path.splitext(args.input)[0]
        # Clean accidental missing N in CHƯƠG if present, or append _FULL_BM.mp4 clearly
        clean_base = base_no_ext.replace("CHƯƠG 20", "CHƯƠNG 20)")
        args.output = f"{clean_base}_FULL_BM.mp4"

    render_lesson_with_intro_and_watermark(args.input, args.output)

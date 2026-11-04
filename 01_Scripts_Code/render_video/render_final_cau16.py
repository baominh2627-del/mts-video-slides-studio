import subprocess
import os
import sys
import shutil
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

FFMPEG = r'C:\Users\DELL\AppData\Local\Programs\Python\Python313\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
VIDEO_IN = r"C:\Users\DELL\Documents\Downloads\giai_cau16_chi_tiet.mp4"
AUDIO_IN = r"c:\Users\DELL\Documents\CODE\DU_AN\master_narration_190s.wav"
LOGO_IN = r"c:\Users\DELL\Documents\CODE\DU_AN\logo_mts_overlay.png"
ASS_PATH = r"c:\Users\DELL\Documents\CODE\DU_AN\subtitles_cau16.ass"

OUT_WORKSPACE = r"c:\Users\DELL\Documents\CODE\DU_AN\CÂN BẰNG NHIỆT_CÂU 16_MTSEducation.mp4"
OUT_DOWNLOAD_1 = r"C:\Users\DELL\Documents\Downloads\CÂN BẰNG NHIỆT_CÂU 16_MTSEducation.mp4"
OUT_DOWNLOAD_2 = r"C:\Users\DELL\Documents\Downloads\giai_cau16_hoan_chinh.mp4"

ass_filter_path = ASS_PATH.replace("\\", "/").replace(":", "\\:")

# Overlay logo in top-left, then burn ASS subtitles in lower third
filter_complex = f"[0:v][2:v]overlay=0:0,ass='{ass_filter_path}'[v]"

cmd = [
    FFMPEG, '-y',
    '-i', VIDEO_IN,
    '-i', AUDIO_IN,
    '-i', LOGO_IN,
    '-filter_complex', filter_complex,
    '-map', '[v]',
    '-map', '1:a',
    '-c:v', 'libx264',
    '-preset', 'fast',
    '-crf', '16',
    '-pix_fmt', 'yuv420p',
    '-r', '30',
    '-c:a', 'aac',
    '-b:a', '320k',
    '-t', '190.00',
    OUT_WORKSPACE
]

print("Rendering final video with pure clear narration, logo & subtitles...", flush=True)
t0 = time.time()
log_path = r"c:\Users\DELL\Documents\CODE\DU_AN\render_cau16.log"
with open(log_path, 'w', encoding='utf-8') as log_f:
    p = subprocess.Popen(cmd, stdout=log_f, stderr=log_f)
    ret = p.wait()

if ret == 0:
    elapsed = time.time() - t0
    size_mb = os.path.getsize(OUT_WORKSPACE) / (1024 * 1024)
    print(f"Render completed in {elapsed:.2f}s! Size: {size_mb:.2f} MB", flush=True)
    for target in [OUT_DOWNLOAD_1, OUT_DOWNLOAD_2]:
        print(f"Copying to {target}...", flush=True)
        shutil.copy(OUT_WORKSPACE, target)
    print("ALL DELIVERABLES SAVED AND READY!", flush=True)
else:
    print(f"FFmpeg error with code {ret}!", flush=True)
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as log_f:
        print(log_f.read()[-1000:], flush=True)
    sys.exit(1)

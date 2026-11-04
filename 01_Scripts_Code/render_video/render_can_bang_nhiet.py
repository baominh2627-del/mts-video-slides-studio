import subprocess
import os
import sys
import time
import shutil

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

FFMPEG = r'C:\Users\DELL\AppData\Local\Programs\Python\Python313\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
INPUT_VIDEO = r'C:\Users\DELL\Documents\Downloads\CÂN BẰNG NHIỆT_MTSEducation_1080p.mp4'
INPUT_BGM = r'C:\Users\DELL\Documents\Downloads\Van_Huann_vhremixx_mashup_violin.mp3'

OUTPUT_WORKSPACE = r'C:\Users\DELL\Documents\CODE\DU_AN\CÂN BẰNG NHIỆT_MTSEducation.mp4'

DOWNLOAD_NAMES = [
    r'C:\Users\DELL\Documents\Downloads\CÂN BẰNG NHIỆT_MTSEducation.mp4',
    r'C:\Users\DELL\Documents\Downloads\VIDEO CHỈNH SỬA_CÂN BẰNG NHIỆT.mp4'
]

SPEED = 1.35
DURATION = 66.10  # 00:01:06.03 as in CapCut (66.10s)
BGM_VOL = 0.4746  # -6.47 dB matching CapCut timeline

# Constant 30 FPS, CRF 16 (highest quality 1080p), fast preset, 320k AAC
cmd = [
    FFMPEG, '-y',
    '-i', INPUT_VIDEO,
    '-stream_loop', '2', '-i', INPUT_BGM,
    '-filter_complex',
    f'[0:v]setpts=PTS/{SPEED},fps=30[v];'
    f'[0:a]atempo={SPEED},volume=1.0[voice];'
    f'[1:a]volume={BGM_VOL},afade=t=out:st=64.6:d=1.5[bgm];'
    '[voice][bgm]amix=inputs=2:duration=first:dropout_transition=2[a]',
    '-map', '[v]',
    '-map', '[a]',
    '-c:v', 'libx264',
    '-r', '30',
    '-preset', 'fast',
    '-crf', '16',
    '-pix_fmt', 'yuv420p',
    '-c:a', 'aac',
    '-b:a', '320k',
    '-t', f'{DURATION}',
    OUTPUT_WORKSPACE
]

print("Rendering CÂN BẰNG NHIỆT_MTSEducation with highest quality 1080p...", flush=True)
t0 = time.time()

log_path = r'C:\Users\DELL\Documents\CODE\DU_AN\ffmpeg_render.log'
with open(log_path, 'w', encoding='utf-8') as log_f:
    p = subprocess.Popen(cmd, stdout=log_f, stderr=log_f)
    ret = p.wait()

if ret == 0:
    elapsed = time.time() - t0
    size_mb = os.path.getsize(OUTPUT_WORKSPACE) / (1024 * 1024)
    print(f"Render completed in {elapsed:.2f}s! Size: {size_mb:.2f} MB", flush=True)
    for target in DOWNLOAD_NAMES:
        print(f"Copying to: {target}...", flush=True)
        shutil.copy(OUTPUT_WORKSPACE, target)
    print("ALL DELIVERABLES SAVED SUCCESSFULLY!", flush=True)
else:
    print(f"FFmpeg exited with error code {ret}!", flush=True)
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as log_f:
        print(log_f.read()[-500:])
    sys.exit(1)

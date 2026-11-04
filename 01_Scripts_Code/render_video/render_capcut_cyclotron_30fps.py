import subprocess
import os
import sys
import time
import shutil

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

FFMPEG = r'C:\Users\DELL\AppData\Local\Programs\Python\Python313\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
INPUT_VIDEO = r'C:\Users\DELL\Documents\Downloads\MÁY GIA TỐC CYCLOTRON_MTSEducation.mp4'
INPUT_BGM = r'C:\Users\DELL\Documents\Downloads\Van_Huann_vhremixx_mashup_violin.mp3'

OUTPUT_WORKSPACE = r'C:\Users\DELL\Documents\CODE\DU_AN\MÁY GIA TỐC CYCLOTRON_CHỈNH SỬA_1080p.mp4'

DOWNLOAD_NAMES = [
    r'C:\Users\DELL\Documents\Downloads\MÁY GIA TỐC CYCLOTRON_CHỈNH SỬA.mp4',
    r'C:\Users\DELL\Documents\Downloads\VIDEO CHỈNH SỬA_MÁY GIA TỐC CYCLOTRON.mp4',
    r'C:\Users\DELL\Documents\Downloads\MÁY GIA TỐC CYCLOTRON_1.3x_1080p.mp4'
]

SPEED = 1.30
DURATION = 182.566 # 00:03:02.57
BGM_VOL = 0.5012   # -6.0 dB as in CapCut

# Force constant 30 FPS output
cmd = [
    FFMPEG, '-y',
    '-i', INPUT_VIDEO,
    '-stream_loop', '3', '-i', INPUT_BGM,
    '-filter_complex',
    f'[0:v]setpts=PTS/{SPEED},fps=30[v];'
    f'[0:a]atempo={SPEED},volume=1.0[voice];'
    f'[1:a]volume={BGM_VOL}[bgm];'
    '[voice][bgm]amix=inputs=2:duration=first:dropout_transition=2[a]',
    '-map', '[v]',
    '-map', '[a]',
    '-c:v', 'libx264',
    '-r', '30',
    '-preset', 'fast',
    '-crf', '17',
    '-pix_fmt', 'yuv420p',
    '-c:a', 'aac',
    '-b:a', '192k',
    '-t', f'{DURATION}',
    OUTPUT_WORKSPACE
]

print("Rendering video with constant 30 FPS...")
t0 = time.time()
res = subprocess.run(cmd)

if res.returncode == 0:
    elapsed = time.time() - t0
    size_mb = os.path.getsize(OUTPUT_WORKSPACE) / (1024 * 1024)
    print(f"Render completed in {elapsed:.2f}s! Size: {size_mb:.2f} MB")
    for target in DOWNLOAD_NAMES:
        print(f"Copying to: {target}...")
        shutil.copy(OUTPUT_WORKSPACE, target)
    print("ALL COPIES UPDATED SUCCESSFULLY!")
else:
    print("FFmpeg error occurred!")
    sys.exit(1)

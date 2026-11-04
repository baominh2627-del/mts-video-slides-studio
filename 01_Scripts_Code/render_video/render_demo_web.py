import subprocess
import os
import sys
import time
import shutil

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

FFMPEG = r'C:\Users\DELL\AppData\Local\Programs\Python\Python313\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
DEMO_1 = r'C:\Users\DELL\Documents\Downloads\demo_1.mp4'
DEMO_2 = r'C:\Users\DELL\Documents\Downloads\demo_2.mp4'
OVERLAY = r'C:\Users\DELL\Documents\CODE\DU_AN\full_overlay_1026.png'
BGM = r'C:\Users\DELL\Documents\Downloads\hoàng đế trở về nhà.mp3'

OUTPUT_WORKSPACE = r'C:\Users\DELL\Documents\CODE\DU_AN\DEMO WEB_MTSEducation.mp4'
OUTPUT_DOWNLOAD = r'C:\Users\DELL\Documents\Downloads\DEMO WEB_MTSEducation.mp4'
OUTPUT_BACKUP = r'C:\Users\DELL\Documents\Downloads\VIDEO CHỈNH SỬA_DEMO WEB.mp4'

DURATION = 26.067

filter_complex = (
    # Cut 0: demo_1 from 0 to 3.936, speed 1.64
    "[0:v]trim=start=0.0:end=3.936,setpts=PTS-STARTPTS,setpts=PTS/1.64,scale=1080:1920:flags=lanczos,fps=30,setsar=1[v0];"
    # Cut 1: demo_2 from 0 to 4.867, speed 4.71
    "[1:v]trim=start=0.0:end=4.867,setpts=PTS-STARTPTS,setpts=PTS/4.71,scale=1080:1920:flags=lanczos,fps=30,setsar=1[v1];"
    # Cut 2: demo_2 from 3.766667 to 55.283333, speed 5.5
    "[1:v]trim=start=3.766667:end=55.283333,setpts=PTS-STARTPTS,setpts=PTS/5.5,scale=1080:1920:flags=lanczos,fps=30,setsar=1[v2];"
    # Cut 3: demo_2 from 55.166666 to 65.246666, speed 6.3
    "[1:v]trim=start=55.166666:end=65.246666,setpts=PTS-STARTPTS,setpts=PTS/6.3,scale=1080:1920:flags=lanczos,fps=30,setsar=1[v3];"
    # Cut 4: demo_2 from 65.400 to 100.233333, speed 5.5
    "[1:v]trim=start=65.400:end=100.233333,setpts=PTS-STARTPTS,setpts=PTS/5.5,scale=1080:1920:flags=lanczos,fps=30,setsar=1[v4];"
    # Cut 5: demo_2 from 100.366666 to 116.236666, speed 6.9
    "[1:v]trim=start=100.366666:end=116.236666,setpts=PTS-STARTPTS,setpts=PTS/6.9,scale=1080:1920:flags=lanczos,fps=30,setsar=1[v5];"
    # Cut 6: demo_2 from 115.733333 to 131.456666, speed 5.3
    "[1:v]trim=start=115.733333:end=131.456666,setpts=PTS-STARTPTS,setpts=PTS/5.3,scale=1080:1920:flags=lanczos,fps=30,setsar=1[v6];"
    # Concat 7 segments
    "[v0][v1][v2][v3][v4][v5][v6]concat=n=7:v=1:a=0[vbase];"
    # Overlay graphics and text
    "[vbase][2:v]overlay=0:0[vfinal];"
    # Audio with fadeout
    f"[3:a]atrim=0:{DURATION},asetpts=PTS-STARTPTS,volume=1.0,afade=t=out:st=24.5:d=1.5[afinal]"
)

cmd = [
    FFMPEG, '-y',
    '-i', DEMO_1,
    '-i', DEMO_2,
    '-i', OVERLAY,
    '-i', BGM,
    '-filter_complex', filter_complex,
    '-map', '[vfinal]',
    '-map', '[afinal]',
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

print("Rendering DEMO WEB_MTSEducation with highest quality 1080p...", flush=True)
t0 = time.time()

log_path = r'C:\Users\DELL\Documents\CODE\DU_AN\render_demo_web.log'
with open(log_path, 'w', encoding='utf-8') as log_f:
    p = subprocess.Popen(cmd, stdout=log_f, stderr=log_f)
    ret = p.wait()

if ret == 0:
    elapsed = time.time() - t0
    size_mb = os.path.getsize(OUTPUT_WORKSPACE) / (1024 * 1024)
    print(f"Render completed in {elapsed:.2f}s! Size: {size_mb:.2f} MB", flush=True)
    for target in [OUTPUT_DOWNLOAD, OUTPUT_BACKUP]:
        print(f"Copying to: {target}...", flush=True)
        shutil.copy(OUTPUT_WORKSPACE, target)
    print("ALL DELIVERABLES SAVED SUCCESSFULLY!", flush=True)
else:
    print(f"FFmpeg error occurred with return code {ret}:", flush=True)
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as log_f:
        print(log_f.read()[-1000:], flush=True)
    sys.exit(1)

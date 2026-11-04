import os, sys, time, subprocess, shutil

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

FFMPEG = r'C:\Users\DELL\AppData\Local\Programs\Python\Python313\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
VIDEO_IN = r"C:\Users\DELL\Documents\Downloads\giai_cau16_chi_tiet.mp4"
AUDIO_IN = r"c:\Users\DELL\Documents\CODE\DU_AN\video2_audio_mix.wav"
LOGO_IN = r"c:\Users\DELL\Documents\CODE\DU_AN\official_logo_mts_video2.png"
CARDS_DIR = r"c:\Users\DELL\Documents\CODE\DU_AN\vivid_cards_v2"

OUT_WORKSPACE = r"c:\Users\DELL\Documents\CODE\DU_AN\CÂN BẰNG NHIỆT_CÂU 16_Video_2.mp4"
OUT_DOWNLOADS = r"C:\Users\DELL\Documents\Downloads\CÂN BẰNG NHIỆT_CÂU 16_Video_2.mp4"

# Critical safety check: Ensure original clean video is not overwritten
ORIGINAL_DELIVERABLE = r"C:\Users\DELL\Documents\Downloads\CÂN BẰNG NHIỆT_CÂU 16_MTSEducation.mp4"
if os.path.exists(ORIGINAL_DELIVERABLE):
    orig_size = os.path.getsize(ORIGINAL_DELIVERABLE)
    print(f"Safety check passed: Original video exists ({orig_size / (1024*1024):.2f} MB) and will remain untouched.")
else:
    print("Warning: Original deliverable not found at expected path.")

# Check all input cards exist
card_specs = [
    ("card1.png", 0.0, 15.0),
    ("card2.png", 15.0, 32.0),
    ("card3.png", 32.0, 54.0),
    ("card4.png", 54.0, 80.0),
    ("card5.png", 80.0, 110.0),
    ("card6.png", 110.0, 130.0),
    ("card7.png", 130.0, 152.0),
    ("card8.png", 152.0, 166.0),
    ("card9.png", 166.0, 184.0),
    ("card10.png", 184.0, 190.0),
]

cmd = [FFMPEG, '-y']

# Input 0: Video
cmd.extend(['-i', VIDEO_IN])

# Input 1: Audio mix
cmd.extend(['-i', AUDIO_IN])

# Input 2: Logo
cmd.extend(['-i', LOGO_IN])

# Inputs 3..12: Cards
for fname, _, _ in card_specs:
    c_path = os.path.join(CARDS_DIR, fname)
    if not os.path.exists(c_path):
        raise FileNotFoundError(f"Missing card: {c_path}")
    cmd.extend(['-i', c_path])

# Filter complex
filter_lines = []
# 1. Overlay logo permanently
filter_lines.append("[0:v][2:v]overlay=0:0[v0]")

# 2. Chain 10 cards with enable
for i, (_, st, ed) in enumerate(card_specs):
    in_tag = f"[v{i}]"
    card_idx = 3 + i
    out_tag = f"[v{i+1}]" if i < len(card_specs) - 1 else "[v_final]"
    filter_lines.append(f"{in_tag}[{card_idx}:v]overlay=40:1620:enable='between(t,{st},{ed})'{out_tag}")

filter_complex = "; ".join(filter_lines)

cmd.extend([
    '-filter_complex', filter_complex,
    '-map', '[v_final]',
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
])

print("Executing FFmpeg rendering for Video 2...", flush=True)
t0 = time.time()
log_path = r"c:\Users\DELL\Documents\CODE\DU_AN\render_video2.log"
with open(log_path, 'w', encoding='utf-8') as log_f:
    p = subprocess.Popen(cmd, stdout=log_f, stderr=log_f)
    ret = p.wait()

elapsed = time.time() - t0
if ret == 0:
    size_mb = os.path.getsize(OUT_WORKSPACE) / (1024 * 1024)
    print(f"Render completed successfully in {elapsed:.2f}s! Size: {size_mb:.2f} MB", flush=True)
    
    print(f"Copying to Downloads: {OUT_DOWNLOADS}...", flush=True)
    shutil.copy(OUT_WORKSPACE, OUT_DOWNLOADS)
    print("Video 2 is exported and ready in Downloads!", flush=True)
else:
    print(f"FFmpeg failed with exit code {ret}!", flush=True)
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as log_f:
        print(log_f.read()[-1500:], flush=True)
    sys.exit(1)

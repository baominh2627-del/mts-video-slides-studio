import subprocess
import os

FFMPEG = r'C:\Users\DELL\AppData\Local\Programs\Python\Python313\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
ORIG_VIDEO = r'C:\Users\DELL\Documents\Downloads\NHIỆT LƯỢNG, NỘI NĂNG, NHIỆT NĂNG.mp4'
BGM_MUSIC = r'C:\Users\DELL\Documents\Downloads\Van_Huann_vhremixx_mashup_violin.mp3'
OUT_AUDIO = r'C:\Users\DELL\Documents\CODE\DU_AN\test_mixed_audio.wav'

# Audio filter graph:
# 1. Voice: atempo=1.35, volume=1.3
# 2. BGM: loop 2 times, volume=0.45
# 3. Mix together, duration=121.43s
cmd = [
    FFMPEG, '-y',
    '-i', ORIG_VIDEO,
    '-stream_loop', '2', '-i', BGM_MUSIC,
    '-filter_complex',
    '[0:a]atempo=1.35,volume=1.3[voice];'
    '[1:a]volume=0.45[bgm];'
    '[voice][bgm]amix=inputs=2:duration=first:dropout_transition=2[outa]',
    '-map', '[outa]',
    '-t', '121.43',
    OUT_AUDIO
]

print("Rendering test mixed audio...")
res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode == 0:
    print(f"Success! Generated: {OUT_AUDIO}, size: {os.path.getsize(OUT_AUDIO)/(1024*1024):.2f} MB")
else:
    print("FFmpeg error:", res.stderr)

import subprocess, sys

sys.stdout.reconfigure(encoding='utf-8')
ff = r'C:/Users/DELL/AppData/Local/Programs/Python/Python313/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'

video_in = r'C:\Users\DELL\Documents\Downloads\giai_cau16_chi_tiet.mp4'
audio_in = r'C:\Users\DELL\Documents\Downloads\giai_cau16_hoan_chinh.mp4'
logo_in = r'c:\Users\DELL\Documents\CODE\DU_AN\logo_mts_overlay.png'
ass_path = r'c\:/Users/DELL/Documents/CODE/DU_AN/subtitles_cau16.ass'

out_test = r'c:\Users\DELL\Documents\CODE\DU_AN\sample_render_5s.mp4'

# Filter complex: overlay logo, then burn subtitles
filter_str = f"[0:v][2:v]overlay=0:0,ass='{ass_path}'[v]"

cmd = [
    ff, '-y',
    '-ss', '0', '-t', '10', '-i', video_in,
    '-ss', '0', '-t', '10', '-i', audio_in,
    '-i', logo_in,
    '-filter_complex', filter_str,
    '-map', '[v]',
    '-map', '1:a',
    '-c:v', 'libx264',
    '-preset', 'fast',
    '-crf', '16',
    '-c:a', 'aac',
    out_test
]

res = subprocess.run(cmd, capture_output=True, text=True, errors='ignore')
print("Returncode:", res.returncode)
if res.returncode != 0:
    print(res.stderr[-1000:])
else:
    print("Sample render 10s succeeded!")

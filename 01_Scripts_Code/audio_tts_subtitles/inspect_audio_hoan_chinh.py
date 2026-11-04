import subprocess, json

ff = r'C:/Users/DELL/AppData/Local/Programs/Python/Python313/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
p = r'C:\Users\DELL\Documents\Downloads\giai_cau16_hoan_chinh.mp4'

# inspect metadata of giai_cau16_hoan_chinh.mp4
cmd = [ff, '-i', p, '-f', 'ffmetadata', '-']
res = subprocess.run(cmd, capture_output=True, text=True, errors='ignore')
print("Metadata:", res.stdout)

# Check volume at multiple points: 5s, 30s, 60s, 90s, 120s, 150s, 180s
for sec in [5, 30, 60, 90, 120, 150, 180]:
    cmd = [ff, '-ss', str(sec), '-t', '5', '-i', p, '-af', 'volumedetect', '-f', 'null', '-']
    res = subprocess.run(cmd, capture_output=True, text=True, errors='ignore')
    for l in res.stderr.splitlines():
        if 'mean_volume' in l or 'max_volume' in l:
            print(f"Sec {sec}: {l.strip()}")

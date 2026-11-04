import subprocess, sys

sys.stdout.reconfigure(encoding='utf-8')
ff = r'C:/Users/DELL/AppData/Local/Programs/Python/Python313/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
p = 'C:/Users/DELL/Documents/Downloads/CÂN BẰNG NHIỆT_MTSEducation_1080p.mp4'

# check volume levels of the video audio
cmd = [ff, '-i', p, '-af', 'volumedetect', '-f', 'null', '-']
res = subprocess.run(cmd, capture_output=True)
err = res.stderr.decode('utf-8', errors='ignore')
for l in err.splitlines():
    if 'max_volume' in l or 'mean_volume' in l:
        print(l.strip())

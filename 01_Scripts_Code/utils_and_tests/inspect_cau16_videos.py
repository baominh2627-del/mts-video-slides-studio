import cv2, subprocess, sys

sys.stdout.reconfigure(encoding='utf-8')
ff = r'C:/Users/DELL/AppData/Local/Programs/Python/Python313/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'

for name in ['giai_cau16_chi_tiet.mp4', 'giai_cau16_hoan_chinh.mp4']:
    p = f'C:/Users/DELL/Documents/Downloads/{name}'
    cap = cv2.VideoCapture(p)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    cnt = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    dur = cnt / fps if fps > 0 else 0
    cap.release()
    print(f"=== {name} ===")
    print(f"  CV2: {w}x{h}, {fps:.2f} fps, {cnt} frames, duration: {dur:.2f}s ({int(dur//60)}m{dur%60:.1f}s)")
    
    res = subprocess.run([ff, '-i', p], capture_output=True)
    err = res.stderr.decode('utf-8', errors='ignore')
    for l in err.splitlines():
        if 'Duration:' in l or 'Stream #' in l:
            print("  FFmpeg:", l.strip())

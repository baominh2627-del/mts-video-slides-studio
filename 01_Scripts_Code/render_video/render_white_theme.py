import os, sys, time, subprocess, shutil

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

FFMPEG = r'C:\Users\DELL\AppData\Local\Programs\Python\Python313\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
DIR_TT = os.path.join(r'C:\Users\DELL\Documents\Downloads', 'GIA_SƯ_2', 'TT')
DIR_DL = r'C:\Users\DELL\Documents\Downloads'

# Color filter to convert vintage warm paper/parchment background to clean pure white
FILTER_WHITE = "colorlevels=rimin=0.04:gimin=0.04:bimin=0.04:rimax=0.79:gimax=0.75:bimax=0.71"

tasks = [
    {
        "src": os.path.join(DIR_TT, "VIDEO CHỈNH SỬA_CÂN BẰNG NHIỆT.mp4"),
        "out_tt": os.path.join(DIR_TT, "VIDEO CHỈNH SỬA_CÂN BẰNG NHIỆT_NỀN TRẮNG.mp4"),
        "out_dl": os.path.join(DIR_DL, "VIDEO CHỈNH SỬA_CÂN BẰNG NHIỆT_NỀN TRẮNG.mp4")
    },
    {
        "src": os.path.join(DIR_TT, "CÂN BẰNG NHIỆT_MTSEducation_1080p.mp4"),
        "out_tt": os.path.join(DIR_TT, "CÂN BẰNG NHIỆT_MTSEducation_1080p_NỀN TRẮNG.mp4"),
        "out_dl": os.path.join(DIR_DL, "CÂN BẰNG NHIỆT_MTSEducation_1080p_NỀN TRẮNG.mp4")
    }
]

for t in tasks:
    src = t["src"]
    out_tt = t["out_tt"]
    out_dl = t["out_dl"]
    
    if not os.path.exists(src):
        print(f"Skipping missing source: {src}")
        continue
    
    print(f"\n=======================================================")
    print(f"Processing: {os.path.basename(src)}")
    print(f"Target: {os.path.basename(out_tt)}")
    
    # We render to a workspace temp path first to avoid any path encoding or lock issues
    temp_out = os.path.join(r"c:\Users\DELL\Documents\CODE\DU_AN", "temp_white_render.mp4")
    if os.path.exists(temp_out):
        try: os.remove(temp_out)
        except: pass
        
    cmd = [
        FFMPEG, '-y',
        '-i', src,
        '-vf', FILTER_WHITE,
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-crf', '16',
        '-pix_fmt', 'yuv420p',
        '-c:a', 'copy',
        temp_out
    ]
    
    t0 = time.time()
    res = subprocess.run(cmd, capture_output=True, text=True, errors='ignore')
    if res.returncode == 0:
        elapsed = time.time() - t0
        size_mb = os.path.getsize(temp_out) / (1024 * 1024)
        print(f"Rendered in {elapsed:.1f}s! Size: {size_mb:.2f} MB")
        
        # Copy to TT directory
        shutil.copy(temp_out, out_tt)
        print(f"Saved to: {out_tt}")
        
        # Copy to Downloads directory
        shutil.copy(temp_out, out_dl)
        print(f"Saved to: {out_dl}")
    else:
        print(f"Error rendering {src}: {res.stderr[-500:]}")

if os.path.exists(temp_out):
    try: os.remove(temp_out)
    except: pass

print("\nALL TASKS COMPLETED SUCCESSFULLY!")

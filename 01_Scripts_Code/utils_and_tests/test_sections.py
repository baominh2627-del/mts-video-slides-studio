import subprocess, speech_recognition as sr, sys

sys.stdout.reconfigure(encoding='utf-8')
ff = r'C:/Users/DELL/AppData/Local/Programs/Python/Python313/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
p = r'C:\Users\DELL\Documents\Downloads\giai_cau16_hoan_chinh.mp4'

r = sr.Recognizer()

# Test slices corresponding to the sections in the docx file!
# Section 1: 0:00 - 0:15
# Section 2: 0:15 - 0:30
# Section 3: 0:32 - 0:54
# Section 9: 2:32 - 2:46 (152 - 166s)

for start, dur, label in [
    (0, 15, "Phần 1 (0-15s)"),
    (15, 17, "Phần 2 (15-32s)"),
    (32, 22, "Phần 3 (32-54s)"),
    (152, 14, "Phần 9 (152-166s)"),
    (184, 6, "Phần 11 (184-190s)")
]:
    out_wav = f'c:/Users/DELL/Documents/CODE/DU_AN/section_{start}.wav'
    subprocess.run([ff, '-y', '-ss', str(start), '-t', str(dur), '-i', p, '-ac', '1', '-ar', '16000', out_wav], capture_output=True)
    with sr.AudioFile(out_wav) as source:
        audio = r.record(source)
    try:
        txt = r.recognize_google(audio, language='vi-VN')
        print(f"{label}: {txt}")
    except Exception as e:
        print(f"{label}: {e}")

import wave, numpy as np, speech_recognition as sr, sys

sys.stdout.reconfigure(encoding='utf-8')
r = sr.Recognizer()

# Let's test with different slices of giai_cau16_hoan_chinh.mp4
# Let's extract without ffmpeg clipping, pure 16k
for start_t in [0.5, 4.5, 9.0, 15.0, 24.0, 32.0, 40.0, 54.0, 80.0, 100.0, 140.0, 152.0, 170.0, 184.0]:
    import subprocess
    ff = r'C:/Users/DELL/AppData/Local/Programs/Python/Python313/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
    out = f'c:/Users/DELL/Documents/CODE/DU_AN/test_{int(start_t)}.wav'
    subprocess.run([ff, '-y', '-ss', str(start_t), '-t', '3.5', '-i', r'C:\Users\DELL\Documents\Downloads\giai_cau16_hoan_chinh.mp4', '-ac', '1', '-ar', '16000', '-af', 'volume=1.5', out], capture_output=True)
    with sr.AudioFile(out) as s:
        audio = r.record(s)
        try:
            txt = r.recognize_google(audio, language='vi-VN')
            print(f"Time {start_t}s: {txt}")
        except sr.UnknownValueError:
            pass
        except Exception as e:
            print(f"Time {start_t}s: Error {e}")

import subprocess, speech_recognition as sr, sys

sys.stdout.reconfigure(encoding='utf-8')
ff = r'C:/Users/DELL/AppData/Local/Programs/Python/Python313/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
p = r'C:\Users\DELL\Documents\Downloads\giai_cau16_hoan_chinh.mp4'

r = sr.Recognizer()

for sec in [1, 5, 20, 35, 60, 90, 120, 150, 180]:
    out_wav = f'c:/Users/DELL/Documents/CODE/DU_AN/test_slice_{sec}.wav'
    subprocess.run([ff, '-y', '-ss', str(sec), '-t', '4', '-i', p, '-ac', '1', '-ar', '16000', out_wav], capture_output=True)
    with sr.AudioFile(out_wav) as source:
        audio = r.record(source)
    try:
        txt = r.recognize_google(audio, language='vi-VN')
        print(f"Sec {sec}: {txt}")
    except sr.UnknownValueError:
        print(f"Sec {sec}: [No speech recognized]")
    except Exception as e:
        print(f"Sec {sec}: Error {e}")

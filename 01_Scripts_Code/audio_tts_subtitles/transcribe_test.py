import speech_recognition as sr
import sys

sys.stdout.reconfigure(encoding='utf-8')
r = sr.Recognizer()
with sr.AudioFile('c:/Users/DELL/Documents/CODE/DU_AN/hoan_chinh_test.wav') as source:
    audio = r.record(source)

try:
    text = r.recognize_google(audio, language='vi-VN')
    print("TRANSCRIPTION:", text)
except Exception as e:
    print("Error:", e)

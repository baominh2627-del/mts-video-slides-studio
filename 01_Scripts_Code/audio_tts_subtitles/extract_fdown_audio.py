import subprocess
import os

FFMPEG = r'C:\Users\DELL\AppData\Local\Programs\Python\Python313\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
VIDEO = r'C:\Users\DELL\Documents\Downloads\FDown.vn_TikTok_Video_Downloader_3387.mp4'
AUDIO = r'C:\Users\DELL\Documents\CODE\DU_AN\fdown_build\extracted_audio.wav'

cmd = [FFMPEG, '-y', '-i', VIDEO, '-vn', '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2', AUDIO]
subprocess.run(cmd, check=True)
print(f"Extracted audio: {AUDIO}, size: {os.path.getsize(AUDIO)/(1024*1024):.2f} MB")

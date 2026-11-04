import subprocess, edge_tts, asyncio, wave, numpy as np

ff = r'C:/Users/DELL/AppData/Local/Programs/Python/Python313/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
p = r'C:\Users\DELL\Documents\Downloads\giai_cau16_hoan_chinh.mp4'

async def test_match():
    # sentence at 0:00: "Câu mười sáu: bình nước hình lăng trụ tam giác"
    c = edge_tts.Communicate("Câu mười sáu: bình nước hình lăng trụ tam giác", "vi-VN-NamMinhNeural")
    await c.save("c:/Users/DELL/Documents/CODE/DU_AN/test_sentence1.mp3")

asyncio.run(test_match())

# extract 0 to 4.5s from giai_cau16_hoan_chinh.mp4
subprocess.run([ff, '-y', '-ss', '0', '-t', '4.5', '-i', p, '-ac', '1', '-ar', '16000', 'c:/Users/DELL/Documents/CODE/DU_AN/hoan_chinh_0_4.wav'], capture_output=True)
subprocess.run([ff, '-y', '-i', 'c:/Users/DELL/Documents/CODE/DU_AN/test_sentence1.mp3', '-ac', '1', '-ar', '16000', 'c:/Users/DELL/Documents/CODE/DU_AN/test_sentence1.wav'], capture_output=True)

with wave.open('c:/Users/DELL/Documents/CODE/DU_AN/hoan_chinh_0_4.wav', 'rb') as f:
    d1 = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16)
with wave.open('c:/Users/DELL/Documents/CODE/DU_AN/test_sentence1.wav', 'rb') as f:
    d2 = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16)

print(f"Hoan chinh 0-4.5s: len={len(d1)/16000:.2f}s, rms={np.sqrt(np.mean(d1.astype(float)**2)):.1f}")
print(f"Synth test: len={len(d2)/16000:.2f}s, rms={np.sqrt(np.mean(d2.astype(float)**2)):.1f}")

import asyncio, edge_tts, wave, numpy as np, subprocess

async def gen():
    text = "Bước sáu: kết quả. t không bằng N chia M."
    c = edge_tts.Communicate(text, "vi-VN-NamMinhNeural")
    await c.save("c:/Users/DELL/Documents/CODE/DU_AN/test_synth.mp3")

asyncio.run(gen())

ff = r'C:/Users/DELL/AppData/Local/Programs/Python/Python313/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
subprocess.run([ff, '-y', '-i', 'c:/Users/DELL/Documents/CODE/DU_AN/test_synth.mp3', '-ac', '1', '-ar', '16000', 'c:/Users/DELL/Documents/CODE/DU_AN/test_synth.wav'], capture_output=True)

with wave.open('c:/Users/DELL/Documents/CODE/DU_AN/test_synth.wav', 'rb') as f:
    synth_data = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16)

with wave.open('c:/Users/DELL/Documents/CODE/DU_AN/hoan_chinh_150s.wav', 'rb') as f:
    orig_data = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16)

print(f"Synth length: {len(synth_data)/16000:.2f}s, Orig slice: {len(orig_data)/16000:.2f}s")

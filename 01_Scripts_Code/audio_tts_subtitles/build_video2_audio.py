import os, sys
import numpy as np
import soundfile as sf

sys.stdout.reconfigure(encoding='utf-8')

master_path = r'c:\Users\DELL\Documents\CODE\DU_AN\master_narration_190s.wav'
ambient_path = r'c:\Users\DELL\Documents\CODE\DU_AN\video_build\ambient_bg.wav'
ding_path = r'C:\Windows\Media\ding.wav'
notify_path = r'C:\Windows\Media\notify.wav'
output_path = r'c:\Users\DELL\Documents\CODE\DU_AN\video2_audio_mix.wav'

print("Loading audio files...")
master, sr = sf.read(master_path)
ambient, _ = sf.read(ambient_path)
ding, _ = sf.read(ding_path)
notify, _ = sf.read(notify_path)

N = len(master) # 8379000 samples = 190.00s
mix = np.zeros((N, 2), dtype=np.float64)

# 1. Narration (Mono to Stereo, vol = 1.0)
mix[:, 0] += master
mix[:, 1] += master

# 2. Ambient BGM (vol = 0.12, fade in 2s, fade out 3s)
bg = ambient[:N].copy() * 0.12
fade_in_len = int(2.0 * sr)
fade_out_len = int(3.0 * sr)

fade_in = np.linspace(0, 1, fade_in_len)[:, None]
bg[:fade_in_len] *= fade_in

fade_out = np.linspace(1, 0, fade_out_len)[:, None]
bg[-fade_out_len:] *= fade_out

mix += bg

# 3. SFX Ding at 152.0s (t0 = 10°C announcement)
idx_ding = int(152.0 * sr)
ding_len = min(len(ding), N - idx_ding)
mix[idx_ding : idx_ding + ding_len] += ding[:ding_len] * 0.35

# 4. SFX Notify at 166.0s (Fast Tip announcement)
idx_notify = int(166.0 * sr)
notify_len = min(len(notify), N - idx_notify)
mix[idx_notify : idx_notify + notify_len] += notify[:notify_len] * 0.35

# 5. Peak check and safe limiter
peak = np.max(np.abs(mix))
print(f"Max peak before normalization: {peak:.3f}")
if peak > 0.95:
    mix = mix * (0.95 / peak)
    print(f"Normalized peak to 0.95")
else:
    print("Headroom is good!")

sf.write(output_path, mix, sr, subtype='PCM_16')
print(f"Saved mixed audio track to: {output_path} (dur: {N/sr:.2f}s)")

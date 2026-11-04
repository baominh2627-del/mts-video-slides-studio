# -*- coding: utf-8 -*-
import os
import sys
import json
import subprocess
import soundfile as sf
import imageio_ffmpeg
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

OUT_DIR = r"C:\Users\DELL\Documents\CODE\DU_AN\audio_build"
BGM_PATH = r"C:\Users\DELL\Documents\Downloads\Van_Huann_vhremixx_mashup_violin.mp3"

with open(os.path.join(OUT_DIR, "scenes_info.json"), "r", encoding="utf-8") as f:
    scenes = json.load(f)

# Concatenate all scene wav files
all_audio = []
sr = 44100

for s in scenes:
    wav_path = s['wav']
    data, s_sr = sf.read(wav_path)
    if s_sr != sr:
        raise ValueError("Sample rate mismatch")
    all_audio.append(data)

full_voice = np.concatenate(all_audio, axis=0)
total_dur = len(full_voice) / sr
print(f"Total concatenated voice duration: {total_dur:.2f} seconds")

voice_full_wav = os.path.join(OUT_DIR, "voice_full.wav")
sf.write(voice_full_wav, full_voice, sr)

# Mix with BGM using FFmpeg
mixed_wav = os.path.join(OUT_DIR, "mixed_audio_final.wav")
cmd = [
    ffmpeg, '-y',
    '-i', voice_full_wav,
    '-stream_loop', '-1',
    '-i', BGM_PATH,
    '-filter_complex',
    '[0:a]volume=1.38[voice];'
    '[1:a]volume=0.36[bgm];'
    '[voice][bgm]amix=inputs=2:duration=first:dropout_transition=2[outa]',
    '-map', '[outa]',
    '-t', str(total_dur),
    mixed_wav
]
subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
print(f"Mixed audio generated: {mixed_wav}")

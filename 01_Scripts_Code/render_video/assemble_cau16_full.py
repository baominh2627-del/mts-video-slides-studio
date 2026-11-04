import asyncio, edge_tts, os, sys, wave, numpy as np, subprocess
import zipfile, xml.etree.ElementTree as ET, re, shutil, time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

FFMPEG = r'C:\Users\DELL\AppData\Local\Programs\Python\Python313\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
DOCX_PATH = r"C:\Users\DELL\Documents\Downloads\Lời thuyết minh video giải Câu 16 (bản 3 phút 10 giây).docx"
AUDIO_DIR = r"c:\Users\DELL\Documents\CODE\DU_AN\cues_audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

# 1. Parse Word document cues
with zipfile.ZipFile(DOCX_PATH) as z:
    xml_content = z.read("word/document.xml")
    tree = ET.fromstring(xml_content)
    paragraphs = []
    for p in tree.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
        texts = [node.text for node in p.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if node.text]
        if texts:
            paragraphs.append("".join(texts))

pattern = re.compile(r'^(\d+:\d+(?:\.\d+)?)\s*[–-]\s*(\d+:\d+(?:\.\d+)?)\s+(.*?)(?:\s+Màn hình:\s*(.*))?$', re.IGNORECASE)

def parse_time(t_str):
    parts = t_str.split(':')
    return int(parts[0]) * 60 + float(parts[1])

cues = []
for p in paragraphs:
    m = pattern.match(p.strip())
    if m:
        t_start = parse_time(m.group(1))
        t_end = parse_time(m.group(2))
        speech = m.group(3).strip()
        screen = m.group(4).strip() if m.group(4) else ""
        cues.append({
            'start': t_start,
            'end': t_end,
            'speech': speech,
            'screen': screen
        })

print(f"Loaded {len(cues)} cues from Word document.", flush=True)

# 2. Fast parallel synthesis with edge_tts (vi-VN-NamMinhNeural)
VOICE = "vi-VN-NamMinhNeural"
sem = asyncio.Semaphore(5)

async def synth_one(idx, c):
    out_mp3 = os.path.join(AUDIO_DIR, f"cue_{idx:02d}.mp3")
    if os.path.exists(out_mp3) and os.path.getsize(out_mp3) > 1000:
        return
    async with sem:
        for attempt in range(4):
            try:
                comm = edge_tts.Communicate(c['speech'], VOICE, rate="+6%")
                await comm.save(out_mp3)
                if os.path.exists(out_mp3) and os.path.getsize(out_mp3) > 500:
                    print(f"  [Done] Cue {idx:02d}: '{c['speech'][:25]}...'", flush=True)
                    return
            except Exception as e:
                print(f"  [Retry {attempt+1}] Cue {idx:02d}: {e}", flush=True)
                await asyncio.sleep(1.0)
        print(f"  [Failed] Cue {idx:02d}", flush=True)

async def synth_all_parallel():
    tasks = [synth_one(i, c) for i, c in enumerate(cues)]
    await asyncio.gather(*tasks)

print("Starting parallel speech synthesis...", flush=True)
asyncio.run(synth_all_parallel())
print("All audio clips ready!", flush=True)

# 3. Time-stretch / pad each cue and build master 190.00s audio track
SAMPLE_RATE = 44100
total_samples = int(190.00 * SAMPLE_RATE)
master_audio = np.zeros(total_samples, dtype=np.float32)

print("Building master audio timeline (190.00s)...", flush=True)
for idx, c in enumerate(cues):
    in_mp3 = os.path.join(AUDIO_DIR, f"cue_{idx:02d}.mp3")
    out_wav = os.path.join(AUDIO_DIR, f"cue_{idx:02d}.wav")
    
    target_dur = c['end'] - c['start']
    
    # Probe duration of MP3
    probe_cmd = [FFMPEG, '-i', in_mp3]
    res = subprocess.run(probe_cmd, capture_output=True, text=True, errors='ignore')
    m_dur = re.search(r'Duration:\s*(\d+):(\d+):(\d+\.\d+)', res.stderr)
    cur_dur = target_dur
    if m_dur:
        cur_dur = int(m_dur.group(1))*3600 + int(m_dur.group(2))*60 + float(m_dur.group(3))
    
    # If audio is longer than slot, speed it up
    speed_factor = 1.0
    if cur_dur > target_dur:
        speed_factor = cur_dur / target_dur
        # cap speedup to 1.35x
        if speed_factor > 1.35:
            speed_factor = 1.35
    
    # Convert to 44.1kHz mono WAV with optional atempo
    if speed_factor > 1.02:
        conv_cmd = [FFMPEG, '-y', '-i', in_mp3, '-af', f'atempo={speed_factor:.3f}', '-ar', str(SAMPLE_RATE), '-ac', '1', out_wav]
    else:
        conv_cmd = [FFMPEG, '-y', '-i', in_mp3, '-ar', str(SAMPLE_RATE), '-ac', '1', out_wav]
    
    subprocess.run(conv_cmd, capture_output=True)
    
    # Read samples
    with wave.open(out_wav, 'rb') as wf:
        n = wf.getnframes()
        data = np.frombuffer(wf.readframes(n), dtype=np.int16).astype(np.float32) / 32768.0
    
    start_idx = int(c['start'] * SAMPLE_RATE)
    end_idx = min(start_idx + len(data), total_samples)
    data_to_add = data[:end_idx - start_idx]
    
    master_audio[start_idx:start_idx + len(data_to_add)] += data_to_add

# Normalize master audio peak to -1.0 dB
max_val = np.max(np.abs(master_audio))
if max_val > 0:
    target_peak = 10 ** (-1.0 / 20) # ~0.891
    master_audio = (master_audio / max_val) * target_peak

# Save master speech wav (16-bit PCM)
master_wav_path = r"c:\Users\DELL\Documents\CODE\DU_AN\master_narration_190s.wav"
master_int16 = (master_audio * 32767).astype(np.int16)
with wave.open(master_wav_path, 'wb') as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(master_int16.tobytes())

print(f"Master narration saved: {master_wav_path} (duration: 190.00s)", flush=True)

# 4. Generate ASS Subtitles
ass_header = """[Script Info]
Title: Giai Cau 16 - MTSEducation
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Segoe UI,38,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,1,2,50,50,140,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def format_ass_time(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    cs = int(round((sec - int(sec)) * 100))
    if cs >= 100:
        s += 1
        cs = 0
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

events = []
for it in cues:
    s_ass = format_ass_time(it['start'])
    e_ass = format_ass_time(it['end'])
    text = it['speech']
    if len(text) > 42:
        words = text.split()
        mid = len(words) // 2
        line1 = " ".join(words[:mid])
        line2 = " ".join(words[mid:])
        text = f"{line1}\\N{line2}"
    events.append(f"Dialogue: 0,{s_ass},{e_ass},Default,,0,0,0,,{text}")

ass_path = r"c:\Users\DELL\Documents\CODE\DU_AN\subtitles_cau16.ass"
with open(ass_path, "w", encoding="utf-8") as f:
    f.write(ass_header + "\n".join(events) + "\n")
print(f"ASS Subtitles saved: {ass_path}", flush=True)

# 5. Render Final 1080p Video with FFmpeg
VIDEO_IN = r"C:\Users\DELL\Documents\Downloads\giai_cau16_chi_tiet.mp4"
BGM_IN = r"C:\Users\DELL\Documents\Downloads\Van_Huann_vhremixx_mashup_violin.mp3"
LOGO_IN = r"c:\Users\DELL\Documents\CODE\DU_AN\logo_mts_overlay.png"

OUT_WORKSPACE = r"c:\Users\DELL\Documents\CODE\DU_AN\CÂN BẰNG NHIỆT_CÂU 16_MTSEducation.mp4"
OUT_DOWNLOAD_1 = r"C:\Users\DELL\Documents\Downloads\CÂN BẰNG NHIỆT_CÂU 16_MTSEducation.mp4"
OUT_DOWNLOAD_2 = r"C:\Users\DELL\Documents\Downloads\giai_cau16_hoan_chinh.mp4"

# Escape backslashes for ass filter
ass_filter_path = ass_path.replace("\\", "/").replace(":", "\\:")

# Overlay logo, burn subtitles, mix voice (vol 1.0) and gentle BGM (vol 0.08 = -22 dB)
filter_complex = (
    f"[0:v][2:v]overlay=0:0,ass='{ass_filter_path}'[v];"
    f"[1:a]volume=1.0[voice];"
    f"[3:a]volume=0.08,afade=t=out:st=187.0:d=3.0[bgm];"
    f"[voice][bgm]amix=inputs=2:duration=first:dropout_transition=2[a]"
)

cmd = [
    FFMPEG, '-y',
    '-i', VIDEO_IN,
    '-i', master_wav_path,
    '-i', LOGO_IN,
    '-stream_loop', '3', '-i', BGM_IN,
    '-filter_complex', filter_complex,
    '-map', '[v]',
    '-map', '[a]',
    '-c:v', 'libx264',
    '-preset', 'fast',
    '-crf', '16',
    '-pix_fmt', 'yuv420p',
    '-r', '30',
    '-c:a', 'aac',
    '-b:a', '320k',
    '-t', '190.00',
    OUT_WORKSPACE
]

print("Rendering final video with FFmpeg...", flush=True)
t0 = time.time()
log_path = r"c:\Users\DELL\Documents\CODE\DU_AN\render_cau16.log"
with open(log_path, 'w', encoding='utf-8') as log_f:
    p = subprocess.Popen(cmd, stdout=log_f, stderr=log_f)
    ret = p.wait()

if ret == 0:
    elapsed = time.time() - t0
    size_mb = os.path.getsize(OUT_WORKSPACE) / (1024 * 1024)
    print(f"Render completed in {elapsed:.2f}s! Size: {size_mb:.2f} MB", flush=True)
    for target in [OUT_DOWNLOAD_1, OUT_DOWNLOAD_2]:
        print(f"Copying to {target}...", flush=True)
        shutil.copy(OUT_WORKSPACE, target)
    print("ALL DELIVERABLES SAVED AND READY!", flush=True)
else:
    print(f"FFmpeg error with code {ret}!", flush=True)
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as log_f:
        print(log_f.read()[-1000:], flush=True)
    sys.exit(1)

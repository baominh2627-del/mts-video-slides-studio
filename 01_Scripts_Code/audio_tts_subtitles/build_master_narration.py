import asyncio, edge_tts, os, sys, wave, numpy as np, subprocess
import zipfile, xml.etree.ElementTree as ET, re

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

print(f"Loaded {len(cues)} cues from Word document.")

# 2. Synthesize each cue with edge_tts (vi-VN-NamMinhNeural)
VOICE = "vi-VN-NamMinhNeural"

async def synth_all():
    print(f"Synthesizing {len(cues)} audio clips...")
    for idx, c in enumerate(cues):
        out_mp3 = os.path.join(AUDIO_DIR, f"cue_{idx:02d}.mp3")
        if os.path.exists(out_mp3) and os.path.getsize(out_mp3) > 1000:
            print(f"  Cue {idx:02d} already exists.")
            continue
        
        # Retry loop
        success = False
        for attempt in range(4):
            try:
                comm = edge_tts.Communicate(c['speech'], VOICE, rate="+5%")
                await comm.save(out_mp3)
                if os.path.exists(out_mp3) and os.path.getsize(out_mp3) > 500:
                    print(f"  Synthesized cue {idx:02d}: '{c['speech'][:30]}...'")
                    success = True
                    break
            except Exception as e:
                print(f"  Attempt {attempt+1} failed for cue {idx:02d}: {e}")
                await asyncio.sleep(1.0)
        
        if not success:
            print(f"  WARNING: Failed to synthesize cue {idx:02d}!")
        await asyncio.sleep(0.2)

asyncio.run(synth_all())
print("All audio clips synthesized!")

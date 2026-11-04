import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

path = r'C:\Users\DELL\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\1024 (1)\draft_content.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("Canvas config:", data.get('canvas_config'))
print("Tracks count:", len(data.get('tracks', [])))

for i, track in enumerate(data.get('tracks', [])):
    print(f"\n--- Track {i} ({track.get('type')}) ---")
    for seg in track.get('segments', []):
        print(f"  Segment: id={seg.get('id')}")
        print(f"    target_timerange={seg.get('target_timerange')}")
        print(f"    source_timerange={seg.get('source_timerange')}")
        print(f"    speed={seg.get('speed')}, volume={seg.get('volume')}")
        print(f"    material_id={seg.get('material_id')}")
        print(f"    extra_material_refs={seg.get('extra_material_refs')}")

print("\n--- Materials ---")
for v in data.get('materials', {}).get('videos', []):
    print("Video material:", v.get('id'), v.get('path'))

for a in data.get('materials', {}).get('audios', []):
    print("Audio material:", a.get('id'), a.get('name'), a.get('path'))

for s in data.get('materials', {}).get('speeds', []):
    print("Speed material:", s.get('id'), s.get('speed'))

# Check Pro flags
text = json.dumps(data, ensure_ascii=False)
for pro_word in ['vocal_separation', 'Thiếu niên', 'vip', 'pro']:
    if pro_word in text.lower():
        print(f"Pro flag keyword found: '{pro_word}'")

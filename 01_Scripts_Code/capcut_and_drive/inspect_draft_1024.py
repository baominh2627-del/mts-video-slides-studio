import json

path = r'C:\Users\DELL\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\1024\draft_content.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("Project keys:", list(data.keys()))
print("Canvas config:", data.get('canvas_config'))
print("Tracks count:", len(data.get('tracks', [])))
for i, track in enumerate(data.get('tracks', [])):
    print(f"Track {i}: type={track.get('type')}, segments={len(track.get('segments', []))}")
    for seg in track.get('segments', []):
        print(f"   seg: id={seg.get('id')}, target_timerange={seg.get('target_timerange')}, source_timerange={seg.get('source_timerange')}, speed={seg.get('speed')}")

# Check materials
print("Materials keys:", list(data.get('materials', {}).keys()))
for mat_type, mats in data.get('materials', {}).items():
    if mats:
        print(f"   {mat_type}: {len(mats)} items")
        for m in mats:
            if isinstance(m, dict) and ('path' in m or 'file_Path' in m or 'name' in m):
                print(f"      - {m.get('name')}: {m.get('path', m.get('file_Path'))}")

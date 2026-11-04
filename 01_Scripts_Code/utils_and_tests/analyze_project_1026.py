import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

path = r'C:\Users\DELL\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\1026\draft_content.json'
with open(path, 'r', encoding='utf-8') as f:
    draft = json.load(f)

duration = draft.get('duration')
fps = draft.get('fps')
width = draft.get('canvas_config', {}).get('width')
height = draft.get('canvas_config', {}).get('height')

print(f"Project duration: {duration} (microseconds = {duration/1000000:.3f}s)")
print(f"Canvas: {width}x{height}, FPS: {fps}")

# Map materials by ID
videos_map = {v['id']: v for v in draft['materials']['videos']}
audios_map = {a['id']: a for a in draft['materials']['audios']}
texts_map = {t['id']: t for t in draft['materials']['texts']}
speeds_map = {s['id']: s for s in draft['materials'].get('speeds', [])}

for idx, tr in enumerate(draft['tracks']):
    print(f"\n--- Track {idx}: type={tr['type']}, id={tr['id']} ---")
    for seg in tr['segments']:
        target_id = seg.get('material_id')
        tr_timerange = seg.get('target_timerange')
        src_timerange = seg.get('source_timerange')
        speed_id = seg.get('extra_material_refs', [])
        speed_val = None
        for ref in speed_id:
            if ref in speeds_map:
                speed_val = speeds_map[ref].get('speed')
        
        detail = ""
        if target_id in videos_map:
            detail = f"Video: {videos_map[target_id].get('path')}"
        elif target_id in audios_map:
            detail = f"Audio: {audios_map[target_id].get('path')}"
        elif target_id in texts_map:
            detail = f"Text: {texts_map[target_id].get('content')}"
            
        print(f"  Segment: start={tr_timerange['start']/1e6:.2f}s, dur={tr_timerange['duration']/1e6:.2f}s | src_start={src_timerange['start']/1e6:.2f}s, src_dur={src_timerange['duration']/1e6:.2f}s | speed={speed_val} | {detail[:80]}")

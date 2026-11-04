import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

path = r'C:\Users\DELL\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\1026\draft_content.json'
with open(path, 'r', encoding='utf-8') as f:
    d = json.load(f)

print("Canvas:", d.get('canvas_config'))
print("Duration:", d.get('duration') / 1e6)
print("FPS:", d.get('fps'))

# Materials
materials = d.get('materials', {})
videos = {v['id']: v for v in materials.get('videos', [])}
audios = {a['id']: a for a in materials.get('audios', [])}
texts = {t['id']: t for t in materials.get('texts', [])}
speeds = {s['id']: s for s in materials.get('speeds', [])}

for i, track in enumerate(d.get('tracks', [])):
    print(f"\nTrack {i}: type={track.get('type')}, count={len(track.get('segments', []))}")
    for j, seg in enumerate(track.get('segments', [])):
        mat_id = seg.get('material_id')
        tr = seg.get('target_timerange')
        sr = seg.get('source_timerange')
        clip = seg.get('clip')
        
        # speed
        sp = 1.0
        for ref in seg.get('extra_material_refs', []):
            if ref in speeds:
                sp = speeds[ref].get('speed', 1.0)
                
        mat = videos.get(mat_id) or audios.get(mat_id) or texts.get(mat_id) or {}
        print(f"  [{j}] mat_id={mat_id[:8]}.. name={mat.get('name') or mat.get('path')}")
        print(f"      target: start={tr['start']/1e6:.3f}s, dur={tr['duration']/1e6:.3f}s")
        if sr:
            print(f"      source: start={sr['start']/1e6:.3f}s, dur={sr['duration']/1e6:.3f}s, speed={sp}")
        if clip:
            print(f"      clip: scale={clip.get('scale')}, transform={clip.get('transform')}")
        if 'content' in mat:
            print(f"      content: {repr(mat['content'])}")

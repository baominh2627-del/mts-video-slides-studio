import os, sys, json

sys.stdout.reconfigure(encoding='utf-8')
p_dir = r'C:\Users\DELL\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\1026'
with open(os.path.join(p_dir, 'draft_content.json'), 'r', encoding='utf-8') as f:
    data = json.load(f)

for idx, tr in enumerate(data.get('tracks', [])):
    print(f"\n================ TRACK {idx}: type={tr.get('type')} ================")
    for s_idx, seg in enumerate(tr.get('segments', [])):
        print(f"--- Segment {s_idx} ---")
        print("  material_id:", seg.get('material_id'))
        print("  target_timerange:", seg.get('target_timerange'))
        print("  source_timerange:", seg.get('source_timerange'))
        print("  speed:", seg.get('speed'))
        print("  volume:", seg.get('volume'))
        print("  clip:", seg.get('clip'))
        print("  extra_material_refs:", seg.get('extra_material_refs'))

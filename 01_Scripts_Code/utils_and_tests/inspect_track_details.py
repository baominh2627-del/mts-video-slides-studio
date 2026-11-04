import os, sys, json

sys.stdout.reconfigure(encoding='utf-8')
proj_dir = r"C:/Users/DELL/AppData/Local/CapCut/User Data/Projects/com.lveditor.draft/1026 (1)"
content_path = os.path.join(proj_dir, "draft_content.json")
with open(content_path, "r", encoding="utf-8") as f:
    data = json.load(f)

for idx, tr in enumerate(data.get("tracks", [])):
    print(f"Track {idx} keys:", {k: v for k, v in tr.items() if k != 'segments'})
    for s_idx, seg in enumerate(tr.get("segments", [])):
        print(f"  Seg {s_idx}:")
        for k, v in seg.items():
            if k not in ['extra_material_refs']:
                print(f"    {k}: {v}")

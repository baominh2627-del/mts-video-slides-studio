import os, sys, json

sys.stdout.reconfigure(encoding='utf-8')
proj_dir = r"C:/Users/DELL/AppData/Local/CapCut/User Data/Projects/com.lveditor.draft/1026 (1)"
content_path = os.path.join(proj_dir, "draft_content.json")
with open(content_path, "r", encoding="utf-8") as f:
    data = json.load(f)

materials = data.get("materials", {})
for k in materials.keys():
    items = materials[k]
    if items:
        print(f"=== {k} ({len(items)}) ===")
        for it in items:
            print(" ", it)

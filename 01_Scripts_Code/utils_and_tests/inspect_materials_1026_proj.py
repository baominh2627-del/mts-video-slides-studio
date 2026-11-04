import os, sys, json

sys.stdout.reconfigure(encoding='utf-8')
p_dir = r'C:\Users\DELL\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\1026'
with open(os.path.join(p_dir, 'draft_content.json'), 'r', encoding='utf-8') as f:
    data = json.load(f)

materials = data.get('materials', {})
print("Materials keys:", list(materials.keys()))
for k, v in materials.items():
    if v:
        print(f"=== {k} ({len(v)}) ===")
        for item in v:
            if isinstance(item, dict):
                # print concise dict
                simple = {k2: item[k2] for k2 in ['id', 'type', 'name', 'path', 'content', 'speed', 'duration', 'has_audio'] if k2 in item}
                print(" ", simple if simple else item.get('id', item))

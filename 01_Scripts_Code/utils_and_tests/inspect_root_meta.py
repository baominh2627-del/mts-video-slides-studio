import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

path = r'C:\Users\DELL\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\root_meta_info.json'
with open(path, 'r', encoding='utf-8') as f:
    root = json.load(f)

print("Root keys:", list(root.keys()))
for k in root:
    if k != 'all_draft_store':
        print(f"{k} = {repr(root[k])[:100]}")
    else:
        print(f"all_draft_store count: {len(root[k])}")
        for d in root[k][:3]:
            print("  draft:", d.get('draft_id'), d.get('draft_name'), d.get('draft_fold_path'))

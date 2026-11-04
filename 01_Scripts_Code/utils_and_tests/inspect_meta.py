import json, sys

sys.stdout.reconfigure(encoding='utf-8')
with open(r'C:/Users/DELL/AppData/Local/CapCut/User Data/Projects/com.lveditor.draft/1026 (1)/draft_meta_info.json', 'r', encoding='utf-8') as f:
    d = json.load(f)
for k, v in d.items():
    print(k, ':', v)

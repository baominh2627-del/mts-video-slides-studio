import json, sys

sys.stdout.reconfigure(encoding='utf-8')
p_dir = r'C:\Users\DELL\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\1026'
with open(f'{p_dir}/draft_content.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

for a in d.get('materials', {}).get('material_animations', []):
    print(a)

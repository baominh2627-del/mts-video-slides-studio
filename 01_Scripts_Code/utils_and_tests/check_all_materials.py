import json, sys

sys.stdout.reconfigure(encoding='utf-8')
with open(r'C:/Users/DELL/AppData/Local/CapCut/User Data/Projects/com.lveditor.draft/1026 (1)/draft_content.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print('Track count:', len(d.get('tracks', [])))
for idx, tr in enumerate(d.get('tracks', [])):
    print('Track', idx, 'type:', tr.get('type'), 'flag:', tr.get('flag'), 'segments:', len(tr.get('segments', [])))

materials = d.get('materials', {})
for k in ['texts', 'stickers', 'effects', 'filters', 'transitions', 'chromas', 'adjusts']:
    items = materials.get(k, [])
    print(k + ':', len(items))

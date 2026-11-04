import json

p_meta = r'C:\Users\DELL\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\1026\draft_meta_info.json'
with open(p_meta, 'r', encoding='utf-8') as f:
    meta = json.load(f)
meta['draft_name'] = 'DEMO WEB'
with open(p_meta, 'w', encoding='utf-8') as f:
    json.dump(meta, f, ensure_ascii=False)

p_root = r'C:\Users\DELL\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\root_meta_info.json'
with open(p_root, 'r', encoding='utf-8') as f:
    root = json.load(f)

# Find draft 1026 and move to front with name DEMO WEB
demo_draft = None
other_drafts = []
for d in root.get('all_draft_store', []):
    if d.get('draft_id') == 'C83AA405-E715-4542-B957-4CB3285AEA83' or d.get('draft_name') in ['1026', 'DEMO WEB']:
        d['draft_name'] = 'DEMO WEB'
        demo_draft = d
    else:
        other_drafts.append(d)

if demo_draft:
    root['all_draft_store'] = [demo_draft] + other_drafts

with open(p_root, 'w', encoding='utf-8') as f:
    json.dump(root, f, ensure_ascii=False)

print("Renamed project to 'DEMO WEB' in meta and root_meta!")

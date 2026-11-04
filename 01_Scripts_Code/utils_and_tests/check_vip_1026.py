import json, sys

sys.stdout.reconfigure(encoding='utf-8')
p = r'C:\Users\DELL\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\1026\draft_content.json'
with open(p, 'r', encoding='utf-8') as f:
    d = json.load(f)

print("Project duration:", d.get('duration'))
for k, v in d.get('materials', {}).items():
    if v:
        for it in v:
            if isinstance(it, dict):
                vip = it.get('vip_type', 0) or it.get('is_vip', False) or it.get('pre_applied_vip_materials', [])
                if vip or k in ['vocal_separations', 'realtime_denoises', 'smart_crops', 'ai_translates', 'smart_relights']:
                    print(f"Material {k}: id={it.get('id')}, type={it.get('type')}, vip={vip}")

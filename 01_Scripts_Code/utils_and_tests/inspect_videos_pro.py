import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

path = r'C:\Users\DELL\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\1024\draft_content.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("vocal_separations:", data.get('materials', {}).get('vocal_separations', []))
for v in data.get('materials', {}).get('videos', []):
    for k, val in v.items():
        if 'vip' in str(val).lower() or 'pro' in str(val).lower():
            print(f"video prop: {k} = {val}")

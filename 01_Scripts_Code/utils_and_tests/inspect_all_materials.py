import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

path = r'C:\Users\DELL\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\1026\draft_content.json'
with open(path, 'r', encoding='utf-8') as f:
    d = json.load(f)

for k, v in d['materials'].items():
    if len(v) > 0:
        print(f"Material category: {k} ({len(v)} items)")
        for item in v:
            if isinstance(item, dict):
                p = item.get('path') or item.get('name')
                if p:
                    print(f"   {p}")

import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

path = r'C:\Users\DELL\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\1024 (1)\draft_content.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("vocal_separations:", data.get('materials', {}).get('vocal_separations', []))
print("audio_effects:", data.get('materials', {}).get('audio_effects', []))
print("texts:", data.get('materials', {}).get('texts', []))
print("effects:", data.get('materials', {}).get('effects', []))

for k, v in data.get('materials', {}).items():
    s = json.dumps(v, ensure_ascii=False)
    if 'vip' in s.lower() or 'pro' in s.lower():
        print(f"Key '{k}' contains pro/vip")

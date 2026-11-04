import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

path = r'C:\Users\DELL\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\1024\draft_content.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# check materials audio_effects
print("audio_effects:", data.get('materials', {}).get('audio_effects', []))

# check if there are other pro flags
for k, v in data.get('materials', {}).items():
    s = json.dumps(v, ensure_ascii=False)
    if 'vip' in s.lower() or 'pro' in s.lower():
        print(f"Key with vip/pro: {k}")

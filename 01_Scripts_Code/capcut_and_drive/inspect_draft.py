import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

path = r'C:\Users\DELL\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\1026\draft_content.json'
with open(path, 'r', encoding='utf-8') as f:
    draft = json.load(f)

materials = draft.get('materials', {})
print("=== VIDEOS ===")
for v in materials.get('videos', []):
    print(f"Video: path={v.get('path')}, duration={v.get('duration')}, type={v.get('type')}")

print("\n=== AUDIOS ===")
for a in materials.get('audios', []):
    print(f"Audio: name={a.get('name')}, path={a.get('path')}, duration={a.get('duration')}")
    # print any pro or extra keys
    for k, val in a.items():
        if any(w in k.lower() for w in ['pro', 'vip', 'paid', 'feature', 'extra']):
            print(f"   {k}: {val}")

print("\n=== TEXTS ===")
for t in materials.get('texts', []):
    print(f"Text: content={t.get('content')}")

# Check any pro_features or vip info in root draft
for k, val in draft.items():
    if any(w in k.lower() for w in ['pro', 'vip', 'paid', 'feature']):
        print(f"Root key: {k} -> {val}")

# Search json string for 'pro' or 'extract' or 'trích xuất'
with open(path, 'r', encoding='utf-8') as f:
    raw_text = f.read()

import re
matches = re.findall(r'"[^"]*(?:pro|vip|extract|trích)[^"]*"\s*:\s*[^,\}\]]+', raw_text, re.IGNORECASE)
print(f"\nPro/Extract matches ({len(matches)}):")
for m in matches[:15]:
    print("  ", m)

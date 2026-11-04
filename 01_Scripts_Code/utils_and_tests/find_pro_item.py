import json
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

path = r'C:\Users\DELL\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\1024\draft_content.json'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

if "Thiếu niên" in text or "thieu nien" in text.lower():
    print("Found 'Thiếu niên' in draft_content.json!")
else:
    print("'Thiếu niên' NOT in draft_content.json directly, searching keys...")

data = json.loads(text)
for k, v in data.get('materials', {}).items():
    s = json.dumps(v, ensure_ascii=False)
    if "Thiếu niên" in s or "thieu nien" in s.lower():
        print(f"Found in materials -> {k}")

import json
import shutil
import os

path = r'C:\Users\DELL\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\1026\draft_content.json'
bak_path = path + '.bak_pre_pro_fix'
if not os.path.exists(bak_path):
    shutil.copy2(path, bak_path)

with open(path, 'r', encoding='utf-8') as f:
    d = json.load(f)

# Fix audio
for a in d.get('materials', {}).get('audios', []):
    if a.get('type') == 'extract_music':
        print(f"Patching audio {a.get('id')}: type extract_music -> music")
        a['type'] = 'music'
        a['name'] = 'hoàng đế trở về nhà.mp3'

# Check if extract_audio_last_index in draft
if 'extract_audio_last_index' in d:
    print("Removing extract_audio_last_index")
    del d['extract_audio_last_index']

with open(path, 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False)

print("draft_content.json patched successfully!")

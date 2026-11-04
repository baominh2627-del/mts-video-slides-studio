import json
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

path = r'C:\Users\DELL\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\1024\draft_content.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for audio in data.get('materials', {}).get('audios', []):
    print("AUDIO:", audio.get('name'), "PATH:", audio.get('path'))

for video in data.get('materials', {}).get('videos', []):
    print("VIDEO:", video.get('name'), "PATH:", video.get('path'))

for text in data.get('materials', {}).get('texts', []):
    print("TEXT:", text.get('content'))

for effect in data.get('materials', {}).get('effects', []):
    print("EFFECT:", effect.get('name'))

import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

path = r'C:\Users\DELL\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\1024\draft_content.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

video_track = data['tracks'][0]
print("Video track:", video_track.get('attribute', {}))
for seg in video_track['segments']:
    print("Video segment volume:", seg.get('volume'), "muted:", seg.get('is_muted'))

# check materials speeds and audios
for s in data['materials'].get('speeds', []):
    print("Speed material:", s)

for a in data['materials'].get('audios', []):
    print("Audio material:", a.get('name'), "volume:", a.get('volume'), "speed:", a.get('speed'))

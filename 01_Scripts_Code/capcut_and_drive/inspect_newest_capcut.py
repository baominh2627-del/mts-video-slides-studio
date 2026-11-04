import os, sys, time, json

sys.stdout.reconfigure(encoding='utf-8')
draft_root = r'C:\Users\DELL\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft'
projects = []
for d in os.listdir(draft_root):
    p = os.path.join(draft_root, d)
    if os.path.isdir(p):
        projects.append((d, os.path.getmtime(p)))

projects.sort(key=lambda x: x[1])
for d, mt in projects[-5:]:
    print(d, '->', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mt)))

newest_proj = projects[-1][0]
print('\nNewest project:', newest_proj)
p_dir = os.path.join(draft_root, newest_proj)
with open(os.path.join(p_dir, 'draft_content.json'), 'r', encoding='utf-8') as f:
    data = json.load(f)

print('Duration (us):', data.get('duration'))
print('Canvas config:', data.get('canvas_config'))
print('FPS:', data.get('fps'))
print('Tracks count:', len(data.get('tracks', [])))
for idx, tr in enumerate(data.get('tracks', [])):
    print(f"Track {idx} type={tr.get('type')}, segments={len(tr.get('segments', []))}")

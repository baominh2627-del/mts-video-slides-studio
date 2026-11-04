import json, glob, os

for p in glob.glob(r'C:\Users\DELL\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\*\draft_content.json'):
    try:
        with open(p, 'r', encoding='utf-8') as f:
            d = json.load(f)
            audios = d.get('materials', {}).get('audios', [])
            for a in audios:
                folder = os.path.basename(os.path.dirname(p))
                t = a.get('type')
                name = a.get('name')
                print(f"{folder}: type='{t}', name={repr(name)[:40]}")
    except Exception as e:
        pass

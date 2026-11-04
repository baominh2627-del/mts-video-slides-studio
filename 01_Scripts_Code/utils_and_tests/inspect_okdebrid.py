with open('okdebrid.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

import re
forms = re.findall(r'<form[^>]*>(.*?)</form>', text, re.DOTALL)
print("Forms:", len(forms))
for f in forms:
    print(f[:200])

for line in text.splitlines():
    if any(k in line.lower() for k in ['studocu', 'action', 'api', 'download', 'fetch']):
        print(line.strip()[:150])

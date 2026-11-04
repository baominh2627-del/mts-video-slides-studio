import urllib.request
import json
import re
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://www.tiktok.com/@huptron100devatli12/photo/7700035136015863047'
req = urllib.request.Request(
    url,
    headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }
)

opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler)
resp = opener.open(req)
html = resp.read().decode('utf-8', errors='ignore')

# Save full html for analysis
with open('tiktok_photo.html', 'w', encoding='utf-8') as f:
    f.write(html)
print(f"Saved tiktok_photo.html ({len(html)} bytes)")

# Search for image URLs in html
# TikTok images usually have format: https://p16-sign-sg.tiktokcdn.com/... or similar
image_urls = re.findall(r'https://[^"\'\s]+\.(?:jpeg|jpg|png|webp)[^"\'\s]*', html)
print(f"Found {len(image_urls)} potential image URLs in HTML")

# Check for tiktokcdn or byteoversea
cdn_images = [u for u in image_urls if 'tiktokcdn' in u or 'byteoversea' in u or 'muscdn' in u]
print(f"Found {len(cdn_images)} CDN image URLs")

# Also look for json scripts
scripts = re.findall(r'<script id="([^"]+)"[^>]*>(.*?)</script>', html)
for sid, scontent in scripts:
    print(f"Script id: {sid}, length: {len(scontent)}")
    if '7700035136015863047' in scontent:
        print(f"  -> Contains Post ID! Trying JSON parse...")
        try:
            j = json.loads(scontent)
            # Find all image URLs in j
            def find_urls(obj):
                urls = []
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        urls.extend(find_urls(v))
                elif isinstance(obj, list):
                    for item in obj:
                        urls.extend(find_urls(item))
                elif isinstance(obj, str):
                    if obj.startswith('http') and ('tiktokcdn' in obj or 'byteoversea' in obj):
                        urls.append(obj)
                return urls
            found = find_urls(j)
            print(f"  -> Found {len(found)} CDN URLs inside script {sid}")
            with open(f'{sid}_urls.txt', 'w', encoding='utf-8') as uf:
                for u in found:
                    uf.write(u + '\n')
        except Exception as e:
            print(f"  -> JSON parse error: {e}")

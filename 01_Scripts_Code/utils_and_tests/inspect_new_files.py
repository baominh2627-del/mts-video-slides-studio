import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

downloads = r'C:\Users\DELL\Documents\Downloads'
for item in os.listdir(downloads):
    if 'fdown' in item.lower() or 'phân biệt' in item.lower() or '3387' in item.lower():
        p = os.path.join(downloads, item)
        print(f"File: {item} | Size: {os.path.getsize(p)} bytes")

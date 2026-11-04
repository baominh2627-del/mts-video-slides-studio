import subprocess
import psutil

for p in psutil.process_iter(['pid', 'name', 'exe']):
    try:
        name = p.info['name']
        if name and 'capcut' in name.lower():
            print(f"Found: PID={p.info['pid']}, Name={name}, Exe={p.info['exe']}")
    except Exception:
        pass

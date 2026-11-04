import os, sys, time

sys.stdout.reconfigure(encoding='utf-8')
d = r"C:\Users\DELL\Documents\Downloads"
now = time.time()
print("Recent files in Downloads:")
for f in os.listdir(d):
    fp = os.path.join(d, f)
    if os.path.isfile(fp):
        mt = os.path.getmtime(fp)
        if now - mt < 10800: # last 3 hours
            t_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mt))
            print(f"  {f} ({os.path.getsize(fp)} bytes, {t_str})")

import shutil
u = shutil.disk_usage('C:\\')
print(f"Total: {u.total / (1024**3):.2f} GB")
print(f"Used: {u.used / (1024**3):.2f} GB")
print(f"Free: {u.free / (1024**3):.2f} GB")

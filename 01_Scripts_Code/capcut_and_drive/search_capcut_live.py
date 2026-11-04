import psutil
import win32gui
import win32process

pids = {}
for p in psutil.process_iter(['pid', 'name']):
    try:
        pids[p.info['pid']] = p.info['name']
    except:
        pass

def enum_cb(hwnd, extra):
    if win32gui.IsWindowVisible(hwnd):
        title = win32gui.GetWindowText(hwnd)
        rect = win32gui.GetWindowRect(hwnd)
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        pname = pids.get(pid, 'unknown')
        if 'capcut' in pname.lower() or 'capcut' in title.lower():
            print(f"HWND={hwnd}, PID={pid}, Name={pname}, Rect={rect}, Title='{title}'")

win32gui.EnumWindows(enum_cb, None)

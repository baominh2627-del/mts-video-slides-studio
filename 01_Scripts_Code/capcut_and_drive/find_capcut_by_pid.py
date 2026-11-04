import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import ctypes
from ctypes import wintypes
import psutil

capcut_pids = set()
for p in psutil.process_iter(['pid', 'name']):
    if p.info['name'] and 'capcut' in p.info['name'].lower():
        capcut_pids.add(p.info['pid'])

print("Active CapCut PIDs:", capcut_pids)

user32 = ctypes.windll.user32
WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

hwnds = []

def enum_proc(hwnd, lparam):
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    if pid.value in capcut_pids:
        vis = user32.IsWindowVisible(hwnd)
        rect = wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        w = rect.right - rect.left
        h = rect.bottom - rect.top
        
        # class name
        cls_buff = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, cls_buff, 256)
        
        # text
        t_buff = ctypes.create_unicode_buffer(256)
        user32.GetWindowTextW(hwnd, t_buff, 256)
        
        print(f"HWND={hwnd}, PID={pid.value}, Vis={vis}, Rect=({rect.left},{rect.top},{w}x{h}), Class={repr(cls_buff.value)}, Title={repr(t_buff.value)}")
        if vis and w > 500 and h > 300:
            hwnds.append((hwnd, pid.value, (rect.left, rect.top, w, h)))
    return True

user32.EnumWindows(WNDENUMPROC(enum_proc), 0)
print(f"Main CapCut windows found: {len(hwnds)}")

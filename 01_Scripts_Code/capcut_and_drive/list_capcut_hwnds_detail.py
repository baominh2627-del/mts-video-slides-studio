import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import ctypes
from ctypes import wintypes
import psutil

user32 = ctypes.windll.user32
user32.SetProcessDPIAware()

h_default_desk = user32.OpenDesktopW("Default", 0, False, 0x01FF)
user32.SetThreadDesktop(h_default_desk)

capcut_pids = set()
for p in psutil.process_iter(['pid', 'name']):
    if p.info['name'] and 'capcut' in p.info['name'].lower():
        capcut_pids.add(p.info['pid'])

def desk_proc(hwnd, lparam):
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    if pid.value in capcut_pids:
        cls_buff = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, cls_buff, 256)
        t_buff = ctypes.create_unicode_buffer(256)
        user32.GetWindowTextW(hwnd, t_buff, 256)
        vis = user32.IsWindowVisible(hwnd)
        rect = wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        w = rect.right - rect.left
        h = rect.bottom - rect.top
        print(f"CapCut HWND={hwnd}, Class={repr(cls_buff.value)}, Title={repr(t_buff.value)}, Vis={vis}, Rect=({rect.left},{rect.top},{w}x{h})")
    return True

DESKENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
user32.EnumDesktopWindows(h_default_desk, DESKENUMPROC(desk_proc), 0)

import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import ctypes
from ctypes import wintypes
import psutil

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

GENERIC_ALL = 0x10000000
DESKTOP_ALL = 0x01FF

# Try OpenDesktopW
h_default_desk = user32.OpenDesktopW("Default", 0, False, DESKTOP_ALL)
print("h_default_desk:", h_default_desk, "Error:", kernel32.GetLastError())

if h_default_desk:
    # SetThreadDesktop
    tid = kernel32.GetCurrentThreadId()
    set_res = user32.SetThreadDesktop(h_default_desk)
    print("SetThreadDesktop res:", set_res, "Error:", kernel32.GetLastError())
    
    capcut_pids = set()
    for p in psutil.process_iter(['pid', 'name']):
        if p.info['name'] and 'capcut' in p.info['name'].lower():
            capcut_pids.add(p.info['pid'])

    def desk_proc(hwnd, lparam):
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value in capcut_pids:
            rect = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            w = rect.right - rect.left
            h = rect.bottom - rect.top
            vis = user32.IsWindowVisible(hwnd)
            print(f"CapCut HWND={hwnd}, PID={pid.value}, Vis={vis}, Rect=({rect.left},{rect.top},{w}x{h})")
        return True

    DESKENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    res = user32.EnumDesktopWindows(h_default_desk, DESKENUMPROC(desk_proc), 0)
    print("EnumDesktopWindows res:", res)

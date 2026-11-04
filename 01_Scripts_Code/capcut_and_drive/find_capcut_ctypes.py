import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32

WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

hwnds = []

def enum_proc(hwnd, lparam):
    if user32.IsWindowVisible(hwnd):
        length = user32.GetWindowTextLengthW(hwnd)
        if length > 0:
            buff = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buff, length + 1)
            title = buff.value
            
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            
            rect = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            w = rect.right - rect.left
            h = rect.bottom - rect.top
            
            if 'capcut' in title.lower() or w > 800:
                print(f"HWND: {hwnd}, PID: {pid.value}, Size: {w}x{h}, Title: {repr(title)}")
                hwnds.append((hwnd, pid.value, title, (rect.left, rect.top, w, h)))
    return True

user32.EnumWindows(WNDENUMPROC(enum_proc), 0)
print(f"Total matching windows: {len(hwnds)}")

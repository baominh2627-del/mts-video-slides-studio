import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

h_winsta = user32.GetProcessWindowStation()
h_desk = user32.GetThreadDesktop(kernel32.GetCurrentThreadId())

print(f"ProcessWindowStation: {h_winsta}, ThreadDesktop: {h_desk}")

# Try to get station name
buff = ctypes.create_unicode_buffer(256)
user32.GetUserObjectInformationW(h_winsta, 2, buff, 512, None)
print(f"Station Name: {buff.value}")

user32.GetUserObjectInformationW(h_desk, 2, buff, 512, None)
print(f"Desktop Name: {buff.value}")

# Try EnumDesktopWindows
count = [0]
def desk_proc(hwnd, lparam):
    count[0] += 1
    return True

DESKENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
res = user32.EnumDesktopWindows(h_desk, DESKENUMPROC(desk_proc), 0)
err = kernel32.GetLastError()
print(f"EnumDesktopWindows result: {res}, Error: {err}, Windows count: {count[0]}")

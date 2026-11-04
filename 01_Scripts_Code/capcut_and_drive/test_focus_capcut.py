import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import ctypes
from ctypes import wintypes
import time
from PIL import ImageGrab

user32 = ctypes.windll.user32
user32.SetProcessDPIAware()

h_default_desk = user32.OpenDesktopW("Default", 0, False, 0x01FF)
user32.SetThreadDesktop(h_default_desk)

# Find CapCut Main Window
capcut_hwnd = None
def desk_proc(hwnd, lparam):
    global capcut_hwnd
    cls_buff = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, cls_buff, 256)
    t_buff = ctypes.create_unicode_buffer(256)
    user32.GetWindowTextW(hwnd, t_buff, 256)
    
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    w = rect.right - rect.left
    h = rect.bottom - rect.top
    vis = user32.IsWindowVisible(hwnd)
    
    if vis and cls_buff.value == 'Qt622QWindowIcon' and t_buff.value == 'CapCut' and w >= 1800:
        capcut_hwnd = hwnd
        print(f"Found CapCut MainWindow HWND={hwnd}, Rect=({rect.left},{rect.top},{w}x{h})")
    return True

DESKENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
user32.EnumDesktopWindows(h_default_desk, DESKENUMPROC(desk_proc), 0)

if capcut_hwnd:
    print(f"Bringing CapCut (HWND={capcut_hwnd}) to front...")
    # Bypass Windows foreground lock
    user32.keybd_event(0x12, 0, 0, 0)
    user32.keybd_event(0x12, 0, 2, 0)
    
    SW_RESTORE = 9
    SW_SHOW = 5
    user32.ShowWindow(capcut_hwnd, SW_RESTORE)
    user32.ShowWindow(capcut_hwnd, SW_SHOW)
    user32.SetForegroundWindow(capcut_hwnd)
    user32.BringWindowToTop(capcut_hwnd)
    time.sleep(1.0)
    
    # Capture screen to verify CapCut is in front
    im = ImageGrab.grab()
    im.save(r'C:\Users\DELL\Documents\CODE\DU_AN\capcut_in_front.png')
    print("Saved capcut_in_front.png")
else:
    print("CapCut main window not found!")

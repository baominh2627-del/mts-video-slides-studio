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
    cls = cls_buff.value
    if 'MainWindow_QMLTYPE' in cls:
        capcut_hwnd = hwnd
        print(f"Found CapCut MainWindow HWND={hwnd}, Class={cls}")
    return True

DESKENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
user32.EnumDesktopWindows(h_default_desk, DESKENUMPROC(desk_proc), 0)

if capcut_hwnd:
    print("Activating CapCut window...")
    # Send Alt key down/up to bypass Windows SetForegroundWindow restriction
    user32.keybd_event(0x12, 0, 0, 0)
    user32.keybd_event(0x12, 0, 2, 0)
    
    SW_RESTORE = 9
    user32.ShowWindow(capcut_hwnd, SW_RESTORE)
    user32.SetForegroundWindow(capcut_hwnd)
    time.sleep(1.0)
    
    # Capture screen
    im = ImageGrab.grab()
    im.save(r'C:\Users\DELL\Documents\CODE\DU_AN\capcut_activated.png')
    print("Saved capcut_activated.png")
else:
    print("CapCut window not found!")

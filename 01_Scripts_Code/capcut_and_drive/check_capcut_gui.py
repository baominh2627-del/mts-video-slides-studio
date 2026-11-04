import ctypes
from ctypes import wintypes
import time
from PIL import ImageGrab
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

user32 = ctypes.windll.user32
user32.SetProcessDPIAware()

screen_w = user32.GetSystemMetrics(0)
screen_h = user32.GetSystemMetrics(1)
print(f"Screen metrics: {screen_w}x{screen_h}")

capcut_windows = []
def enum_cb(hwnd, lparam):
    if not user32.IsWindowVisible(hwnd):
        return True
    length = user32.GetWindowTextLengthW(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buff, length + 1)
    cls_buff = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, cls_buff, 256)
    title = buff.value
    cls = cls_buff.value
    
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    w = rect.right - rect.left
    h = rect.bottom - rect.top
    
    if 'CapCut' in title or 'MainWindow_QMLTYPE' in cls or '1026' in title or 'CapCut' in cls:
        print(f"HWND={hwnd}, Title='{title}', Class='{cls}', Rect=({rect.left}, {rect.top}, {rect.right}, {rect.bottom}) [Size: {w}x{h}]")
        capcut_windows.append((hwnd, title, cls, rect))
    return True

WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
user32.EnumWindows(WNDENUMPROC(enum_cb), 0)

im = ImageGrab.grab()
im.save(r'C:\Users\DELL\Documents\CODE\DU_AN\current_screen.png')
print(f"Saved current_screen.png, size: {im.size}")

import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
import ctypes
from ctypes import wintypes
import time
from PIL import Image

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

user32.SetProcessDPIAware()

h_desk = user32.OpenDesktopW('Default', 0, False, 0x01FF)
user32.SetThreadDesktop(h_desk)

capcut_hwnd = None
def desk_proc(hwnd, lparam):
    global capcut_hwnd
    tb = ctypes.create_unicode_buffer(256)
    user32.GetWindowTextW(hwnd, tb, 256)
    cb = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, cb, 256)
    if 'capcut' in tb.value.lower() and 'qt6' in cb.value.lower():
        rect = wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        w = rect.right - rect.left
        h = rect.bottom - rect.top
        if w > 1000 and h > 500:
            capcut_hwnd = hwnd
    return True

DESKENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
user32.EnumDesktopWindows(h_desk, DESKENUMPROC(desk_proc), 0)

if not capcut_hwnd:
    print("CapCut main window not found!")
    exit(1)

print(f"Target CapCut HWND: {capcut_hwnd}")

# Bring to front
user32.keybd_event(0x12, 0, 0, 0)
user32.keybd_event(0x12, 0, 2, 0)

SW_SHOWMAXIMIZED = 3
user32.ShowWindow(capcut_hwnd, SW_SHOWMAXIMIZED)
user32.SetForegroundWindow(capcut_hwnd)
time.sleep(0.8)

# Capture
w = user32.GetSystemMetrics(0)
h = user32.GetSystemMetrics(1)
hdc_screen = user32.GetDC(0)
hdc_mem = gdi32.CreateCompatibleDC(hdc_screen)
h_bm = gdi32.CreateCompatibleBitmap(hdc_screen, w, h)
gdi32.SelectObject(hdc_mem, h_bm)

SRCCOPY = 0x00CC0020
gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc_screen, 0, 0, SRCCOPY)

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ('biSize', wintypes.DWORD),
        ('biWidth', wintypes.LONG),
        ('biHeight', wintypes.LONG),
        ('biPlanes', wintypes.WORD),
        ('biBitCount', wintypes.WORD),
        ('biCompression', wintypes.DWORD),
        ('biSizeImage', wintypes.DWORD),
        ('biXPelsPerMeter', wintypes.LONG),
        ('biYPelsPerMeter', wintypes.LONG),
        ('biClrUsed', wintypes.DWORD),
        ('biClrImportant', wintypes.DWORD)
    ]

bmi = BITMAPINFOHEADER()
bmi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
bmi.biWidth = w
bmi.biHeight = -h
bmi.biPlanes = 1
bmi.biBitCount = 32
bmi.biCompression = 0

buf = ctypes.create_string_buffer(w * h * 4)
gdi32.GetDIBits(hdc_mem, h_bm, 0, h, buf, ctypes.byref(bmi), 0)

im = Image.frombuffer('RGBA', (w, h), buf, 'raw', 'BGRA', 0, 1).convert('RGB')
im.save(r'C:\Users\DELL\Documents\CODE\DU_AN\capcut_live_check.png')
print("Saved capcut_live_check.png")

gdi32.DeleteObject(h_bm)
gdi32.DeleteDC(hdc_mem)
user32.ReleaseDC(0, hdc_screen)

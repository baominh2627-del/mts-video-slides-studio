import ctypes
from ctypes import wintypes
import time
from PIL import Image

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

user32.SetProcessDPIAware()

h_desk = user32.OpenDesktopW('Default', 0, False, 0x01FF)
user32.SetThreadDesktop(h_desk)

# Click Xuat button at (1734, 22)
print("Clicking Xuat button at (1734, 22)...")
user32.SetCursorPos(1734, 22)
time.sleep(0.1)

MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(0.1)
user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

print("Waiting 2.0s for Export modal...")
time.sleep(2.0)

# Capture screen
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
im.save(r'C:\Users\DELL\Documents\CODE\DU_AN\capcut_export_modal.png')
print("Saved capcut_export_modal.png")

gdi32.DeleteObject(h_bm)
gdi32.DeleteDC(hdc_mem)
user32.ReleaseDC(0, hdc_screen)

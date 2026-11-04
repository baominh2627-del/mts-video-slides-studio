import ctypes
from ctypes import wintypes
import sys
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
kernel32 = ctypes.windll.kernel32

user32.SetProcessDPIAware()

h_desk = user32.OpenDesktopW('Default', 0, False, 0x01FF)
res = user32.SetThreadDesktop(h_desk)
print(f"SetThreadDesktop result: {res}")

# Get DC of Default desktop
hdc_screen = user32.GetDC(0)
w = user32.GetSystemMetrics(0)
h = user32.GetSystemMetrics(1)
print(f"Screen metrics: {w}x{h}")

hdc_mem = gdi32.CreateCompatibleDC(hdc_screen)
h_bm = gdi32.CreateCompatibleBitmap(hdc_screen, w, h)
gdi32.SelectObject(hdc_mem, h_bm)

SRCCOPY = 0x00CC0020
gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc_screen, 0, 0, SRCCOPY)

# Read bitmap data
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
bmi.biHeight = -h  # top-down
bmi.biPlanes = 1
bmi.biBitCount = 32
bmi.biCompression = 0

buf = ctypes.create_string_buffer(w * h * 4)
gdi32.GetDIBits(hdc_mem, h_bm, 0, h, buf, ctypes.byref(bmi), 0)

im = Image.frombuffer('RGBA', (w, h), buf, 'raw', 'BGRA', 0, 1).convert('RGB')
im.save(r'C:\Users\DELL\Documents\CODE\DU_AN\capcut_live_screen.png')
print("Saved capcut_live_screen.png successfully!")

# Clean up
gdi32.DeleteObject(h_bm)
gdi32.DeleteDC(hdc_mem)
user32.ReleaseDC(0, hdc_screen)

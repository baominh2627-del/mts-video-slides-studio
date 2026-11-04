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

# Click "Quay lại phần chỉnh sửa" at (750, 870)
print("Clicking 'Quay lại phần chỉnh sửa' at (750, 870)...")
user32.SetCursorPos(750, 870)
time.sleep(0.1)

MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(0.1)
user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

time.sleep(1.0)

# Capture screen
im = ImageGrab.grab()
im.save(r'C:\Users\DELL\Documents\CODE\DU_AN\after_close_modal.png')
print("Saved after_close_modal.png")

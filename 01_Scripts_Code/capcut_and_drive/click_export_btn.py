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

# Click center of Xuất button: (1737, 22)
print("Moving cursor to (1737, 22) and clicking...")
user32.SetCursorPos(1737, 22)
time.sleep(0.2)

# Mouse event: left down, left up
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(0.1)
user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

print("Clicked! Waiting 2 seconds for export dialog...")
time.sleep(2.0)

# Capture screen
im = ImageGrab.grab()
im.save(r'C:\Users\DELL\Documents\CODE\DU_AN\after_click_export.png')
print("Saved after_click_export.png")

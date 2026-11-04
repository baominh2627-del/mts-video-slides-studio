import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import ctypes
import time
from PIL import ImageGrab

user32 = ctypes.windll.user32
h_default_desk = user32.OpenDesktopW("Default", 0, False, 0x01FF)
user32.SetThreadDesktop(h_default_desk)

# Capture current screen
screenshot = ImageGrab.grab()
screenshot.save(r'C:\Users\DELL\Documents\CODE\DU_AN\current_screen.png')
print("Saved current_screen.png, size:", screenshot.size)

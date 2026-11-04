import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import ctypes
from ctypes import wintypes
import time

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

DESKTOP_ALL = 0x01FF
h_default_desk = user32.OpenDesktopW("Default", 0, False, DESKTOP_ALL)
user32.SetThreadDesktop(h_default_desk)

import uiautomation as auto

# Let's search for controls with Name='Xuất' or similar
print("Searching for 'Xuất' control in UIAutomation...")
export_btn = auto.Control(searchDepth=10, Name='Xuất')
if export_btn.Exists(0, 0):
    print("Found Export button:", export_btn)
    print("Rect:", export_btn.BoundingRectangle)
else:
    print("Button 'Xuất' not directly found by Name, searching by other criteria...")
    # Let's inspect root children
    root = auto.GetRootControl()
    for c in root.GetChildren():
        print(f"Top: Name='{c.Name}', Class='{c.ClassName}', Rect={c.BoundingRectangle}")

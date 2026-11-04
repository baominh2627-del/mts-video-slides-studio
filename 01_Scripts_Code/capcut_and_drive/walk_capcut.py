import ctypes, sys
sys.stdout.reconfigure(encoding='utf-8')
desk = ctypes.windll.user32.OpenDesktopW('Default', 0, False, 0x01FF)
ctypes.windll.user32.SetThreadDesktop(desk)

import uiautomation as auto

capcut_win = auto.WindowControl(searchDepth=1, SubName='CapCut')
if capcut_win.Exists(1, 1):
    print("Found CapCut window:", capcut_win.Name, capcut_win.BoundingRectangle)
    for c, depth in auto.WalkControl(capcut_win, maxDepth=5):
        if c.Name:
            print(f"{'  '*depth} {c.ControlType} Name='{c.Name}' Rect={c.BoundingRectangle}")
else:
    print("CapCut window not found")

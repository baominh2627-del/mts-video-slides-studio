import ctypes, sys
sys.stdout.reconfigure(encoding='utf-8')
desk = ctypes.windll.user32.OpenDesktopW('Default', 0, False, 0x01FF)
ctypes.windll.user32.SetThreadDesktop(desk)

import uiautomation as auto

capcut_win = auto.WindowControl(searchDepth=1, ClassName='Qt622QWindowIcon')
if not capcut_win.Exists(0, 0):
    print("CapCut window not found by ClassName Qt622QWindowIcon")
    # try searching by Name
    capcut_win = auto.WindowControl(searchDepth=1, SubName='CapCut')

if capcut_win.Exists(1, 1):
    print("Found CapCut window:", capcut_win.Name, capcut_win.BoundingRectangle)
    # Search for button with Name containing 'Xuất' or 'Export'
    export_btn = capcut_win.ButtonControl(SubName='Xuất')
    if export_btn.Exists(1, 1):
        print("Found Xuất button:", export_btn.Name, export_btn.BoundingRectangle)
    else:
        print("Xuất button not found directly. Listing buttons in top bar...")
        for c, depth in auto.WalkControl(capcut_win, maxDepth=4):
            if c.ControlType in [auto.ControlType.ButtonControl, auto.ControlType.TextControl] and c.Name:
                if any(k in c.Name for k in ['Xuất', 'Pro', 'Chia sẻ', 'Cơ bản', 'Tốc độ', 'Dự án', '1026']):
                    print(f"  {c.ControlType} Name='{c.Name}' Rect={c.BoundingRectangle}")
else:
    print("Could not find CapCut window")

import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import uiautomation as auto

print("Searching for CapCut window...")
capcut_win = auto.WindowControl(searchDepth=2, ClassName='MainWindow')
if not capcut_win.Exists(0, 0):
    capcut_win = auto.WindowControl(searchDepth=2, SubName='CapCut')

print("Found window:", capcut_win.Exists(0, 0))
if capcut_win.Exists(0, 0):
    print("CapCut Window Name:", capcut_win.Name)
    print("CapCut BoundingRectangle:", capcut_win.BoundingRectangle)
else:
    # let's list all windows with WindowControl
    w = auto.GetRootControl().GetFirstChildControl()
    while w:
        print(f"Win: Name='{w.Name}', Class='{w.ClassName}', PID={w.ProcessId}")
        w = w.GetNextSiblingControl()

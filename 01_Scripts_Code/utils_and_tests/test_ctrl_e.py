import ctypes, time, sys
sys.stdout.reconfigure(encoding='utf-8')
desk = ctypes.windll.user32.OpenDesktopW('Default', 0, False, 0x01FF)
ctypes.windll.user32.SetThreadDesktop(desk)

# Remember current foreground
old_fg = ctypes.windll.user32.GetForegroundWindow()

capcut_hwnd = 3476938 # or find CapCut
for hwnd in [3476938, 2885974, 4984820]:
    if ctypes.windll.user32.IsWindow(hwnd):
        capcut_hwnd = hwnd
        break

print(f"Target CapCut hwnd: {capcut_hwnd}, Old FG: {old_fg}")

# SetForegroundWindow
ctypes.windll.user32.SetForegroundWindow(capcut_hwnd)
time.sleep(0.5)

# Send Ctrl+E via keybd_event
VK_CONTROL = 0x11
VK_E = 0x45
KEYEVENTF_KEYUP = 0x0002

ctypes.windll.user32.keybd_event(VK_CONTROL, 0, 0, 0)
ctypes.windll.user32.keybd_event(VK_E, 0, 0, 0)
time.sleep(0.05)
ctypes.windll.user32.keybd_event(VK_E, 0, KEYEVENTF_KEYUP, 0)
ctypes.windll.user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)

time.sleep(1.0)

# Check what windows opened
from PIL import ImageGrab
im = ImageGrab.grab()
im.save('c:/Users/DELL/Documents/CODE/DU_AN/after_ctrl_e.png')
print("Saved after_ctrl_e.png")

# Restore old foreground
if old_fg:
    ctypes.windll.user32.SetForegroundWindow(old_fg)

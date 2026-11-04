import win32gui
import win32process

capcut_pids = {2880, 24248, 26188, 26416, 27124, 27128, 27140, 27360, 28156, 30572}

def enum_cb(hwnd, extra):
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    if pid in capcut_pids:
        title = win32gui.GetWindowText(hwnd)
        rect = win32gui.GetWindowRect(hwnd)
        vis = win32gui.IsWindowVisible(hwnd)
        cls = win32gui.GetClassName(hwnd)
        print(f"HWND={hwnd}, PID={pid}, Visible={vis}, Rect={rect}, Class={cls}, Title='{title}'")

win32gui.EnumWindows(enum_cb, None)

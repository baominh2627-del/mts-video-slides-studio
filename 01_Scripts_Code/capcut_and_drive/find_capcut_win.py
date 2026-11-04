import win32gui
import win32process

def enum_windows_callback(hwnd, extra):
    if win32gui.IsWindowVisible(hwnd):
        title = win32gui.GetWindowText(hwnd)
        rect = win32gui.GetWindowRect(hwnd)
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        if 'capcut' in title.lower() or (rect[2] - rect[0] > 500 and rect[3] - rect[1] > 300):
            print(f"HWND={hwnd}, PID={pid}, Rect={rect}, Title='{title}'")

win32gui.EnumWindows(enum_windows_callback, None)

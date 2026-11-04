for pkg in ['pyautogui', 'pywinauto', 'uiautomation', 'win32gui', 'win32con']:
    try:
        __import__(pkg)
        print(f"{pkg}: AVAILABLE")
    except ImportError:
        print(f"{pkg}: NOT AVAILABLE")

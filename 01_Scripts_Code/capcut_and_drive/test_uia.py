import pygetwindow as gw

try:
    titles = gw.getAllTitles()
    print("Window titles count:", len(titles))
    for t in titles:
        if t.strip():
            print("Title:", repr(t))
except Exception as e:
    print("pygetwindow error:", e)

try:
    import uiautomation as auto
    root = auto.GetRootControl()
    print("UIAutomation root:", root)
    for child in root.GetChildren():
        print(f"Child: Name='{child.Name}', Class='{child.ClassName}', ControlType='{child.ControlTypeName}'")
except Exception as e:
    print("uiautomation error:", e)

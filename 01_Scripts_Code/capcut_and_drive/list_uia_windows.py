import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import uiautomation as auto

root = auto.GetRootControl()
print("UIAutomation root found!")
for child in root.GetChildren():
    print(f"Child: Name='{child.Name}', Class='{child.ClassName}', ControlType='{child.ControlTypeName}', ProcessId={child.ProcessId}")

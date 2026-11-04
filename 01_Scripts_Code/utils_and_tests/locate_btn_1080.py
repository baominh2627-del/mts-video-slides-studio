import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import cv2
import numpy as np

im = cv2.imread(r'C:\Users\DELL\Documents\CODE\DU_AN\capcut_in_front.png')
# Check top bar: y: 0 to 50, x: 1600 to 1900
crop = im[0:50, 1650:1850]
cv2.imwrite(r'C:\Users\DELL\Documents\CODE\DU_AN\xuat_btn_1080.png', crop)

# Cyan button: BGR where B > 150, G > 150, R < 100
mask = (crop[:, :, 0] > 150) & (crop[:, :, 1] > 150) & (crop[:, :, 2] < 100)
y_idx, x_idx = np.where(mask)
if len(x_idx) > 0:
    min_x, max_x = int(x_idx.min()) + 1650, int(x_idx.max()) + 1650
    min_y, max_y = int(y_idx.min()), int(y_idx.max())
    cx = (min_x + max_x) // 2
    cy = (min_y + max_y) // 2
    print(f"Xuất button in 1080p: x=[{min_x}, {max_x}], y=[{min_y}, {max_y}], center=({cx}, {cy})")

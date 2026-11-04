import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import cv2
import numpy as np

im = cv2.imread(r'C:\Users\DELL\.gemini\antigravity\brain\835e6faf-41ce-4061-8bb6-9ca9efc0ff6c\.user_uploaded\media_1792815394091_e1e155a5.png')
# crop right side of top bar (x from 800 to 1024, y from 0 to 45)
crop = im[0:45, 850:980]
cv2.imwrite(r'C:\Users\DELL\Documents\CODE\DU_AN\xuat_btn_crop.png', crop)

# find the teal button in this crop
# In the crop:
mask = (crop[:, :, 0] > 140) & (crop[:, :, 1] > 140) & (crop[:, :, 2] < 80)
y_idx, x_idx = np.where(mask)
if len(x_idx) > 0:
    min_x, max_x = int(x_idx.min()) + 850, int(x_idx.max()) + 850
    min_y, max_y = int(y_idx.min()), int(y_idx.max())
    cx = (min_x + max_x) // 2
    cy = (min_y + max_y) // 2
    print(f"Xuất button in 1024: x=[{min_x}, {max_x}], y=[{min_y}, {max_y}], center=({cx}, {cy})")
    
    # In 1920:
    scale = 1920.0 / 1024.0
    print(f"In 1920: center=({cx * scale:.1f}, {cy * scale:.1f})")

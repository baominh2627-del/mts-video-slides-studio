import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import cv2
import numpy as np

im = cv2.imread(r'C:\Users\DELL\.gemini\antigravity\brain\835e6faf-41ce-4061-8bb6-9ca9efc0ff6c\.user_uploaded\media_1792815394091_e1e155a5.png')
h, w, _ = im.shape

# Top bar is y: 0 to 40
top_bar = im[0:45, :]

# The "Xuất" button is teal/cyan (high green and blue, lower red: BGR ~ [180, 180, 0])
# Let's find cyan pixels in top bar
mask = (top_bar[:, :, 0] > 140) & (top_bar[:, :, 1] > 140) & (top_bar[:, :, 2] < 80)
y_idx, x_idx = np.where(mask)

if len(x_idx) > 0:
    min_x, max_x = int(x_idx.min()), int(x_idx.max())
    min_y, max_y = int(y_idx.min()), int(y_idx.max())
    cx = (min_x + max_x) // 2
    cy = (min_y + max_y) // 2
    print(f"In 1024x537: 'Xuất' button is at x=[{min_x}, {max_x}], y=[{min_y}, {max_y}], center=({cx}, {cy})")
    
    # Scale to 1920x1020
    scale_x = 1920.0 / w
    scale_y = 1020.0 / 537.0 # wait, let's check top bar height scaling
    # In desktop window, top bar is fixed height ~36-40px, or scaled proportionally
    print(f"Scaled to 1920x1020: x={cx * scale_x:.1f}, y={cy * (1020.0/537.0):.1f}")
else:
    print("Could not find cyan mask, let's inspect right side of top bar")
    cv2.imwrite(r'C:\Users\DELL\Documents\CODE\DU_AN\top_bar_right.png', im[0:45, int(w*0.7):])

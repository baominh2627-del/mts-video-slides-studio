import cv2
import numpy as np

im = cv2.imread(r'C:\Users\DELL\Documents\CODE\DU_AN\fdown_build\frame_0pct_0.0s.jpg')
h, w, _ = im.shape
print(f"Frame size: {w}x{h}")

# 1. Top-left green logo bbox
tl_crop = im[20:140, 20:150]
tl_mask = (tl_crop[:, :, 1] > 80) & (tl_crop[:, :, 1] > tl_crop[:, :, 0].astype(int) + 20) & (tl_crop[:, :, 1] > tl_crop[:, :, 2].astype(int) + 20)
y_idx, x_idx = np.where(tl_mask)
if len(y_idx) > 0:
    min_y, max_y = int(y_idx.min() + 20), int(y_idx.max() + 20)
    min_x, max_x = int(x_idx.min() + 20), int(x_idx.max() + 20)
    print(f"Top-left logo: y=[{min_y}, {max_y}] (h={max_y-min_y}), x=[{min_x}, {max_x}] (w={max_x-min_x})")

# 2. Bottom green text bbox
bot_crop = im[920:990, 30:550]
bot_mask = (bot_crop[:, :, 1] > 80) & (bot_crop[:, :, 1] > bot_crop[:, :, 0].astype(int) + 20) & (bot_crop[:, :, 1] > bot_crop[:, :, 2].astype(int) + 20)
y_idx, x_idx = np.where(bot_mask)
if len(y_idx) > 0:
    min_y, max_y = int(y_idx.min() + 920), int(y_idx.max() + 920)
    min_x, max_x = int(x_idx.min() + 30), int(x_idx.max() + 30)
    print(f"Bottom text: y=[{min_y}, {max_y}] (h={max_y-min_y}), x=[{min_x}, {max_x}] (w={max_x-min_x})")

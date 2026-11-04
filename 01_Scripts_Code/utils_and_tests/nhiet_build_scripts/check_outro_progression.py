import cv2
import numpy as np

for s in [150.0, 152.0, 154.0, 156.0, 158.0, 159.0]:
    im = cv2.imread(rf'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\check_outro_{s:.1f}s.jpg')
    if im is None:
        im = cv2.imread(rf'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\scene_{s:.1f}s.jpg')
    # Check green pixels in logo area [200:310, 230:360]
    crop = im[200:310, 230:360]
    mask = (crop[:, :, 1] > 90) & (crop[:, :, 1] > crop[:, :, 0].astype(int) + 20) & (crop[:, :, 1] > crop[:, :, 2].astype(int) + 20)
    # Check if Delta U is visible at y: [400, 520], x: [150, 430]
    du_crop = im[400:520, 150:430]
    du_white = np.count_nonzero(du_crop > 150)
    print(f's={s}s: green logo pixels = {np.count_nonzero(mask)}, Delta U brightness = {du_white}')

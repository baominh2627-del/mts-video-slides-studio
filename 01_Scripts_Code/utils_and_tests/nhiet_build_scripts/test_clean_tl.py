import cv2
import numpy as np

im = cv2.imread(r'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\frame_5s.jpg')

# Interpolate column 68 to 82 using column 66 and column 84
c_left = im[15:140, 66].astype(float)
c_right = im[15:140, 84].astype(float)

for x in range(67, 84):
    alpha = (x - 66) / (84.0 - 66.0)
    im[15:140, x] = np.clip(c_left * (1.0 - alpha) + c_right * alpha, 0, 255).astype(np.uint8)

cv2.imwrite(r'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\tl_corner_cleaned.jpg', im[0:180, 0:240])
print('Saved tl_corner_cleaned.jpg')

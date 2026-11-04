import cv2
import numpy as np

orig = cv2.imread(r'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\frame_5s.jpg')
# crop top left corner
tl_crop = orig[0:180, 0:240]
cv2.imwrite(r'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\tl_corner_orig.jpg', tl_crop)

# Let's inspect max brightness and colors in this crop
print('tl_crop shape:', tl_crop.shape)
print('tl_crop mean:', np.mean(tl_crop, axis=(0,1)))

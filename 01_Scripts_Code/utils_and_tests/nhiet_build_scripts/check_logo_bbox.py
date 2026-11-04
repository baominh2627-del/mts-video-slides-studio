import cv2
import numpy as np

orig = cv2.imread(r'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\check_outro_160.0s.jpg')
h, w, _ = orig.shape
print(f'Dimensions: {w}x{h}')

crop = orig[180:330, 180:400]
# Old logo has green pixels
mask = (crop[:, :, 1] > 90) & (crop[:, :, 1] > crop[:, :, 0].astype(int) + 20) & (crop[:, :, 1] > crop[:, :, 2].astype(int) + 20)
y_idx, x_idx = np.where(mask)
if len(y_idx) > 0:
    min_y, max_y = int(y_idx.min() + 180), int(y_idx.max() + 180)
    min_x, max_x = int(x_idx.min() + 180), int(x_idx.max() + 180)
    print(f'Green logo bounding box: y=[{min_y}, {max_y}], x=[{min_x}, {max_x}]')
else:
    print('No green pixels found in crop range')

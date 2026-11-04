import cv2
import numpy as np

f4764 = cv2.imread(r'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\cut_frame_4764.jpg')
f4765 = cv2.imread(r'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\cut_frame_4765.jpg')
f4766 = cv2.imread(r'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\cut_frame_4766.jpg')

# Check difference between 4764 and 4765, 4765 and 4766
print('Diff 4764-4765:', np.mean(np.abs(f4764.astype(float) - f4765.astype(float))))
print('Diff 4765-4766:', np.mean(np.abs(f4765.astype(float) - f4766.astype(float))))

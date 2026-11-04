import cv2
import numpy as np

orig = cv2.imread(r'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\tl_corner_orig.jpg')

# Let's inspect where pixels differ from background
# Background around x=10..30, y=10..150 is very uniform dark navy
bg_sample = orig[10:150, 10:40]
print('Background mean BGR:', np.mean(bg_sample, axis=(0,1)))

# Let's check brightness across columns x from 40 to 120
col_means = [np.mean(orig[20:135, x]) for x in range(40, 130)]
print('Column means x=40..129:', col_means)

# Let's see where the artifact is located:
# Notice x=60 to 110 has the artifact column

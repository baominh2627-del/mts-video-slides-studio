import cv2
import numpy as np

# Load s_05.jpg and s_15.jpg
img5 = cv2.imread(r"c:\Users\DELL\Documents\CODE\DU_AN\scenes_cb\s_05.jpg")
img15 = cv2.imread(r"c:\Users\DELL\Documents\CODE\DU_AN\scenes_cb\s_15.jpg")
img25 = cv2.imread(r"c:\Users\DELL\Documents\CODE\DU_AN\scenes_cb\s_25.jpg")
img65 = cv2.imread(r"c:\Users\DELL\Documents\CODE\DU_AN\scenes_cb\s_65.jpg")

# Apply colorlevels to all
def apply_white(bgr):
    res = bgr.astype(np.float32)
    res[:,:,0] = np.clip((res[:,:,0] - 10.2) / (181.05 - 10.2) * 255.0, 0, 255)
    res[:,:,1] = np.clip((res[:,:,1] - 10.2) / (191.25 - 10.2) * 255.0, 0, 255)
    res[:,:,2] = np.clip((res[:,:,2] - 10.2) / (201.45 - 10.2) * 255.0, 0, 255)
    return res.astype(np.uint8)

w5 = apply_white(img5)
w15 = apply_white(img15)
w25 = apply_white(img25)
w65 = apply_white(img65)

# Let's inspect the frequency / properties of the horizontal stripes
# Take a vertical slice in a pure background area of w5, e.g. x=500, y from 100 to 500
slice_bg = w5[150:350, 500, 0] # Blue channel (which is grayscale background)
print("Background slice values (first 30 pixels):", slice_bg[:30])

# Let's measure the period of stripes:
# Peak to peak distance
diffs = np.diff(slice_bg.astype(int))
print("Diffs min/max:", np.min(diffs), np.max(diffs))

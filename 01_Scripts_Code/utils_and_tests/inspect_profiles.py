import cv2
import numpy as np

img = cv2.imread(r"c:\Users\DELL\Documents\CODE\DU_AN\inspect_vid\sec_08.jpg")

def apply_white(bgr):
    res = bgr.astype(np.float32)
    res[:,:,0] = np.clip((res[:,:,0] - 10.2) / (181.05 - 10.2) * 255.0, 0, 255)
    res[:,:,1] = np.clip((res[:,:,1] - 10.2) / (191.25 - 10.2) * 255.0, 0, 255)
    res[:,:,2] = np.clip((res[:,:,2] - 10.2) / (201.45 - 10.2) * 255.0, 0, 255)
    return res.astype(np.uint8)

white = apply_white(img)
gray = cv2.cvtColor(white, cv2.COLOR_BGR2GRAY)

# Let's inspect a crop with text and stripes:
# e.g., the 40°C box at [320:410, 1130:1310]
crop_box = white[320:410, 1130:1310]
cv2.imwrite(r"c:\Users\DELL\Documents\CODE\DU_AN\crop_box_orig.png", crop_box)

# And a crop of background stripes only: [200:290, 800:950]
crop_bg = white[200:290, 800:950]
cv2.imwrite(r"c:\Users\DELL\Documents\CODE\DU_AN\crop_bg_orig.png", crop_bg)

print("Saved crop images")

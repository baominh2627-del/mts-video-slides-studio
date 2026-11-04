import cv2
import numpy as np

img = cv2.imread(r"c:\Users\DELL\Documents\CODE\DU_AN\inspect_vid\sec_08.jpg")
h, w, c = img.shape

# 1. White levels
def apply_white(bgr):
    res = bgr.astype(np.float32)
    res[:,:,0] = np.clip((res[:,:,0] - 10.2) / (181.05 - 10.2) * 255.0, 0, 255)
    res[:,:,1] = np.clip((res[:,:,1] - 10.2) / (191.25 - 10.2) * 255.0, 0, 255)
    res[:,:,2] = np.clip((res[:,:,2] - 10.2) / (201.45 - 10.2) * 255.0, 0, 255)
    return res.astype(np.uint8)

white = apply_white(img)
gray = cv2.cvtColor(white, cv2.COLOR_BGR2GRAY)

# Let's inspect v_clean (vertical dilation with k=7)
k_v7 = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 7))
v_clean = cv2.dilate(white, k_v7)
cv2.imwrite(r"c:\Users\DELL\Documents\CODE\DU_AN\test_v_clean_08.jpg", v_clean)

# Let's see what happens if we find the difference between white and v_clean
diff = cv2.absdiff(white, v_clean)
cv2.imwrite(r"c:\Users\DELL\Documents\CODE\DU_AN\test_diff_08.jpg", diff)
print("Saved test_v_clean_08.jpg and test_diff_08.jpg")

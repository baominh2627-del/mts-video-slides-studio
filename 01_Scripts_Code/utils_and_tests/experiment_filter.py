import cv2
import numpy as np
import os

# Load test frame from scenes_cb/s_05.jpg
img = cv2.imread(r"c:\Users\DELL\Documents\CODE\DU_AN\scenes_cb\s_05.jpg")
h, w, c = img.shape
print(f"Loaded s_05.jpg: shape {img.shape}")

# Let's inspect the white levels transformation first
# In render_white_theme.py:
# colorlevels=rimin=0.04:gimin=0.04:bimin=0.04:rimax=0.79:gimax=0.75:bimax=0.71
# In 0-255:
# r_min = 0.04*255 = 10.2, r_max = 0.79*255 = 201.45
# g_min = 0.04*255 = 10.2, g_max = 0.75*255 = 191.25
# b_min = 0.04*255 = 10.2, b_max = 0.71*255 = 181.05

def apply_colorlevels(bgr):
    # bgr order in opencv: b=0, g=1, r=2
    res = bgr.astype(np.float32)
    # B: [10.2, 181.05] -> [0, 255]
    res[:,:,0] = np.clip((res[:,:,0] - 10.2) / (181.05 - 10.2) * 255.0, 0, 255)
    # G: [10.2, 191.25] -> [0, 255]
    res[:,:,1] = np.clip((res[:,:,1] - 10.2) / (191.25 - 10.2) * 255.0, 0, 255)
    # R: [10.2, 201.45] -> [0, 255]
    res[:,:,2] = np.clip((res[:,:,2] - 10.2) / (201.45 - 10.2) * 255.0, 0, 255)
    return res.astype(np.uint8)

white_img = apply_colorlevels(img)
cv2.imwrite(r"c:\Users\DELL\Documents\CODE\DU_AN\test_exp_white.jpg", white_img)
print("Saved test_exp_white.jpg")

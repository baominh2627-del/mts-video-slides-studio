import cv2
import numpy as np

img26 = cv2.imread(r"c:\Users\DELL\Documents\CODE\DU_AN\inspect_vid\sec_26.jpg")
h, w, c = img26.shape

# White levels
res = img26.astype(np.float32)
res[:,:,0] = np.clip((img26[:,:,0].astype(float) - 10.2) / (181.05 - 10.2) * 255.0, 0, 255)
res[:,:,1] = np.clip((img26[:,:,1].astype(float) - 10.2) / (191.25 - 10.2) * 255.0, 0, 255)
res[:,:,2] = np.clip((img26[:,:,2].astype(float) - 10.2) / (201.45 - 10.2) * 255.0, 0, 255)
white = res.astype(np.uint8)
gray = cv2.cvtColor(white, cv2.COLOR_BGR2GRAY)

# Dilate with k=19
k_v19 = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 19))
dilated = cv2.dilate(white, k_v19)
# Flatten near white to 255
d_gray = cv2.cvtColor(dilated, cv2.COLOR_BGR2GRAY)
dilated[d_gray > 160] = [255, 255, 255]

# Build protection mask
fg_mask = np.zeros((h, w), dtype=bool)

# 1. Outer frame border
fg_mask[18:40, 18:1902] = True
fg_mask[1040:1062, 18:1902] = True
fg_mask[18:1062, 18:40] = True
fg_mask[18:1062, 1880:1902] = True

# 2. MTSEducation Badge
fg_mask[20:105, 20:380] = True

# 3. Subtitle box
fg_mask[800:925, 480:1440] = True

# 4. Red indicator lines and arrows:
is_red = (white[:,:,2].astype(int) - white[:,:,0].astype(int) > 15) & \
         (white[:,:,2].astype(int) - white[:,:,1].astype(int) > 15)
is_red_dilated = cv2.dilate(is_red.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))).astype(bool)
fg_mask[is_red_dilated] = True

# 5. Detect and protect all callout boxes:
white_fill = (gray > 245).astype(np.uint8)
k3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
eroded = cv2.erode(white_fill, k3)
num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(eroded)

for i in range(1, num_labels):
    bx, by, bw, bh, area = stats[i]
    if bx < 15 or by < 15 or bx + bw > w - 15 or by + bh > h - 15:
        continue
    if bw > 800 or bh > 350:
        continue
    if bh >= 12 and bw >= 20 and area >= 300:
        pad = 6
        y1 = max(0, by - pad)
        y2 = min(h, by + bh + pad)
        x1 = max(0, bx - pad)
        x2 = min(w, bx + bw + pad)
        fg_mask[y1:y2, x1:x2] = True

# 6. Stand rod & thermometer (X: 560..660):
fg_mask[30:1040, 560:660] = True

# Compose
out = dilated.copy()
out[fg_mask] = white[fg_mask]

# Outer margins pure white
out[:18, :] = [255, 255, 255]
out[1062:, :] = [255, 255, 255]
out[:, :18] = [255, 255, 255]
out[:, 1902:] = [255, 255, 255]

cv2.imwrite(r"c:\Users\DELL\Documents\CODE\DU_AN\test_clean_26_final.jpg", out)
print("Saved test_clean_26_final.jpg!")

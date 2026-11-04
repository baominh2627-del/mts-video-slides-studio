import cv2
import numpy as np

img = cv2.imread(r"c:\Users\DELL\Documents\CODE\DU_AN\inspect_vid\sec_08.jpg")
h, w, c = img.shape

# White levels
res = img.astype(np.float32)
res[:,:,0] = np.clip((img[:,:,0].astype(float) - 10.2) / (181.05 - 10.2) * 255.0, 0, 255)
res[:,:,1] = np.clip((img[:,:,1].astype(float) - 10.2) / (191.25 - 10.2) * 255.0, 0, 255)
res[:,:,2] = np.clip((img[:,:,2].astype(float) - 10.2) / (201.45 - 10.2) * 255.0, 0, 255)
white = res.astype(np.uint8)
gray = cv2.cvtColor(white, cv2.COLOR_BGR2GRAY)

# Start with a PURE WHITE canvas
canvas = np.full((h, w, 3), 255, dtype=np.uint8)

# Now, copy over each foreground element with pixel-perfect precision!

# 1. Outer Frame double border: [20..38 on all sides]
canvas[18:40, 18:1902] = white[18:40, 18:1902]
canvas[1040:1062, 18:1902] = white[1040:1062, 18:1902]
canvas[18:1062, 18:40] = white[18:1062, 18:40]
canvas[18:1062, 1880:1902] = white[18:1062, 1880:1902]

# 2. MTSEducation Badge at top-left
canvas[20:105, 20:380] = white[20:105, 20:380]

# 3. Question Card [65:290, 65:775]
canvas[65:290, 65:775] = white[65:290, 65:775]

# 4. Stand rod & arm & thermometer:
# Stand rod: [40:1040, 965:990]
canvas[40:1040, 965:990] = white[40:1040, 965:990]
# Stand connector arm: [115:135, 980:1100]
canvas[115:135, 980:1100] = white[115:135, 980:1100]
# Thermometer tube: [60:1040, 1070:1125]
canvas[60:1040, 1070:1125] = white[60:1040, 1070:1125]

# 5. Beaker & Burner & Tongs:
# Beaker: [520:960, 1075:1475]
canvas[520:960, 1075:1475] = white[520:960, 1075:1475]
# Burner & Coals & Legs: [670:1040, 1400:1720]
# But outside the burner bowl and legs, we only want the actual burner pixels!
# Burner pixels are dark (< 180) or colored (spheres):
burner_zone = white[670:1040, 1400:1720]
b_gray = gray[670:1040, 1400:1720]
b_colored = (burner_zone[:,:,2].astype(int) - burner_zone[:,:,0].astype(int) > 20)
b_mask = (b_gray < 220) | b_colored
canvas[670:1040, 1400:1720][b_mask] = burner_zone[b_mask]

# Tongs: [450:800, 1550:1885]
tongs_zone = white[450:800, 1550:1885]
t_gray = gray[450:800, 1550:1885]
t_mask = (t_gray < 160) # Tongs metal bars are very dark
# Dilate tongs mask slightly to keep smooth anti-aliased edge
t_mask = cv2.dilate(t_mask.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))).astype(bool)
canvas[450:800, 1550:1885][t_mask] = tongs_zone[t_mask]

# 6. Red lines & indicators anywhere in the frame:
is_red = (white[:,:,2].astype(int) - white[:,:,0].astype(int) > 18) & \
         (white[:,:,2].astype(int) - white[:,:,1].astype(int) > 18)
is_red_dilated = cv2.dilate(is_red.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))).astype(bool)
canvas[is_red_dilated] = white[is_red_dilated]

# 7. Automatically detect and copy all callout boxes (40°C, 90°C?, 100°C)
white_fill = (gray > 245).astype(np.uint8)
k3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
eroded = cv2.erode(white_fill, k3)
num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(eroded)

for i in range(1, num_labels):
    bx, by, bw, bh, area = stats[i]
    if bx < 15 or by < 15 or bx + bw > w - 15 or by + bh > h - 15:
        continue
    # Ignore Question Card (already copied) and huge boxes
    if bw > 800 or bh > 350:
        continue
    if bh >= 14 and bw >= 22 and area >= 500:
        pad = 6
        y1 = max(0, by - pad)
        y2 = min(h, by + bh + pad)
        x1 = max(0, bx - pad)
        x2 = min(w, bx + bw + pad)
        canvas[y1:y2, x1:x2] = white[y1:y2, x1:x2]

# 8. Subtitle bubble at bottom:
canvas[765:925, 460:1460] = white[765:925, 460:1460]

# 9. Apply CYAN-BLUE WATER TINT inside Beaker:
water_mask = np.zeros((h, w), dtype=np.float32)
for y in range(675, 955):
    for x in range(1085, 1465):
        meniscus_y = 680 + 15 * (1.0 - ((x - 1275) / 185.0)**2) if abs(x - 1275) <= 185 else 999
        bottom_y = 945 + 15 * (1.0 - ((x - 1275) / 185.0)**2) if abs(x - 1275) <= 185 else 0
        if y >= meniscus_y and y <= bottom_y:
            water_mask[y, x] = 1.0
water_mask = cv2.GaussianBlur(water_mask, (13, 13), 0)

for y in range(670, 960):
    depth = np.clip((y - 680) / 260.0, 0.0, 1.0)
    b_col = 245 * (1 - depth) + 225 * depth
    g_col = 195 * (1 - depth) + 140 * depth
    r_col = 50 * (1 - depth) + 10 * depth
    blue_color = np.array([b_col, g_col, r_col], dtype=np.float32)
    
    tint = canvas[y, :, :].astype(np.float32) * (blue_color / 255.0)
    tint = np.clip(tint * 1.1 + blue_color * 0.15, 0, 255)
    
    alpha = water_mask[y, :, None] * 0.65
    canvas[y, :, :] = (canvas[y, :, :].astype(np.float32) * (1.0 - alpha) + tint * alpha).astype(np.uint8)

cv2.imwrite(r"c:\Users\DELL\Documents\CODE\DU_AN\test_composite_08.jpg", canvas)
print("Saved test_composite_08.jpg!")

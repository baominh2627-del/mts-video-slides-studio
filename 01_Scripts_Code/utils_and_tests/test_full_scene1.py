import cv2
import numpy as np

img = cv2.imread(r"c:\Users\DELL\Documents\CODE\DU_AN\inspect_vid\sec_08.jpg")
h, w, c = img.shape

# 1. White balance
def apply_white(bgr):
    res = bgr.astype(np.float32)
    res[:,:,0] = np.clip((bgr[:,:,0].astype(float) - 10.2) / (181.05 - 10.2) * 255.0, 0, 255)
    res[:,:,1] = np.clip((bgr[:,:,1].astype(float) - 10.2) / (191.25 - 10.2) * 255.0, 0, 255)
    res[:,:,2] = np.clip((bgr[:,:,2].astype(float) - 10.2) / (201.45 - 10.2) * 255.0, 0, 255)
    return res.astype(np.uint8)

white = apply_white(img)
gray = cv2.cvtColor(white, cv2.COLOR_BGR2GRAY)

clean = white.copy()

# 2. Complete background wall clearing for left half & empty zones
# Margin & outer border:
# Frame double line is at [20..38, 1882..1900, 20..38, 1042..1060]
# Outside frame: pure white
clean[:20, :] = [255, 255, 255]
clean[1060:, :] = [255, 255, 255]
clean[:, :20] = [255, 255, 255]
clean[:, 1900:] = [255, 255, 255]

# Left half (around card, above card, below card, between card & rod):
clean[38:65, 38:965] = [255, 255, 255] # above card
clean[65:588, 38:65] = [255, 255, 255] # left of card
clean[65:588, 772:965] = [255, 255, 255] # right of card
clean[588:1042, 38:460] = [255, 255, 255] # bottom-left quadrant (left of subtitle)
clean[588:740, 460:965] = [255, 255, 255] # below card, above subtitle

# Between rod and thermometer:
clean[38:118, 985:1080] = [255, 255, 255]
clean[132:1042, 985:1080] = [255, 255, 255]

# Top wall above beaker/burner/labels (Y: 38..290, X: 1125..1882):
clean[38:290, 1125:1882] = [255, 255, 255]

# Now, in the zone containing labels and apparatus (Y: 290..1042, X: 1080..1882):
# Let's apply our stripe detection filter!
zone_gray = gray[290:1042, 1080:1882]
zh, zw = zone_gray.shape

# Periodic stripe filter on this zone:
is_dark = (zone_gray < 195)
stripe_zone_mask = np.zeros((zh, zw), dtype=bool)

for y in range(4, zh - 4):
    cur = is_dark[y, :]
    # Bright above and bright below
    b_above = (zone_gray[y-2, :] > 180) | (zone_gray[y-3, :] > 180)
    b_below = (zone_gray[y+2, :] > 180) | (zone_gray[y+3, :] > 180)
    
    # Dark neighbor 4..7 px away
    d_above = is_dark[y-4, :] | is_dark[y-5, :] | is_dark[y-6, :] | is_dark[y-7, :] if y >= 7 else False
    d_below = is_dark[y+4, :] | is_dark[y+5, :] | is_dark[y+6, :] | is_dark[y+7, :] if y < zh - 7 else False
    
    # Periodic stripe
    stripe_zone_mask[y, :] = cur & b_above & b_below & (d_above | d_below)

# Protect the burner coals, glowing spheres, tongs, beaker water from stripe removal
# Burner & spheres zone: [670-290 : 1040-290, 1400-1080 : 1750-1080]
# Sphere colors have strong red/orange saturation (R > G + 30):
zone_bgr = clean[290:1042, 1080:1882]
is_colored = (zone_bgr[:,:,2].astype(int) - zone_bgr[:,:,0].astype(int) > 25) # high red
stripe_zone_mask[is_colored] = False

# Protect water inside beaker (X: 1085..1465, Y: 680..950 in full frame)
# in zone coordinates: Y: 680-290..950-290, X: 1085-1080..1465-1080
beaker_y1 = 670 - 290
beaker_y2 = 960 - 290
beaker_x1 = 1085 - 1080
beaker_x2 = 1465 - 1080
stripe_zone_mask[beaker_y1:beaker_y2, beaker_x1:beaker_x2] = False

# Protect subtitle box in full frame: [740-290:960-290, 460-1080:1480-1080]
sub_x1 = max(0, 460 - 1080)
sub_x2 = min(zw, 1480 - 1080)
sub_y1 = 740 - 290
sub_y2 = 960 - 290
stripe_zone_mask[sub_y1:sub_y2, sub_x1:sub_x2] = False

# Apply stripe removal to zone:
zone_bgr[stripe_zone_mask] = [255, 255, 255]
clean[290:1042, 1080:1882] = zone_bgr

# 3. Apply the Cyan-Blue Water Tint to Beaker
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
    
    tint = clean[y, :, :].astype(np.float32) * (blue_color / 255.0)
    tint = np.clip(tint * 1.1 + blue_color * 0.15, 0, 255)
    
    alpha = water_mask[y, :, None] * 0.65
    clean[y, :, :] = (clean[y, :, :].astype(np.float32) * (1.0 - alpha) + tint * alpha).astype(np.uint8)

cv2.imwrite(r"c:\Users\DELL\Documents\CODE\DU_AN\test_full_clean_08.jpg", clean)
print("Saved test_full_clean_08.jpg!")

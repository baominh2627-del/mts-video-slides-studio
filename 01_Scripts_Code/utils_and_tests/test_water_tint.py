import cv2
import numpy as np

img = cv2.imread(r"c:\Users\DELL\Documents\CODE\DU_AN\inspect_vid\sec_08.jpg")
h, w, c = img.shape

# Apply colorlevels to make parchment pure white first
def apply_white(bgr):
    res = bgr.astype(np.float32)
    res[:,:,0] = np.clip((res[:,:,0] - 10.2) / (181.05 - 10.2) * 255.0, 0, 255)
    res[:,:,1] = np.clip((res[:,:,1] - 10.2) / (191.25 - 10.2) * 255.0, 0, 255)
    res[:,:,2] = np.clip((res[:,:,2] - 201.45) / (201.45 - 10.2) * 255.0, 0, 255) # wait, rimax is 201.45!
    # Let's fix formula:
    # (val - min) / (max - min) * 255
    res[:,:,0] = np.clip((bgr[:,:,0].astype(float) - 10.2) / (181.05 - 10.2) * 255.0, 0, 255)
    res[:,:,1] = np.clip((bgr[:,:,1].astype(float) - 10.2) / (191.25 - 10.2) * 255.0, 0, 255)
    res[:,:,2] = np.clip((bgr[:,:,2].astype(float) - 10.2) / (201.45 - 10.2) * 255.0, 0, 255)
    return res.astype(np.uint8)

white = apply_white(img)

# Water region in sec_08.jpg:
# Beaker outline:
# Top meniscus: around Y=680, curving down slightly in middle.
# Bottom: around Y=950.
# Left: X=1085
# Right: X=1465

# Let's test a mask for the water
water_mask = np.zeros((h, w), dtype=np.float32)

# Create an elliptical cylinder mask for water
for y in range(670, 960):
    for x in range(1085, 1465):
        # Meniscus curve at top: ellipse center (1275, 685), rx=185, ry=25
        # If above meniscus curve, 0
        meniscus_y = 680 + 15 * (1.0 - ((x - 1275) / 185.0)**2) if abs(x - 1275) <= 185 else 999
        bottom_y = 945 + 15 * (1.0 - ((x - 1275) / 185.0)**2) if abs(x - 1275) <= 185 else 0
        if y >= meniscus_y and y <= bottom_y:
            water_mask[y, x] = 1.0

# Blur mask edges for smooth glass blending
water_mask = cv2.GaussianBlur(water_mask, (15, 15), 0)

# Tint water blue (xanh lam: beautiful cyan-blue like #00AEEF / RGB(0, 174, 239) -> BGR(239, 174, 0))
# Let's test a gradient blue (lighter at top, slightly deeper at bottom)
water_tinted = white.copy().astype(np.float32)
for y in range(h):
    # depth factor from 0.0 (top) to 1.0 (bottom)
    depth = np.clip((y - 680) / 260.0, 0.0, 1.0)
    # top: BGR (245, 190, 40), bottom: BGR (230, 140, 10)
    b_col = 245 * (1 - depth) + 225 * depth
    g_col = 195 * (1 - depth) + 140 * depth
    r_col = 50 * (1 - depth) + 10 * depth
    blue_color = np.array([b_col, g_col, r_col], dtype=np.float32)
    
    # Where pixel is white/bright, blend strongly; where pixel is dark (refraction line, sphere), multiply
    # Multiply blend gives natural transparent liquid look!
    lum = white[y, :, :].astype(np.float32) / 255.0 # 0 to 1
    # Tint formula: orig * (blue_color / 255)
    tint = white[y, :, :].astype(np.float32) * (blue_color / 255.0)
    # Also add a slight luminous glow for clear water
    tint = np.clip(tint * 1.1 + blue_color * 0.15, 0, 255)
    
    alpha = water_mask[y, :, None] * 0.65
    water_tinted[y, :, :] = white[y, :, :] * (1.0 - alpha) + tint * alpha

cv2.imwrite(r"c:\Users\DELL\Documents\CODE\DU_AN\test_water_tint_08.jpg", water_tinted.astype(np.uint8))
print("Saved test_water_tint_08.jpg")

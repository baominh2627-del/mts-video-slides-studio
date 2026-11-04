import cv2
import numpy as np

def process_frame(img, timestamp_sec):
    h, w, c = img.shape
    
    # Scene 2 (Math graph slide from 26.83s to 60.33s):
    # Already clean, just needs pure white levels!
    # Let's apply white levels to all frames first
    res = img.astype(np.float32)
    res[:,:,0] = np.clip((img[:,:,0].astype(float) - 10.2) / (181.05 - 10.2) * 255.0, 0, 255)
    res[:,:,1] = np.clip((img[:,:,1].astype(float) - 10.2) / (191.25 - 10.2) * 255.0, 0, 255)
    res[:,:,2] = np.clip((img[:,:,2].astype(float) - 10.2) / (201.45 - 10.2) * 255.0, 0, 255)
    white = res.astype(np.uint8)
    
    if 26.83 <= timestamp_sec < 60.33:
        # Scene 2: math diagram slide has no stripes
        return white

    gray = cv2.cvtColor(white, cv2.COLOR_BGR2GRAY)
    
    # Base clean canvas: start from white
    # Compute v_clean: vertical max filter (erases all horizontal stripes of height <= 4)
    k_v7 = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 7))
    v_clean = cv2.dilate(white, k_v7)
    
    # Now, build a FOREGROUND PROTECTION MASK where we MUST preserve original pixels:
    fg_mask = np.zeros((h, w), dtype=bool)
    
    # 1. Outer Frame Border (20..38 on all sides)
    fg_mask[18:40, 18:1902] = True
    fg_mask[1040:1062, 18:1902] = True
    fg_mask[18:1062, 18:40] = True
    fg_mask[18:1062, 1880:1902] = True
    
    # 2. MTSEducation Badge at top-left
    fg_mask[20:105, 20:380] = True
    
    # 3. Subtitle box at bottom
    fg_mask[740:980, 250:1650] = True
    
    # 4. Colored pixels (red lines, indicators, glowing burner spheres)
    # Saturation / color difference:
    is_colored = (np.abs(white[:,:,2].astype(int) - white[:,:,0].astype(int)) > 20) | \
                 (np.abs(white[:,:,1].astype(int) - white[:,:,0].astype(int)) > 20)
    # Dilate colored pixels slightly to keep anti-aliased edges
    k_col = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    is_colored_dilated = cv2.dilate(is_colored.astype(np.uint8), k_col).astype(bool)
    fg_mask[is_colored_dilated] = True
    
    # 5. Automatically detect all callout boxes and Question Card
    # White fill interior:
    white_fill = (gray > 245).astype(np.uint8)
    k3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    eroded = cv2.erode(white_fill, k3)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(eroded)
    
    for i in range(1, num_labels):
        bx, by, bw, bh, area = stats[i]
        # Ignore outer margins
        if bx < 15 or by < 15 or bx + bw > w - 15 or by + bh > h - 15:
            continue
        if bh >= 14 and bw >= 22 and area >= 500:
            # Ignore huge boxes that span the whole screen (like outer border)
            if bw > 800 or bh > 350:
                continue
            # Protect box and its borders
            pad_y = 6
            pad_x = 6
            y1 = max(0, by - pad_y)
            y2 = min(h, by + bh + pad_y)
            x1 = max(0, bx - pad_x)
            x2 = min(w, bx + bw + pad_x)
            fg_mask[y1:y2, x1:x2] = True
            
    # 6. Scene-specific apparatus protection:
    # Wide shot (0 to 12.5s and 60.33 to 66.10s):
    is_wide_shot = (timestamp_sec < 12.5) or (timestamp_sec >= 60.33)
    if is_wide_shot:
        # Stand rod:
        fg_mask[40:1040, 965:990] = True
        # Stand arm to thermometer:
        fg_mask[115:135, 975:1100] = True
        # Thermometer tube:
        fg_mask[60:1040, 1070:1125] = True
        # Glass Beaker:
        fg_mask[520:1040, 1075:1475] = True
        # Burner & Coals & Legs:
        fg_mask[670:1040, 1400:1720] = True
        # Tongs entering from right:
        fg_mask[450:800, 1550:1885] = True
    else:
        # Zoomed shot (12.5s to 26.83s):
        # Stand rod and thermometer:
        fg_mask[30:1040, 560:660] = True
        # Beaker rim at bottom:
        fg_mask[920:1040, 500:1500] = True
        
    # 7. Compose final result:
    # Where fg_mask is True: keep original crisp white pixels!
    # Where fg_mask is False: use v_clean (which has 0 stripes, pure white wall)!
    out = v_clean.copy()
    out[fg_mask] = white[fg_mask]
    
    # Make sure outer margins (outside outer frame) are 100% pure white
    out[:18, :] = [255, 255, 255]
    out[1062:, :] = [255, 255, 255]
    out[:, :18] = [255, 255, 255]
    out[:, 1902:] = [255, 255, 255]
    
    # 8. Apply Cyan-Blue Water Tint:
    if is_wide_shot:
        # Beaker water region in wide shot:
        # Water meniscus at ~680 to bottom ~950, X: 1085..1465
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
            
            tint = out[y, :, :].astype(np.float32) * (blue_color / 255.0)
            tint = np.clip(tint * 1.1 + blue_color * 0.15, 0, 255)
            
            alpha = water_mask[y, :, None] * 0.65
            out[y, :, :] = (out[y, :, :].astype(np.float32) * (1.0 - alpha) + tint * alpha).astype(np.uint8)
            
    return out

# Test on 4 key frames
for sec, val in [('08', 8.0), ('16', 16.0), ('26', 26.0), ('62', 62.0)]:
    p = f"c:\\Users\\DELL\\Documents\\CODE\\DU_AN\\inspect_vid\\sec_{sec}.jpg"
    img = cv2.imread(p)
    res = process_frame(img, val)
    cv2.imwrite(f"c:\\Users\\DELL\\Documents\\CODE\\DU_AN\\test_master_{sec}.jpg", res)
    print(f"Processed master {sec}")

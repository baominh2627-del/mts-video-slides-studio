import cv2
import numpy as np

img26 = cv2.imread(r"c:\Users\DELL\Documents\CODE\DU_AN\inspect_vid\sec_26.jpg")
img08 = cv2.imread(r"c:\Users\DELL\Documents\CODE\DU_AN\inspect_vid\sec_08.jpg")

def test_pipeline(img, timestamp_sec, name):
    h, w, c = img.shape
    
    # White levels mapping
    res = img.astype(np.float32)
    res[:,:,0] = np.clip((img[:,:,0].astype(float) - 10.2) / (181.05 - 10.2) * 255.0, 0, 255)
    res[:,:,1] = np.clip((img[:,:,1].astype(float) - 10.2) / (191.25 - 10.2) * 255.0, 0, 255)
    res[:,:,2] = np.clip((img[:,:,2].astype(float) - 10.2) / (201.45 - 10.2) * 255.0, 0, 255)
    white = res.astype(np.uint8)
    
    gray = cv2.cvtColor(white, cv2.COLOR_BGR2GRAY)
    
    # 1. v_clean: vertical max with k=11
    k_v11 = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 11))
    v_clean = cv2.dilate(white, k_v11)
    
    # Flatten near-white to pure 255
    v_gray = cv2.cvtColor(v_clean, cv2.COLOR_BGR2GRAY)
    v_clean[v_gray > 175] = [255, 255, 255]
    
    # 2. Build foreground protection mask
    fg_mask = np.zeros((h, w), dtype=bool)
    
    # Outer Frame Border
    fg_mask[18:40, 18:1902] = True
    fg_mask[1040:1062, 18:1902] = True
    fg_mask[18:1062, 18:40] = True
    fg_mask[18:1062, 1880:1902] = True
    
    # MTSEducation Badge at top-left
    fg_mask[20:105, 20:380] = True
    
    # Subtitle box at bottom (exact range)
    fg_mask[770:930, 460:1460] = True
    
    # Colored pixels (red lines, indicators, glowing spheres)
    # Saturation / color difference: R > B + 15 or G > B + 15
    is_colored = (white[:,:,2].astype(int) - white[:,:,0].astype(int) > 15) | \
                 (white[:,:,1].astype(int) - white[:,:,0].astype(int) > 15)
    k_col = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    is_colored_dilated = cv2.dilate(is_colored.astype(np.uint8), k_col).astype(bool)
    fg_mask[is_colored_dilated] = True
    
    # Automatically detect all callout boxes and Question Card
    white_fill = (gray > 245).astype(np.uint8)
    k3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    eroded = cv2.erode(white_fill, k3)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(eroded)
    
    for i in range(1, num_labels):
        bx, by, bw, bh, area = stats[i]
        if bx < 15 or by < 15 or bx + bw > w - 15 or by + bh > h - 15:
            continue
        if bh >= 14 and bw >= 22 and area >= 500:
            if bw > 850 or bh > 350:
                continue
            pad = 6
            y1 = max(0, by - pad)
            y2 = min(h, by + bh + pad)
            x1 = max(0, bx - pad)
            x2 = min(w, bx + bw + pad)
            fg_mask[y1:y2, x1:x2] = True
            
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
        # Tongs:
        fg_mask[450:800, 1550:1885] = True
    else:
        # Zoomed shot:
        # Stand rod and thermometer:
        fg_mask[30:1040, 560:660] = True
        # Red level indicator line across thermometer:
        fg_mask[80:110, 560:1450] = True
        # Beaker rim at bottom:
        fg_mask[920:1040, 500:1500] = True
        
    out = v_clean.copy()
    out[fg_mask] = white[fg_mask]
    
    # Margins pure white
    out[:18, :] = [255, 255, 255]
    out[1062:, :] = [255, 255, 255]
    out[:, :18] = [255, 255, 255]
    out[:, 1902:] = [255, 255, 255]
    
    # Water tint for wide shot:
    if is_wide_shot:
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
            
    cv2.imwrite(f"c:\\Users\\DELL\\Documents\\CODE\\DU_AN\\test_v2_{name}.jpg", out)
    print(f"Saved test_v2_{name}.jpg")

test_pipeline(img08, 8.0, "08")
test_pipeline(img26, 26.0, "26")

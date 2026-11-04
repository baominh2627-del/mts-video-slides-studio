import cv2
import numpy as np

def render_perfect_frame(img, t_sec):
    h, w, c = img.shape
    
    # 1. White point remap
    res = img.astype(np.float32)
    res[:,:,0] = np.clip((img[:,:,0].astype(float) - 10.2) / (181.05 - 10.2) * 255.0, 0, 255)
    res[:,:,1] = np.clip((img[:,:,1].astype(float) - 10.2) / (191.25 - 10.2) * 255.0, 0, 255)
    res[:,:,2] = np.clip((img[:,:,2].astype(float) - 10.2) / (201.45 - 10.2) * 255.0, 0, 255)
    white = res.astype(np.uint8)
    
    # Scene 2 (26.83s to 60.33s): Math diagram has no stripes, perfect clean white
    if 26.83 <= t_sec < 60.33:
        return white

    gray = cv2.cvtColor(white, cv2.COLOR_BGR2GRAY)
    
    # 2. Base clean background via vertical dilation k=21
    k_v21 = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 21))
    v_clean = cv2.dilate(white, k_v21)
    v_gray = cv2.cvtColor(v_clean, cv2.COLOR_BGR2GRAY)
    v_clean[v_gray > 160] = [255, 255, 255]
    
    # 3. Build foreground protection mask
    fg_mask = np.zeros((h, w), dtype=bool)
    
    # Outer frame border (20..38)
    fg_mask[18:40, 18:1902] = True
    fg_mask[1040:1062, 18:1902] = True
    fg_mask[18:1062, 18:40] = True
    fg_mask[18:1062, 1880:1902] = True
    
    # Top-left badge
    fg_mask[20:105, 20:380] = True
    
    is_scene1_wide = (t_sec < 12.5)
    is_scene3_wide = (t_sec >= 60.33)
    
    # Subtitle bubble:
    if is_scene1_wide or is_scene3_wide:
        fg_mask[765:920, 480:1440] = True
    else:
        fg_mask[825:920, 480:1440] = True
    
    # Red features: lines, arrows, red numbers, glowing spheres
    is_red = (white[:,:,2].astype(int) - white[:,:,0].astype(int) > 30) & \
             (white[:,:,2].astype(int) - white[:,:,1].astype(int) > 18)
    k_col = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    is_red_dilated = cv2.dilate(is_red.astype(np.uint8), k_col).astype(bool)
    fg_mask[is_red_dilated] = True
    
    # Automatically detect all callout boxes and Question Card
    white_fill = (gray > 245).astype(np.uint8)
    k3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    eroded = cv2.erode(white_fill, k3)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(eroded)
    
    for i in range(1, num_labels):
        bx, by, bw, bh, area = stats[i]
        if bx < 15 or by < 15 or bx + bw > w - 15 or by + bh > h - 15:
            continue
        if bw > 850 or bh > 350:
            continue
        # Callout boxes have bh >= 12 and bw >= 20 and area >= 300
        if bh >= 12 and bw >= 20 and area >= 300:
            pad = 6
            y1 = max(0, by - pad)
            y2 = min(h, by + bh + pad)
            x1 = max(0, bx - pad)
            x2 = min(w, bx + bw + pad)
            fg_mask[y1:y2, x1:x2] = True
            
    if is_scene1_wide:
        # Question card:
        fg_mask[60:295, 60:780] = True
        # Stand rod:
        fg_mask[40:1040, 965:995] = True
        # Connector arm:
        fg_mask[115:135, 975:1100] = True
        # Thermometer:
        fg_mask[60:1040, 1070:1125] = True
        # Glass Beaker:
        fg_mask[520:1040, 1070:1465] = True
        # Burner & Coals & Legs:
        fg_mask[670:1040, 1400:1720] = True
        # Tongs:
        fg_mask[450:800, 1550:1885] = True
    elif is_scene3_wide:
        # Scene 3: Question card "Cần 21 quả, không phải 4"
        fg_mask[60:295, 60:420] = True
        # Stand rod (at X=930):
        fg_mask[40:1040, 915:945] = True
        # Connector arm:
        fg_mask[115:135, 925:1050] = True
        # Thermometer:
        fg_mask[60:1040, 1020:1075] = True
        # Glass Beaker:
        fg_mask[520:1040, 1020:1415] = True
        # Burner & Coals & Legs:
        fg_mask[670:1040, 1350:1670] = True
        # Tongs:
        fg_mask[450:800, 1500:1885] = True
    else:
        # Zoomed shot (12.5s to 26.83s):
        # Stand rod and thermometer:
        fg_mask[30:1040, 560:660] = True
        # Beaker rim at bottom:
        fg_mask[935:1040, 500:1500] = True
        
    # 4. Compose output
    out = v_clean.copy()
    out[fg_mask] = white[fg_mask]
    
    # Outer margins pure white
    out[:18, :] = [255, 255, 255]
    out[1062:, :] = [255, 255, 255]
    out[:, :18] = [255, 255, 255]
    out[:, 1902:] = [255, 255, 255]
    
    # 5. Apply Cyan-Blue Water Tint inside Beaker:
    if is_scene1_wide:
        cx = 1260
        rx = 185
        meniscus_base = 680
        bottom_base = 945
        apply_beaker_water(out, cx, rx, meniscus_base, bottom_base)
    elif is_scene3_wide:
        cx = 1205
        rx = 185
        meniscus_base = 680
        bottom_base = 945
        apply_beaker_water(out, cx, rx, meniscus_base, bottom_base)
    elif 12.5 <= t_sec < 26.83:
        for y in range(940, 1040):
            depth = np.clip((y - 940) / 100.0, 0.0, 1.0)
            blue_col = np.array([240, 180, 20], dtype=np.float32)
            alpha = depth * 0.45
            out[y, 560:1450, :] = (out[y, 560:1450, :].astype(np.float32) * (1.0 - alpha) + \
                                   out[y, 560:1450, :].astype(np.float32) * (blue_col / 255.0) * alpha).astype(np.uint8)
                                   
    return out

def apply_beaker_water(frame, cx, rx, meniscus_base, bottom_base):
    h, w, c = frame.shape
    water_mask = np.zeros((h, w), dtype=np.float32)
    x1 = int(cx - rx)
    x2 = int(cx + rx)
    y1 = int(meniscus_base - 10)
    y2 = int(bottom_base + 20)
    
    for y in range(y1, y2):
        for x in range(x1, x2):
            dx = (x - cx) / float(rx)
            if abs(dx) <= 1.0:
                men_y = meniscus_base + 15 * (1.0 - dx**2)
                bot_y = bottom_base + 15 * (1.0 - dx**2)
                if y >= men_y and y <= bot_y:
                    water_mask[y, x] = 1.0
                    
    water_mask = cv2.GaussianBlur(water_mask, (13, 13), 0)
    
    for y in range(y1, y2):
        depth = np.clip((y - meniscus_base) / float(bottom_base - meniscus_base), 0.0, 1.0)
        b_col = 245 * (1 - depth) + 225 * depth
        g_col = 195 * (1 - depth) + 140 * depth
        r_col = 45 * (1 - depth) + 10 * depth
        blue_color = np.array([b_col, g_col, r_col], dtype=np.float32)
        
        orig_row = frame[y, :, :].astype(np.float32)
        tint = orig_row * (blue_color / 255.0)
        tint = np.clip(tint * 1.1 + blue_color * 0.15, 0, 255)
        
        alpha = water_mask[y, :, None] * 0.65
        frame[y, :, :] = (orig_row * (1.0 - alpha) + tint * alpha).astype(np.uint8)

# Run on sample frames
for sec, val in [('08', 8.0), ('16', 16.0), ('26', 26.0), ('62', 62.0), ('65', 65.0)]:
    p = f"c:\\Users\\DELL\\Documents\\CODE\\DU_AN\\inspect_vid\\sec_{sec}.jpg"
    img = cv2.imread(p)
    res = render_perfect_frame(img, val)
    cv2.imwrite(f"c:\\Users\\DELL\\Documents\\CODE\\DU_AN\\v3_{sec}.jpg", res)
    print(f"Rendered v3_{sec}.jpg")

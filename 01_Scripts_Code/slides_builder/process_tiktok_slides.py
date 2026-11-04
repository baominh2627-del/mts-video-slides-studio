import cv2
import numpy as np
import os
import shutil
from PIL import Image, ImageDraw, ImageFont

raw_dir = r'C:\Users\DELL\Documents\CODE\DU_AN\tiktok_slides_raw'
proc_dir = r'C:\Users\DELL\Documents\CODE\DU_AN\tiktok_slides_processed'
downloads_dir = r'C:\Users\DELL\Documents\Downloads\TIKTOK_SLIDES_MTSEducation'

os.makedirs(proc_dir, exist_ok=True)
os.makedirs(downloads_dir, exist_ok=True)

# Fonts
font_vna = ImageFont.truetype(r'C:\Windows\Fonts\timesbd.ttf', 21)
font_box_mts = ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf', 42)
font_footer = ImageFont.truetype(r'C:\Windows\Fonts\timesbi.ttf', 22)

# Specific slide header divider y-thresholds (everything y < y_top is cleared)
HEADER_CLEAR_Y = {
    2: 52,
    3: 67,
    4: 44,
    5: 65,
    6: 96,
    7: 52,
    8: 53
}

# Exact footer divider line y-coordinates (measured from LaTeX typesetting)
FOOTER_DIV_Y = {
    2: 1377,
    3: 1394,
    4: 1371,
    5: 1392,
    6: 1423,
    7: 1379,
    8: 1380
}

# Copy Slide 01 directly (clean cover slide)
shutil.copy2(os.path.join(raw_dir, 'slide_01.jpg'), os.path.join(proc_dir, 'slide_01.jpg'))
shutil.copy2(os.path.join(raw_dir, 'slide_01.jpg'), os.path.join(downloads_dir, 'slide_01.jpg'))
print("Slide 01: Copied successfully (cover slide)")

total_replaced = 0

for s_idx in range(2, 9):
    fname = f'slide_{s_idx:02d}.jpg'
    img_path = os.path.join(raw_dir, fname)
    img = cv2.imread(img_path)
    h, w = img.shape[:2]

    # 1. Clean diagonal neutral-gray watermarks
    b, g, r = img[:, :, 0].astype(int), img[:, :, 1].astype(int), img[:, :, 2].astype(int)
    is_light = np.minimum(np.minimum(b, g), r) > 160
    is_neutral = (np.maximum(np.maximum(b, g), r) - np.minimum(np.minimum(b, g), r)) < 25
    is_wm = is_light & is_neutral

    # Protect slide 07 physical apparatus photo
    if s_idx == 7:
        is_wm[1108:1224, 724:920] = False

    img[is_wm] = [255, 255, 255]

    # Clean right edge border artifact (specifically on slide 08)
    img[:, 1065:] = [255, 255, 255]

    # 2. Header cleaning
    top_clear_y = HEADER_CLEAR_Y.get(s_idx, 52)
    img[:top_clear_y, :] = [255, 255, 255]

    # Slide 02 specific: clear 'M' logo inside square box
    if s_idx == 2:
        img[56:164, 74:194] = [255, 255, 255]

    # 3. Footer cleaning & crisp divider reconstruction
    bot_div_y = FOOTER_DIV_Y[s_idx]
    # Clear branding below divider line, preserving page number on right (x >= 920)
    img[bot_div_y + 1:, :920] = [255, 255, 255]
    # Draw pristine thin divider line above footer text & page number
    cv2.line(img, (65, bot_div_y), (1015, bot_div_y), (190, 190, 190), 1)

    # 4. Find all [VNA] locations dynamically
    # Look for blue 'Câu' text in x: 55..105, y: 60..1350
    is_blue = (b > 80) & (r < 60) & ((b - r) > 40)
    is_blue[:, :55] = False
    is_blue[:, 105:] = False
    is_blue[:60, :] = False
    is_blue[1350:, :] = False

    ys, xs = np.where(is_blue)
    vna_list = []
    if len(ys) > 0:
        unique_ys = np.sort(np.unique(ys))
        groups = []
        cur_group = [unique_ys[0]]
        for y in unique_ys[1:]:
            if y - cur_group[-1] <= 10:
                cur_group.append(y)
            else:
                groups.append(cur_group)
                cur_group = [y]
        groups.append(cur_group)

        for g in groups:
            if len(g) >= 8:
                c_ymin = max(0, min(g) - 4)
                c_ymax = min(h, max(g) + 4)
                # Look for red [VNA] in x: 120..240
                r_crop = r[c_ymin:c_ymax, 120:240]
                b_crop = b[c_ymin:c_ymax, 120:240]
                is_red = (r_crop > 90) & (b_crop < 80) & ((r_crop - b_crop) > 30)
                rys, rxs = np.where(is_red)
                if len(rys) > 15:
                    red_xmin = 120 + int(np.min(rxs))
                    red_xmax = 120 + int(np.max(rxs))
                    red_ymin = c_ymin + int(np.min(rys))
                    red_ymax = c_ymin + int(np.max(rys))
                    vna_list.append((red_xmin, red_ymin, red_xmax, red_ymax))

    # Erase old [VNA] bounding boxes
    for (xmin, ymin, xmax, ymax) in vna_list:
        img[ymin - 3:ymax + 4, xmin - 4:xmax + 5] = [255, 255, 255]

    # Convert to PIL for drawing replacement text
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)

    # Slide 02 header box: Draw 'MTS'
    if s_idx == 2:
        draw.text((80, 84), "MTS", fill=(30, 95, 205), font=font_box_mts)

    # Footer: Draw 'MTSEducation'
    draw.text((65, bot_div_y + 5), "MTSEducation", fill=(30, 60, 180), font=font_footer)

    # Draw [MTS] for each detected question
    for (xmin, ymin, xmax, ymax) in vna_list:
        draw.text((xmin - 1, ymin - 2), "[MTS]", fill=(158, 36, 38), font=font_vna)

    # Save output
    out_proc = os.path.join(proc_dir, fname)
    out_down = os.path.join(downloads_dir, fname)
    pil_img.save(out_proc, quality=98)
    pil_img.save(out_down, quality=98)

    print(f"{fname}: Replaced {len(vna_list)} occurrences of [VNA] with [MTS], cleaned header & footer (div_y={bot_div_y})")
    total_replaced += len(vna_list)

print(f"\nProcessing Complete! Total [MTS] replacements across all slides: {total_replaced}")

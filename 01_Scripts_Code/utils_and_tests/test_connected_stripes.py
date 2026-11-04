import cv2
import numpy as np

def test_stripe_remover(img_path, out_name):
    img = cv2.imread(img_path)
    h, w, c = img.shape
    
    # 1. White levels mapping
    res = img.astype(np.float32)
    res[:,:,0] = np.clip((bgr[:,:,0].astype(float) - 10.2) / (181.05 - 10.2) * 255.0, 0, 255) if False else None
    
def clean_image(img):
    h, w, c = img.shape
    # White balance
    res = img.astype(np.float32)
    res[:,:,0] = np.clip((img[:,:,0].astype(float) - 10.2) / (181.05 - 10.2) * 255.0, 0, 255)
    res[:,:,1] = np.clip((img[:,:,1].astype(float) - 10.2) / (191.25 - 10.2) * 255.0, 0, 255)
    res[:,:,2] = np.clip((img[:,:,2].astype(float) - 10.2) / (201.45 - 10.2) * 255.0, 0, 255)
    white = res.astype(np.uint8)
    
    gray = cv2.cvtColor(white, cv2.COLOR_BGR2GRAY)
    
    # Binary threshold of dark pixels (stripes, text, borders)
    # Background paper is 255 (pure white). Stripes are < 210.
    dark_mask = (gray < 215).astype(np.uint8)
    
    # Outer frame margin: double border at [20..38, 1882..1900, 20..38, 1042..1060]
    # We clear outer margins to pure white
    dark_mask[:20, :] = 0
    dark_mask[1060:, :] = 0
    dark_mask[:, :20] = 0
    dark_mask[:, 1900:] = 0
    
    # Let's find connected components of dark pixels
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(dark_mask, connectivity=8)
    
    stripe_mask = np.zeros((h, w), dtype=bool)
    
    for i in range(1, num_labels):
        comp_x, comp_y, comp_w, comp_h, comp_area = stats[i]
        
        # Characteristic of a horizontal stripe:
        # Height is small (<= 4 pixels)
        # Width is substantial (>= 15 pixels)
        # Aspect ratio comp_w / comp_h >= 4
        # OR height <= 3 and area < 4000
        if comp_h <= 4 and comp_w >= 12 and (comp_w / max(1, comp_h)) >= 3.0:
            stripe_mask[labels == i] = True
        elif comp_h <= 3:
            # Any tiny horizontal specks/dips of height <= 3
            stripe_mask[labels == i] = True
            
    # Also, dilate stripe_mask vertically by 1px to catch anti-aliased soft edges of the stripes
    k_v3 = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 3))
    stripe_mask_dilated = cv2.dilate(stripe_mask.astype(np.uint8), k_v3).astype(bool)
    
    # But do NOT touch pixels that are part of thick foreground (height > 5)
    # Thick foreground mask:
    fg_thick = np.zeros((h, w), dtype=bool)
    for i in range(1, num_labels):
        comp_x, comp_y, comp_w, comp_h, comp_area = stats[i]
        if comp_h > 4 and comp_area > 30:
            fg_thick[labels == i] = True
            
    k_circle = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    fg_thick_protected = cv2.dilate(fg_thick.astype(np.uint8), k_circle).astype(bool)
    
    # Also protect colored pixels (high red or blue)
    is_colored = (np.abs(white[:,:,2].astype(int) - white[:,:,0].astype(int)) > 20) | \
                 (np.abs(white[:,:,1].astype(int) - white[:,:,0].astype(int)) > 20)
    fg_thick_protected[is_colored] = True
    
    final_stripe_mask = stripe_mask_dilated & (~fg_thick_protected)
    
    # Replace detected stripes with pure white 255
    result = white.copy()
    result[final_stripe_mask] = [255, 255, 255]
    
    # Outer margins pure white
    result[:20, :] = [255, 255, 255]
    result[1060:, :] = [255, 255, 255]
    result[:, :20] = [255, 255, 255]
    result[:, 1900:] = [255, 255, 255]
    
    return result

for sec in ['08', '16', '26', '62']:
    p = f"c:\\Users\\DELL\\Documents\\CODE\\DU_AN\\inspect_vid\\sec_{sec}.jpg"
    img = cv2.imread(p)
    res = clean_image(img)
    cv2.imwrite(f"c:\\Users\\DELL\\Documents\\CODE\DU_AN\\test_cc_clean_{sec}.jpg", res)
    print(f"Saved test_cc_clean_{sec}.jpg")

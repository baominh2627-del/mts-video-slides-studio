import cv2
import numpy as np

# Load sec_08, sec_16, sec_26, sec_62
def test_frame(frame_path, name):
    img = cv2.imread(frame_path)
    h, w, c = img.shape
    
    # 1. White levels mapping
    res = img.astype(np.float32)
    res[:,:,0] = np.clip((res[:,:,0] - 10.2) / (181.05 - 10.2) * 255.0, 0, 255)
    res[:,:,1] = np.clip((res[:,:,1] - 10.2) / (191.25 - 10.2) * 255.0, 0, 255)
    res[:,:,2] = np.clip((res[:,:,2] - 10.2) / (201.45 - 10.2) * 255.0, 0, 255)
    white = res.astype(np.uint8)
    
    gray = cv2.cvtColor(white, cv2.COLOR_BGR2GRAY)
    
    # 2. Let's find all foreground elements:
    # Notice: In the background, the stripes are thin horizontal lines of height 1-3px.
    # What if we apply a horizontal morphological closing with length 25?
    # Letters, spheres, boxes, apparatus have high 2D complexity!
    # Let's look at vertical gradient vs horizontal gradient:
    # Stripes have |dy| >> |dx|.
    
    # But even better: Let's look at connected components of WHITE!
    # Any box or card has an interior of solid white with area > 1000 pixels and aspect ratio < 10!
    # Let's threshold white interior:
    white_interior = (gray >= 250).astype(np.uint8)
    
    # Find connected components of pure white
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(white_interior)
    
    # Create foreground mask
    fg_mask = np.zeros((h, w), dtype=np.uint8)
    
    # Foreground boxes: any white component that has height > 15 and width > 15
    for i in range(1, num_labels):
        x, y, comp_w, comp_h, area = stats[i]
        # Ignore components that touch the outer boundary (the outside margin)
        if x <= 5 or y <= 5 or (x + comp_w >= w - 5) or (y + comp_h >= h - 5):
            continue
        # If height > 15 and width > 20: that's an interior of a box or card!
        if comp_h > 15 and comp_w > 20 and area > 400:
            # Expand by 10 pixels to cover the border and text!
            y1 = max(0, y - 8)
            y2 = min(h, y + comp_h + 8)
            x1 = max(0, x - 8)
            x2 = min(w, x + comp_w + 8)
            fg_mask[y1:y2, x1:x2] = 255
            
    # Also include the badge at top left
    fg_mask[20:105, 20:380] = 255
    
    # Also include subtitle area at bottom
    fg_mask[740:980, 250:1650] = 255
    
    cv2.imwrite(f"c:\\Users\\DELL\\Documents\\CODE\\DU_AN\\auto_fg_{name}.png", fg_mask)
    print(f"Processed {name}")

test_frame(r"c:\Users\DELL\Documents\CODE\DU_AN\inspect_vid\sec_08.jpg", "08")
test_frame(r"c:\Users\DELL\Documents\CODE\DU_AN\inspect_vid\sec_16.jpg", "16")
test_frame(r"c:\Users\DELL\Documents\CODE\DU_AN\inspect_vid\sec_26.jpg", "26")
test_frame(r"c:\Users\DELL\Documents\CODE\DU_AN\inspect_vid\sec_62.jpg", "62")

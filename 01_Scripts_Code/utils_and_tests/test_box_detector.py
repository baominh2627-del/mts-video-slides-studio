import cv2
import numpy as np

# Let's inspect sec_08, sec_16, sec_20, sec_26, sec_62
# How to detect a callout box:
# In the original image (or white balance image),
# A callout box is a rectangular region with:
# 1) Solid white background interior (at least 20x20 pixels with mean > 240 and std < 15)
# 2) Bounded by black border lines!

def find_boxes(gray):
    # Binary threshold for near-white fill
    white_fill = (gray > 245).astype(np.uint8)
    
    # Erode slightly to disconnect from border
    k3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    eroded = cv2.erode(white_fill, k3)
    
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(eroded)
    
    boxes = []
    for i in range(1, num_labels):
        x, y, w, h, area = stats[i]
        # Ignore outer background margins
        if x < 15 or y < 15 or x + w > gray.shape[1] - 15 or y + h > gray.shape[0] - 15:
            continue
        # In a callout box interior, h >= 15 and w >= 25 and area >= 500
        # Background stripe gaps have h <= 4, so eroded completely eliminates ALL background stripes!
        # Because background stripe white gaps are only 3-4px tall, erode(3,3) reduces their height to 0 or 1!
        if h >= 15 and w >= 25 and area >= 600:
            boxes.append((x - 6, y - 6, w + 12, h + 12))
            
    return boxes

for sec in ['08', '16', '20', '26', '62']:
    p = f"c:\\Users\\DELL\\Documents\\CODE\\DU_AN\\inspect_vid\\sec_{sec}.jpg"
    img = cv2.imread(p)
    res = img.astype(np.float32)
    res[:,:,0] = np.clip((img[:,:,0].astype(float) - 10.2) / (181.05 - 10.2) * 255.0, 0, 255)
    res[:,:,1] = np.clip((img[:,:,1].astype(float) - 10.2) / (191.25 - 10.2) * 255.0, 0, 255)
    res[:,:,2] = np.clip((img[:,:,2].astype(float) - 10.2) / (201.45 - 10.2) * 255.0, 0, 255)
    white = res.astype(np.uint8)
    gray = cv2.cvtColor(white, cv2.COLOR_BGR2GRAY)
    
    boxes = find_boxes(gray)
    print(f"Frame {sec} found {len(boxes)} boxes:")
    dbg = white.copy()
    for b in boxes:
        print("  ", b)
        cv2.rectangle(dbg, (b[0], b[1]), (b[0]+b[2], b[1]+b[3]), (0, 0, 255), 2)
    cv2.imwrite(f"c:\\Users\\DELL\\Documents\\CODE\\DU_AN\\dbg_boxes_{sec}.jpg", dbg)

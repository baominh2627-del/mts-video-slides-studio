import cv2, numpy as np, sys
sys.stdout.reconfigure(encoding='utf-8')

# Load the uploaded screenshot
img = cv2.imread(r'C:/Users/DELL/.gemini/antigravity/brain/835e6faf-41ce-4061-8bb6-9ca9efc0ff6c/.user_uploaded/media_1792979804685_65595b5f.png')
# Find the teal/cyan Xuat button
# Xuat button is teal background: in RGB it's roughly (0, 190-220, 190-220) or cyan
# Let's inspect the colors in the top right region
h, w = img.shape[:2]
tr = img[0:int(h*0.08), int(w*0.85):int(w*0.95)]
print("Top right region shape:", tr.shape)

# Let's find pixels where G > 180 and B > 180 and R < 100
cyan_mask = (tr[:, :, 0] > 160) & (tr[:, :, 1] > 160) & (tr[:, :, 2] < 100)
y_indices, x_indices = np.where(cyan_mask)
if len(x_indices) > 0:
    center_x = int(np.mean(x_indices)) + int(w * 0.85)
    center_y = int(np.mean(y_indices))
    print(f"Xuất button in screenshot: ({center_x}, {center_y}) out of ({w}, {h})")
    # Scale to 1920x1080 screen:
    screen_x = int(center_x * 1920 / w)
    screen_y = int(center_y * 1080 / h)
    print(f"Projected screen coords: ({screen_x}, {screen_y})")
else:
    print("Could not locate cyan button by color, printing color ranges...")
    print("Max values in tr:", np.max(tr, axis=(0,1)))

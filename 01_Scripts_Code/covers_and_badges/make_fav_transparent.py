import cv2, numpy as np

fav = cv2.imread(r'C:\Users\DELL\Documents\Downloads\favicon_xanh.png')
# Background is pure white [255, 255, 255]
# Let's create an alpha channel where white pixels are transparent
# Distance from white:
dist_white = np.linalg.norm(255 - fav.astype(float), axis=2)
# Alpha is proportional to distance from white, saturated at 40
alpha = np.clip(dist_white / 30.0 * 255, 0, 255).astype(np.uint8)

fav_rgba = np.dstack([fav, alpha])
# crop non-transparent
ys, xs = np.where(alpha > 10)
fav_clean = fav_rgba[ys.min():ys.max()+1, xs.min():xs.max()+1]
cv2.imwrite('c:/Users/DELL/Documents/CODE/DU_AN/favicon_transparent.png', fav_clean)
print("Saved favicon_transparent.png shape:", fav_clean.shape)

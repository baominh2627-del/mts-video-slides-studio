import cv2, numpy as np

im = cv2.imread(r'c:\Users\DELL\Documents\CODE\DU_AN\mts_logo_extracted.png', cv2.IMREAD_UNCHANGED)
alpha = im[:, :, 3]
ys, xs = np.where(alpha > 10)

# crop tightly with 10px margin
y1 = max(0, ys.min() - 10)
y2 = min(im.shape[0], ys.max() + 10)
x1 = max(0, xs.min() - 10)
x2 = min(im.shape[1], xs.max() + 10)

cropped = im[y1:y2, x1:x2]
out_p = r'c:\Users\DELL\Documents\CODE\DU_AN\mts_logo_clean.png'
cv2.imwrite(out_p, cropped)
print(f"Cropped logo size: {cropped.shape}, saved to: {out_p}")

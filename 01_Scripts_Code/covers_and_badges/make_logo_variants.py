import cv2, numpy as np

im = cv2.imread(r'c:\Users\DELL\Documents\CODE\DU_AN\mts_logo_clean.png', cv2.IMREAD_UNCHANGED)
alpha = im[:, :, 3]

# Create white background preview
bg_white = np.ones((im.shape[0], im.shape[1], 3), dtype=np.uint8) * 255
mask = alpha > 10
bg_white[mask] = im[mask, :3]
cv2.imwrite('c:/Users/DELL/Documents/CODE/DU_AN/logo_on_white.jpg', cv2.resize(bg_white, (400, 400)))

# Invert to white logo for dark background
logo_white = np.zeros_like(im)
logo_white[:, :, :3] = 255 # pure white strokes
logo_white[:, :, 3] = alpha # keep original smooth alpha antialiasing!
cv2.imwrite('c:/Users/DELL/Documents/CODE/DU_AN/mts_logo_white.png', logo_white)

# Invert to cyan logo (#38BDF8 -> BGR [248, 189, 56])
logo_cyan = np.zeros_like(im)
logo_cyan[:, :, 0] = 248
logo_cyan[:, :, 1] = 189
logo_cyan[:, :, 2] = 56
logo_cyan[:, :, 3] = alpha
cv2.imwrite('c:/Users/DELL/Documents/CODE/DU_AN/mts_logo_cyan.png', logo_cyan)

print("Saved logo variants!")

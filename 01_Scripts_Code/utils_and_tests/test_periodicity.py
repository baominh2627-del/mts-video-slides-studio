import cv2
import numpy as np

img = cv2.imread(r"c:\Users\DELL\Documents\CODE\DU_AN\crop_box_orig.png")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
h, w = gray.shape

# Let's inspect the periodicity:
# For each pixel (y, x), check if it is dark (gray < 200)
# And if in the column x, there are multiple dark peaks spaced ~4 to 7 pixels apart!

# We can detect this with 1D vertical autocorrelation or simple local peak detection:
# In periodic stripes, gray(y) has oscillations with period ~5px.
# Let's measure:
# If we compute: is there a dark peak at y, and also dark peaks around y-5 and y+5?
is_dark = (gray < 190).astype(np.uint8)

# Check vertical periodicity:
# For a stripe at y:
# It has a dark neighbor around y-5 (+/- 1) AND y+5 (+/- 1)
# AND it has bright pixels around y-2..y-3 and y+2..y+3!
stripe_mask = np.zeros((h, w), dtype=bool)

for y in range(8, h - 8):
    # Check if current pixel is dark
    current_dark = is_dark[y, :]
    
    # Check bright gap above (y-2 or y-3) and below (y+2 or y+3)
    bright_above = (gray[y-2, :] > 200) | (gray[y-3, :] > 200)
    bright_below = (gray[y+2, :] > 200) | (gray[y+3, :] > 200)
    
    # Check another dark stripe above (around y-5..y-7) or below (around y+5..y+7)
    dark_above = (is_dark[y-4, :] | is_dark[y-5, :] | is_dark[y-6, :] | is_dark[y-7, :])
    dark_below = (is_dark[y+4, :] | is_dark[y+5, :] | is_dark[y+6, :] | is_dark[y+7, :])
    
    # In periodic hatching, BOTH above and below have matching dark stripes, OR at least one has periodic spacing!
    # And crucially, INSIDE a letter or box, there is NO bright gap of 200+ immediately 2px away that is followed by another stripe!
    # Inside the 40°C box, the interior is pure white (gray > 250).
    # The top border of 40°C has white INSIDE the box (y+2..y+20 > 250), so dark_below is completely FALSE!
    # Because inside the box, there are NO dark stripes below the top border for 30+ pixels!
    is_periodic = current_dark & bright_above & bright_below & dark_above & dark_below
    stripe_mask[y, :] = is_periodic

# Let's see what stripe_mask detected!
result = img.copy()
result[stripe_mask] = [255, 255, 255]

cv2.imwrite(r"c:\Users\DELL\Documents\CODE\DU_AN\test_periodic_mask.png", (stripe_mask.astype(np.uint8)*255))
cv2.imwrite(r"c:\Users\DELL\Documents\CODE\DU_AN\test_periodic_result.png", result)
print("Saved periodic test")

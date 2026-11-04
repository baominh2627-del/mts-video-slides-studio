import cv2
import numpy as np
from inspect_stripes import w5, w15, w25, w65

# Let's test on w5 and w25
# In w5 and w25, let's explore removing horizontal stripes.

# APPROACH A: Horizontal run-length of dark pixels
# If a pixel is dark (in gray < 200) and is part of a horizontal continuous or semi-continuous run of dark pixels
# that spans a long distance (e.g. > 50px) without vertical thickness > 4px!
# Notice: Background stripes have vertical thickness <= 3px and horizontal length >= 40px!

def remove_stripes_morph_run(img_bgr):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    
    # Stripes are dark lines on bright background.
    # Vertical thickness is 1 to 3 pixels.
    # What if we apply a vertical morphological closing (or opening of inverted)?
    # For dark lines on white:
    # A vertical dilation with a kernel of height 5 (e.g. 5x1) will replace any dark line of height <= 3
    # with the surrounding white pixels!
    # Let's test vertical max filter (dilation in grayscale):
    k_v = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 6))
    v_dilated = cv2.dilate(img_bgr, k_v)
    
    return v_dilated

# APPROACH B: Detect stripes specifically
# A stripe has:
# 1) Low vertical thickness (<= 3px)
# 2) High horizontal continuity
# 3) High vertical gradient (top and bottom edges)
# Let's see what happens if we find the difference between img_bgr and v_dilated:
# diff = v_dilated - img_bgr
# In pure stripes, diff > 50.
# In thick objects (vertical rod, letters that have vertical strokes, spheres), diff is small except at top/bottom horizontal edges!

def remove_stripes_smart(img_bgr):
    # Convert to float
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    
    # Vertical dilation k=6
    k_v6 = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 6))
    dilated = cv2.dilate(img_bgr, k_v6)
    
    # Now, how to distinguish background stripes from foreground horizontal edges?
    # Horizontal stripes have almost NO horizontal gradient across a span of e.g. 15 pixels!
    # Let's compute horizontal gradient |dx|:
    dx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    abs_dx = cv2.convertScaleAbs(dx)
    
    # In background stripes, abs_dx is very low (smooth horizontally)!
    # In text, icons, spheres, stand, abs_dx is high!
    # Let's check a horizontal blur of abs_dx:
    k_h = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 1))
    dx_smoothed = cv2.dilate(abs_dx, k_h)
    
    # Where dx_smoothed is LOW (< 25) AND vertical dilation changed the pixel significantly:
    # that is purely a horizontal stripe!
    gray_dilated = cv2.cvtColor(dilated, cv2.COLOR_BGR2GRAY)
    diff = cv2.subtract(gray_dilated, gray)
    
    stripe_mask = (diff > 30) & (dx_smoothed < 30)
    
    # Also, background stripes are only where the background is light (dilated is near white, e.g. > 200)
    stripe_mask = stripe_mask & (gray_dilated > 180)
    
    result = img_bgr.copy()
    # Replace stripe pixels with 255 (pure white)
    result[stripe_mask] = [255, 255, 255]
    
    return result, stripe_mask.astype(np.uint8)*255

res5_a = remove_stripes_morph_run(w5)
res5_b, mask5_b = remove_stripes_smart(w5)
res25_b, mask25_b = remove_stripes_smart(w25)

cv2.imwrite(r"c:\Users\DELL\Documents\CODE\DU_AN\test_stripes_smart_5.jpg", res5_b)
cv2.imwrite(r"c:\Users\DELL\Documents\CODE\DU_AN\test_mask_smart_5.jpg", mask5_b)
cv2.imwrite(r"c:\Users\DELL\Documents\CODE\DU_AN\test_stripes_smart_25.jpg", res25_b)
print("Saved test images!")

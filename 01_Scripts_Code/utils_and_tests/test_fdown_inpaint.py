import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

im = cv2.imread(r'C:\Users\DELL\Documents\CODE\DU_AN\fdown_build\frame_30pct_71.2s.jpg')
h, w, _ = im.shape

# 1. Inpaint top-left logo
tl_crop = im[30:130, 30:140]
tl_mask = ((tl_crop[:, :, 1] > 60) & (tl_crop[:, :, 1] > tl_crop[:, :, 0].astype(int) + 15) & (tl_crop[:, :, 1] > tl_crop[:, :, 2].astype(int) + 15)).astype(np.uint8) * 255
# Dilate mask slightly
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
tl_mask_dil = cv2.dilate(tl_mask, kernel, iterations=2)
im[30:130, 30:140] = cv2.inpaint(tl_crop, tl_mask_dil, 5, cv2.INPAINT_TELEA)

# 2. Inpaint bottom text
bot_crop = im[950:995, 40:536]
bot_mask = ((bot_crop[:, :, 1] > 60) & (bot_crop[:, :, 1] > bot_crop[:, :, 0].astype(int) + 15) & (bot_crop[:, :, 1] > bot_crop[:, :, 2].astype(int) + 15)).astype(np.uint8) * 255
bot_mask_dil = cv2.dilate(bot_mask, kernel, iterations=2)
im[950:995, 40:536] = cv2.inpaint(bot_crop, bot_mask_dil, 5, cv2.INPAINT_TELEA)

# Save cleaned base
cv2.imwrite(r'C:\Users\DELL\Documents\CODE\DU_AN\fdown_build\test_inpainted.jpg', im)
print("Saved test_inpainted.jpg")

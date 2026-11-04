import cv2, sys

im_top = cv2.imread('c:/Users/DELL/Documents/CODE/DU_AN/slice_top.jpg')
im_bot = cv2.imread('c:/Users/DELL/Documents/CODE/DU_AN/slice_bot.jpg')

# Check where white or bright pixels are in top and bot
top_bright = (im_top > 200).sum(axis=2) == 3
bot_bright = (im_bot > 200).sum(axis=2) == 3

print("Top bright pixels count:", top_bright.sum())
print("Bot bright pixels count:", bot_bright.sum())

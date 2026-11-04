import cv2

im = cv2.imread('c:/Users/DELL/Documents/CODE/DU_AN/chitiet_30s.jpg')
# Let's save slices:
# Top: 0 - 300
# Upper middle: 300 - 800
# Center: 800 - 1300
# Lower middle: 1300 - 1650
# Bottom: 1650 - 1920

cv2.imwrite('c:/Users/DELL/Documents/CODE/DU_AN/slice_top.jpg', im[0:300, :])
cv2.imwrite('c:/Users/DELL/Documents/CODE/DU_AN/slice_uppermid.jpg', im[300:800, :])
cv2.imwrite('c:/Users/DELL/Documents/CODE/DU_AN/slice_center.jpg', im[800:1300, :])
cv2.imwrite('c:/Users/DELL/Documents/CODE/DU_AN/slice_lowermid.jpg', im[1300:1650, :])
cv2.imwrite('c:/Users/DELL/Documents/CODE/DU_AN/slice_bot.jpg', im[1650:1920, :])
print("Saved slices")

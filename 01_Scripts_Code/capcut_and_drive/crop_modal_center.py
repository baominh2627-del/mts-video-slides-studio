import cv2

im = cv2.imread(r'C:\Users\DELL\Documents\CODE\DU_AN\after_click_export.png')
# modal is centered: x from 650 to 1270, y from 400 to 820
crop = im[400:830, 650:1270]
cv2.imwrite(r'C:\Users\DELL\Documents\CODE\DU_AN\modal_center.png', crop)
print("Saved modal_center.png")

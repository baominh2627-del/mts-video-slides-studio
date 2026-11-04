import cv2

im = cv2.imread(r'C:\Users\DELL\Documents\CODE\DU_AN\after_click_export.png')
crop = im[840:920, 650:1270]
cv2.imwrite(r'C:\Users\DELL\Documents\CODE\DU_AN\modal_buttons.png', crop)
print("Saved modal_buttons.png")

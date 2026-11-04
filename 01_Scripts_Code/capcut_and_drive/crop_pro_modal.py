import cv2

im = cv2.imread(r'C:\Users\DELL\Documents\CODE\DU_AN\after_click_export.png')
# crop the list of Pro features in the modal:
# y from 530 to 760, x from 350 to 650
crop = im[530:760, 350:650]
cv2.imwrite(r'C:\Users\DELL\Documents\CODE\DU_AN\modal_pro_items.png', crop)
print("Saved modal_pro_items.png")

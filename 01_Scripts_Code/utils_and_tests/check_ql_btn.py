import cv2

im = cv2.imread(r'C:\Users\DELL\Documents\CODE\DU_AN\after_click_export.png')
# search for text 'Quay lại phần chỉnh sửa' in [760:820, 650:850]
crop = im[760:820, 680:860]
cv2.imwrite(r'C:\Users\DELL\Documents\CODE\DU_AN\btn_quaylai_1080.png', crop)
print("Crop shape:", crop.shape, "Center:", 680 + crop.shape[1]//2, 760 + crop.shape[0]//2)

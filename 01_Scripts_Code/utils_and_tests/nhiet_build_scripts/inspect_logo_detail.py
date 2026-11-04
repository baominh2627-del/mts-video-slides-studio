import cv2
orig = cv2.imread(r'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\check_outro_160.0s.jpg')
cv2.imwrite(r'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\logo_area_detail.jpg', orig[190:330, 200:380])
print('Saved logo_area_detail.jpg')

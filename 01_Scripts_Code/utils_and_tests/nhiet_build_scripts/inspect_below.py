import cv2
orig = cv2.imread(r'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\check_outro_160.0s.jpg')
cv2.imwrite(r'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\below_logo.jpg', orig[300:420, 150:430])
print('Saved below_logo.jpg')

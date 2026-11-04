import cv2
im = cv2.imread(r'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\scene_156.0s.jpg')
cv2.imwrite(r'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\inspect_156s.jpg', im[180:350, 150:420])
print('Saved inspect_156s.jpg')

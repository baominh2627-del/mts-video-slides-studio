import cv2

for s in [5, 30, 90, 120, 150]:
    im = cv2.imread(rf'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\frame_{s}s.jpg')
    top = im[0:160, :]
    cv2.imwrite(rf'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\top_{s}s.jpg', top)
print('Saved tops')

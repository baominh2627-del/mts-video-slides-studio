import cv2

f4760 = cv2.imread(r'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\cut_frame_4760.jpg')
f4764 = cv2.imread(r'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\cut_frame_4764.jpg')
f4765 = cv2.imread(r'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\cut_frame_4765.jpg')

# Check text in top center: "GHI NHỚ"
# "GHI NHỚ" is around y: [100, 160], x: [150, 420]
print('f4760 top center mean:', f4760[100:160, 150:420].mean())
print('f4764 top center mean:', f4764[100:160, 150:420].mean())
print('f4765 top center mean:', f4765[100:160, 150:420].mean())

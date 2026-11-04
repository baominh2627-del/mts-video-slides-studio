import cv2

cap = cv2.VideoCapture(r'C:\Users\DELL\Documents\Downloads\NHIỆT LƯỢNG, NỘI NĂNG, NHIỆT NĂNG.mp4')
fps = cap.get(cv2.CAP_PROP_FPS)

for s in [10, 15, 20, 25, 45, 65, 85, 105]:
    cap.set(cv2.CAP_PROP_POS_MSEC, s * 1000)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(rf'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\clean_bg_{s}s.jpg', frame)
        print(f'Extracted clean_bg_{s}s.jpg')
cap.release()

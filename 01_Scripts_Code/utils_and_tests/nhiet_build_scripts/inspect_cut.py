import cv2

cap = cv2.VideoCapture(r'C:\Users\DELL\Documents\Downloads\NHIỆT LƯỢNG, NỘI NĂNG, NHIỆT NĂNG.mp4')
fps = cap.get(cv2.CAP_PROP_FPS)

for f_idx in [4760, 4762, 4764, 4765, 4766, 4767]:
    cap.set(cv2.CAP_PROP_POS_FRAMES, f_idx)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(rf'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\cut_frame_{f_idx}.jpg', frame)
        print(f'Saved cut_frame_{f_idx}.jpg')
cap.release()

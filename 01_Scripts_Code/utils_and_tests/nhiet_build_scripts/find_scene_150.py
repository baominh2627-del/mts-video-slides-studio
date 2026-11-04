import cv2

cap = cv2.VideoCapture(r'C:\Users\DELL\Documents\Downloads\NHIỆT LƯỢNG, NỘI NĂNG, NHIỆT NĂNG.mp4')
fps = cap.get(cv2.CAP_PROP_FPS)

for s in [148.0, 150.0, 152.0, 153.0, 154.0]:
    f_idx = int(s * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, f_idx)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(rf'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\scene_{s}s.jpg', frame)
        print(f'{s}s (frame {f_idx})')
cap.release()

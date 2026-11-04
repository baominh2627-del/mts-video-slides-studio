import cv2

# check frames 4700 to 4760
cap = cv2.VideoCapture(r'C:\Users\DELL\Documents\Downloads\NHIỆT LƯỢNG, NỘI NĂNG, NHIỆT NĂNG.mp4')
fps = cap.get(cv2.CAP_PROP_FPS)

# Where does "GHI NHỚ" scene actually start?
for s in [155.0, 156.0, 157.0, 157.5, 158.0]:
    f_idx = int(s * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, f_idx)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(rf'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\scene_{s}s.jpg', frame)
        print(f'{s}s (frame {f_idx}): mean {frame[100:160, 150:420].mean():.1f}')
cap.release()

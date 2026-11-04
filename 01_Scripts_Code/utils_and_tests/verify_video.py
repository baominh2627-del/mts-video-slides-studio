import cv2

video_path = r'C:\Users\DELL\Documents\Downloads\VIDEO CHỈNH SỬA.mp4'
cap = cv2.VideoCapture(video_path)

fps = cap.get(cv2.CAP_PROP_FPS)
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
total_f = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print(f"Verification: {w}x{h} @ {fps} FPS, {total_f} frames ({total_f/fps:.2f}s)")

for s in [5, 30, 70, 119]:
    cap.set(cv2.CAP_PROP_POS_MSEC, s * 1000)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(rf'C:\Users\DELL\Documents\CODE\DU_AN\verify_final_{s}s.jpg', frame)
        print(f"Saved verify_final_{s}s.jpg")
cap.release()

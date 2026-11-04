import cv2

video_path = r'C:\Users\DELL\Documents\Downloads\MÁY GIA TỐC CYCLOTRON_MTSEducation.mp4'
cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
total_f = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print(f"Cyclotron Output: {w}x{h} @ {fps} FPS, {total_f} frames ({total_f/fps:.2f}s)")

for s in [10, 60, 140, 230]:
    cap.set(cv2.CAP_PROP_POS_MSEC, s * 1000)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(rf'C:\Users\DELL\Documents\CODE\DU_AN\fdown_build\verify_cyclotron_{s}s.jpg', frame)
        print(f"Saved verify_cyclotron_{s}s.jpg")
cap.release()

import cv2

video_path = r'C:\Users\DELL\Documents\Downloads\MÁY GIA TỐC CYCLOTRON_CHỈNH SỬA.mp4'
cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
total_f = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
duration = total_f / fps

print(f"Final Edited Video: {w}x{h} @ {fps} FPS, {total_f} frames ({duration:.2f}s = {int(duration//60):02d}:{int(duration%60):02d})")

# Sample frames at 15s, 60s, 120s, 175s
for s in [15, 60, 120, 175]:
    cap.set(cv2.CAP_PROP_POS_MSEC, s * 1000)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(rf'C:\Users\DELL\Documents\CODE\DU_AN\fdown_build\verify_capcut_{s}s.jpg', frame)
        print(f"Saved verify_capcut_{s}s.jpg")
cap.release()

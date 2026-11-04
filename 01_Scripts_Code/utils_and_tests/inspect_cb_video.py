import cv2, os

p = r"C:/Users/DELL/Documents/Downloads/CÂN BẰNG NHIỆT_MTSEducation_1080p.mp4"
cap = cv2.VideoCapture(p)
fps = cap.get(cv2.CAP_PROP_FPS)
count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"Video: {w}x{h}, {fps} fps, {count} frames, duration: {count/fps:.2f}s")

for sec in [1.0, 10.0, 30.0, 60.0, 80.0]:
    frame_idx = int(sec * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
    ret, frame = cap.read()
    if ret:
        out_name = f"c:/Users/DELL/Documents/CODE/DU_AN/frame_cb_{int(sec)}s.jpg"
        cv2.imwrite(out_name, frame)
        print(f"Saved {out_name}")
cap.release()

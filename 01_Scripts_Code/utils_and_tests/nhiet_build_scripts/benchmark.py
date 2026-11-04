import cv2
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont

t0 = time.time()
cap = cv2.VideoCapture(r'C:\Users\DELL\Documents\Downloads\NHIỆT LƯỢNG, NỘI NĂNG, NHIỆT NĂNG.mp4')
fps = cap.get(cv2.CAP_PROP_FPS)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print(f'Total frames: {total_frames}, FPS: {fps}')

count = 0
for _ in range(100):
    ret, frame = cap.read()
    if not ret:
        break
    # Inpaint seam
    c_left = frame[15:140, 66].astype(float)
    c_right = frame[15:140, 84].astype(float)
    for x in range(67, 84):
        alpha = (x - 66) / (84.0 - 66.0)
        frame[15:140, x] = np.clip(c_left * (1.0 - alpha) + c_right * alpha, 0, 255).astype(np.uint8)
    count += 1
cap.release()
t1 = time.time()
print(f'100 frames processed in {t1 - t0:.3f}s -> ~{count / (t1 - t0):.1f} fps')

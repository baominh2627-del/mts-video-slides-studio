import cv2
import time
import numpy as np

cap = cv2.VideoCapture(r'C:\Users\DELL\Documents\Downloads\NHIỆT LƯỢNG, NỘI NĂNG, NHIỆT NĂNG.mp4')
t0 = time.time()
for _ in range(100):
    ret, frame = cap.read()
    if not ret: break
    resized = cv2.resize(frame, (1080, 1920), interpolation=cv2.INTER_CUBIC)
cap.release()
t1 = time.time()
print(f'100 frames resized in {t1 - t0:.3f}s -> ~{100 / (t1 - t0):.1f} fps')

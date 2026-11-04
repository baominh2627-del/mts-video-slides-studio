# -*- coding: utf-8 -*-
import sys
import os
import cv2

sys.stdout.reconfigure(encoding='utf-8')

for fname in ["PHƯƠNG TRÌNH MAXWALL_NoWatermark.mp4", "PHƯƠNG TRÌNH MAXWALL.mp4"]:
    path = os.path.join(r"C:\Users\DELL\Documents\Downloads", fname)
    if os.path.exists(path):
        cap = cv2.VideoCapture(path)
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        dur = count / fps if fps > 0 else 0
        print(f"File: {fname}")
        print(f"Size: {os.path.getsize(path) / (1024*1024):.2f} MB")
        print(f"Resolution: {w}x{h}, FPS: {fps}, Frames: {count}, Duration: {dur:.2f}s ({dur/60:.2f}m)")
        cap.release()

# Extract frames from NoWatermark
path = os.path.join(r"C:\Users\DELL\Documents\Downloads", "PHƯƠNG TRÌNH MAXWALL_NoWatermark.mp4")
cap = cv2.VideoCapture(path)
fps = cap.get(cv2.CAP_PROP_FPS)
count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
dur = count / fps if fps > 0 else 0

out_dir = r"C:\Users\DELL\Documents\CODE\DU_AN\sample_frames"
os.makedirs(out_dir, exist_ok=True)

# Sample evenly across the video
sample_times = [1, 10, 30, 60, 90, 120, 150, 180, 210, dur - 2]
for t in sample_times:
    if t < dur:
        frame_idx = int(t * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if ret:
            out_file = os.path.join(out_dir, f"frame_{int(t)}s.jpg")
            cv2.imwrite(out_file, frame)
            print(f"Extracted: {out_file}")
cap.release()
print("Done extracting keyframes.")

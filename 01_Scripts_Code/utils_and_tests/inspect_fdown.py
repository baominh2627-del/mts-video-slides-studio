import os
import sys
import cv2
sys.stdout.reconfigure(encoding='utf-8')

video_path = r'C:\Users\DELL\Documents\Downloads\FDown.vn_TikTok_Video_Downloader_3387.mp4'

cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
duration = total_frames / fps if fps > 0 else 0

print(f"File: {video_path}")
print(f"Resolution: {w}x{h}")
print(f"FPS: {fps}")
print(f"Total Frames: {total_frames}")
print(f"Duration: {duration:.2f}s ({duration/60:.2f} mins)")

# Extract sample frames across the video: 0%, 10%, 25%, 50%, 75%, 90%, 98%
os.makedirs(r'C:\Users\DELL\Documents\CODE\DU_AN\fdown_build', exist_ok=True)
for pct in [0, 5, 15, 30, 50, 70, 85, 95, 99]:
    f_idx = int(total_frames * (pct / 100.0))
    f_idx = min(f_idx, total_frames - 1)
    cap.set(cv2.CAP_PROP_POS_FRAMES, f_idx)
    ret, frame = cap.read()
    if ret:
        t_sec = f_idx / fps
        cv2.imwrite(rf'C:\Users\DELL\Documents\CODE\DU_AN\fdown_build\frame_{pct}pct_{t_sec:.1f}s.jpg', frame)
        print(f"Saved frame {pct}% at {t_sec:.1f}s (size {frame.shape[1]}x{frame.shape[0]})")

cap.release()

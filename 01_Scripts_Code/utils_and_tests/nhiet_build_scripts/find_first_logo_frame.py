import cv2
import numpy as np

cap = cv2.VideoCapture(r'C:\Users\DELL\Documents\Downloads\NHIỆT LƯỢNG, NỘI NĂNG, NHIỆT NĂNG.mp4')
fps = cap.get(cv2.CAP_PROP_FPS)

# Let's inspect frames around 157s to 159s (around frame 4700 to 4770)
start_frame = int(157.0 * fps)
end_frame = int(160.0 * fps)

cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
for f_idx in range(start_frame, end_frame):
    ret, frame = cap.read()
    if not ret: break
    # check green pixels in logo area [206:303, 233:351]
    crop = frame[200:310, 230:360]
    mask = (crop[:, :, 1] > 90) & (crop[:, :, 1] > crop[:, :, 0].astype(int) + 20) & (crop[:, :, 1] > crop[:, :, 2].astype(int) + 20)
    green_count = np.count_nonzero(mask)
    if green_count > 50:
        print(f'First frame with green logo: frame {f_idx} (time {f_idx/fps:.2f}s, green_count={green_count})')
        break
cap.release()

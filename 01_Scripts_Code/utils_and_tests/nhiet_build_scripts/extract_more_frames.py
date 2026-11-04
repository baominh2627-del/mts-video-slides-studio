import cv2

for s in [5, 30, 60, 90, 120, 150]:
    fn = rf'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\check_outro_{float(s):.1f}s.jpg'
    # if doesn't exist, extract from video
    import os
    if not os.path.exists(fn):
        cap = cv2.VideoCapture(r'C:\Users\DELL\Documents\Downloads\NHIỆT LƯỢNG, NỘI NĂNG, NHIỆT NĂNG.mp4')
        cap.set(cv2.CAP_PROP_POS_MSEC, s * 1000)
        ret, frame = cap.read()
        cap.release()
        if ret:
            cv2.imwrite(rf'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\frame_{s}s.jpg', frame)
            fn = rf'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\frame_{s}s.jpg'
    print(f'Frame {s}s ready')

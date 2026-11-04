import cv2

for name in ['giai_cau16_chi_tiet.mp4', 'giai_cau16_hoan_chinh.mp4']:
    cap = cv2.VideoCapture(f'C:/Users/DELL/Documents/Downloads/{name}')
    for sec in [5, 30, 60, 90, 120, 150, 180]:
        cap.set(cv2.CAP_PROP_POS_MSEC, sec * 1000)
        ret, frame = cap.read()
        if ret:
            cv2.imwrite(f'c:/Users/DELL/Documents/CODE/DU_AN/{name[:10]}_{sec}s.jpg', frame)
    cap.release()
print("Saved comparison frames")

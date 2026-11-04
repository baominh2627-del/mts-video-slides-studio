import cv2, os

cap1 = cv2.VideoCapture(r'C:\Users\DELL\Documents\Downloads\giai_cau16_chi_tiet.mp4')
cap2 = cv2.VideoCapture(r'C:\Users\DELL\Documents\Downloads\giai_cau16_hoan_chinh.mp4')

diffs = []
for sec in [5, 30, 60, 90, 120, 150, 180]:
    cap1.set(cv2.CAP_PROP_POS_MSEC, sec * 1000)
    cap2.set(cv2.CAP_PROP_POS_MSEC, sec * 1000)
    r1, f1 = cap1.read()
    r2, f2 = cap2.read()
    cv2.imwrite(f'c:/Users/DELL/Documents/CODE/DU_AN/chitiet_{sec}s.jpg', f1)
    cv2.imwrite(f'c:/Users/DELL/Documents/CODE/DU_AN/hoanchinh_{sec}s.jpg', f2)
    diff = cv2.absdiff(f1, f2)
    diffs.append((sec, diff.sum()))

cap1.release()
cap2.release()
for sec, d in diffs:
    print(f"Sec {sec}: difference sum = {d}")

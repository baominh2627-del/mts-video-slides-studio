import cv2
import numpy as np

im = cv2.imread(r'C:\Users\DELL\Documents\CODE\DU_AN\after_click_export.png')
# crop around [350:480, 760:810]
crop = im[760:810, 350:500]
cv2.imwrite(r'C:\Users\DELL\Documents\CODE\DU_AN\btn_quaylai.png', crop)
print("Saved btn_quaylai.png, center:", 350 + crop.shape[1]//2, 760 + crop.shape[0]//2)

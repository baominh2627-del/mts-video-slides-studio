# -*- coding: utf-8 -*-
"""
Pipeline tạo 2 bộ Slides TikTok (1080x1440) chuẩn MTSEducation cho:
ĐỀ THI THỬ HSG VẬT LÝ 12 - TRƯỜNG THPT PHỤ DỰC (CHƯƠNG NHIỆT & KHÍ LÝ TƯỞNG)
Set 1: Đề không đáp án (xóa tô vàng đáp án để học sinh tự làm, bố cục hoàn hảo)
Set 2: Đề có đáp án (giữ nguyên tô vàng đáp án)
"""

import os
import sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8')

# Directories
NATIVE_DIR = r"C:\Users\DELL\.gemini\antigravity\brain\544f119c-06b5-4b24-b041-6f9293a453ac\phu_duc_native"
BASE_COVER_PATH = r"C:\Users\DELL\Documents\Downloads\GIA_SƯ_2\TT\TIKTOK_SLIDES_MTSEducation\slide_01.jpg"
PLAYFAIR_FONT = r"C:\Users\DELL\Documents\CODE\DU_AN\PlayfairDisplay.ttf"

OUT_SET1_GIASU = r"C:\Users\DELL\Documents\Downloads\GIA_SƯ_2\TT\DE_HSG_LY12_NHIET_KHI_DE_KHONG_MTSEducation"
OUT_SET1_DOWN = r"C:\Users\DELL\Documents\Downloads\DE_HSG_LY12_NHIET_KHI_DE_KHONG_MTSEducation"

OUT_SET2_GIASU = r"C:\Users\DELL\Documents\Downloads\GIA_SƯ_2\TT\DE_HSG_LY12_NHIET_KHI_DAP_AN_MTSEducation"
OUT_SET2_DOWN = r"C:\Users\DELL\Documents\Downloads\DE_HSG_LY12_NHIET_KHI_DAP_AN_MTSEducation"

for d in [OUT_SET1_GIASU, OUT_SET1_DOWN, OUT_SET2_GIASU, OUT_SET2_DOWN]:
    os.makedirs(d, exist_ok=True)

# Load native raw pages (2311 x 3060)
pages = []
for i in range(1, 8):
    fn = os.path.join(NATIVE_DIR, f"page_{i:02d}.jpeg")
    im = cv2.imread(fn)
    pages.append(im)
print(f"Loaded {len(pages)} native pages.")

# Fonts
f_mts = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 44)
f_title = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 34)
f_footer = ImageFont.truetype(r"C:\Windows\Fonts\timesbi.ttf", 23)
f_times_bd = ImageFont.truetype(r"C:\Windows\Fonts\timesbd.ttf", 42)
f_times_reg = ImageFont.truetype(r"C:\Windows\Fonts\times.ttf", 40)

# Colors
C_BG = (255, 255, 255)
C_BOX_BORDER = (170, 170, 170)
C_DIVIDER = (30, 115, 190)
C_LOGO_MTS = (30, 95, 205)
C_TITLE_RED = (215, 15, 15)
C_FOOTER_LINE = (190, 190, 190)
C_FOOTER_BRAND = (30, 60, 180)
C_FOOTER_NUM = (20, 20, 20)

# Helper function: remove yellow highlight
def remove_yellow(cv_img):
    hsv = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV)
    h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    # Yellow mask
    yellow_mask = (h >= 18) & (h <= 38) & (s > 40) & (v > 140)
    res = cv_img.copy()
    res[yellow_mask] = [255, 255, 255]
    return res

# Helper function: enhance contrast & clean noise
def enhance_contrast(cv_img, is_set2=False):
    hsv = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV)
    h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    
    # Yellow protection in Set 2
    if is_set2:
        yellow_prot = (h >= 18) & (h <= 38) & (s > 40) & (v > 140)
    else:
        yellow_prot = np.zeros(cv_img.shape[:2], dtype=bool)
        
    rgb_min = np.min(cv_img, axis=2)
    # Background threshold
    bg_mask = (((v > 220) & (s < 35)) | (rgb_min > 225)) & (~yellow_prot)
    
    # Text masks
    black_mask = (v < 160) & (s < 60) & (~bg_mask) & (~yellow_prot)
    red_mask = ((h < 15) | (h > 165)) & (s > 40) & (v > 50) & (~yellow_prot)
    blue_mask = (h >= 95) & (h <= 135) & (s > 35) & (v > 45) & (~yellow_prot)
    
    res = cv_img.copy()
    res[bg_mask] = [255, 255, 255]
    
    for c in range(3):
        ch = res[:, :, c].astype(np.float32)
        ch[black_mask] = np.clip(ch[black_mask] * 0.35, 0, 255)
        res[:, :, c] = ch.astype(np.uint8)
        
    # Enrich red and blue
    red_target = np.array([20, 20, 205], dtype=np.float32)
    alpha_r = (s[red_mask] / 255.0)[:, np.newaxis]
    orig_r = res[red_mask].astype(np.float32)
    res[red_mask] = np.clip(orig_r * (1.0 - alpha_r * 0.75) + red_target * (alpha_r * 0.75), 0, 255).astype(np.uint8)
    
    blue_target = np.array([195, 95, 25], dtype=np.float32)
    alpha_b = (s[blue_mask] / 255.0)[:, np.newaxis]
    orig_b = res[blue_mask].astype(np.float32)
    res[blue_mask] = np.clip(orig_b * (1.0 - alpha_b * 0.75) + blue_target * (alpha_b * 0.75), 0, 255).astype(np.uint8)
    
    return res

# Helper: clean magenta/green highlights on headers
def clean_header_artifacts(cv_img):
    hsv = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV)
    h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    mag_mask = (h >= 140) & (h <= 170) & (s > 70) & (v > 100)
    green_mask = (h >= 35) & (h <= 85) & (s > 70) & (v > 100)
    res = cv_img.copy()
    res[mag_mask] = [255, 255, 255]
    res[green_mask] = [255, 255, 255]
    return res

print("Image processing functions defined.")

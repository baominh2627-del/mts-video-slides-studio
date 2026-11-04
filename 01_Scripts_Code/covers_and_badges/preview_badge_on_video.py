import cv2
from PIL import Image

frame = Image.open('c:/Users/DELL/Documents/CODE/DU_AN/chitiet_5s.jpg')
overlay = Image.open('c:/Users/DELL/Documents/CODE/DU_AN/official_logo_mts_overlay.png')

combined = Image.alpha_composite(frame.convert('RGBA'), overlay)
crop = combined.crop((20, 30, 500, 180))
crop.convert('RGB').save('c:/Users/DELL/Documents/CODE/DU_AN/badge_on_video_frame.jpg')
print("Saved badge_on_video_frame.jpg")

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

im = cv2.imread(r'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\frame_30s.jpg')

# Inpaint seam
c_left = im[15:140, 66].astype(float)
c_right = im[15:140, 84].astype(float)
for x in range(67, 84):
    alpha = (x - 66) / (84.0 - 66.0)
    im[15:140, x] = np.clip(c_left * (1.0 - alpha) + c_right * alpha, 0, 255).astype(np.uint8)

im_pil = Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).convert('RGBA')

# Create an overlay layer for clean transparency
overlay = Image.new('RGBA', im_pil.size, (0, 0, 0, 0))
draw = ImageDraw.Draw(overlay)

font_bold = r'C:\Windows\Fonts\segoeuib.ttf'
font_brand = ImageFont.truetype(font_bold, 15)

# Badge: [20, 24, 175, 58]
pill_box = [20, 24, 175, 58]
draw.rounded_rectangle(pill_box, radius=9, fill=(15, 23, 42, 220), outline=(56, 189, 248, 240), width=1)

# Cyan accent dot
draw.ellipse([32, 37, 40, 45], fill=(56, 189, 248, 255))
# Brand text
draw.text((47, 30), 'MTSEducation', font=font_brand, fill=(255, 255, 255, 255))

result = Image.alpha_composite(im_pil, overlay).convert('RGB')
result.save(r'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\test_topleft_v2.jpg', quality=95)
print('Saved test_topleft_v2.jpg')

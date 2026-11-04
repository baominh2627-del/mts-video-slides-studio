import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Load test frame
frame = cv2.imread(r'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\frame_30s.jpg')

# 1. Inpaint seam in 576x1024
c_left = frame[15:140, 66].astype(float)
c_right = frame[15:140, 84].astype(float)
for x in range(67, 84):
    alpha = (x - 66) / (84.0 - 66.0)
    frame[15:140, x] = np.clip(c_left * (1.0 - alpha) + c_right * alpha, 0, 255).astype(np.uint8)

# 2. Resize to 1080x1920
frame_1080 = cv2.resize(frame, (1080, 1920), interpolation=cv2.INTER_CUBIC)

# 3. Create PIL overlay
pil_img = Image.fromarray(cv2.cvtColor(frame_1080, cv2.COLOR_BGR2RGB)).convert('RGBA')
overlay = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
draw = ImageDraw.Draw(overlay)

font_bold = r'C:\Windows\Fonts\segoeuib.ttf'
font_brand = ImageFont.truetype(font_bold, 28)

# Pill: [40, 48, 330, 114]
draw.rounded_rectangle([40, 48, 330, 114], radius=16, fill=(15, 23, 42, 220), outline=(56, 189, 248, 240), width=2)
# Cyan dot
draw.ellipse([60, 71, 76, 87], fill=(56, 189, 248, 255))
# Text
draw.text((88, 60), 'MTSEducation', font=font_brand, fill=(255, 255, 255, 255))

result = Image.alpha_composite(pil_img, overlay).convert('RGB')
result.save(r'C:\Users\DELL\Documents\CODE\DU_AN\nhiet_build\test_1080_watermark.jpg', quality=95)
print('Saved test_1080_watermark.jpg')

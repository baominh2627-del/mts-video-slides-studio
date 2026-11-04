import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
draw = ImageDraw.Draw(overlay)

# Load the official logo
logo_pil = Image.open('c:/Users/DELL/Documents/CODE/DU_AN/favicon_transparent.png')
# Resize logo icon to 64x64
icon_size = 64
logo_icon = logo_pil.resize((icon_size, icon_size), Image.LANCZOS)

# Fonts
font_path = r'C:\Windows\Fonts\arialbd.ttf'
badge_font = ImageFont.truetype(font_path, 34)
badge_text = "MTSEducation"
bbox = badge_font.getbbox(badge_text)
text_w = bbox[2] - bbox[0]
text_h = bbox[3] - bbox[1]

# Pill dimensions
pad_x = 24
pad_y = 14
gap = 16
pill_w = pad_x + icon_size + gap + text_w + pad_x
pill_h = max(icon_size, text_h) + pad_y * 2
bx, by = 40, 50

# Draw dark rounded pill with cyan border
draw.rounded_rectangle([bx, by, bx + pill_w, by + pill_h], radius=24, fill=(15, 23, 42, 235), outline=(56, 189, 248, 255), width=2)

# Paste the official logo icon
icon_x = bx + pad_x
icon_y = by + (pill_h - icon_size) // 2
overlay.paste(logo_icon, (icon_x, icon_y), logo_icon)

# Draw text MTSEducation
text_x = icon_x + icon_size + gap
text_y = by + (pill_h - text_h) // 2 - 4
draw.text((text_x, text_y), badge_text, fill=(255, 255, 255, 255), font=badge_font)

out_overlay = r'c:\Users\DELL\Documents\CODE\DU_AN\official_logo_mts_overlay.png'
overlay.save(out_overlay)
print(f"Saved official logo overlay: {out_overlay}")

# Save a crop of just the badge to preview
badge_crop = overlay.crop((bx - 5, by - 5, bx + pill_w + 5, by + pill_h + 5))
badge_crop.save('c:/Users/DELL/Documents/CODE/DU_AN/badge_preview.png')
print("Saved badge_preview.png")

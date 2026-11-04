import sys
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8')

W, H = 1080, 1920
overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(overlay)

# Load the official logo icon from favicon_transparent.png
logo_pil = Image.open('favicon_transparent.png')
icon_size = 44
logo_icon = logo_pil.resize((icon_size, icon_size), Image.LANCZOS)

# Font for MTSEducation
font_path = r'C:\Windows\Fonts\arialbd.ttf'
badge_font = ImageFont.truetype(font_path, 24)
text = "MTSEducation"
bbox = badge_font.getbbox(text)
tw = bbox[2] - bbox[0]
th = bbox[3] - bbox[1]

pad_x = 16
gap = 12
pw = pad_x + icon_size + gap + tw + pad_x
ph = 58
bx, by = 35, 50

# Draw rounded badge
d.rounded_rectangle([bx, by, bx+pw, by+ph], radius=18, fill=(15, 23, 42, 240), outline=(56, 189, 248), width=2)
overlay.paste(logo_icon, (bx + pad_x, by + (ph - icon_size)//2), logo_icon)
d.text((bx + pad_x + icon_size + gap, by + (ph - th)//2 - 2), text, font=badge_font, fill=(255, 255, 255))

out_path = r'c:\Users\DELL\Documents\CODE\DU_AN\official_logo_mts_video2.png'
overlay.save(out_path)
print(f"Saved official_logo_mts_video2.png successfully! (size: {overlay.size})")

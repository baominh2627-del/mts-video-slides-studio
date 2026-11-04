from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
draw = ImageDraw.Draw(overlay)

# Badge at top-left
font_path = r'C:\Windows\Fonts\arialbd.ttf'
badge_font = ImageFont.truetype(font_path, 32)
badge_text = "MTSEducation"
bbox = badge_font.getbbox(badge_text)
bw = bbox[2] - bbox[0] + 50
bh = bbox[3] - bbox[1] + 26
bx, by = 40, 50

# Rounded rectangle badge
draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=20, fill=(15, 23, 42, 230), outline=(56, 189, 248, 255), width=2)
# Cyan dot
draw.ellipse([bx + 16, by + 14, bx + 28, by + 26], fill=(56, 189, 248, 255))
# Text
draw.text((bx + 38, by + 10), badge_text, fill=(255, 255, 255, 255), font=badge_font)

out_p = r'c:\Users\DELL\Documents\CODE\DU_AN\logo_mts_overlay.png'
overlay.save(out_p)
print("Saved logo overlay to:", out_p)

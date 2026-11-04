& "C:\Users\DELL\AppData\Local\Programs\Python\Python313\python.exe" -c "
import cv2, os, sys, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8')

# Output directories
dir_giasu = r'C:\Users\DELL\Documents\Downloads\GIA_SƯ_2\TT\TIKTOK_SLIDES_KHI_LY_TUONG_MTSEducation'
dir_down = r'C:\Users\DELL\Documents\Downloads\TIKTOK_SLIDES_KHI_LY_TUONG_MTSEducation'
dir_proj = r'C:\Users\DELL\Documents\CODE\DU_AN\TIKTOK_SLIDES_KHI_LY_TUONG_MTSEducation'

for d in [dir_giasu, dir_down, dir_proj]:
    os.makedirs(d, exist_ok=True)

# 1. GENERATE SLIDE 01 (COVER)
print('Generating Slide 01 (Cover)...')
prev_cover_path = r'C:\Users\DELL\Documents\Downloads\GIA_SƯ_2\TT\TIKTOK_SLIDES_MTSEducation\slide_01.jpg'
orig_pil = Image.open(prev_cover_path)
cv_img = cv2.cvtColor(np.array(orig_pil), cv2.COLOR_RGB2BGR)

# Mask only 'Vật Lí Nhiệt' (x=335..900, y=635..775)
mask = np.zeros(cv_img.shape[:2], dtype=np.uint8)
text_box = cv_img[635:775, 335:900]
dark = np.mean(text_box, axis=2) < 140
mask[635:775, 335:900][dark] = 255

kernel = np.ones((7,7), np.uint8)
mask_dil = cv2.dilate(mask, kernel, iterations=2)
inpainted = cv2.inpaint(cv_img, mask_dil, 7, cv2.INPAINT_TELEA)

slide01_pil = Image.fromarray(cv2.cvtColor(inpainted, cv2.COLOR_BGR2RGB))
draw01 = ImageDraw.Draw(slide01_pil)
font_cover = ImageFont.truetype(r'C:\Windows\Fonts\timesbd.ttf', 95)
draw01.text((345, 646), 'Khí Lí Tưởng', fill=(48, 30, 52), font=font_cover)

slide_images = [slide01_pil]

# Fonts for content slides
font_box_mts = ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf', 44)
font_box_title = ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf', 32)
font_footer = ImageFont.truetype(r'C:\Windows\Fonts\timesbi.ttf', 24)

# 2. GENERATE SLIDES 02 TO 23
raw_dir = r'C:\Users\DELL\Documents\CODE\DU_AN\khi_ly_tuong_raw'

for p_num in range(1, 23):
    print(f'Processing Page {p_num} (Slide {p_num+1:02d})...')
    canvas = Image.new('RGB', (1080, 1440), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    raw_file = os.path.join(raw_dir, f'page_{p_num:02d}.jpeg')
    page_im = Image.open(raw_file)
    cw, ch = page_im.size

    if p_num == 1:
        # Slide 02 has Header Box
        box_x0, box_y0, box_x1, box_y1 = 65, 36, 1015, 115
        draw.rectangle([box_x0, box_y0, box_x1, box_y1], outline=(170, 170, 170), width=1)
        draw.text((box_x0 + 15, box_y0 + 15), 'MTS', fill=(30, 95, 205), font=font_box_mts)
        div_x = box_x0 + 125
        draw.line([(div_x, box_y0), (div_x, box_y1)], fill=(30, 120, 200), width=2)

        title_text = 'KHÍ LÝ TƯỞNG - NÂNG CAO'
        tb = draw.textbbox((0, 0), title_text, font=font_box_title)
        tw = tb[2] - tb[0]
        title_x = div_x + ((box_x1 - div_x) - tw) // 2
        draw.text((title_x, box_y0 + 23), title_text, fill=(215, 20, 20), font=font_box_title)

        # Content area: y=130..1365 (h=1235)
        avail_w, avail_h = 980, 1235
        scale = min(avail_w / cw, avail_h / ch)
        nw, nh = int(cw * scale), int(ch * scale)
        scaled_page = page_im.resize((nw, nh), Image.Resampling.LANCZOS)
        cx = (1080 - nw) // 2
        cy = 130 + (avail_h - nh) // 2
        canvas.paste(scaled_page, (cx, cy))
    else:
        # Slides 03..23: Clean top margin
        avail_w, avail_h = 980, 1320
        scale = min(avail_w / cw, avail_h / ch)
        nw, nh = int(cw * scale), int(ch * scale)
        scaled_page = page_im.resize((nw, nh), Image.Resampling.LANCZOS)
        cx = (1080 - nw) // 2
        if nh < 1100:
            cy = 80
        else:
            cy = 40 + (avail_h - nh) // 2
        canvas.paste(scaled_page, (cx, cy))

    # Footer
    foot_y = 1380
    draw.line([(65, foot_y), (1015, foot_y)], fill=(190, 190, 190), width=1)
    draw.text((65, foot_y + 8), 'MTSEducation', fill=(30, 60, 180), font=font_footer)
    num_str = str(p_num)
    pb = draw.textbbox((0, 0), num_str, font=font_footer)
    pw = pb[2] - pb[0]
    draw.text((1015 - pw, foot_y + 8), num_str, fill=(20, 20, 20), font=font_footer)

    slide_images.append(canvas)

# 3. SAVE TO ALL LOCATIONS
print(f'Saving {len(slide_images)} slides to directories...')
for idx, s_im in enumerate(slide_images):
    fn = f'slide_{idx+1:02d}.jpg'
    for d in [dir_giasu, dir_down, dir_proj]:
        p = os.path.join(d, fn)
        s_im.save(p, quality=98)

# 4. SAVE COMBINED PDF
pdf_targets = [
    r'C:\Users\DELL\Documents\Downloads\GIA_SƯ_2\TT\TIKTOK_SLIDES_KHI_LY_TUONG_MTSEducation.pdf',
    r'C:\Users\DELL\Documents\Downloads\TIKTOK_SLIDES_KHI_LY_TUONG_MTSEducation.pdf',
    r'C:\Users\DELL\Downloads\TIKTOK_SLIDES_KHI_LY_TUONG_MTSEducation.pdf',
    r'C:\Users\DELL\Documents\CODE\DU_AN\TIKTOK_SLIDES_KHI_LY_TUONG_MTSEducation.pdf'
]

print('Generating combined PDF...')
slide_images[0].save(pdf_targets[0], save_all=True, append_images=slide_images[1:], resolution=100.0)
for t in pdf_targets[1:]:
    shutil.copy2(pdf_targets[0], t)
    print(f'Saved PDF to: {t}')

print('ALL 23 SLIDES & PDFS GENERATED SUCCESSFULLY!')
"
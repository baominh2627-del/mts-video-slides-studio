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
print('--- Generating Slide 01 (Cover) ---')
orig_path = r'C:\Users\DELL\Documents\Downloads\GIA_SƯ_2\TT\TIKTOK_SLIDES_MTSEducation\slide_01.jpg'
orig_im = Image.open(orig_path)
cv_img = cv2.cvtColor(np.array(orig_im), cv2.COLOR_RGB2BGR)

# Mask only 'Vật Lí Nhiệt' (x=325..900, y=630..785)
roi = cv_img[630:785, 325:900]
dark = (np.mean(roi, axis=2) < 155).astype(np.uint8) * 255
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
dark_dil = cv2.dilate(dark, kernel, iterations=2)

mask = np.zeros(cv_img.shape[:2], dtype=np.uint8)
mask[630:785, 325:900] = dark_dil

# Halftone grain extraction & synthesis
clean_patch = cv_img[280:480, 250:850].astype(np.float32)
blur_patch = cv2.GaussianBlur(clean_patch, (21, 21), 5.0)
grain_patch = clean_patch - blur_patch

inp = cv2.inpaint(cv_img, mask, 7, cv2.INPAINT_TELEA)

roi_h, roi_w = dark_dil.shape
grain_tile = grain_patch[:roi_h, :roi_w]
mask_float = (dark_dil > 0).astype(np.float32)[:, :, np.newaxis]
inp_roi = inp[630:785, 325:900].astype(np.float32)
restored_roi = np.clip(inp_roi + grain_tile * mask_float, 0, 255).astype(np.uint8)
inp[630:785, 325:900] = restored_roi

slide01_pil = Image.fromarray(cv2.cvtColor(inp, cv2.COLOR_BGR2RGB))
draw01 = ImageDraw.Draw(slide01_pil)

font_cover_path = r'C:\Users\DELL\Documents\CODE\DU_AN\PlayfairDisplay.ttf'
f_cover = ImageFont.truetype(font_cover_path, 88)
f_cover.set_variation_by_axes([750])
draw01.text((345, 638), 'Khí Lý Tưởng', fill=(46, 28, 50), font=f_cover)

slide_images = [slide01_pil]
print('Slide 01 generated successfully.')

# 2. ENHANCE PAGE FUNCTION
def enhance_page(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]

    rgb_min = np.min(img, axis=2)
    bg_mask = ((v > 225) & (s < 35)) | (rgb_min > 230)
    black_mask = (v < 165) & (s < 60) & (~bg_mask)
    red_mask = ((h < 15) | (h > 165)) & (s > 40) & (v > 50)
    blue_mask = (h >= 95) & (h <= 135) & (s > 35) & (v > 45)

    res = img.copy()
    res[bg_mask] = [255, 255, 255]

    for c in range(3):
        ch = res[:, :, c].astype(np.float32)
        ch[black_mask] = np.clip(ch[black_mask] * 0.4, 0, 255)
        res[:, :, c] = ch.astype(np.uint8)

    red_target = np.array([20, 20, 205], dtype=np.float32)
    alpha_r = (s[red_mask] / 255.0)[:, np.newaxis]
    orig_r = res[red_mask].astype(np.float32)
    res[red_mask] = np.clip(orig_r * (1.0 - alpha_r * 0.75) + red_target * (alpha_r * 0.75), 0, 255).astype(np.uint8)

    blue_target = np.array([195, 95, 25], dtype=np.float32)
    alpha_b = (s[blue_mask] / 255.0)[:, np.newaxis]
    orig_b = res[blue_mask].astype(np.float32)
    res[blue_mask] = np.clip(orig_b * (1.0 - alpha_b * 0.75) + blue_target * (alpha_b * 0.75), 0, 255).astype(np.uint8)

    return res

# Typography for content slides
f_mts = ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf', 44)
f_title = ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf', 35)
f_footer = ImageFont.truetype(r'C:\Windows\Fonts\timesbi.ttf', 23)

raw_dir = r'c:\Users\DELL\Documents\CODE\DU_AN\khi_ly_tuong_raw'

# 3. GENERATE CONTENT SLIDES (SLIDES 02 TO 23)
print('--- Generating Content Slides (02 to 23) ---')
for p_num in range(1, 23):
    canvas = Image.new('RGB', (1080, 1440), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    raw_path = os.path.join(raw_dir, f'page_{p_num:02d}.jpeg')
    raw_cv = cv2.imread(raw_path)
    enh_cv = enhance_page(raw_cv)
    enh_pil = Image.fromarray(cv2.cvtColor(enh_cv, cv2.COLOR_BGR2RGB))
    cw, ch = enh_pil.size

    foot_y = 1380

    if p_num == 1:
        # Slide 02 Header Box
        box_x0, box_y0, box_x1, box_y1 = 65, 38, 1015, 110
        draw.rectangle([box_x0, box_y0, box_x1, box_y1], outline=(170, 170, 170), width=1)

        div_x = 180
        draw.line([(div_x, box_y0), (div_x, box_y1)], fill=(30, 115, 190), width=2)

        tb_mts = draw.textbbox((0, 0), 'MTS', font=f_mts)
        w_mts, h_mts = tb_mts[2] - tb_mts[0], tb_mts[3] - tb_mts[1]
        draw.text((box_x0 + (div_x - box_x0 - w_mts) // 2, box_y0 + (box_y1 - box_y0 - h_mts) // 2 - 3),
                  'MTS', fill=(30, 95, 205), font=f_mts)

        title = 'KHÍ LÝ TƯỞNG - NÂNG CAO'
        tb_t = draw.textbbox((0, 0), title, font=f_title)
        w_t, h_t = tb_t[2] - tb_t[0], tb_t[3] - tb_t[1]
        draw.text((div_x + (box_x1 - div_x - w_t) // 2, box_y0 + (box_y1 - box_y0 - h_t) // 2 - 3),
                  title, fill=(215, 15, 15), font=f_title)

        avail_w, avail_h = 970, 1235
        scale = min(avail_w / cw, avail_h / ch)
        nw, nh = int(cw * scale), int(ch * scale)
        scaled = enh_pil.resize((nw, nh), Image.Resampling.LANCZOS)
        cx = (1080 - nw) // 2
        cy = 130 + (avail_h - nh) // 2
        canvas.paste(scaled, (cx, cy))
    else:
        # Slides 03..23
        avail_w, avail_h = 970, 1315
        scale = min(avail_w / cw, avail_h / ch)
        nw, nh = int(cw * scale), int(ch * scale)
        scaled = enh_pil.resize((nw, nh), Image.Resampling.LANCZOS)
        cx = (1080 - nw) // 2
        if nh < 1150:
            cy = 65
        else:
            cy = 45 + (avail_h - nh) // 2
        canvas.paste(scaled, (cx, cy))

    # Crisp footer
    draw.line([(65, foot_y), (1015, foot_y)], fill=(190, 190, 190), width=1)
    draw.text((65, foot_y + 6), 'MTSEducation', fill=(30, 60, 180), font=f_footer)

    num_str = str(p_num)
    pb = draw.textbbox((0, 0), num_str, font=f_footer)
    pw = pb[2] - pb[0]
    draw.text((1015 - pw, foot_y + 6), num_str, fill=(20, 20, 20), font=f_footer)

    slide_images.append(canvas)
    print(f'Slide {p_num+1:02d} (Page {p_num:02d}) created.')

# 4. SAVE ALL SLIDES TO 3 TARGET DIRECTORIES
print(f'Saving {len(slide_images)} slides to directories...')
for idx, s_im in enumerate(slide_images):
    fn = f'slide_{idx+1:02d}.jpg'
    for d in [dir_giasu, dir_down, dir_proj]:
        p = os.path.join(d, fn)
        s_im.save(p, quality=98)

# 5. GENERATE AND OVERWRITE COMBINED PDF
pdf_targets = [
    r'C:\Users\DELL\Documents\Downloads\GIA_SƯ_2\TT\TIKTOK_SLIDES_KHI_LY_TUONG_MTSEducation.pdf',
    r'C:\Users\DELL\Documents\Downloads\TIKTOK_SLIDES_KHI_LY_TUONG_MTSEducation.pdf',
    r'C:\Users\DELL\Documents\CODE\DU_AN\TIKTOK_SLIDES_KHI_LY_TUONG_MTSEducation.pdf'
]

print('Generating combined PDF...')
slide_images[0].save(pdf_targets[0], save_all=True, append_images=slide_images[1:], resolution=100.0)
for t in pdf_targets[1:]:
    shutil.copy2(pdf_targets[0], t)
    print(f'Copied PDF to: {t}')

print('ALL DONE SUCCESSFULLY!')
"
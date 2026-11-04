# -*- coding: utf-8 -*-
"""
Video Generator: Phương trình Van der Waals cho khí thực (Bản Storytelling & Hình Ảnh Thực)
- Kể chuyện liền mạch, phong cách tài liệu khoa học trực quan
- 100% hình ảnh thực từ tư liệu khoa học & Wikimedia Commons:
  + Chân dung thật của Johannes D. van der Waals cắt nền (Presenter xuất hiện và dùng que chỉ)
  + Sơ đồ thực nghiệm hệ số nén Z (Compressibility Factor)
  + Sơ đồ lực hút Van der Waals giữa 2 nguyên tử phân cực
  + Đồ thị thế năng tương tác phân tử Lennard-Jones
  + Đồ thị thực nghiệm đẳng nhiệt CO2 của Thomas Andrews (với điểm tới hạn K 31.1°C)
  + Huy chương giải Nobel Vật lý 1910
- Nói đến phần nào que chỉ và vòng tiêu điểm sáng rực chỉ vào phần đó
- Watermark: MTSEducation (trên trái & dưới phải) + Outro đăng ký kênh
- Độ phân giải: 1024 x 576, 30 FPS, âm thanh đồng bộ
"""

import os
import sys
import json
import math
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

sys.stdout.reconfigure(encoding='utf-8')

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
BUILD_DIR = r"C:\Users\DELL\Documents\CODE\DU_AN\video_build"
REAL_DIR = r"C:\Users\DELL\Documents\CODE\DU_AN\real_assets"
OUTPUT_MP4 = r"C:\Users\DELL\Documents\CODE\DU_AN\PHUONG_TRINH_VAN_DER_WAALS_MTSEducation.mp4"
TIMELINE_JSON = os.path.join(BUILD_DIR, "timeline.json")
AUDIO_MASTER = os.path.join(BUILD_DIR, "audio_master_remix_mastered.wav")

WIDTH = 1024
HEIGHT = 576
CANVAS_WIDTH = 1920
CANVAS_HEIGHT = 1080
SCALE = CANVAS_WIDTH / WIDTH # 1.875
FPS = 30

# Load Fonts (Native 1080p scaled)
FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_REG = "C:/Windows/Fonts/segoeui.ttf"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, round(size * SCALE))
    except Exception:
        return ImageFont.load_default()

f_brand = get_font(FONT_BOLD, 22)
f_brand_sub = get_font(FONT_BOLD, 15)
f_badge = get_font(FONT_BOLD, 13)
f_header_title = get_font(FONT_BOLD, 20)
f_card_title = get_font(FONT_BOLD, 16)
f_body = get_font(FONT_REG, 14)
f_body_b = get_font(FONT_BOLD, 14)
f_body_sm = get_font(FONT_REG, 13)
f_body_sm_b = get_font(FONT_BOLD, 13)
f_math_xl = get_font(FONT_BOLD, 28)
f_math_lg = get_font(FONT_BOLD, 21)
f_math_md = get_font(FONT_BOLD, 17)
f_sub = get_font(FONT_BOLD, 22)

class ScaledDraw:
    def __init__(self, raw_draw, scale=SCALE):
        self.d = raw_draw
        self.s = scale

    def _sp(self, pt):
        return (round(pt[0] * self.s), round(pt[1] * self.s))

    def _sbox(self, box):
        return [round(c * self.s) for c in box]

    def text(self, xy, text, *args, **kwargs):
        return self.d.text(self._sp(xy), text, *args, **kwargs)

    def textbbox(self, xy, text, *args, **kwargs):
        bx = self.d.textbbox(self._sp(xy), text, *args, **kwargs)
        return tuple(c / self.s for c in bx)

    def rounded_rectangle(self, xy, radius=0, *args, **kwargs):
        if 'width' in kwargs:
            kwargs['width'] = max(1, round(kwargs['width'] * self.s))
        return self.d.rounded_rectangle(self._sbox(xy), radius=round(radius * self.s), *args, **kwargs)

    def rectangle(self, xy, *args, **kwargs):
        if 'width' in kwargs:
            kwargs['width'] = max(1, round(kwargs['width'] * self.s))
        return self.d.rectangle(self._sbox(xy), *args, **kwargs)

    def ellipse(self, xy, *args, **kwargs):
        if 'width' in kwargs:
            kwargs['width'] = max(1, round(kwargs['width'] * self.s))
        return self.d.ellipse(self._sbox(xy), *args, **kwargs)

    def line(self, xy, *args, **kwargs):
        if 'width' in kwargs:
            kwargs['width'] = max(1, round(kwargs['width'] * self.s))
        s_xy = [self._sp(p) for p in xy]
        return self.d.line(s_xy, *args, **kwargs)

class ScaledImage:
    def __init__(self, raw_img, scale=SCALE):
        self.raw_img = raw_img
        self.s = scale
        self.width = int(raw_img.width / scale)
        self.height = int(raw_img.height / scale)

    def paste(self, im, box=None, mask=None):
        if box is not None:
            if isinstance(box, tuple) or isinstance(box, list):
                if len(box) == 2:
                    s_box = (round(box[0] * self.s), round(box[1] * self.s))
                elif len(box) == 4:
                    s_box = [round(c * self.s) for c in box]
                else:
                    s_box = box
            else:
                s_box = box
        else:
            s_box = None
            
        target_w = max(1, round(im.width * self.s))
        target_h = max(1, round(im.height * self.s))
        im_s = im.resize((target_w, target_h), Image.Resampling.LANCZOS)
        
        mask_s = None
        if mask is not None:
            mask_s = mask.resize((target_w, target_h), Image.Resampling.LANCZOS)
            
        self.raw_img.paste(im_s, s_box, mask_s)

def create_canvas():
    raw_img = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), BG_DARK)
    s_img = ScaledImage(raw_img, SCALE)
    s_draw = ScaledDraw(ImageDraw.Draw(raw_img), SCALE)
    return raw_img, s_img, s_draw

# Colors
BG_DARK = (13, 17, 28)
CARD_BG = (20, 27, 42)
CARD_BORDER = (45, 58, 85)
CYAN_ACCENT = (56, 189, 248)
GREEN_ACCENT = (74, 222, 128)
RED_ACCENT = (248, 113, 113)
GOLD_ACCENT = (250, 204, 21)
AMBER_ACCENT = (251, 146, 60)
PURPLE_ACCENT = (192, 132, 252)

# Load real assets
vdw_cutout = Image.open(os.path.join(REAL_DIR, "vdw_presenter_crisp.png")).convert("RGBA")
img_andrews = Image.open(os.path.join(REAL_DIR, "Carbon_dioxide_isotherms.png")).convert("RGB")
img_lj = Image.open(os.path.join(REAL_DIR, "Graph_of_Lennard-Jones_potential.png")).convert("RGB")
img_vdw_force = Image.open(os.path.join(REAL_DIR, "Force_de_van_de_Waals.png")).convert("RGB")
img_z = Image.open(os.path.join(REAL_DIR, "Compressibility_factor.jpg")).convert("RGB")
img_nobel = Image.open(os.path.join(REAL_DIR, "nobel_thumb.jpg")).convert("RGB")

with open(TIMELINE_JSON, "r", encoding="utf-8") as f:
    timeline_data = json.load(f)

TOTAL_DURATION = timeline_data["total_duration"]
TOTAL_FRAMES = int(TOTAL_DURATION * FPS)
CLIPS = timeline_data["timeline"]

def get_current_subtitle(t):
    for c in CLIPS:
        if c["start"] <= t <= c["end"]:
            return c["text"]
    return ""

def draw_header_watermark(draw, scene_badge, title_text="PHƯƠNG TRÌNH VAN DER WAALS"):
    # Brand Top-Left (MTSEducation)
    draw.text((32, 22), "MTSEducation", font=f_brand, fill=(0, 0, 0))
    draw.text((30, 20), "MTSEducation", font=f_brand, fill=(255, 255, 255))
    
    # Secondary watermark bottom right
    draw.text((WIDTH - 120, HEIGHT - 25), "MTSEducation", font=f_brand_sub, fill=(130, 145, 170))
    
    # Header Center Badge
    badge_w = 460
    badge_x = (WIDTH - badge_w) // 2
    draw.rounded_rectangle([badge_x - 1, 12, badge_x + badge_w + 1, 52], radius=10, fill=(180, 30, 30))
    draw.rounded_rectangle([badge_x, 13, badge_x + badge_w, 51], radius=9, fill=(220, 38, 38))
    
    bbox_t = draw.textbbox((0, 0), title_text, font=f_header_title)
    tw = bbox_t[2] - bbox_t[0]
    draw.text((badge_x + (badge_w - tw) // 2, 20), title_text, font=f_header_title, fill=(255, 255, 255))
    
    # Scene sub-badge
    if scene_badge:
        bbox_sb = draw.textbbox((0, 0), scene_badge, font=f_badge)
        sb_w = bbox_sb[2] - bbox_sb[0] + 16
        draw.rounded_rectangle([30, 52, 30 + sb_w, 74], radius=5, fill=(30, 41, 59), outline=(71, 85, 105), width=1)
        draw.text((38, 55), scene_badge, font=f_badge, fill=CYAN_ACCENT)

def draw_subtitle(draw, text):
    if not text:
        return
    text = text.upper()
    max_w = WIDTH - 60
    lines = [text]
    bbox = draw.textbbox((0, 0), text, font=f_sub)
    if (bbox[2] - bbox[0]) > max_w:
        words = text.split()
        mid = len(words) // 2
        lines = [" ".join(words[:mid]), " ".join(words[mid:])]
        
    line_h = 28
    total_h = len(lines) * line_h
    start_y = HEIGHT - 55 - (total_h - line_h)
    
    for l_idx, line in enumerate(lines):
        l_bbox = draw.textbbox((0, 0), line, font=f_sub)
        lw = l_bbox[2] - l_bbox[0]
        x = (WIDTH - lw) // 2
        y = start_y + l_idx * line_h
        
        draw.rounded_rectangle([x - 14, y - 4, x + lw + 14, y + line_h - 2], radius=6, fill=(10, 10, 15))
        for ox in [-2, -1, 0, 1, 2]:
            for oy in [-2, -1, 0, 1, 2]:
                if ox != 0 or oy != 0:
                    draw.text((x + ox, y + oy), line, font=f_sub, fill=(0, 0, 0))
        draw.text((x, y), line, font=f_sub, fill=(255, 235, 50))

def draw_van_der_waals_presenter(img, draw, target_point=None, scale=0.33, pos=(720, 200), name_label=True):
    """
    Renders the real Van der Waals cutout and draws an elegant golden pointer wand
    held in his hand pointing towards target_point (tx, ty), plus a laser spotlight
    focus ring on the target without drawing long lines across other text/images.
    """
    pw = int(vdw_cutout.width * scale)
    ph = int(vdw_cutout.height * scale)
    vdw_scaled = vdw_cutout.resize((pw, ph), Image.Resampling.LANCZOS)
    
    hx = pos[0] + int(pw * 0.28)
    hy = pos[1] + int(ph * 0.58)
    
    if target_point:
        tx, ty = target_point
        angle = math.atan2(ty - hy, tx - hx)
        dist = math.hypot(tx - hx, ty - hy)
        # Realistic wand length (max 85px) - never cuts across other cards or text!
        wand_len = min(85, max(40, dist * 0.6))
        wx = hx + wand_len * math.cos(angle)
        wy = hy + wand_len * math.sin(angle)
        
        # Golden pointer wand held in hand
        draw.line([(hx, hy), (wx, wy)], fill=GOLD_ACCENT, width=4)
        draw.ellipse([wx - 3, wy - 3, wx + 3, wy + 3], fill=(255, 255, 255), outline=GOLD_ACCENT, width=1)
        
        # Target Laser Spotlight (clean, non-intrusive, highlights term without obscuring)
        draw.ellipse([tx - 6, ty - 6, tx + 6, ty + 6], fill=(255, 255, 255), outline=RED_ACCENT, width=2)
        draw.ellipse([tx - 13, ty - 13, tx + 13, ty + 13], outline=RED_ACCENT, width=2)

    # Paste presenter onto image
    img.paste(vdw_scaled, pos, vdw_scaled)
    
    if name_label:
        draw.rounded_rectangle([pos[0] + 15, pos[1] + ph - 22, pos[0] + pw - 15, pos[1] + ph + 4], radius=5, fill=(15, 23, 42), outline=GOLD_ACCENT, width=1)
        draw.text((pos[0] + 30, pos[1] + ph - 19), "J. D. van der Waals", font=f_body_sm_b, fill=(255, 255, 255))

# ==================== SCENE 1 (INTRO ĐỔI MỚI) ====================
def render_frame_scene1(t, sub_text):
    raw_img, img, draw = create_canvas()
    
    if t < 25.0:
        # Phase 1 & 2: Giới thiệu Phương trình khí lý tưởng PV = nRT & 2 Giả định kinh điển
        draw_header_watermark(draw, "PHẦN 1: MÔ HÌNH KHÍ LÝ TƯỞNG")
        
        # Left Card: Ideal Gas Equation
        draw.rounded_rectangle([45, 90, 500, 485], radius=14, fill=CARD_BG, outline=CYAN_ACCENT, width=2)
        draw.rounded_rectangle([65, 105, 480, 140], radius=8, fill=(18, 40, 65))
        draw.text((100, 112), "PHƯƠNG TRÌNH KHÍ LÝ TƯỞNG", font=f_card_title, fill=CYAN_ACCENT)
        
        # Giant Equation Box
        draw.rounded_rectangle([65, 165, 480, 265], radius=12, fill=(15, 23, 42), outline=CYAN_ACCENT, width=2)
        draw.text((120, 195), "P · V  =  n · R · T", font=f_math_xl, fill=(255, 255, 255))
        
        # Breakdown labels
        draw.rounded_rectangle([75, 290, 260, 325], radius=6, fill=(20, 35, 55), outline=(50, 75, 110), width=1)
        draw.text((90, 298), "P : Áp suất khối khí", font=f_body_sm, fill=(220, 235, 255))
        
        draw.rounded_rectangle([285, 290, 470, 325], radius=6, fill=(20, 35, 55), outline=(50, 75, 110), width=1)
        draw.text((300, 298), "V : Thể tích bình chứa", font=f_body_sm, fill=(220, 235, 255))
        
        draw.rounded_rectangle([75, 345, 260, 380], radius=6, fill=(20, 35, 55), outline=(50, 75, 110), width=1)
        draw.text((90, 353), "n : Số mol khí", font=f_body_sm, fill=(220, 235, 255))
        
        draw.rounded_rectangle([285, 345, 470, 380], radius=6, fill=(20, 35, 55), outline=(50, 75, 110), width=1)
        draw.text((300, 353), "T : Nhiệt độ Kelvin (K)", font=f_body_sm, fill=(220, 235, 255))
        
        draw.text((70, 430), "• Mô hình đơn giản, kinh điển trong sách giáo khoa.", font=f_body, fill=(200, 215, 235))
        draw.text((70, 458), "• Nhưng được xây dựng trên 2 giả định hoàn hảo!", font=f_body_b, fill=GOLD_ACCENT)
        
        # Right Card: The 2 Perfect Assumptions
        draw.rounded_rectangle([525, 90, 975, 485], radius=14, fill=CARD_BG, outline=AMBER_ACCENT, width=2)
        draw.rounded_rectangle([545, 105, 955, 140], radius=8, fill=(50, 35, 15))
        draw.text((585, 112), "2 GIẢ ĐỊNH CỦA KHÍ LÝ TƯỞNG", font=f_card_title, fill=AMBER_ACCENT)
        
        # Assumption 1 Box (lights up if 14.0 <= t < 20.0)
        a1_active = (14.0 <= t < 20.0)
        a1_outline = CYAN_ACCENT if a1_active else (60, 75, 100)
        a1_bg = (20, 40, 65) if a1_active else (15, 20, 32)
        draw.rounded_rectangle([545, 160, 955, 275], radius=10, fill=a1_bg, outline=a1_outline, width=2 if a1_active else 1)
        draw.text((565, 175), "GIẢ ĐỊNH 1: PHÂN TỬ LÀ CHẤT ĐIỂM", font=f_body_b, fill=CYAN_ACCENT if a1_active else (220, 230, 245))
        draw.text((565, 205), "• Coi các phân tử chỉ là các điểm hình học.", font=f_body_sm, fill=(200, 215, 235))
        draw.text((565, 235), "-> Thể tích bản thân phân tử = 0 (V_hạt = 0)", font=f_body_sm_b, fill=GREEN_ACCENT)
        if a1_active:
            draw.ellipse([920, 175, 940, 195], fill=RED_ACCENT)
            
        # Assumption 2 Box (lights up if t >= 20.0)
        a2_active = (t >= 20.0)
        a2_outline = AMBER_ACCENT if a2_active else (60, 75, 100)
        a2_bg = (50, 30, 15) if a2_active else (15, 20, 32)
        draw.rounded_rectangle([545, 295, 955, 410], radius=10, fill=a2_bg, outline=a2_outline, width=2 if a2_active else 1)
        draw.text((565, 310), "GIẢ ĐỊNH 2: KHÔNG LỰC TƯƠNG TÁC", font=f_body_b, fill=AMBER_ACCENT if a2_active else (220, 230, 245))
        draw.text((565, 340), "• Không có bất kỳ lực hút hay đẩy nào giữa các hạt.", font=f_body_sm, fill=(200, 215, 235))
        draw.text((565, 370), "-> Chỉ va chạm đàn hồi tuyệt đối (F_hút = 0)", font=f_body_sm_b, fill=GOLD_ACCENT)
        if a2_active:
            draw.ellipse([920, 310, 940, 330], fill=RED_ACCENT)
            
        draw.text((550, 440), "[!] Cả 2 giả định này đều KHÔNG CÓ THẬT trong tự nhiên!", font=f_body_sm_b, fill=RED_ACCENT)
        
    else:
        # Phase 3: Khí thực sai lệch & Đồ thị thực Z & Nhà vật lý Van der Waals vào cuộc (t >= 25.0s)
        draw_header_watermark(draw, "PHẦN 1: NGHỊCH LÝ KHÍ THỰC")
        
        # Left Card: Real Scientific Diagram (Compressibility Factor Z)
        draw.rounded_rectangle([45, 90, 520, 485], radius=14, fill=CARD_BG, outline=CARD_BORDER, width=2)
        draw.rounded_rectangle([65, 105, 500, 140], radius=8, fill=(18, 40, 65))
        draw.text((105, 112), "SỰ SAI LỆCH CỦA KHÍ THỰC (HỆ SỐ Z)", font=f_card_title, fill=CYAN_ACCENT)
        
        # Paste Real Diagram: Compressibility_factor
        z_w, z_h = 210, 310
        z_scaled = img_z.resize((z_w, z_h), Image.Resampling.LANCZOS)
        draw.rounded_rectangle([65, 155, 65 + z_w + 4, 155 + z_h + 4], radius=8, fill=(255, 255, 255), outline=CYAN_ACCENT, width=2)
        img.paste(z_scaled, (67, 157))
        
        # Bullet points next to real image
        draw.text((295, 175), "• Khí lý tưởng: Z = 1", font=f_body_b, fill=GREEN_ACCENT)
        draw.text((295, 200), "  (Không kích thước, không lực hút)", font=f_body_sm, fill=(200, 215, 235))
        
        draw.text((295, 255), "• Áp suất vừa: Z < 1", font=f_body_b, fill=RED_ACCENT)
        draw.text((295, 280), "  -> Lực hút chiếm ưu thế", font=f_body_sm, fill=(240, 180, 180))
        
        draw.text((295, 345), "• Áp suất cao: Z > 1", font=f_body_b, fill=AMBER_ACCENT)
        draw.text((295, 370), "  -> Thể tích phân tử cản trở", font=f_body_sm, fill=(255, 220, 180))
        
        draw.text((70, 465), "[!] Định luật PV = nRT thất bại khi áp suất tăng cao!", font=f_body_sm_b, fill=GOLD_ACCENT)
        
        # Right Card: Van der Waals steps into the story!
        draw.rounded_rectangle([545, 90, 975, 485], radius=14, fill=CARD_BG, outline=GOLD_ACCENT, width=2)
        draw.rounded_rectangle([565, 105, 955, 140], radius=8, fill=(50, 35, 15))
        draw.text((610, 112), "NHÀ VẬT LÝ VÀO CUỘC (NĂM 1873)", font=f_card_title, fill=GOLD_ACCENT)
        
        draw.text((565, 155), "Johannes Diderik van der Waals phát hiện:", font=f_body, fill=(220, 230, 245))
        draw.text((565, 185), "1. Phân tử có kích thước thật -> Cần trừ b", font=f_body_b, fill=GREEN_ACCENT)
        draw.text((565, 215), "2. Giữa các hạt có lực hút -> Cần bù áp suất a", font=f_body_b, fill=AMBER_ACCENT)
        
        # Presenter with clean wand pointing to the breakthroughs without crossing text
        target = (560, 185)
        draw_van_der_waals_presenter(img, draw, target_point=target, scale=0.34, pos=(690, 245))
        
    draw_subtitle(draw, sub_text)
    return raw_img

# ==================== SCENE 2 ====================
def render_frame_scene2(t, sub_text):
    raw_img, img, draw = create_canvas()
    draw_header_watermark(draw, "PHẦN 2: THỂ TÍCH RIÊNG (b)")
    
    # Left Card: Physical Molecular Exclusion (Exclusion Sphere 2r)
    draw.rounded_rectangle([45, 90, 520, 485], radius=14, fill=CARD_BG, outline=CARD_BORDER, width=2)
    draw.rounded_rectangle([65, 105, 500, 140], radius=8, fill=(18, 40, 65))
    draw.text((95, 112), "BẢN CHẤT THỂ TÍCH LOẠI TRỪ (EXCLUDED VOLUME)", font=f_card_title, fill=CYAN_ACCENT)
    
    # Molecular sphere schematic
    draw.rounded_rectangle([65, 155, 500, 350], radius=10, fill=(10, 15, 25), outline=(40, 60, 90), width=1)
    
    c1x, c1y = 200, 250
    r = 28
    # Exclusion sphere radius 2r = 56
    draw.ellipse([c1x - 2*r, c1y - 2*r, c1x + 2*r, c1y + 2*r], fill=(25, 65, 45), outline=GREEN_ACCENT, width=2)
    draw.ellipse([c1x - r, c1y - r, c1x + r, c1y + r], fill=(40, 130, 200), outline=(200, 230, 255), width=2)
    draw.text((c1x - 14, c1y - 10), "Hạt 1", font=f_body_sm_b, fill=(255, 255, 255))
    
    # Approaching second sphere
    ang = t * 1.5
    c2x = int(c1x + 2 * r * math.cos(ang))
    c2y = int(c1y + 2 * r * math.sin(ang))
    draw.ellipse([c2x - r, c2y - r, c2x + r, c2y + r], fill=(220, 80, 50), outline=(255, 200, 180), width=2)
    draw.text((c2x - 14, c2y - 10), "Hạt 2", font=f_body_sm_b, fill=(255, 255, 255))
    draw.line([(c1x, c1y), (c2x, c2y)], fill=GOLD_ACCENT, width=2)
    
    draw.text((320, 175), "• Bán kính loại trừ: 2r", font=f_body_sm_b, fill=GOLD_ACCENT)
    draw.text((320, 210), "• V_cặp = (4/3)pi(2r)³ = 8·v0", font=f_body_sm_b, fill=GREEN_ACCENT)
    draw.text((320, 245), "• Bình quân 1 hạt: 4·v0", font=f_body_sm, fill=(210, 225, 240))
    draw.text((320, 280), "• 1 mol hạt: b = 4·NA·v0", font=f_body_sm_b, fill=CYAN_ACCENT)
    
    draw.text((70, 375), "• Phân tử không phải chất điểm, mà có thể tích riêng b.", font=f_body, fill=(220, 230, 245))
    draw.text((70, 405), "• Khi nén chặt, các phân tử cản trở lẫn nhau chuyển động.", font=f_body, fill=(220, 230, 245))
    draw.text((70, 435), "-> Không gian tự do thực tế bị co cụm lại: (V - n·b)", font=f_body_b, fill=GREEN_ACCENT)
    
    # Right Card: Formula & Van der Waals Presenter Pointing!
    draw.rounded_rectangle([545, 90, 975, 485], radius=14, fill=CARD_BG, outline=GREEN_ACCENT, width=2)
    draw.rounded_rectangle([565, 105, 955, 140], radius=8, fill=(20, 55, 35))
    draw.text((630, 112), "HIỆU CHỈNH THỂ TÍCH TỰ DO", font=f_card_title, fill=GREEN_ACCENT)
    
    # Glowing Formula Box
    draw.rounded_rectangle([565, 160, 955, 240], radius=12, fill=(12, 45, 30), outline=GREEN_ACCENT, width=2)
    draw.text((615, 185), "V_tự do  =  V  -  n · b", font=f_math_xl, fill=GREEN_ACCENT)
    
    draw.text((565, 260), "Thay vào phương trình khí lý tưởng:", font=f_body, fill=(200, 215, 235))
    draw.rounded_rectangle([565, 290, 955, 345], radius=10, fill=(18, 30, 48), outline=(60, 80, 110), width=1)
    draw.text((615, 305), "P · ( V  -  n · b )  =  n · R · T", font=f_math_lg, fill=GOLD_ACCENT)
    
    # Van der Waals pointer pointing to the V - nb formula!
    target = (780, 200) if t > 50.0 else (420, 230)
    draw_van_der_waals_presenter(img, draw, target_point=target, scale=0.33, pos=(710, 310))
    
    draw_subtitle(draw, sub_text)
    return raw_img

# ==================== SCENE 3 ====================
def render_frame_scene3(t, sub_text):
    raw_img, img, draw = create_canvas()
    draw_header_watermark(draw, "PHẦN 3: LỰC TƯƠNG TÁC (a)")
    
    # Left Card: Real Intermolecular Forces (Dipole Induction & Lennard-Jones)
    draw.rounded_rectangle([45, 90, 530, 485], radius=14, fill=CARD_BG, outline=CARD_BORDER, width=2)
    draw.rounded_rectangle([65, 105, 510, 140], radius=8, fill=(45, 30, 60))
    draw.text((105, 112), "HÌNH ẢNH THỰC: LỰC HÚT VAN DER WAALS", font=f_card_title, fill=PURPLE_ACCENT)
    
    # Top real image: Force_de_van_de_Waals (180h)
    fw, fh = 260, 140
    f_scaled = img_vdw_force.resize((fw, fh), Image.Resampling.LANCZOS)
    draw.rounded_rectangle([65, 155, 65 + fw + 4, 155 + fh + 4], radius=8, fill=(255, 255, 255), outline=PURPLE_ACCENT, width=1)
    img.paste(f_scaled, (67, 157))
    
    draw.text((345, 165), "Lực Van der Waals:", font=f_body_b, fill=AMBER_ACCENT)
    draw.text((345, 195), "• Lưỡng cực cảm ứng", font=f_body_sm, fill=(220, 230, 245))
    draw.text((345, 225), "• Hút các hạt về nhau", font=f_body_sm, fill=(220, 230, 245))
    draw.text((345, 255), "• Tỷ lệ với 1 / r⁶", font=f_body_sm_b, fill=CYAN_ACCENT)
    
    # Bottom real image: Lennard-Jones potential graph
    ljw, ljh = 240, 140
    lj_scaled = img_lj.resize((ljw, ljh), Image.Resampling.LANCZOS)
    draw.rounded_rectangle([65, 315, 65 + ljw + 4, 315 + ljh + 4], radius=8, fill=(255, 255, 255), outline=CYAN_ACCENT, width=1)
    img.paste(lj_scaled, (67, 317))
    
    draw.text((320, 325), "Đồ thị thế năng LJ:", font=f_body_b, fill=CYAN_ACCENT)
    draw.text((320, 355), "• Vực thế sâu: Hút (-eps)", font=f_body_sm, fill=(200, 220, 240))
    draw.text((320, 385), "• Thành dựng: Đẩy lõi (b)", font=f_body_sm, fill=(240, 180, 180))
    draw.text((320, 415), "-> Cơ sở cho hằng số a & b", font=f_body_sm_b, fill=GOLD_ACCENT)
    
    draw.text((70, 465), "[!] Khi va chạm thành bình, phân tử bị kéo giật lùi -> Giảm áp suất!", font=f_body_sm_b, fill=RED_ACCENT)
    
    # Right Card: Pressure Deficit Formula & Presenter
    draw.rounded_rectangle([555, 90, 975, 485], radius=14, fill=CARD_BG, outline=AMBER_ACCENT, width=2)
    draw.rounded_rectangle([575, 105, 955, 140], radius=8, fill=(60, 35, 15))
    draw.text((645, 112), "HIỆU CHỈNH ÁP SUẤT NỘI", font=f_card_title, fill=AMBER_ACCENT)
    
    # Internal Pressure Box
    draw.rounded_rectangle([575, 155, 955, 240], radius=12, fill=(45, 25, 10), outline=AMBER_ACCENT, width=2)
    draw.text((615, 172), "Áp suất nội:   Pi  =  a · n² / V²", font=f_math_lg, fill=AMBER_ACCENT)
    draw.text((605, 208), "(a: Hằng số đo độ mạnh lực hút liên phân tử)", font=f_body_sm, fill=(220, 190, 160))
    
    draw.rounded_rectangle([575, 260, 955, 325], radius=10, fill=(18, 30, 48), outline=(60, 80, 110), width=1)
    draw.text((605, 280), "P_lý tưởng  =  P  +  ( a · n² / V² )", font=f_math_lg, fill=GREEN_ACCENT)
    
    # Van der Waals pointer pointing cleanly to the attraction force diagram or formula
    target = (775, 175) if t > 95.0 else (280, 195)
    draw_van_der_waals_presenter(img, draw, target_point=target, scale=0.33, pos=(710, 290))
    
    draw_subtitle(draw, sub_text)
    return raw_img

# ==================== SCENE 4 ====================
def render_frame_scene4(t, sub_text):
    raw_img, img, draw = create_canvas()
    draw_header_watermark(draw, "PHẦN 4: PHƯƠNG TRÌNH KINH ĐIỂN")
    
    # Top Card: Master Equation
    draw.rounded_rectangle([45, 88, 720, 230], radius=14, fill=CARD_BG, outline=GOLD_ACCENT, width=2)
    draw.rounded_rectangle([65, 98, 700, 126], radius=6, fill=(50, 40, 10))
    draw.text((220, 102), "PHƯƠNG TRÌNH TRẠNG THÁI VAN DER WAALS", font=f_badge, fill=GOLD_ACCENT)
    
    # Master Equation
    eq_y = 138
    draw.text((65, eq_y), "(  P  +  ", font=f_math_xl, fill=(255, 255, 255))
    draw.text((155, eq_y), "a·n² / V²", font=f_math_xl, fill=AMBER_ACCENT)
    draw.text((290, eq_y), "  ) · (  V  -  ", font=f_math_xl, fill=(255, 255, 255))
    draw.text((435, eq_y), "n·b", font=f_math_xl, fill=GREEN_ACCENT)
    draw.text((505, eq_y), "  )  =  n·R·T", font=f_math_xl, fill=(255, 255, 255))
    
    # 3 Badges below
    draw.rounded_rectangle([80, 185, 280, 215], radius=6, fill=(50, 30, 15), outline=AMBER_ACCENT, width=1)
    draw.text((95, 192), "Áp suất hiệu chỉnh", font=f_body_sm_b, fill=AMBER_ACCENT)
    
    draw.rounded_rectangle([300, 185, 480, 215], radius=6, fill=(15, 45, 25), outline=GREEN_ACCENT, width=1)
    draw.text((315, 192), "Thể tích tự do", font=f_body_sm_b, fill=GREEN_ACCENT)
    
    draw.rounded_rectangle([500, 185, 690, 215], radius=6, fill=(15, 35, 55), outline=CYAN_ACCENT, width=1)
    draw.text((520, 192), "Nhiệt động học (nRT)", font=f_body_sm_b, fill=CYAN_ACCENT)
    
    # Right mini card with Van der Waals presenter
    draw.rounded_rectangle([735, 88, 975, 485], radius=14, fill=CARD_BG, outline=CARD_BORDER, width=2)
    draw.rounded_rectangle([750, 98, 960, 126], radius=6, fill=(25, 40, 60))
    draw.text((790, 102), "DIỄN GIẢI THÔNG SỐ", font=f_badge, fill=CYAN_ACCENT)
    
    # Bottom Card: Data Table
    draw.rounded_rectangle([45, 242, 720, 485], radius=14, fill=CARD_BG, outline=CARD_BORDER, width=2)
    draw.rounded_rectangle([65, 252, 700, 280], radius=6, fill=(20, 30, 50))
    draw.text((180, 256), "BẢNG HẰNG SỐ a & b CỦA MỘT SỐ KHÍ THỰC TẾ", font=f_card_title, fill=CYAN_ACCENT)
    
    # Headers
    draw.text((65, 290), "Chất khí", font=f_body_b, fill=GOLD_ACCENT)
    draw.text((185, 290), "a (L²·bar/mol²)", font=f_body_b, fill=GOLD_ACCENT)
    draw.text((320, 290), "b (L/mol)", font=f_body_b, fill=GOLD_ACCENT)
    draw.text((430, 290), "Ý nghĩa thực nghiệm", font=f_body_b, fill=GOLD_ACCENT)
    draw.line([(65, 312), (700, 312)], fill=(50, 65, 90), width=1)
    
    rows = [
        ("Helium (He)", "0.034", "0.0237", "Siêu nhỏ, gần lý tưởng nhất", GREEN_ACCENT),
        ("Hydro (H2)", "0.244", "0.0266", "Rất nhẹ, thể tích riêng nhỏ", CYAN_ACCENT),
        ("Oxy (O2)", "1.360", "0.0318", "Khí khí quyển, lực hút trung bình", (220, 230, 240)),
        ("Cacbonic (CO2)", "3.590", "0.0427", "Phân tử lớn, lực hút mạnh", AMBER_ACCENT),
        ("Hơi nước (H2O)", "5.460", "0.0305", "Liên kết hydro -> a cực lớn!", RED_ACCENT),
    ]
    
    ry = 325
    for r_gas, r_a, r_b, r_desc, r_col in rows:
        # Highlight pulse if active
        if ("Helium" in r_gas and 135.0 <= t <= 145.0) or ("CO2" in r_gas and t > 145.0) or ("H2O" in r_gas and t > 145.0):
            draw.rounded_rectangle([60, ry - 3, 705, ry + 25], radius=5, fill=(40, 50, 70), outline=GOLD_ACCENT, width=1)
            
        draw.text((65, ry), r_gas, font=f_body_b, fill=r_col)
        draw.text((215, ry), r_a, font=f_body, fill=(255, 255, 255))
        draw.text((345, ry), r_b, font=f_body, fill=(255, 255, 255))
        draw.text((430, ry), r_desc, font=f_body_sm, fill=(210, 225, 245))
        ry += 30
        draw.line([(65, ry - 3), (700, ry - 3)], fill=(30, 42, 60), width=1)
        
    # Target for pointer: point at Helium row or CO2/H2O
    target = (350, 450) if t > 145.0 else (350, 335)
    draw_van_der_waals_presenter(img, draw, target_point=target, scale=0.34, pos=(745, 150))
    
    draw_subtitle(draw, sub_text)
    return raw_img

# ==================== SCENE 5 ====================
def render_frame_scene5(t, sub_text):
    raw_img, img, draw = create_canvas()
    draw_header_watermark(draw, "PHẦN 5: ĐẲNG NHIỆT & TỚI HẠN")
    
    # Left Card: REAL Thomas Andrews CO2 Experimental Isotherms Image!
    draw.rounded_rectangle([45, 90, 530, 485], radius=14, fill=CARD_BG, outline=CARD_BORDER, width=2)
    draw.rounded_rectangle([65, 105, 510, 140], radius=8, fill=(18, 40, 65))
    draw.text((85, 112), "HÌNH ẢNH THỰC: ĐẲNG NHIỆT ANDREWS (CO2)", font=f_card_title, fill=CYAN_ACCENT)
    
    # Paste Real Andrews Diagram: Carbon_dioxide_isotherms.png
    aw, ah = 310, 310
    a_scaled = img_andrews.resize((aw, ah), Image.Resampling.LANCZOS)
    draw.rounded_rectangle([65, 155, 65 + aw + 4, 155 + ah + 4], radius=8, fill=(255, 255, 255), outline=GOLD_ACCENT, width=2)
    img.paste(a_scaled, (67, 157))
    
    # Annotations next to Andrews graph
    draw.text((395, 175), "• T > Tc:", font=f_body_b, fill=CYAN_ACCENT)
    draw.text((395, 195), "  Chỉ là thể khí", font=f_body_sm, fill=(200, 215, 235))
    
    draw.text((395, 240), "• Điểm tới hạn K:", font=f_body_b, fill=RED_ACCENT)
    draw.text((395, 260), "  Tc = 31.1 °C", font=f_body_sm_b, fill=GOLD_ACCENT)
    draw.text((395, 280), "  Pc = 7.38 MPa", font=f_body_sm_b, fill=GOLD_ACCENT)
    
    draw.text((395, 330), "• T < Tc:", font=f_body_b, fill=AMBER_ACCENT)
    draw.text((395, 350), "  Vùng nằm ngang:", font=f_body_sm, fill=(240, 200, 180))
    draw.text((395, 370), "  Hóa lỏng bão hòa", font=f_body_sm_b, fill=AMBER_ACCENT)
    
    draw.text((70, 465), "Thông số tới hạn:  Vc = 3b  |  Pc = a / (27b²)  |  Tc = 8a / (27Rb)", font=f_body_sm_b, fill=GOLD_ACCENT)
    
    # Right Card: Nobel Prize & Van der Waals Presenter / Outro
    draw.rounded_rectangle([550, 90, 975, 485], radius=14, fill=CARD_BG, outline=GOLD_ACCENT, width=2)
    
    if t > 182.0:
        # Final Outro Card
        draw.rounded_rectangle([570, 105, 955, 140], radius=8, fill=(70, 20, 20))
        draw.text((640, 112), "CẢM ƠN CÁC BẠN ĐÃ THEO DÕI!", font=f_card_title, fill=(255, 255, 255))
        
        draw.rounded_rectangle([595, 165, 930, 310], radius=16, fill=(15, 23, 42), outline=CYAN_ACCENT, width=2)
        draw.text((670, 195), "MTSEducation", font=f_math_xl, fill=(255, 255, 255))
        draw.text((645, 250), "Học Khoa Học & Vật Lý Trực Quan", font=f_body_b, fill=CYAN_ACCENT)
        
        draw.rounded_rectangle([620, 335, 905, 395], radius=10, fill=(220, 38, 38))
        draw.text((650, 352), "[!] LIKE & ĐĂNG KÝ KÊNH", font=f_math_md, fill=(255, 255, 255))
        
        draw.text((605, 430), "Chúc các bạn học tập tốt và thành công!", font=f_body, fill=(200, 215, 235))
    else:
        # Nobel 1910 Presentation
        draw.rounded_rectangle([570, 105, 955, 140], radius=8, fill=(50, 40, 15))
        draw.text((615, 112), "[NOBEL VẬT LÝ NĂM 1910]", font=f_card_title, fill=GOLD_ACCENT)
        
        # Real Nobel medal thumb
        nw, nh = 135, 135
        n_scaled = img_nobel.resize((nw, nh), Image.Resampling.LANCZOS)
        draw.rounded_rectangle([580, 155, 580 + nw + 4, 155 + nh + 4], radius=8, fill=(30, 40, 60), outline=GOLD_ACCENT, width=2)
        img.paste(n_scaled, (582, 157))
        
        draw.text((735, 165), "Giải Nobel Vật lý:", font=f_body_b, fill=GOLD_ACCENT)
        draw.text((735, 195), "• Trao tặng năm 1910", font=f_body_sm, fill=(220, 230, 245))
        draw.text((735, 225), "• Cho công trình khí & lỏng", font=f_body_sm, fill=(220, 230, 245))
        draw.text((735, 255), "• Cơ sở hóa lỏng Helium", font=f_body_sm_b, fill=CYAN_ACCENT)
        
        # Pointer pointing to Critical Point K on Andrews diagram (x=195, y=325) or Nobel medal
        target = (650, 220) if t > 175.0 else (195, 325)
        draw_van_der_waals_presenter(img, draw, target_point=target, scale=0.33, pos=(710, 290))
        
    draw_subtitle(draw, sub_text)
    return raw_img

def render_frame(frame_idx):
    t = frame_idx / FPS
    sub = get_current_subtitle(t)
    
    if t < 31.74:
        return render_frame_scene1(t, sub)
    elif t < 69.98:
        return render_frame_scene2(t, sub)
    elif t < 115.28:
        return render_frame_scene3(t, sub)
    elif t < 157.18:
        return render_frame_scene4(t, sub)
    else:
        return render_frame_scene5(t, sub)

def main():
    print("=" * 50)
    print("STARTING STORYTELLING VIDEO RENDER WITH REAL ASSETS & VAN DER WAALS PRESENTER (1080p FULL HD)")
    print(f"Total Duration: {TOTAL_DURATION:.2f}s | FPS: {FPS} | Frames: {TOTAL_FRAMES} | Resolution: {CANVAS_WIDTH}x{CANVAS_HEIGHT}")
    print(f"Output: {OUTPUT_MP4}")
    print("=" * 50)
    
    temp_video = os.path.join(BUILD_DIR, "story_stream_1080p.mp4")
    
    cmd = [
        FFMPEG, "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{CANVAS_WIDTH}x{CANVAS_HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        temp_video
    ]
    
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    
    print_interval = FPS * 10
    for f_idx in range(TOTAL_FRAMES):
        frame_img = render_frame(f_idx)
        proc.stdin.write(frame_img.tobytes())
        
        if f_idx % print_interval == 0:
            pct = (f_idx / TOTAL_FRAMES) * 100
            print(f"Render progress: {f_idx}/{TOTAL_FRAMES} frames ({pct:.1f}%) | Time: {f_idx/FPS:.1f}s / {TOTAL_DURATION:.1f}s", flush=True)
            
    proc.stdin.close()
    stderr_out = proc.stderr.read().decode('utf-8', errors='ignore')
    proc.wait()
    
    if proc.returncode != 0:
        print("FFmpeg error:", stderr_out)
        return
        
    print("Video encoded! Now muxing with master audio...")
    
    mux_cmd = [
        FFMPEG, "-y",
        "-i", temp_video,
        "-i", AUDIO_MASTER,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        OUTPUT_MP4
    ]
    subprocess.run(mux_cmd, check=True)
    
    # Also copy to Downloads
    dl_target = r"C:\Users\DELL\Documents\Downloads\PHƯƠNG TRÌNH VAN DER WAALS_MTSEducation.mp4"
    import shutil
    shutil.copyfile(OUTPUT_MP4, dl_target)
    
    size_mb = os.path.getsize(OUTPUT_MP4) / (1024 * 1024)
    print("\n" + "=" * 50)
    print("🎉 STORYTELLING VIDEO CREATED SUCCESSFULLY!")
    print(f"Workspace: {OUTPUT_MP4}")
    print(f"Downloads: {dl_target}")
    print(f"Size: {size_mb:.2f} MB | Duration: {TOTAL_DURATION:.2f}s ({TOTAL_DURATION/60:.2f} mins)")
    print("=" * 50)

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
import os
import sys
import json
import math
import subprocess
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

sys.stdout.reconfigure(encoding='utf-8')

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
WORKSPACE = r"C:\Users\DELL\Documents\CODE\DU_AN"
AUDIO_DIR = os.path.join(WORKSPACE, "audio_build")
RECORDS_DIR = os.path.join(WORKSPACE, "web_records")
MIXED_AUDIO = os.path.join(AUDIO_DIR, "mixed_audio_final.wav")
OUTPUT_MP4 = os.path.join(WORKSPACE, "VIDEO_DEMO_MTSEDUCATION.mp4")
OUTPUT_DOWNLOADS = r"C:\Users\DELL\Documents\Downloads\VIDEO_DEMO_MTSEDUCATION.mp4"

W, H = 1080, 1920
FPS = 30.0

# Fonts
font_bold = "C:/Windows/Fonts/segoeuib.ttf" if os.path.exists("C:/Windows/Fonts/segoeuib.ttf") else "C:/Windows/Fonts/arialbd.ttf"
font_reg = "C:/Windows/Fonts/segoeui.ttf" if os.path.exists("C:/Windows/Fonts/segoeui.ttf") else "C:/Windows/Fonts/arial.ttf"
font_tahoma = "C:/Windows/Fonts/tahomabd.ttf"

f_wm = ImageFont.truetype(font_bold, 30)
f_badge = ImageFont.truetype(font_bold, 30)
f_title = ImageFont.truetype(font_bold, 54)
f_subtitle = ImageFont.truetype(font_bold, 34)
f_caption = ImageFont.truetype(font_bold, 40)
f_feature = ImageFont.truetype(font_bold, 26)
f_cta_bold = ImageFont.truetype(font_bold, 36)
f_cta_sub = ImageFont.truetype(font_bold, 28)
f_addr = ImageFont.truetype(font_bold, 22)

# Load scene audio & text info
with open(os.path.join(AUDIO_DIR, "scenes_info.json"), "r", encoding="utf-8") as f:
    scenes_data = json.load(f)

# Visual configuration per scene (Pastel Educational Infographic Theme)
# Colors:
# - Navy: (16, 40, 92) #10285C
# - Cobalt: (66, 107, 255) #426BFF
# - Sky Blue: (217, 240, 255) #D9F0FF
# - Pastel Pink: (255, 217, 240) #FFD9F0
# - Lavender: (232, 220, 255) #E8DCFF
# - Mint: (209, 242, 235) #D1F2EB
# - Soft Yellow: (255, 243, 176) #FFF3B0
# - Coral Red: (225, 29, 72) #E11D48

SCENE_CONFIG = [
    {
        'id': 1,
        'badge': "🚨 CẢNH BÁO 2K9 · 2K10 · 2K11 🌸",
        'badge_bg': (255, 217, 240),      # Pastel Pink
        'title': "BẠN ĐANG THIẾU ĐỀ ÔN CHUẨN?",
        'brush_bg': (255, 243, 176),      # Soft yellow brush
        'sub': "✨ Bế tắc vì cấu trúc đề mới 2025-2026? Đừng lo!",
        'sub_color': (66, 107, 255),      # Cobalt
        'addr': "🔒 https://mtsedu.vercel.app",
        'video': os.path.join(RECORDS_DIR, "scene_1.mp4"),
    },
    {
        'id': 2,
        'badge': "📚 KHO ĐỀ TN THPT 2025-2026 ✨",
        'badge_bg': (217, 240, 255),      # Sky Blue
        'title': "TOÁN · LÝ · HÓA · SỬ · ANH",
        'brush_bg': (217, 240, 255),      # Soft sky blue brush
        'sub': "🎯 Chuẩn 100% Ma Trận & Barem Bộ GD&ĐT",
        'sub_color': (66, 107, 255),
        'addr': "🔒 https://mtsedu.vercel.app/#physics",
        'video': os.path.join(RECORDS_DIR, "scene_2.mp4"),
    },
    {
        'id': 3,
        'badge': "🚀 ĐỘT PHÁ CÁC KỲ THI RIÊNG 🌟",
        'badge_bg': (232, 220, 255),      # Lavender
        'title': "HSA · TSA · V-ACT",
        'brush_bg': (232, 220, 255),      # Soft lavender brush
        'sub': "🏛️ ĐHQG Hà Nội · Bách Khoa · ĐHQG TP.HCM",
        'sub_color': (66, 107, 255),
        'addr': "🔒 https://mtsedu.vercel.app/#hsa",
        'video': os.path.join(RECORDS_DIR, "scene_3.mp4"),
    },
    {
        'id': 4,
        'badge': "⚡ PHÒNG THI ONLINE THỰC CHIẾN ⏱️",
        'badge_bg': (209, 242, 235),      # Mint
        'title': "BẤM GIỜ & CHẤM ĐIỂM NGAY",
        'brush_bg': (209, 242, 235),      # Soft mint brush
        'sub': "💡 Tự động chấm điểm + Lời giải chi tiết 100%",
        'sub_color': (66, 107, 255),
        'addr': "🔒 https://baominh2627-del.github.io/bai-ktra-vat-ly-nhiet-ly-12/",
        'video': os.path.join(RECORDS_DIR, "scene_4.mp4"),
    },
    {
        'id': 5,
        'badge': "🎁 ĐẶC QUYỀN 0 ĐỒNG TOÀN BỘ 🐧",
        'badge_bg': (255, 217, 240),      # Pastel Pink
        'title': "HOÀN TOÀN MIỄN PHÍ 100%",
        'brush_bg': (255, 217, 240),      # Soft pink brush
        'sub': "🔥 ĐẶC BIỆT DÀNH CHO CHIẾN BINH 2K9!",
        'sub_color': (225, 29, 72),       # Coral Red
        'addr': "🔒 https://mtsedu.vercel.app/#mock_exams",
        'video': os.path.join(RECORDS_DIR, "scene_5.mp4"),
    },
    {
        'id': 6,
        'badge': "🔥 BẮT ĐẦU NGAY ĐỂ BỨT PHÁ 🚀",
        'badge_bg': (217, 240, 255),      # Sky Blue
        'title': "MTSEDU.VERCEL.APP",
        'brush_bg': (255, 243, 176),      # Soft yellow brush
        'sub': "📞 Hotline & Zalo: 0372 336 302",
        'sub_color': (16, 40, 92),        # Navy
        'addr': "🔒 https://mtsedu.vercel.app/#contact",
        'video': os.path.join(RECORDS_DIR, "scene_6.mp4"),
    }
]

# Pre-render base background image with pastel watercolor washes
print("Pre-rendering pastel educational background...")
base_bg = Image.new("RGBA", (W, H), (255, 255, 255, 255))
wash = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d_wash = ImageDraw.Draw(wash)

# Soft watercolor gradients
d_wash.ellipse([-160, -100, 620, 520], fill=(217, 240, 255, 140))       # Top-Left Sky Blue
d_wash.ellipse([W - 520, -120, W + 220, 560], fill=(232, 220, 255, 130)) # Top-Right Lavender
d_wash.ellipse([W - 360, 680, W + 160, 1220], fill=(255, 217, 240, 110)) # Center-Right Pink
d_wash.ellipse([-140, H - 680, 480, H + 120], fill=(191, 232, 255, 130)) # Bottom-Left Cyan
d_wash.ellipse([W - 420, H - 460, W + 160, H + 120], fill=(255, 225, 245, 120)) # Bottom-Right Pink/Lavender

base_bg = Image.alpha_composite(base_bg, wash)
d_base = ImageDraw.Draw(base_bg)

# Draw cute hand-drawn doodles on background
def draw_sparkle(draw, cx, cy, size, color):
    draw.line([(cx - size, cy), (cx + size, cy)], fill=color, width=3)
    draw.line([(cx, cy - size), (cx, cy + size)], fill=color, width=3)
    draw.line([(cx - size//2, cy - size//2), (cx + size//2, cy + size//2)], fill=color, width=2)
    draw.line([(cx - size//2, cy + size//2), (cx + size//2, cy - size//2)], fill=color, width=2)

draw_sparkle(d_base, 90, 220, 18, (66, 107, 255))
draw_sparkle(d_base, W - 100, 200, 22, (255, 120, 180))
draw_sparkle(d_base, 80, 1360, 16, (66, 107, 255))
draw_sparkle(d_base, W - 90, 1380, 20, (255, 180, 50))

# Doodle curves
d_base.arc([W - 180, 280, W - 60, 400], start=180, end=320, fill=(66, 107, 255), width=3)
d_base.arc([60, 360, 180, 480], start=0, end=140, fill=(255, 140, 180), width=3)

# 3 Feature Pills
features = [
    ("⚡ Bấm Giờ Thật", (191, 232, 255)),
    ("💯 Chấm Điểm Ngay", (167, 243, 208)),
    ("📖 Giải Chi Tiết", (255, 217, 240))
]

def render_frame(scene_idx, frame_in_scene, total_frames_in_scene, global_frame, web_frame, scene_info, scene_cfg):
    # Copy base pastel background
    img = base_bg.copy()
    draw = ImageDraw.Draw(img)
    
    # Gentle breathing pulse (1.008x max) synchronized to beat - NO harsh glitch/shake
    beat_interval = 13.33
    frames_since_beat = (global_frame % beat_interval)
    decay = max(0.0, 1.0 - (frames_since_beat / 6.0)) if frames_since_beat < 6.0 else 0.0
    gentle_scale = 1.0 + 0.008 * decay
    
    # Cute floating bounce on decorative elements
    float_y = int(math.sin(global_frame * 0.08) * 3)
    
    # 1. BROWSER MOCKUP (Light Paper/Mac Style)
    bx = 40
    by = 440 + float_y
    base_w, base_h = 1000, 680
    header_h = 46
    
    cur_w = int(base_w * gentle_scale)
    cur_h = int(base_h * gentle_scale)
    offset_x = (cur_w - base_w) // 2
    offset_y = (cur_h - base_h) // 2
    cur_bx = bx - offset_x
    cur_by = by - offset_y
    
    # Soft drop shadow behind browser window
    shadow_pad = 12
    draw.rounded_rectangle([cur_bx - shadow_pad, cur_by - shadow_pad, cur_bx + cur_w + shadow_pad, cur_by + cur_h + shadow_pad],
                           radius=30, fill=(210, 230, 255))
    
    # Window body
    draw.rounded_rectangle([cur_bx, cur_by, cur_bx + cur_w, cur_by + cur_h], radius=24, fill=(255, 255, 255), outline=(66, 107, 255), width=3)
    
    # Window Header
    draw.rounded_rectangle([cur_bx, cur_by, cur_bx + cur_w, cur_by + header_h + 10], radius=24, fill=(234, 244, 255))
    draw.rectangle([cur_bx, cur_by + 20, cur_bx + cur_w, cur_by + header_h], fill=(234, 244, 255))
    draw.line([(cur_bx, cur_by + header_h), (cur_bx + cur_w, cur_by + header_h)], fill=(191, 232, 255), width=2)
    
    # 3 traffic dots
    draw.ellipse([cur_bx + 25, cur_by + 16, cur_bx + 39, cur_by + 30], fill=(255, 107, 107))
    draw.ellipse([cur_bx + 48, cur_by + 16, cur_bx + 62, cur_by + 30], fill=(255, 209, 102))
    draw.ellipse([cur_bx + 71, cur_by + 16, cur_bx + 85, cur_by + 30], fill=(6, 214, 160))
    
    # Address bar capsule
    addr_x = cur_bx + 110
    addr_w = cur_w - 140
    draw.rounded_rectangle([addr_x, cur_by + 8, addr_x + addr_w, cur_by + header_h - 8], radius=14, fill=(255, 255, 255), outline=(191, 232, 255), width=2)
    draw.text((addr_x + 18, cur_by + 11), scene_cfg['addr'], font=f_addr, fill=(16, 40, 92))
    
    # Put web recording inside
    if web_frame is not None:
        web_content_h = cur_h - header_h
        web_resized = cv2.resize(web_frame, (cur_w, web_content_h), interpolation=cv2.INTER_LINEAR)
        web_pil = Image.fromarray(cv2.cvtColor(web_resized, cv2.COLOR_BGR2RGB))
        img.paste(web_pil, (cur_bx, cur_by + header_h))
        
    # Re-draw crisp rounded border
    draw.rounded_rectangle([cur_bx, cur_by, cur_bx + cur_w, cur_by + cur_h], radius=24, outline=(66, 107, 255), width=3)
    
    # 2. TOP WATERMARK & HOTLINE
    draw.text((45, 38), "MTS Education ✦", font=f_wm, fill=(16, 40, 92))
    draw.line([(45, 75), (285, 75)], fill=(66, 107, 255), width=3)
    
    draw.rounded_rectangle([W - 390, 32, W - 45, 82], radius=18, fill=(255, 255, 255), outline=(191, 232, 255), width=2)
    draw.text((W - 370, 44), "HOTLINE: 0372 336 302", font=f_addr, fill=(16, 40, 92))
    
    # 3. SCENE BADGE (Pill Box with Pastel Fill)
    badge_txt = scene_cfg['badge']
    bb = draw.textbbox((0, 0), badge_txt, font=f_badge)
    bw = bb[2] - bb[0] + 50
    bx_badge = (W - bw) // 2
    draw.rounded_rectangle([bx_badge, 105, bx_badge + bw, 162], radius=20, fill=scene_cfg['badge_bg'], outline=(66, 107, 255), width=2)
    draw.text((bx_badge + 25, 115), badge_txt, font=f_badge, fill=(16, 40, 92))
    
    # 4. MAIN HEADLINE WITH PASTEL BRUSH HIGHLIGHT
    title_txt = scene_cfg['title']
    tb = draw.textbbox((0, 0), title_txt, font=f_title)
    tw = tb[2] - tb[0]
    title_x = (W - tw) // 2
    # Pastel highlight brush behind title
    draw.rounded_rectangle([title_x - 18, 192, title_x + tw + 18, 256], radius=16, fill=scene_cfg['brush_bg'])
    draw.text((title_x, 190), title_txt, font=f_title, fill=(16, 40, 92))
    
    # 5. SUBTITLE
    sub_txt = scene_cfg['sub']
    sb = draw.textbbox((0, 0), sub_txt, font=f_subtitle)
    sub_x = (W - (sb[2] - sb[0])) // 2
    draw.text((sub_x, 275), sub_txt, font=f_subtitle, fill=scene_cfg['sub_color'])
    
    # 6. DYNAMIC SUBTITLE CARD (Paper Card Style)
    subs = scene_info['subtitles']
    sub_phase = min(len(subs) - 1, int((frame_in_scene / total_frames_in_scene) * len(subs)))
    cur_sub_text = subs[sub_phase]
    
    cap_box = [50, 1165, W - 50, 1295]
    draw.rounded_rectangle([cap_box[0] - 6, cap_box[1] - 6, cap_box[2] + 6, cap_box[3] + 6], radius=24, fill=(215, 235, 255))
    draw.rounded_rectangle(cap_box, radius=20, fill=(255, 255, 255), outline=(66, 107, 255), width=2)
    cb = draw.textbbox((0, 0), cur_sub_text, font=f_caption)
    # Highlight color: Cobalt Blue for odd phase, Navy for even phase
    sub_col = (66, 107, 255) if sub_phase % 2 == 1 else (16, 40, 92)
    draw.text(((W - (cb[2] - cb[0])) // 2, 1205), cur_sub_text, font=f_caption, fill=sub_col)
    
    # 7. 3 FLOATING FEATURE BADGES
    pill_w = 300
    pill_gap = 25
    start_px = (W - (3 * pill_w + 2 * pill_gap)) // 2
    for fi, (ftxt, fbg) in enumerate(features):
        px = start_px + fi * (pill_w + pill_gap)
        draw.rounded_rectangle([px, 1325, px + pill_w, 1385], radius=16, fill=(255, 255, 255), outline=(66, 107, 255), width=2)
        draw.rounded_rectangle([px + 3, 1328, px + pill_w - 3, 1382], radius=14, fill=fbg)
        fb = draw.textbbox((0, 0), ftxt, font=f_feature)
        draw.text((px + (pill_w - (fb[2] - fb[0])) // 2, 1342), ftxt, font=f_feature, fill=(16, 40, 92))
        
    # 8. BOTTOM STICKY CTA BANNER (Paper Card with Cobalt & Pastel Borders)
    cta_box = [40, 1420, W - 40, 1870]
    draw.rounded_rectangle([cta_box[0] - 8, cta_box[1] - 8, cta_box[2] + 8, cta_box[3] + 8], radius=30, fill=(210, 230, 255))
    draw.rounded_rectangle(cta_box, radius=24, fill=(255, 255, 255), outline=(66, 107, 255), width=3)
    
    # Top pastel accent bar inside card
    draw.rounded_rectangle([cta_box[0] + 3, cta_box[1] + 3, cta_box[2] - 3, cta_box[1] + 120], radius=22, fill=(255, 217, 240))
    draw.rectangle([cta_box[0] + 3, cta_box[1] + 50, cta_box[2] - 3, cta_box[1] + 120], fill=(255, 217, 240))
    
    t1 = "🎁 HOÀN TOÀN MIỄN PHÍ 100%!"
    t2 = "DÀNH CHO HỌC SINH 2K11, 2K10 & ĐẶC BIỆT 2K9"
    t3 = "🌐 Website: MTSEDU.VERCEL.APP"
    t4 = "📞 Hotline & Zalo: 0372 336 302"
    
    b_t1 = draw.textbbox((0, 0), t1, font=f_cta_bold)
    b_t2 = draw.textbbox((0, 0), t2, font=f_cta_sub)
    b_t3 = draw.textbbox((0, 0), t3, font=f_cta_bold)
    b_t4 = draw.textbbox((0, 0), t4, font=f_cta_bold)
    
    draw.text(((W - (b_t1[2] - b_t1[0])) // 2, 1445), t1, font=f_cta_bold, fill=(225, 29, 72)) # Coral red
    draw.text(((W - (b_t2[2] - b_t2[0])) // 2, 1500), t2, font=f_cta_sub, fill=(16, 40, 92))
    
    # Divider line with cute doodle dots
    draw.line([(80, 1580), (W - 80, 1580)], fill=(191, 232, 255), width=2)
    
    draw.text(((W - (b_t3[2] - b_t3[0])) // 2, 1615), t3, font=f_cta_bold, fill=(66, 107, 255))
    draw.text(((W - (b_t4[2] - b_t4[0])) // 2, 1690), t4, font=f_cta_bold, fill=(16, 40, 92))
    
    # Big CTA Button with subtle pulsing glow
    btn_y = 1765
    btn_w = 880
    btn_h = 74
    btn_x = (W - btn_w) // 2
    # Gentle button pulse
    btn_pulse_col = (66, 107, 255) if (global_frame // 15) % 2 == 0 else (50, 90, 240)
    draw.rounded_rectangle([btn_x, btn_y, btn_x + btn_w, btn_y + btn_h], radius=20, fill=btn_pulse_col, outline=(191, 232, 255), width=2)
    btn_text = "👉 TRUY CẬP NGAY ĐỂ NHẬN TÀI KHOẢN VIP 👈"
    bb = draw.textbbox((0, 0), btn_text, font=f_cta_sub)
    draw.text((btn_x + (btn_w - (bb[2] - bb[0])) // 2, btn_y + 20), btn_text, font=f_cta_sub, fill=(255, 255, 255))
    
    return cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)

def main():
    print("Initializing Pastel Educational Video rendering pipeline...")
    scene_frames_list = []
    total_video_frames = 0
    for s in scenes_data:
        n_frames = int(round(s['duration'] * FPS))
        scene_frames_list.append(n_frames)
        total_video_frames += n_frames
        
    print(f"Total video frames: {total_video_frames} ({total_video_frames/FPS:.2f} seconds)")

    pipe_cmd = [
        FFMPEG, '-y',
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-s', f'{W}x{H}',
        '-pix_fmt', 'bgr24',
        '-r', str(FPS),
        '-i', '-',
        '-i', MIXED_AUDIO,
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-crf', '18',
        '-pix_fmt', 'yuv420p',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-shortest',
        OUTPUT_MP4
    ]
    
    proc = subprocess.Popen(pipe_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    global_frame = 0
    for s_idx, (s_data, s_cfg, n_frames) in enumerate(zip(scenes_data, SCENE_CONFIG, scene_frames_list)):
        print(f"\nRendering Scene {s_idx+1}/{len(scenes_data)}: {s_cfg['title']} ({n_frames} frames)...")
        cap = cv2.VideoCapture(s_cfg['video'])
        
        for f_in_scene in range(n_frames):
            ret, web_frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, web_frame = cap.read()
                
            frame_bgr = render_frame(s_idx, f_in_scene, n_frames, global_frame, web_frame, s_data, s_cfg)
            proc.stdin.write(frame_bgr.tobytes())
            global_frame += 1
            
            if f_in_scene % 60 == 0 or f_in_scene == n_frames - 1:
                progress = (global_frame / total_video_frames) * 100
                print(f"  Frame {global_frame}/{total_video_frames} ({progress:.1f}%)", flush=True)
                
        cap.release()
        
    proc.stdin.close()
    proc.wait()
    
    if proc.returncode != 0:
        raise RuntimeError("FFmpeg render failed")
        
    print(f"\nPastel Render completed successfully -> {OUTPUT_MP4}")
    
    import shutil
    try:
        shutil.copy2(OUTPUT_MP4, OUTPUT_DOWNLOADS)
        print(f"Copied to Downloads: {OUTPUT_DOWNLOADS}")
    except Exception as e:
        print(f"Copy note: {e}")

if __name__ == '__main__':
    main()

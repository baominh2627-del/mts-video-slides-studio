# -*- coding: utf-8 -*-
import os
import sys
import json
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
font_arial_bold = r"C:\Windows\Fonts\arialbd.ttf"
font_tahoma_bold = r"C:\Windows\Fonts\tahomabd.ttf"
font_impact = r"C:\Windows\Fonts\impact.ttf"

f_wm = ImageFont.truetype(font_tahoma_bold, 28)
f_badge = ImageFont.truetype(font_tahoma_bold, 30)
f_title = ImageFont.truetype(font_arial_bold, 52)
f_subtitle = ImageFont.truetype(font_tahoma_bold, 32)
f_caption = ImageFont.truetype(font_arial_bold, 40)
f_feature = ImageFont.truetype(font_tahoma_bold, 26)
f_cta_bold = ImageFont.truetype(font_arial_bold, 36)
f_cta_sub = ImageFont.truetype(font_tahoma_bold, 28)
f_addr = ImageFont.truetype(font_tahoma_bold, 22)

# Load scene info
with open(os.path.join(AUDIO_DIR, "scenes_info.json"), "r", encoding="utf-8") as f:
    scenes_data = json.load(f)

# Visual configuration per scene
SCENE_CONFIG = [
    {
        'id': 1,
        'badge': "🚨 CẢNH BÁO KHẨN CẤP",
        'badge_color': (239, 68, 68),       # Red
        'title': "DÀNH RIÊNG 2K9 - 2K10 - 2K11",
        'title_color': (255, 75, 75),
        'sub': "⚡ Bạn đang bế tắc vì thiếu đề chuẩn?",
        'sub_color': (255, 234, 0),
        'addr': "🔒 https://mtsedu.vercel.app",
        'video': os.path.join(RECORDS_DIR, "scene_1.mp4"),
    },
    {
        'id': 2,
        'badge': "📚 KHO ĐỀ TN THPT 2025-2026",
        'badge_color': (59, 130, 246),      # Blue
        'title': "TOÁN · LÝ · HÓA · SỬ · ANH",
        'title_color': (255, 234, 0),
        'sub': "🎯 Chuẩn 100% Ma Trận Đề Bộ GD&ĐT",
        'sub_color': (0, 242, 254),
        'addr': "🔒 https://mtsedu.vercel.app/#physics",
        'video': os.path.join(RECORDS_DIR, "scene_2.mp4"),
    },
    {
        'id': 3,
        'badge': "🚀 ĐỘT PHÁ KỲ THI RIÊNG",
        'badge_color': (168, 85, 247),     # Purple
        'title': "HSA · TSA · V-ACT",
        'title_color': (0, 242, 254),
        'sub': "🔥 ĐHQG Hà Nội · Bách Khoa · ĐHQG HCM",
        'sub_color': (255, 234, 0),
        'addr': "🔒 https://mtsedu.vercel.app/#hsa",
        'video': os.path.join(RECORDS_DIR, "scene_3.mp4"),
    },
    {
        'id': 4,
        'badge': "⚡ TRẢI NGHIỆM THI THỰC CHIẾN",
        'badge_color': (34, 197, 94),      # Green
        'title': "BẤM GIỜ & CHẤM ĐIỂM NGAY",
        'title_color': (74, 222, 128),
        'sub': "💡 Tự động chấm điểm + Lời giải chi tiết",
        'sub_color': (255, 255, 255),
        'addr': "🔒 https://baominh2627-del.github.io/bai-ktra-vat-ly-nhiet-ly-12/",
        'video': os.path.join(RECORDS_DIR, "scene_4.mp4"),
    },
    {
        'id': 5,
        'badge': "🎁 ƯU ĐÃI ĐẶC BIỆT 0 ĐỒNG",
        'badge_color': (245, 158, 11),     # Amber/Gold
        'title': "HOÀN TOÀN MIỄN PHÍ 100%",
        'title_color': (255, 220, 0),
        'sub': "💥 ĐẶC BIỆT DÀNH CHO CHIẾN BINH 2K9!",
        'sub_color': (255, 75, 75),
        'addr': "🔒 https://mtsedu.vercel.app/#mock_exams",
        'video': os.path.join(RECORDS_DIR, "scene_5.mp4"),
    },
    {
        'id': 6,
        'badge': "🔥 ĐĂNG KÝ HỌC NGAY HÔM NAY",
        'badge_color': (236, 72, 153),     # Pink/Red
        'title': "MTSEDU.VERCEL.APP",
        'title_color': (255, 234, 0),
        'sub': "📞 Hotline & Zalo: 0372 336 302",
        'sub_color': (0, 242, 254),
        'addr': "🔒 https://mtsedu.vercel.app/#contact",
        'video': os.path.join(RECORDS_DIR, "scene_6.mp4"),
    }
]

# Helper text with outline
def draw_text_stroke(draw, pos, text, font, fill, stroke_fill=(0, 0, 0), stroke_w=4):
    x, y = pos
    draw.text((x, y), text, font=font, fill=fill, stroke_width=stroke_w, stroke_fill=stroke_fill)

# Base background with dark navy gradient & subtle cyber grid
print("Pre-rendering base background...")
base_bg = np.zeros((H, W, 3), dtype=np.uint8)
for y in range(H):
    ratio = y / H
    r = int(7 + 9 * ratio)
    g = int(11 + 14 * ratio)
    b = int(22 + 28 * ratio)
    base_bg[y, :] = (b, g, r)  # BGR

# Draw subtle grid lines
for gx in range(0, W, 80):
    cv2.line(base_bg, (gx, 0), (gx, H), (30, 22, 16), 1)
for gy in range(0, H, 80):
    cv2.line(base_bg, (0, gy), (W, gy), (30, 22, 16), 1)

# Floating feature pills
features = [
    ("⚡ BẤM GIỜ THI THẬT", (59, 130, 246)),
    ("💯 CHẤM ĐIỂM TỨC THÌ", (34, 197, 94)),
    ("📖 GIẢI CHI TIẾT 100%", (245, 158, 11))
]

def render_frame(scene_idx, frame_in_scene, total_frames_in_scene, global_frame, web_frame, scene_info, scene_cfg):
    frame = base_bg.copy()
    
    # Beat calculations (~135 BPM -> beat every 13.3 frames)
    beat_interval = 13.33
    frames_since_beat = (global_frame % beat_interval)
    is_beat_punch = frames_since_beat < 4.0
    decay = max(0.0, 1.0 - (frames_since_beat / 4.0)) if is_beat_punch else 0.0
    
    # Giật giật effects: punch scale & screen shake on the beat
    punch_scale = 1.0 + 0.025 * decay
    shake_dx = int(np.sin(global_frame * 3.7) * 6 * decay) if is_beat_punch else 0
    shake_dy = int(np.cos(global_frame * 4.3) * 5 * decay) if is_beat_punch else 0
    
    # Scene transition flash (first 3 frames of each scene)
    transition_flash = 0.0
    if frame_in_scene < 4:
        transition_flash = (4 - frame_in_scene) / 4.0 * 0.28
    
    # 1. BROWSER MOCKUP WITH WEB FRAME
    bx = 40 + shake_dx
    by = 440 + shake_dy
    base_w, base_h = 1000, 680
    header_h = 44
    
    # Apply punch scale to browser mockup
    cur_w = int(base_w * punch_scale)
    cur_h = int(base_h * punch_scale)
    offset_x = (cur_w - base_w) // 2
    offset_y = (cur_h - base_h) // 2
    cur_bx = bx - offset_x
    cur_by = by - offset_y
    
    if web_frame is not None:
        web_content_h = cur_h - header_h
        web_resized = cv2.resize(web_frame, (cur_w, web_content_h), interpolation=cv2.INTER_LINEAR)
        
        # Header
        cv2.rectangle(frame, (cur_bx, cur_by), (cur_bx + cur_w, cur_by + header_h), (38, 30, 24), -1)
        # Dots
        cv2.circle(frame, (cur_bx + 25, cur_by + 22), 7, (86, 95, 255), -1)
        cv2.circle(frame, (cur_bx + 48, cur_by + 22), 7, (46, 189, 255), -1)
        cv2.circle(frame, (cur_bx + 71, cur_by + 22), 7, (63, 201, 39), -1)
        # Address bar container
        cv2.rectangle(frame, (cur_bx + 105, cur_by + 8), (cur_bx + cur_w - 30, cur_by + header_h - 8), (22, 17, 14), -1)
        
        # Put web content
        y_start = max(0, cur_by + header_h)
        y_end = min(H, cur_by + header_h + web_content_h)
        x_start = max(0, cur_bx)
        x_end = min(W, cur_bx + cur_w)
        
        web_crop_y_end = y_end - y_start
        web_crop_x_end = x_end - x_start
        if web_crop_y_end > 0 and web_crop_x_end > 0:
            frame[y_start:y_end, x_start:x_end] = web_resized[0:web_crop_y_end, 0:web_crop_x_end]
            
        # Glowing border on beat
        border_col = scene_cfg['badge_color']
        if decay > 0:
            b_glow = tuple(int(min(255, c + 80 * decay)) for c in border_col)
            cv2.rectangle(frame, (cur_bx - 2, cur_by - 2), (cur_bx + cur_w + 2, cur_by + cur_h + 2), (b_glow[2], b_glow[1], b_glow[0]), 3)
        else:
            cv2.rectangle(frame, (cur_bx - 2, cur_by - 2), (cur_bx + cur_w + 2, cur_by + cur_h + 2), (border_col[2], border_col[1], border_col[0]), 2)

    # Convert to PIL for crisp text & UI overlays
    img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    
    # Top Watermarks
    draw.text((45, 35), "MTS Education ✦", font=f_wm, fill=(255, 255, 255))
    draw.text((W - 390, 38), "HOTLINE: 0372 336 302", font=f_addr, fill=(180, 220, 255))
    
    # Scene Badge
    badge_txt = scene_cfg['badge']
    bb = draw.textbbox((0, 0), badge_txt, font=f_badge)
    bw = bb[2] - bb[0] + 44
    bx_badge = (W - bw) // 2
    # Pulsing badge background
    draw.rounded_rectangle([bx_badge, 95, bx_badge + bw, 152], radius=15, fill=(18, 25, 45), outline=scene_cfg['badge_color'], width=2)
    draw.text((bx_badge + 22, 105), badge_txt, font=f_badge, fill=(255, 255, 255))
    
    # Main Headline
    title_txt = scene_cfg['title']
    tb = draw.textbbox((0, 0), title_txt, font=f_title)
    tw = tb[2] - tb[0]
    draw_text_stroke(draw, ((W - tw) // 2, 175), title_txt, font=f_title, fill=scene_cfg['title_color'], stroke_w=6)
    
    # Sub-Headline
    sub_txt = scene_cfg['sub']
    sb = draw.textbbox((0, 0), sub_txt, font=f_subtitle)
    draw_text_stroke(draw, ((W - (sb[2] - sb[0])) // 2, 255), sub_txt, font=f_subtitle, fill=scene_cfg['sub_color'], stroke_w=4)
    
    # Address Bar URL inside mockup
    draw.text((cur_bx + 125, cur_by + 11), scene_cfg['addr'], font=f_addr, fill=(170, 195, 230))
    
    # Subtitle Card (Y: 1160 - 1310)
    subs = scene_info['subtitles']
    sub_phase = min(len(subs) - 1, int((frame_in_scene / total_frames_in_scene) * len(subs)))
    cur_sub_text = subs[sub_phase]
    
    cap_box = [50, 1165, W - 50, 1295]
    draw.rounded_rectangle(cap_box, radius=20, fill=(12, 18, 32), outline=(255, 255, 255), width=2)
    cb = draw.textbbox((0, 0), cur_sub_text, font=f_caption)
    # Highlight keywords with yellow
    draw_text_stroke(draw, ((W - (cb[2] - cb[0])) // 2, 1205), cur_sub_text, font=f_caption, fill=(255, 234, 0) if sub_phase % 2 == 1 else (255, 255, 255), stroke_w=3)
    
    # 3 Floating Feature Badges (Y: 1325 - 1395)
    pill_w = 300
    pill_gap = 25
    start_px = (W - (3 * pill_w + 2 * pill_gap)) // 2
    for fi, (ftxt, fcol) in enumerate(features):
        px = start_px + fi * (pill_w + pill_gap)
        draw.rounded_rectangle([px, 1325, px + pill_w, 1385], radius=14, fill=(15, 22, 40), outline=fcol, width=2)
        fb = draw.textbbox((0, 0), ftxt, font=f_feature)
        draw.text((px + (pill_w - (fb[2] - fb[0])) // 2, 1340), ftxt, font=f_feature, fill=(255, 255, 255))
        
    # Bottom Sticky High-Converting CTA Banner (Y: 1420 - 1880)
    cta_box = [40, 1420, W - 40, 1870]
    # Gold border with animated pulsing glow
    border_pulse = (255, 215, 0) if (global_frame // 10) % 2 == 0 else (255, 165, 0)
    draw.rounded_rectangle(cta_box, radius=24, fill=(14, 20, 36), outline=border_pulse, width=3)
    
    # CTA Content inside box
    t1 = "🎁 HOÀN TOÀN MIỄN PHÍ 100%!"
    t2 = "DÀNH CHO HỌC SINH 2K11, 2K10 & ĐẶC BIỆT 2K9"
    t3 = "🌐 Website: MTSEDU.VERCEL.APP"
    t4 = "📞 Hotline & Zalo: 0372 336 302"
    
    b_t1 = draw.textbbox((0, 0), t1, font=f_cta_bold)
    b_t2 = draw.textbbox((0, 0), t2, font=f_cta_sub)
    b_t3 = draw.textbbox((0, 0), t3, font=f_cta_bold)
    b_t4 = draw.textbbox((0, 0), t4, font=f_cta_bold)
    
    draw_text_stroke(draw, ((W - (b_t1[2] - b_t1[0])) // 2, 1460), t1, font=f_cta_bold, fill=(255, 225, 0), stroke_w=4)
    draw_text_stroke(draw, ((W - (b_t2[2] - b_t2[0])) // 2, 1530), t2, font=f_cta_sub, fill=(255, 75, 75), stroke_w=3)
    
    # Divider line
    draw.line([(80, 1600), (W - 80, 1600)], fill=(45, 60, 95), width=2)
    
    draw_text_stroke(draw, ((W - (b_t3[2] - b_t3[0])) // 2, 1630), t3, font=f_cta_bold, fill=(0, 242, 254), stroke_w=4)
    draw_text_stroke(draw, ((W - (b_t4[2] - b_t4[0])) // 2, 1705), t4, font=f_cta_bold, fill=(255, 255, 255), stroke_w=4)
    
    # Pulsing Button
    btn_y = 1775
    btn_w = 880
    btn_h = 70
    btn_x = (W - btn_w) // 2
    btn_col = (220, 38, 38) if (global_frame // 8) % 2 == 0 else (185, 28, 28)
    draw.rounded_rectangle([btn_x, btn_y, btn_x + btn_w, btn_y + btn_h], radius=18, fill=btn_col, outline=(255, 255, 255), width=2)
    btn_text = "👉 TRUY CẬP NGAY ĐỂ NHẬN TÀI KHOẢN VIP 👈"
    bb = draw.textbbox((0, 0), btn_text, font=f_cta_sub)
    draw_text_stroke(draw, (btn_x + (btn_w - (bb[2] - bb[0])) // 2, btn_y + 18), btn_text, font=f_cta_sub, fill=(255, 255, 255), stroke_w=2)
    
    final_bgr = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    
    # Apply White Flash if transition or heavy beat
    if transition_flash > 0:
        white_overlay = np.full_like(final_bgr, 255)
        final_bgr = cv2.addWeighted(final_bgr, 1.0 - transition_flash, white_overlay, transition_flash, 0)
    elif decay > 0.6:
        beat_flash = (decay - 0.6) * 0.22
        white_overlay = np.full_like(final_bgr, 255)
        final_bgr = cv2.addWeighted(final_bgr, 1.0 - beat_flash, white_overlay, beat_flash, 0)
        
    return final_bgr

def main():
    print("Initializing video rendering pipeline...")
    # Calculate frames per scene
    scene_frames_list = []
    total_video_frames = 0
    for s in scenes_data:
        n_frames = int(round(s['duration'] * FPS))
        scene_frames_list.append(n_frames)
        total_video_frames += n_frames
        
    print(f"Total video frames: {total_video_frames} ({total_video_frames/FPS:.2f} seconds)")

    # Open ffmpeg subprocess pipe
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
        err = proc.stderr.read().decode('utf-8', errors='ignore')
        raise RuntimeError(f"FFmpeg render failed: {err}")
        
    print(f"\nRender completed successfully -> {OUTPUT_MP4}")
    
    # Copy to Downloads folder
    import shutil
    try:
        shutil.copy2(OUTPUT_MP4, OUTPUT_DOWNLOADS)
        print(f"Copied to Downloads: {OUTPUT_DOWNLOADS}")
    except Exception as e:
        print(f"Copy note: {e}")

if __name__ == '__main__':
    main()

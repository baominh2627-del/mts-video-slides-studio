# -*- coding: utf-8 -*-
import os
import sys
import json
import subprocess
from gtts import gTTS
import soundfile as sf
import imageio_ffmpeg

sys.stdout.reconfigure(encoding='utf-8')
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
OUT_DIR = r"C:\Users\DELL\Documents\CODE\DU_AN\audio_build"
os.makedirs(OUT_DIR, exist_ok=True)

SCENES = [
    {
        'id': 1,
        'name': 'hook',
        'speed': 1.35,
        'badge': '🚨 CẢNH BÁO KHẨN CẤP',
        'title': 'DÀNH RIÊNG 2K9 - 2K10 - 2K11',
        'text': 'Cảnh báo học sinh 2k9, 2k10 và 2k11! Bạn đang bế tắc vì thiếu nguồn luyện đề chuẩn cấu trúc mới?',
        'subtitles': [
            'Cảnh báo học sinh 2K9, 2K10 và 2K11!',
            'Bạn đang bế tắc vì thiếu đề chuẩn cấu trúc mới?'
        ]
    },
    {
        'id': 2,
        'name': 'thpt',
        'speed': 1.35,
        'badge': '📚 KHO ĐỀ TN THPT 2025-2026',
        'title': 'TOÁN - LÝ - HÓA - ANH - SỬ',
        'text': 'Đã có MTSEducation! Kho đề thi thử tốt nghiệp THPT chuẩn 100%: Toán bứt phá, Vật lý trực quan, Hóa học chuyên sâu, cùng Tiếng Anh và Lịch Sử bám sát barem Bộ Giáo Dục!',
        'subtitles': [
            'Đã có MTSEducation - Cứu tinh của bạn!',
            'Kho đề thi tốt nghiệp THPT chuẩn 100%:',
            'Toán bứt phá - Vật lý trực quan - Hóa chuyên sâu!',
            'Cùng Tiếng Anh & Lịch Sử bám sát barem mới!'
        ]
    },
    {
        'id': 3,
        'name': 'ky_thi_rieng',
        'speed': 1.35,
        'badge': '🚀 ĐỘT PHÁ KỲ THI RIÊNG',
        'title': 'HSA (ĐHQGHN) · TSA (BÁCH KHOA) · V-ACT',
        'text': 'Đột phá vào đại học top đầu cùng các kỳ thi riêng: Đánh giá năng lực HSA ĐHQG Hà Nội, Đánh giá tư duy TSA Bách Khoa và V-ACT! Tư duy định lượng, định tính đầy đủ mọi dạng bài!',
        'subtitles': [
            'Đột phá vào đại học top đầu cùng kỳ thi riêng!',
            'ĐGNL HSA ĐHQGHN - ĐGTD TSA Bách Khoa - V-ACT!',
            'Tư duy Định lượng & Định tính chuẩn thực chiến!'
        ]
    },
    {
        'id': 4,
        'name': 'thi_that',
        'speed': 1.35,
        'badge': '⚡ TRẢI NGHIỆM THI THỰC CHIẾN',
        'title': 'CHẤM ĐIỂM & GIẢI CHI TIẾT',
        'text': 'Phòng thi thực chiến bấm giờ chuẩn thi thật! Làm bài mượt mà, nộp bài có ngay kết quả kèm lời giải chi tiết từng bước giúp bạn hiểu bản chất!',
        'subtitles': [
            'Phòng thi online chuẩn bấm giờ thi thật!',
            'Tích chọn đáp án nhanh, chống gian lận cực đỉnh!',
            'Nộp bài chấm điểm ngay - Lời giải chi tiết 100%!'
        ]
    },
    {
        'id': 5,
        'name': 'mien_phi',
        'speed': 1.30,
        'badge': '🎁 ƯU ĐÃI ĐẶC QUYỀN 0 ĐỒNG',
        'title': 'HOÀN TOÀN MIỄN PHÍ 100%',
        'text': 'Đặc biệt: Toàn bộ kho đề đỉnh cao này mở HOÀN TOÀN MIỄN PHÍ cho học sinh 2k11, 2k10, và đặc biệt là các sĩ tử 2k9 đang tăng tốc về đích!',
        'subtitles': [
            'ĐẶC BIỆT: MỞ HOÀN TOÀN MIỄN PHÍ 100%!',
            'Dành riêng cho học sinh 2K11, 2K10...',
            'Và ĐẶC BIỆT là các sĩ tử 2K9 đang về đích!'
        ]
    },
    {
        'id': 6,
        'name': 'cta',
        'speed': 1.32,
        'badge': '🔥 ĐĂNG KÝ NGAY HÔM NAY',
        'title': 'MTSEDU.VERCEL.APP · 0372 336 302',
        'text': 'Cơ hội vàng nâng điểm! Truy cập ngay website MTSEDU chấm VERCEL chấm APP hoặc liên hệ Zalo 0372 336 302 để nhận tài khoản VIP ngay hôm nay!',
        'subtitles': [
            'Cơ hội vàng nâng band điểm cấp tốc!',
            'Truy cập ngay: MTSEDU.VERCEL.APP',
            'Hotline & Zalo: 0372 336 302 - Bắt đầu ngay!'
        ]
    }
]

def main():
    total_dur = 0
    results = []
    
    for s in SCENES:
        sid = s['id']
        sname = s['name']
        raw_mp3 = os.path.join(OUT_DIR, f"raw_scene_{sid}_{sname}.mp3")
        wav = os.path.join(OUT_DIR, f"scene_{sid}_{sname}.wav")
        
        print(f"Generating TTS for scene {sid} ({sname})...")
        tts = gTTS(text=s['text'], lang='vi', slow=False)
        tts.save(raw_mp3)
        
        speed = s['speed']
        cmd = [
            ffmpeg, '-y',
            '-i', raw_mp3,
            '-filter:a', f'atempo={speed}',
            '-ar', '44100',
            '-ac', '2',
            wav
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        
        data, sr = sf.read(wav)
        dur = len(data) / sr
        s['duration'] = dur
        total_dur += dur
        
        results.append({
            'id': sid,
            'name': sname,
            'badge': s['badge'],
            'title': s['title'],
            'duration': dur,
            'text': s['text'],
            'subtitles': s['subtitles'],
            'wav': wav
        })
        print(f" -> Scene {sid}: {dur:.2f}s | Speed: {speed}x")

    print(f"\n==========================================")
    print(f" TOTAL VOICE DURATION: {total_dur:.2f} seconds")
    print(f"==========================================")
    
    with open(os.path.join(OUT_DIR, "scenes_info.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
import os
import sys
import asyncio
import edge_tts
import soundfile as sf
import subprocess
import imageio_ffmpeg

sys.stdout.reconfigure(encoding='utf-8')
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
OUT_DIR = r"C:\Users\DELL\Documents\CODE\DU_AN\audio_build"
os.makedirs(OUT_DIR, exist_ok=True)

SCENES = [
    {
        'id': 1,
        'name': 'hook',
        'rate': '+12%',
        'text': 'Cảnh báo khẩn cấp dành riêng cho học sinh 2k9, 2k10 và 2k11! Bạn đang bế tắc vì không tìm được nguồn luyện đề chuẩn cấu trúc mới?'
    },
    {
        'id': 2,
        'name': 'thpt',
        'rate': '+14%',
        'text': 'Đừng lo, MTSEducation chính là cứu tinh của bạn! Hệ thống đề thi thử tốt nghiệp Trung học phổ thông cực khủng: Trọn bộ Toán học bứt phá, Vật lý trực quan, Hóa học chuyên sâu, cùng Tiếng Anh và Lịch Sử bám sát 100% định dạng đề mới nhất của Bộ Giáo Dục!'
    },
    {
        'id': 3,
        'name': 'ky_thi_rieng',
        'rate': '+12%',
        'text': 'Đặc biệt, mở lối vào các trường đại học top đầu với bộ đề độc quyền: Đánh giá năng lực H S A Đại học Quốc gia Hà Nội, Đánh giá tư duy T S A Bách Khoa và V A C T! Tư duy định lượng, định tính, khoa học bám sát thực tế!'
    },
    {
        'id': 4,
        'name': 'thi_that',
        'rate': '+12%',
        'text': 'Vào phòng thi thực chiến cực đã! Đồng hồ bấm giờ chuẩn thi thật, tích chọn đáp án thông minh. Nộp bài xong là có ngay kết quả kèm lời giải chi tiết từng bước, giúp bạn quét sạch lỗ hổng kiến thức!'
    },
    {
        'id': 5,
        'name': 'mien_phi',
        'rate': '+10%',
        'text': 'Và tin cực vui: Tất cả những đề thi đỉnh cao này đang được mở HOÀN TOÀN MIỄN PHÍ cho học sinh 2k11, 2k10, và đặc biệt là các sĩ tử 2k9 đang tăng tốc về đích!'
    },
    {
        'id': 6,
        'name': 'cta',
        'rate': '+12%',
        'text': 'Cơ hội vàng nâng band điểm! Truy cập ngay website M T S E D U chấm VERCEL chấm APP hoặc liên hệ Zalo 0372 336 302 để nhận tài khoản VIP ngay hôm nay!'
    }
]

async def gen():
    total_dur = 0
    results = []
    for s in SCENES:
        sid = s['id']
        sname = s['name']
        mp3 = os.path.join(OUT_DIR, f"scene_{sid}_{sname}.mp3")
        wav = os.path.join(OUT_DIR, f"scene_{sid}_{sname}.wav")
        
        # If wav already exists and is valid, skip synthesize to save time
        if not (os.path.exists(wav) and os.path.getsize(wav) > 10000):
            success = False
            for att in range(6):
                try:
                    if os.path.exists(mp3):
                        os.remove(mp3)
                    comm = edge_tts.Communicate(s['text'], voice='vi-VN-NamMinhNeural', rate=s['rate'])
                    await asyncio.wait_for(comm.save(mp3), timeout=15.0)
                    if os.path.exists(mp3) and os.path.getsize(mp3) > 1000:
                        success = True
                        break
                except Exception as e:
                    print(f"Retry {att+1} for scene {sid}: {e}", flush=True)
                    await asyncio.sleep(1.5 * (att + 1))
            
            if not success:
                raise RuntimeError(f"Could not generate scene {sid}")
            
            subprocess.run([ffmpeg, '-y', '-i', mp3, '-ar', '44100', '-ac', '2', wav],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            await asyncio.sleep(0.8)

        data, sr = sf.read(wav)
        dur = len(data) / sr
        s['duration'] = dur
        total_dur += dur
        results.append({
            'id': sid,
            'name': sname,
            'duration': dur,
            'text': s['text'],
            'wav': wav
        })
        print(f"Scene {sid} ({sname}): {dur:.2f}s | {s['text'][:40]}...", flush=True)

    print(f"\n>>> TOTAL VOICE DURATION: {total_dur:.2f}s <<<", flush=True)
    import json
    with open(os.path.join(OUT_DIR, "scenes_info.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    asyncio.run(gen())

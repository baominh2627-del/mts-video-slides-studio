# -*- coding: utf-8 -*-
import os
import sys
import asyncio
import subprocess
import json
import edge_tts
import soundfile as sf
import numpy as np
import imageio_ffmpeg

sys.stdout.reconfigure(encoding='utf-8')

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
OUT_DIR = r"C:\Users\DELL\Documents\CODE\DU_AN\video_build"
os.makedirs(OUT_DIR, exist_ok=True)

# List of narration lines organized by scene
SCENES_SCRIPT = [
    # Scene 1: Introduction & Ideal Gas Limitations (0 - ~35s)
    {
        "scene_id": 1,
        "title": "GIỚI THIỆU & MÔ HÌNH KHÍ LÝ TƯỞNG",
        "badge": "PHẦN 1: GIỚI THIỆU",
        "lines": [
            "Trong chương trình vật lý, phương trình trạng thái khí lý tưởng P nhân V bằng n R T đã trở nên vô cùng quen thuộc.",
            "Mô hình này rất đẹp và đơn giản, nhưng lại dựa trên hai giả định hoàn hảo không có trong thực tế.",
            "Một là: các phân tử được coi là chất điểm hình học, nghĩa là thể tích bản thân của chúng bằng không.",
            "Hai là: hoàn toàn không có bất kỳ lực hút hay đẩy nào giữa các phân tử, ngoại trừ khi va chạm đàn hồi.",
            "Nhưng ở điều kiện áp suất cao hoặc nhiệt độ thấp, khí thực bắt đầu bộc lộ sự sai lệch rất lớn so với lý thuyết!"
        ]
    },
    # Scene 2: Volume Correction - b parameter (~35s - ~75s)
    {
        "scene_id": 2,
        "title": "HIỆU CHỈNH THỂ TÍCH RIÊNG (HẰNG SỐ b)",
        "badge": "PHẦN 2: THỂ TÍCH RIÊNG",
        "lines": [
            "Năm 1873, nhà vật lý Johannes van der Waals đã đưa ra hai hiệu chỉnh mang tính cách mạng.",
            "Hiệu chỉnh thứ nhất xuất phát từ kích thước thật của phân tử khí.",
            "Trong thực tế, mỗi phân tử là một quả cầu vật chất chiếm một thể tích không gian xác định.",
            "Do đó, không gian tự do để các phân tử chuyển động không phải là toàn bộ thể tích V của bình chứa.",
            "Một phần thể tích đã bị chính các phân tử khác chiếm chỗ và ngăn cản chuyển động.",
            "Gọi b là thể tích chiếm chỗ hiệu dụng của một mol khí, thì thể tích tự do thực tế phải là V trừ đi n nhân b.",
            "Đây chính là hiệu chỉnh thể tích đầu tiên trong phương trình!"
        ]
    },
    # Scene 3: Pressure Correction - a parameter (~75s - ~125s)
    {
        "scene_id": 3,
        "title": "HIỆU CHỈNH ÁP SUẤT TƯƠNG TÁC (HẰNG SỐ a)",
        "badge": "PHẦN 3: LỰC TƯƠNG TÁC",
        "lines": [
            "Hiệu chỉnh thứ hai, cũng là điểm cốt lõi nhất, chính là lực hút tương tác giữa các phân tử.",
            "Ở sâu bên trong lòng khối khí, mỗi phân tử bị các phân tử bao quanh hút đều về mọi hướng, khiến hợp lực bằng không.",
            "Nhưng khi một phân tử bay đến gần sát thành bình, phía sau nó là một tập hợp các phân tử khác đang hút kéo nó lại.",
            "Lực kéo giật lùi này làm giảm đáng kể vận tốc và động lượng khi phân tử va đập vào thành bình.",
            "Kết quả là, áp suất thực tế P mà ta đo được luôn nhỏ hơn áp suất lý tưởng ban đầu!",
            "Đại lượng sụt giảm này gọi là áp suất nội, tỷ lệ thuận với bình phương mật độ phân tử.",
            "Van der Waals xác định lượng bù áp suất nội là a nhân n bình phương chia cho V bình phương.",
            "Để có áp suất lý tưởng, ta phải cộng thêm lượng bù này vào áp suất thực tế!"
        ]
    },
    # Scene 4: Full Equation & Molecular Constants (~125s - ~160s)
    {
        "scene_id": 4,
        "title": "PHƯƠNG TRÌNH HOÀN CHỈNH & Ý NGHĨA",
        "badge": "PHẦN 4: PHƯƠNG TRÌNH KINH ĐIỂN",
        "lines": [
            "Kết hợp cả hai hiệu chỉnh trên, ta có phương trình Van der Waals kinh điển cho khí thực.",
            "Mở ngoặc P cộng a nhân n bình phương trên V bình phương đóng ngoặc, nhân với V trừ n b, bằng n R T.",
            "Đối với một mol khí, phương trình được viết gọn lại là, P cộng a trên V m bình phương, nhân với V m trừ b, bằng R T.",
            "Hằng số a phản ánh độ mạnh của tương tác.",
            "Còn hằng số b biểu thị độ lớn thể tích riêng của chúng.",
            "Ví dụ, Khí Helium có phân tử siêu nhỏ nên a và b rất bé, gần như là khí lý tưởng.",
            "Ngược lại, khí cacbon dioxit và hơi nước có phân tử lớn và lực hút mạnh nên a và b rất cao."
        ]
    },
    # Scene 5: Isotherms, Critical Point & Outro (~160s - ~185s)
    {
        "scene_id": 5,
        "title": "ĐƯỜNG ĐẲNG NHIỆT & KẾT LUẬN",
        "badge": "PHẦN 5: ĐẲNG NHIỆT & TỚI HẠN",
        "lines": [
            "Khi ở áp suất rất thấp hoặc nhiệt độ cao, thể tích V trở nên rất lớn so với n b.",
            "Lúc này, các số hạng hiệu chỉnh triệt tiêu và phương trình Van der Waals quay về định luật khí lý tưởng.",
            "Đặc biệt, phương trình này còn mô tả chính xác hiện tượng hóa lỏng và dự đoán nhiệt độ tới hạn của chất khí.",
            "Thành tựu vĩ đại này đã mang về cho Van der Waals giải Nobel Vật lý danh giá vào năm 1910.",
            "Cảm ơn các bạn đã theo dõi! Hãy nhấn Like và Đăng ký kênh MTSEducation để đón xem thêm nhiều bài học khoa học thú vị nhé!"
        ]
    }
]

async def synthesize_with_retry(text, out_mp3, max_retries=6):
    for attempt in range(max_retries):
        try:
            if os.path.exists(out_mp3):
                try:
                    os.remove(out_mp3)
                except Exception:
                    pass
            comm = edge_tts.Communicate(text, voice="vi-VN-NamMinhNeural", rate="+4%")
            await asyncio.wait_for(comm.save(out_mp3), timeout=12.0)
            if os.path.exists(out_mp3) and os.path.getsize(out_mp3) > 1000:
                return True
        except Exception as e:
            print(f"Retry {attempt+1}/{max_retries} for line '{text[:25]}...': {e}", flush=True)
            await asyncio.sleep(1.0 * (attempt + 1))
    raise RuntimeError(f"Failed to synthesize after {max_retries} attempts: {text}")

async def generate_speech_clips():
    clip_info = []
    
    global_idx = 0
    for scene in SCENES_SCRIPT:
        scene_id = scene["scene_id"]
        for line_idx, line_text in enumerate(scene["lines"]):
            out_mp3 = os.path.join(OUT_DIR, f"clip_{global_idx:03d}.mp3")
            out_wav = os.path.join(OUT_DIR, f"clip_{global_idx:03d}.wav")
            
            # Check if valid wav already exists
            if not (os.path.exists(out_wav) and os.path.getsize(out_wav) > 5000):
                await synthesize_with_retry(line_text, out_mp3)
                # Convert to 44100Hz stereo wav
                subprocess.run([
                    FFMPEG, "-y", "-i", out_mp3,
                    "-ar", "44100", "-ac", "2", out_wav
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                await asyncio.sleep(0.3)  # Gentle spacing to avoid rate limiting
            
            data, sr = sf.read(out_wav)
            dur = len(data) / sr
            
            clip_info.append({
                "clip_id": global_idx,
                "scene_id": scene_id,
                "scene_title": scene["title"],
                "scene_badge": scene["badge"],
                "text": line_text,
                "duration": dur,
                "wav_path": out_wav
            })
            print(f"Ready clip {global_idx:03d} ({dur:.2f}s): {line_text[:45]}...")
            global_idx += 1

    return clip_info

async def main():
    print("Generating speech clips...")
    clips = await generate_speech_clips()
    
    # Concatenate with 0.22s pause between sentences
    pause_samples = int(0.22 * 44100)
    pause_data = np.zeros((pause_samples, 2), dtype=np.float32)
    
    full_audio = []
    current_time = 0.0
    timeline = []
    
    for c in clips:
        data, sr = sf.read(c["wav_path"])
        if len(data.shape) == 1:
            data = np.column_stack([data, data])
            
        start_t = current_time
        dur = len(data) / sr
        end_t = start_t + dur
        
        timeline.append({
            "clip_id": c["clip_id"],
            "scene_id": c["scene_id"],
            "scene_title": c["scene_title"],
            "scene_badge": c["scene_badge"],
            "text": c["text"],
            "start": start_t,
            "end": end_t,
            "duration": dur
        })
        
        full_audio.append(data)
        full_audio.append(pause_data)
        current_time = end_t + 0.22
        
    merged = np.vstack(full_audio)
    merged_wav = os.path.join(OUT_DIR, "narration_master.wav")
    sf.write(merged_wav, merged, 44100)
    
    total_dur = len(merged) / 44100
    print(f"\nNarration Master Generated! Total Duration: {total_dur:.2f}s ({total_dur/60:.2f} mins)")
    
    # Save timeline metadata
    meta_path = os.path.join(OUT_DIR, "timeline.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_duration": total_dur,
            "scenes": SCENES_SCRIPT,
            "timeline": timeline
        }, f, ensure_ascii=False, indent=2)
        
    print(f"Timeline metadata saved to: {meta_path}")

if __name__ == "__main__":
    asyncio.run(main())

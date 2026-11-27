# -*- coding: utf-8 -*-
"""
Tạo bộ Demo Giọng Nữ Ngọt Ngào (Sweet Female Voice Demo) cho DU_AN.
Kết hợp:
1. Điều chỉnh ngữ điệu (rate & pitch) theo từng câu/vế câu bằng Microsoft HoaiMyNeural.
2. Chuỗi xử lý âm thanh phòng thu (Warm EQ + De-harsh + Air Shimmer + Soft Compressor + Room Intimacy).
3. Nhạc nền Felt-Piano / Music-Box nhẹ nhàng tự tổng hợp (100% không bản quyền) với hiệu ứng tự động giảm âm (ducking) khi có giọng nói.
"""
import asyncio
import base64
import json
import os
import subprocess
import sys
import edge_tts
import imageio_ffmpeg
import numpy as np
import soundfile as sf

sys.stdout.reconfigure(encoding="utf-8")

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
SR = 44100
VOICE = "vi-VN-HoaiMyNeural"

BASE_OUT_DIR = r"C:\Users\DELL\Documents\CODE\DU_AN\02_San_Pham_Hoan_Chinh\Audio_Va_Timeline\Demo_Giong_Nu_Ngot_Ngao"
TEMP_DIR = os.path.join(BASE_OUT_DIR, "_temp_phrases")
os.makedirs(TEMP_DIR, exist_ok=True)

DEMOS = [
    {
        "slug": "01_tam_tinh_ngot_ngao",
        "title": "Tâm Tình Ngọt Ngào & Chữa Lành",
        "subtitle": "Ấm áp, dịu dàng như radio đêm khuya",
        "tag": "Ngọt ngào nhất",
        "with_bgm": True,
        "phrases": [
            {
                "text": "Chào bạn nha! Hôm nay của bạn thế nào rồi, có vất vả lắm không?",
                "rate": "-4%",
                "pitch": "+6Hz",
                "pause": 0.40,
            },
            {
                "text": "Dù ngoài kia có bận rộn đến đâu, thì giây phút này cũng là dành riêng cho bạn nghỉ ngơi đấy.",
                "rate": "-5%",
                "pitch": "+4Hz",
                "pause": 0.42,
            },
            {
                "text": "Hít một hơi thật sâu nè, thả lỏng đôi vai một chút xíu thôi.",
                "rate": "-6%",
                "pitch": "+4Hz",
                "pause": 0.45,
            },
            {
                "text": "Cảm ơn bạn vì hôm nay đã cố gắng thật nhiều. Chúc bạn luôn bình yên, và giữ mãi nụ cười thật ngọt ngào trên môi nhé!",
                "rate": "-4%",
                "pitch": "+5Hz",
                "pause": 0.20,
            },
        ],
    },
    {
        "slug": "02_ke_chuyen_trong_treo",
        "title": "Kể Chuyện & Vlog Trong Trẻo",
        "subtitle": "Tươi tắn, đáng yêu cho TikTok / Reels / Podcast ngắn",
        "tag": "Trong trẻo",
        "with_bgm": True,
        "phrases": [
            {
                "text": "Có bao giờ bạn tự hỏi, điều gì khiến một ngày bình thường bỗng trở nên thật đặc biệt không?",
                "rate": "-2%",
                "pitch": "+7Hz",
                "pause": 0.36,
            },
            {
                "text": "Đôi khi chẳng phải điều gì lớn lao đâu nha, chỉ là một tách trà thơm ấm nóng, một bản nhạc dịu êm,",
                "rate": "-3%",
                "pitch": "+6Hz",
                "pause": 0.32,
            },
            {
                "text": "và một lời chào thật ngọt ngào, gửi đến bạn ngay lúc này nè!",
                "rate": "-3%",
                "pitch": "+7Hz",
                "pause": 0.20,
            },
        ],
    },
    {
        "slug": "03_thuyet_minh_tuoi_tan",
        "title": "Thuyết Minh Bài Giảng Thân Thiện",
        "subtitle": "Rõ chữ, truyền cảm hứng học tập cho video bài giảng",
        "tag": "Bài giảng",
        "with_bgm": False,
        "phrases": [
            {
                "text": "Xin chào các bạn học sinh thân mến! Chào mừng các bạn đã quay trở lại với bài học thú vị ngày hôm nay nha!",
                "rate": "+0%",
                "pitch": "+6Hz",
                "pause": 0.34,
            },
            {
                "text": "Đừng lo lắng nếu thấy công thức hơi dài một chút nhé, vì mình sẽ bật mí ngay một mẹo siêu dễ nhớ!",
                "rate": "+0%",
                "pitch": "+5Hz",
                "pause": 0.35,
            },
            {
                "text": "Chỉ cần ba phút thôi là bạn sẽ nắm trọn bí kíp ngay nè. Cùng mình bắt đầu nhé!",
                "rate": "+0%",
                "pitch": "+6Hz",
                "pause": 0.20,
            },
        ],
    },
]


async def synth_phrase(text: str, rate: str, pitch: str, out_wav: str):
    raw_mp3 = out_wav.replace(".wav", ".mp3")
    for attempt in range(5):
        try:
            if os.path.exists(raw_mp3):
                os.remove(raw_mp3)
            comm = edge_tts.Communicate(text, voice=VOICE, rate=rate, pitch=pitch)
            await asyncio.wait_for(comm.save(raw_mp3), timeout=15.0)
            if os.path.exists(raw_mp3) and os.path.getsize(raw_mp3) > 800:
                break
        except Exception as e:
            print(f"  Retry {attempt + 1} for '{text[:25]}...': {e}")
            await asyncio.sleep(1.0 * (attempt + 1))
    else:
        raise RuntimeError(f"Failed to synthesize: {text}")

    subprocess.run(
        [FFMPEG, "-y", "-i", raw_mp3, "-ar", str(SR), "-ac", "2", out_wav],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )


def trim_and_microfade(audio: np.ndarray, threshold: float = 0.003) -> np.ndarray:
    """Cắt khoảng lặng thừa ở đầu/cuối mỗi vế câu và thêm micro-fade mượt chống click."""
    mono = np.max(np.abs(audio), axis=1)
    idx = np.where(mono > threshold)[0]
    if len(idx) == 0:
        return audio
    pad_head = int(0.03 * SR)
    pad_tail = int(0.06 * SR)
    start = max(0, idx[0] - pad_head)
    end = min(len(audio), idx[-1] + pad_tail)
    clipped = audio[start:end].copy()

    fade_in = min(int(0.018 * SR), len(clipped) // 4)
    fade_out = min(int(0.030 * SR), len(clipped) // 4)
    if fade_in > 0:
        env_in = (0.5 * (1.0 - np.cos(np.pi * np.linspace(0, 1, fade_in))))[:, None]
        clipped[:fade_in] *= env_in
    if fade_out > 0:
        env_out = (0.5 * (1.0 + np.cos(np.pi * np.linspace(0, 1, fade_out))))[:, None]
        clipped[-fade_out:] *= env_out
    return clipped


def add_cozy_booth_air(stereo: np.ndarray) -> np.ndarray:
    """Tạo độ ấm không gian phòng thu rất nhẹ (decorrelated L/R early reflection ở -27dB)."""
    n = len(stereo)
    out = stereo.copy()
    delay_l = int(0.034 * SR)
    delay_r = int(0.049 * SR)
    # Làm dịu tần số cao của phản xạ bằng trung bình trượt ngắn để ấm tự nhiên
    kernel = np.ones(14) / 14.0
    mono = 0.5 * (stereo[:, 0] + stereo[:, 1])
    warm_ref = np.convolve(mono, kernel, mode="same")
    if n > delay_l:
        out[delay_l:, 0] += warm_ref[:-delay_l] * 0.042
    if n > delay_r:
        out[delay_r:, 1] += warm_ref[:-delay_r] * 0.038
    return out


def master_sweet_vocal(raw_wav: str, mastered_wav: str, mastered_mp3: str, preview_mp3: str):
    """Áp dụng EQ ngọt ấm + khử chói 3.4kHz + tăng độ thoáng (air) + nén mượt."""
    af_chain = (
        "highpass=f=75,"
        "equalizer=f=195:t=q:w=1.1:g=2.1,"
        "equalizer=f=3400:t=q:w=1.5:g=-2.0,"
        "treble=g=2.3:f=9500,"
        "acompressor=threshold=-19dB:ratio=2.1:attack=14:release=180:makeup=2.4dB,"
        "alimiter=limit=0.93"
    )
    temp_eq_wav = raw_wav.replace(".wav", "_eq.wav")
    subprocess.run(
        [FFMPEG, "-y", "-i", raw_wav, "-af", af_chain, "-ar", str(SR), "-ac", "2", temp_eq_wav],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )
    eq_audio, _ = sf.read(temp_eq_wav)
    sweet_audio = add_cozy_booth_air(eq_audio)
    peak = np.max(np.abs(sweet_audio))
    if peak > 0.94:
        sweet_audio *= 0.94 / peak
    sf.write(mastered_wav, sweet_audio, SR, subtype="PCM_16")

    # Xuất MP3 chất lượng cao 192kbps
    subprocess.run(
        [FFMPEG, "-y", "-i", mastered_wav, "-codec:a", "libmp3lame", "-b:a", "192k", mastered_mp3],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )
    # Xuất MP3 gọn nhẹ 64kbps cho trình nghe thử trực tiếp
    subprocess.run(
        [FFMPEG, "-y", "-i", mastered_wav, "-codec:a", "libmp3lame", "-b:a", "64k", "-ac", "1", preview_mp3],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )


def synthesize_felt_piano_bgm(duration_sec: float) -> np.ndarray:
    """Tổng hợp tiếng đàn Felt-Piano / Rhodes dịu dàng (Fmaj9 - Em7 - Dm9 - Cmaj9)."""
    total_samples = int(duration_sec * SR)
    bgm = np.zeros((total_samples, 2), dtype=np.float64)

    # Hợp âm rải nhẹ nhàng (tần số Hz, độ lệch pan -1..1)
    chords = [
        # Fmaj9: F3, C4, E4, G4, A4
        [(174.61, -0.05), (261.63, -0.22), (329.63, 0.18), (392.00, -0.28), (440.00, 0.30)],
        # Em7: E3, B3, D4, G4, B4
        [(164.81, 0.05), (246.94, -0.20), (293.66, 0.22), (392.00, -0.25), (493.88, 0.32)],
        # Dm9: D3, A3, C4, E4, F4
        [(146.83, -0.04), (220.00, -0.18), (261.63, 0.20), (329.63, -0.26), (349.23, 0.28)],
        # Cmaj9: C3, G3, B3, D4, E4
        [(130.81, 0.00), (196.00, -0.20), (246.94, 0.20), (293.66, -0.28), (329.63, 0.30)],
    ]

    bar_dur = 3.60
    arp_offsets = [0.00, 0.34, 0.68, 1.04, 1.52]
    note_dur = 3.20
    note_samples = int(note_dur * SR)
    t = np.arange(note_samples) / SR

    attack_samples = int(0.022 * SR)
    attack_env = np.ones_like(t)
    attack_env[:attack_samples] = 0.5 * (1.0 - np.cos(np.pi * np.linspace(0, 1, attack_samples)))

    bar_idx = 0
    cur_bar_time = 0.0
    while cur_bar_time < duration_sec:
        chord = chords[bar_idx % len(chords)]
        for i, (freq, pan) in enumerate(chord):
            onset = int((cur_bar_time + arp_offsets[i]) * SR)
            if onset >= total_samples:
                break
            length = min(note_samples, total_samples - onset)
            tt = t[:length]
            # Âm sắc ấm áp của Felt Piano pha chút chuông mảnh
            tone = (
                1.00 * np.sin(2 * np.pi * freq * tt) * np.exp(-tt / 2.1)
                + 0.20 * np.sin(2 * np.pi * (2 * freq) * tt) * np.exp(-tt / 1.0)
                + 0.04 * np.sin(2 * np.pi * (3 * freq) * tt) * np.exp(-tt / 0.50)
                + 0.018 * np.sin(2 * np.pi * (4 * freq) * tt) * np.exp(-tt / 0.14)
            )
            vel = 0.85 if i == 0 else (0.72 if i < 3 else 0.64)
            wave = tone * attack_env[:length] * vel

            gain_l = np.sqrt(0.5 * (1.0 - pan))
            gain_r = np.sqrt(0.5 * (1.0 + pan))
            bgm[onset : onset + length, 0] += wave * gain_l
            bgm[onset : onset + length, 1] += wave * gain_r

        cur_bar_time += bar_dur
        bar_idx += 1

    peak = np.max(np.abs(bgm))
    if peak > 0:
        bgm /= peak
    return bgm


def mix_vocal_with_piano(vocal_wav: str, out_mix_wav: str, out_mix_mp3: str, preview_mix_mp3: str):
    vocal, _ = sf.read(vocal_wav)
    intro_sec = 1.25
    outro_sec = 2.30
    vocal_dur = len(vocal) / SR
    total_dur = intro_sec + vocal_dur + outro_sec

    bgm = synthesize_felt_piano_bgm(total_dur)
    total_n = len(bgm)
    mix = np.zeros((total_n, 2), dtype=np.float64)

    intro_n = int(intro_sec * SR)
    vocal_end_n = intro_n + len(vocal)

    # Đường bao âm lượng BGM: dạo đầu dịu -> duck xuống dưới giọng nói -> ngân nhẹ cuối bài rồi tắt dần
    bgm_env = np.full(total_n, 0.082, dtype=np.float64)
    # Fade-in 0.8s lên 0.145 rồi hạ mượt xuống 0.082 trước khi giọng đọc vào
    fi_n = int(0.75 * SR)
    bgm_env[:fi_n] = np.linspace(0.0, 0.145, fi_n)
    bgm_env[fi_n:intro_n] = np.linspace(0.145, 0.082, intro_n - fi_n)

    # Sau khi giọng đọc kết thúc, nâng nhẹ lên 0.125 rồi fade-out mượt
    swell_n = int(0.55 * SR)
    if vocal_end_n + swell_n < total_n:
        bgm_env[vocal_end_n : vocal_end_n + swell_n] = np.linspace(0.082, 0.125, swell_n)
        rem_n = total_n - (vocal_end_n + swell_n)
        bgm_env[vocal_end_n + swell_n :] = 0.125 * (
            0.5 * (1.0 + np.cos(np.pi * np.linspace(0, 1, rem_n)))
        )

    mix += bgm * bgm_env[:, None]
    mix[intro_n:vocal_end_n] += vocal * 0.96

    peak = np.max(np.abs(mix))
    if peak > 0.95:
        mix *= 0.95 / peak

    sf.write(out_mix_wav, mix, SR, subtype="PCM_16")
    subprocess.run(
        [FFMPEG, "-y", "-i", out_mix_wav, "-codec:a", "libmp3lame", "-b:a", "192k", out_mix_mp3],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )
    subprocess.run(
        [FFMPEG, "-y", "-i", out_mix_wav, "-codec:a", "libmp3lame", "-b:a", "64k", "-ac", "1", preview_mix_mp3],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )
    return total_dur


async def main():
    manifest = []
    for demo in DEMOS:
        slug = demo["slug"]
        print(f"\n=== Đang tạo Demo: {demo['title']} ({slug}) ===")
        segments = []
        full_transcript = []
        for idx, p in enumerate(demo["phrases"]):
            p_wav = os.path.join(TEMP_DIR, f"{slug}_p{idx:02d}.wav")
            await synth_phrase(p["text"], p["rate"], p["pitch"], p_wav)
            audio, _ = sf.read(p_wav)
            trimmed = trim_and_microfade(audio)
            segments.append(trimmed)
            pause_n = int(p["pause"] * SR)
            if pause_n > 0:
                segments.append(np.zeros((pause_n, 2), dtype=np.float64))
            full_transcript.append(p["text"])
            await asyncio.sleep(0.25)

        concat_audio = np.vstack(segments)
        raw_concat_wav = os.path.join(TEMP_DIR, f"{slug}_raw.wav")
        sf.write(raw_concat_wav, concat_audio, SR, subtype="PCM_16")

        vocal_wav = os.path.join(BASE_OUT_DIR, f"{slug}_giong_moc.wav")
        vocal_mp3 = os.path.join(BASE_OUT_DIR, f"{slug}_giong_moc.mp3")
        preview_vocal = os.path.join(TEMP_DIR, f"{slug}_preview_vocal.mp3")
        master_sweet_vocal(raw_concat_wav, vocal_wav, vocal_mp3, preview_vocal)
        vocal_dur = len(concat_audio) / SR
        print(f"  -> Giọng mộc Studio: {vocal_mp3} ({vocal_dur:.2f}s)")

        entry = {
            "slug": slug,
            "title": demo["title"],
            "subtitle": demo["subtitle"],
            "tag": demo["tag"],
            "transcript": " ".join(full_transcript),
            "phrases": [p["text"] for p in demo["phrases"]],
            "vocal_wav": vocal_wav,
            "vocal_mp3": vocal_mp3,
            "vocal_duration": round(vocal_dur, 2),
            "preview_vocal_b64": base64.b64encode(open(preview_vocal, "rb").read()).decode("ascii"),
        }

        if demo["with_bgm"]:
            mix_wav = os.path.join(BASE_OUT_DIR, f"{slug}_mix_piano.wav")
            mix_mp3 = os.path.join(BASE_OUT_DIR, f"{slug}_mix_piano.mp3")
            preview_mix = os.path.join(TEMP_DIR, f"{slug}_preview_mix.mp3")
            mix_dur = mix_vocal_with_piano(vocal_wav, mix_wav, mix_mp3, preview_mix)
            print(f"  -> Bản phối Piano ấm áp: {mix_mp3} ({mix_dur:.2f}s)")
            entry["mix_wav"] = mix_wav
            entry["mix_mp3"] = mix_mp3
            entry["mix_duration"] = round(mix_dur, 2)
            entry["preview_mix_b64"] = base64.b64encode(open(preview_mix, "rb").read()).decode("ascii")

        manifest.append(entry)

    manifest_path = os.path.join(TEMP_DIR, "demo_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"\nHoàn tất! Manifest lưu tại: {manifest_path}")


if __name__ == "__main__":
    asyncio.run(main())

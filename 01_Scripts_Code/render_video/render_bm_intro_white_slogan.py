# -*- coding: utf-8 -*-
"""
BM Modern White-Studio 3D Extruded Intro Generator (1920x1080 @ 60fps, 5.00s)
Inspired by reference 3D architectural intro + BM modern effects:
- Pure crisp #FFFFFF white background
- BM Logo + Slogan underneath: "KHƠI NGUỒN TRI THỨC, KIẾN TẠO TƯƠNG LAI"
- Real 3D perspective camera sweep (homography + multi-layer 3D extruded walls + soft floor shadow)
- RGB chromatic aberration edge shimmer on 3D rise + 4-point star glint + diagonal specular light sweep
- Graceful 3D pull-back zoom & dissolve into pure #FFFFFF white at the end

Outputs 2 primary videos (+ 1 bonus combined audio mix):
1. BM_Intro_1_NenTrang_HieuUng_VoiceBM.mp4  (Edits above + Modern SFX & English "BM" /bi: em/ glide)
2. BM_Intro_2_NenTrang_NhacMau_LocTapAm.mp4 (Edits above + Denoised & Stereo-Remastered Sample BGM)
3. BM_Intro_2_KemVoiceBM_NhacMau_LocTapAm.mp4 (Bonus: Cleaned Sample BGM + "BM" voiceover)
"""

import os
import sys
import math
import time
import asyncio
import subprocess
import numpy as np
import cv2
import soundfile as sf
import edge_tts
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

BASE_DIR = r"C:\Users\DELL\Documents\CODE\DU_AN"
WORK_DIR = os.path.join(BASE_DIR, "video_build", "bm_white_slogan_work")
OUT_DIR = os.path.join(BASE_DIR, "02_San_Pham_Hoan_Chinh", "Video_Intro_BM")
UPLOADED_LOGO = r"C:/Users/DELL/.gemini/antigravity/brain/fc42d3cf-3a2f-4081-bebf-02ad4d23944a/.user_uploaded/media_1795590490460_51e6674a.mp4"
LOGO_JPG = r"C:/Users/DELL/.gemini/antigravity/brain/fc42d3cf-3a2f-4081-bebf-02ad4d23944a/.user_uploaded/media_1795588966074_a11371d4.jpg"
REF_VIDEO = r"C:/Users/DELL/.gemini/antigravity/brain/fc42d3cf-3a2f-4081-bebf-02ad4d23944a/.user_uploaded/media_1795590490460_51e6674a.mp4"

os.makedirs(WORK_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

W, H = 1920, 1080
FPS = 60
DURATION = 5.00
N_FRAMES = int(round(DURATION * FPS))  # 300 frames
SR = 48000

SLOGAN_TEXT = "KHƠI NGUỒN TRI THỨC, KIẾN TẠO TƯƠNG LAI"


# ==============================================================================
# Math & Easing Helpers
# ==============================================================================
def clamp01(x):
    return np.clip(x, 0.0, 1.0)


def smoothstep(edge0, edge1, x):
    t = np.clip((x - edge0) / max(1e-6, (edge1 - edge0)), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def smootherstep(edge0, edge1, x):
    t = np.clip((x - edge0) / max(1e-6, (edge1 - edge0)), 0.0, 1.0)
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)


def ease_out_expo(t):
    t = float(np.clip(t, 0.0, 1.0))
    return 1.0 if t >= 1.0 else 1.0 - math.pow(2.0, -10.0 * t)


def ease_out_cubic(t):
    t = float(np.clip(t, 0.0, 1.0))
    return 1.0 - math.pow(1.0 - t, 3.0)


def ease_in_out_cubic(t):
    t = float(np.clip(t, 0.0, 1.0))
    return 4.0 * t * t * t if t < 0.5 else 1.0 - math.pow(-2.0 * t + 2.0, 3.0) / 2.0


# ==============================================================================
# 1. AUDIO ENGINE:
#    Track 1: Custom Modern SFX + English "BM" ("bi em") Stereo Glide (5.00s)
#    Track 2: Surgically Denoised & Stereo-Remastered Sample BGM (5.00s)
#    Track 2B: Cleaned Sample BGM + "BM" Voiceover (5.00s)
# ==============================================================================
async def ensure_voice_raw(wav_path):
    if os.path.exists(wav_path) and os.path.getsize(wav_path) > 5000:
        return
    mp3_path = wav_path.replace(".wav", ".mp3")
    comm = edge_tts.Communicate("B M", voice="en-US-ChristopherNeural", rate="-4%", pitch="-2Hz")
    await comm.save(mp3_path)
    subprocess.run(
        [FFMPEG, "-y", "-i", mp3_path, "-ar", str(SR), "-ac", "1", wav_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )


def fft_eq(signal, sr, gains_db_points):
    n = len(signal)
    spec = np.fft.rfft(signal)
    freqs = np.fft.rfftfreq(n, d=1.0 / sr)
    log_f = np.log10(np.maximum(freqs, 10.0))
    pts_f = np.log10([p[0] for p in gains_db_points])
    pts_g = [p[1] for p in gains_db_points]
    db_curve = np.interp(log_f, pts_f, pts_g)
    hp = np.clip((freqs - 45.0) / 45.0, 0.0, 1.0) ** 2
    gain = (10.0 ** (db_curve / 20.0)) * hp
    return np.fft.irfft(spec * gain, n=n).astype(np.float32)


def make_swept_whoosh(n_samples, sr, t_start, t_end, f_start, f_peak, f_end, pan_start, pan_end, amp=0.22):
    out = np.zeros((n_samples, 2), dtype=np.float32)
    i0 = max(0, int(t_start * sr))
    i1 = min(n_samples, int(t_end * sr))
    length = i1 - i0
    if length <= 1024:
        return out

    rng = np.random.default_rng(int(t_start * 10000) + 42)
    white = rng.standard_normal(length).astype(np.float32)
    spec = np.fft.rfft(white)
    freqs = np.fft.rfftfreq(length, 1.0 / sr)
    pink_weight = 1.0 / np.sqrt(np.maximum(freqs, 40.0) / 200.0)
    pink = np.fft.irfft(spec * pink_weight, n=length).astype(np.float32)

    win_size = 1024
    hop = 256
    window = np.hanning(win_size).astype(np.float32)
    y = np.zeros(length + win_size, dtype=np.float32)
    f_bins = np.fft.rfftfreq(win_size, 1.0 / sr)

    n_hops = (length - win_size) // hop
    for h in range(max(1, n_hops)):
        pos = h * hop
        prog = h / max(1, n_hops - 1)
        if prog < 0.45:
            p2 = float(smoothstep(0.0, 0.45, prog))
            fc = f_start * ((f_peak / f_start) ** p2)
        else:
            p2 = float(smoothstep(0.45, 1.0, prog))
            fc = f_peak * ((f_end / f_peak) ** p2)

        frame = pink[pos : pos + win_size] * window
        fspec = np.fft.rfft(frame)
        log_dist = np.log2(np.maximum(f_bins, 20.0) / fc)
        bp = np.exp(-0.5 * (log_dist / 0.65) ** 2)
        filtered = np.fft.irfft(fspec * bp, n=win_size) * window
        y[pos : pos + win_size] += filtered

    y = y[:length]
    mx = np.max(np.abs(y)) + 1e-6
    y = (y / mx) * amp
    t_norm = np.linspace(0.0, 1.0, length, dtype=np.float32)
    env = np.maximum(0.0, np.sin(np.pi * (t_norm ** 0.85))) ** 1.6
    y *= env

    pan = pan_start + (pan_end - pan_start) * smoothstep(0.0, 1.0, np.linspace(0, 1, length))
    theta = (pan + 1.0) * (np.pi / 4.0)
    out[i0:i1, 0] += (y * np.cos(theta)).astype(np.float32)
    out[i0:i1, 1] += (y * np.sin(theta)).astype(np.float32)
    return out


def apply_stereo_studio_reverb(stereo_in, sr, wet=0.25, predelay_ms=28.0):
    n = len(stereo_in)
    mono = 0.5 * (stereo_in[:, 0] + stereo_in[:, 1])
    tank_in = fft_eq(mono, sr, [(60, -12), (180, -2), (1200, 0), (4500, -4), (9000, -14), (16000, -24)])

    predelay = int(predelay_ms * 0.001 * sr)
    rev_L = np.zeros(n, dtype=np.float32)
    rev_R = np.zeros(n, dtype=np.float32)

    taps_L = [(31, 0.42), (47, 0.34), (73, 0.28), (109, 0.23), (157, 0.19), (223, 0.15), (307, 0.115), (401, 0.085), (521, 0.06), (659, 0.04)]
    taps_R = [(37, 0.42), (53, 0.34), (83, 0.28), (127, 0.23), (173, 0.19), (241, 0.15), (331, 0.115), (433, 0.085), (557, 0.06), (691, 0.04)]

    for delay_ms, gain in taps_L:
        d = predelay + int(delay_ms * 0.001 * sr)
        if d < n:
            rev_L[d:] += tank_in[: n - d] * gain
    for delay_ms, gain in taps_R:
        d = predelay + int(delay_ms * 0.001 * sr)
        if d < n:
            rev_R[d:] += tank_in[: n - d] * gain

    smear_d = int(0.013 * sr)
    if smear_d < n:
        rev_L[smear_d:] = 0.72 * rev_L[smear_d:] + 0.28 * rev_R[: n - smear_d]
        rev_R[smear_d:] = 0.72 * rev_R[smear_d:] + 0.28 * rev_L[: n - smear_d]

    out = stereo_in.copy()
    out[:, 0] += wet * rev_L
    out[:, 1] += wet * rev_R
    return out


def build_voice_bm_stereo_layer(n_total, voice_start_t=1.55, amp=0.84):
    raw_voice_wav = os.path.join(WORK_DIR, "v_christopher_bm_space.wav")
    asyncio.run(ensure_voice_raw(raw_voice_wav))
    v_data, _ = sf.read(raw_voice_wav)
    if v_data.ndim > 1:
        v_data = v_data[:, 0]
    v_data = v_data.astype(np.float32)

    nz = np.where(np.abs(v_data) > 0.008)[0]
    v0 = max(0, nz[0] - int(0.018 * SR))
    v1 = min(len(v_data), nz[-1] + int(0.085 * SR))
    voice = v_data[v0:v1].copy()

    fi = int(0.012 * SR)
    fo = int(0.055 * SR)
    voice[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32) ** 1.5
    voice[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32) ** 1.5

    voice = fft_eq(
        voice,
        SR,
        [(60, -10.0), (110, +1.5), (170, +3.2), (360, -2.2), (1200, +0.5), (3400, +2.6), (6800, +4.2), (11500, +4.5), (16500, +1.0)],
    )
    voice = voice / (np.max(np.abs(voice)) + 1e-6)
    voice = np.tanh(1.25 * voice) / np.tanh(1.25) * amp

    vs0 = int(voice_start_t * SR)
    vs1 = min(n_total, vs0 + len(voice))
    v_len = vs1 - vs0
    voice = voice[:v_len]

    v_prog = np.linspace(0.0, 1.0, v_len, dtype=np.float32)
    v_pan = -0.20 + 0.40 * smoothstep(0.08, 0.88, v_prog)
    v_theta = (v_pan + 1.0) * (np.pi / 4.0)

    voice_track = np.zeros((n_total, 2), dtype=np.float32)
    voice_track[vs0:vs1, 0] = voice * np.cos(v_theta)
    haas = int(0.00035 * SR)
    r_sig = voice * np.sin(v_theta)
    voice_track[vs0 + haas : min(n_total, vs1 + haas), 1] = r_sig[: min(v_len, n_total - (vs0 + haas))]

    return apply_stereo_studio_reverb(voice_track, SR, wet=0.25, predelay_ms=28.0)


def build_all_audio_tracks():
    n_total = int(round(DURATION * SR))
    t = np.arange(n_total, dtype=np.float32) / SR

    # ------------------------------------------------------------------
    # Track 1: Custom Modern SFX + English "BM" Stereo Glide (5.00s)
    # ------------------------------------------------------------------
    mix1 = np.zeros((n_total, 2), dtype=np.float32)
    mix1 += make_swept_whoosh(n_total, SR, 0.05, 0.98, 170, 1950, 420, -0.80, -0.05, amp=0.17)
    mix1 += make_swept_whoosh(n_total, SR, 0.16, 1.05, 210, 2300, 480, +0.80, +0.05, amp=0.17)

    # Silky contour riser (0.08s -> 1.02s)
    rm = (t >= 0.08) & (t <= 1.02)
    tr = (t[rm] - 0.08) / 0.94
    phase_r = 2.0 * np.pi * SR * np.cumsum((260.0 + 920.0 * (tr ** 2.0)) / SR)
    riser_sig = (0.030 * np.sin(phase_r) + 0.015 * np.sin(2.0 * phase_r)) * (np.maximum(0.0, np.sin(np.pi * tr)) ** 1.3)
    mix1[rm, 0] += riser_sig * (0.6 + 0.4 * np.cos(6.0 * tr))
    mix1[rm, 1] += riser_sig * (0.6 + 0.4 * np.sin(6.0 * tr))

    # Clean Sub-Bass Lock-in + Crystal Chime at t = 1.02s
    imp_t0 = 1.02
    im = (t >= imp_t0) & (t <= 2.00)
    ti = t[im] - imp_t0
    inst_freq = 48.0 + 90.0 * np.exp(-ti / 0.038)
    sub_phase = 2.0 * np.pi * np.cumsum(inst_freq / SR)
    sub_env = (1.0 - np.exp(-ti / 0.004)) * np.exp(-ti / 0.24)
    sub_wave = np.tanh(1.35 * np.sin(sub_phase)) * sub_env * 0.40
    glass_click = (
        0.085 * np.sin(2 * np.pi * 2936.6 * ti) * np.exp(-ti / 0.045)
        + 0.055 * np.sin(2 * np.pi * 4400.0 * ti) * np.exp(-ti / 0.028)
    ) * (1.0 - np.exp(-ti / 0.002))
    mix1[im, 0] += sub_wave + glass_click * 0.95
    mix1[im, 1] += sub_wave + glass_click * 1.05

    # Warm Modern Dmaj9 Crystal Chord (D3, A3, F#4, C#5, E5) from 1.02s -> 4.90s
    cm = (t >= 1.02) & (t <= 4.92)
    tc = t[cm] - 1.02
    notes = [
        (146.83, 0.075, 0.0),    # D3
        (220.00, 0.060, -0.25),  # A3
        (369.99, 0.052, +0.25),  # F#4
        (554.37, 0.042, -0.45),  # C#5
        (659.25, 0.036, +0.45),  # E5
        (1174.66, 0.015, +0.15), # D6 crystal bell
    ]
    pad_L = np.zeros_like(tc)
    pad_R = np.zeros_like(tc)
    attack = 1.0 - np.exp(-tc / 0.06)
    decay = np.exp(-tc / 1.85)
    tail_fade = 1.0 - smoothstep(3.10, 3.82, tc)
    d_in = smoothstep(0.42, 0.56, tc)
    d_out = smoothstep(1.25, 1.58, tc)
    duck = 1.0 - 0.52 * (d_in * (1.0 - d_out))
    pad_env = attack * decay * tail_fade * duck

    for freq, amp, pan in notes:
        s1 = np.sin(2.0 * np.pi * (freq - 0.32) * tc)
        s2 = np.sin(2.0 * np.pi * (freq + 0.32) * tc + 0.7)
        tone = 0.5 * (s1 + s2) + 0.14 * np.sin(4.0 * np.pi * freq * tc) * np.exp(-tc / 0.55)
        th = (pan + 1.0) * (np.pi / 4.0)
        pad_L += tone * amp * math.cos(th)
        pad_R += tone * amp * math.sin(th)

    mix1[cm, 0] += pad_L * pad_env
    mix1[cm, 1] += pad_R * pad_env

    # Light-sweep airy sheen whoosh + "BM" stereo voiceover (1.55s)
    mix1 += make_swept_whoosh(n_total, SR, 1.48, 2.46, 650, 4200, 1100, -0.65, +0.65, amp=0.115)
    voice_layer = build_voice_bm_stereo_layer(n_total, voice_start_t=1.55, amp=0.85)
    mix1 += voice_layer

    # Soft zoom-out air tail (3.75s -> 4.75s)
    mix1 += make_swept_whoosh(n_total, SR, 3.75, 4.75, 950, 520, 180, -0.15, +0.15, amp=0.055)

    master_fade = np.ones(n_total, dtype=np.float32)
    master_fade[: int(0.02 * SR)] = np.linspace(0.0, 1.0, int(0.02 * SR))
    end_mask = t > 4.35
    master_fade[end_mask] = 1.0 - smoothstep(4.35, 4.92, t[end_mask])
    mix1 = np.nan_to_num(mix1 * master_fade[:, None], nan=0.0)
    pk1 = np.max(np.abs(mix1)) + 1e-6
    if pk1 > 0.88:
        mix1 *= 0.88 / pk1

    wav_v1 = os.path.join(WORK_DIR, "audio_v1_modern_bm.wav")
    sf.write(wav_v1, mix1, SR, subtype="PCM_16")

    # ------------------------------------------------------------------
    # Track 2: Surgically Denoised & Stereo-Remastered Sample Video BGM (5.00s)
    # ------------------------------------------------------------------
    ref_raw_wav = os.path.join(WORK_DIR, "ref_extracted_raw.wav")
    subprocess.run(
        [FFMPEG, "-y", "-i", REF_VIDEO, "-ar", str(SR), "-ac", "1", ref_raw_wav],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )
    raw_ref, _ = sf.read(ref_raw_wav)
    mono_ref = raw_ref.astype(np.float32) if raw_ref.ndim == 1 else raw_ref.mean(axis=1).astype(np.float32)

    # Noise reference from silent gap (5.45s -> 6.85s, strictly before "Ta ghi này" at 7.0s!)
    noise_ref = mono_ref[int(5.45 * SR) : int(6.85 * SR)]
    # Exact 5.00s musical intro phrase (0.64s -> 5.64s)
    music_seg = mono_ref[int(0.64 * SR) : int(0.64 * SR) + n_total].copy()

    # STFT Wiener Spectral Denoising + Sub-hum & Codec Mosquito Removal
    n_fft = 2048
    hop = 512
    win = np.hanning(n_fft).astype(np.float32)
    n_fn = max(1, (len(noise_ref) - n_fft) // hop)
    n_mags = [np.abs(np.fft.rfft(noise_ref[k * hop : k * hop + n_fft] * win)) for k in range(n_fn)]
    noise_floor = np.percentile(np.vstack(n_mags), 88, axis=0) if n_mags else np.zeros(n_fft // 2 + 1)
    freqs_stft = np.fft.rfftfreq(n_fft, 1.0 / SR)
    codec_floor = 0.0019 * (1.0 + 2.6 * np.clip((freqs_stft - 4800.0) / 7000.0, 0.0, 1.0))
    thresh = np.maximum(noise_floor * 2.3, codec_floor)

    padded = np.pad(music_seg, (n_fft, n_fft))
    clean_pad = np.zeros_like(padded)
    wsum = np.zeros_like(padded)
    for k in range((len(padded) - n_fft) // hop):
        p = k * hop
        sp = np.fft.rfft(padded[p : p + n_fft] * win)
        mag = np.abs(sp) + 1e-9
        gain = np.clip((np.maximum(mag - thresh, 0.0) / mag) ** 1.65, 0.0, 1.0)
        bp = np.clip((freqs_stft - 58.0) / 35.0, 0.0, 1.0) * (1.0 - np.clip((freqs_stft - 12200.0) / 2800.0, 0.0, 1.0))
        clean_pad[p : p + n_fft] += np.fft.irfft(sp * gain * bp, n=n_fft) * win
        wsum[p : p + n_fft] += win * win
    clean_mono = (clean_pad / np.maximum(wsum, 1e-6))[n_fft : n_fft + n_total].astype(np.float32)

    # Warm Piano & Crystal Bell Mastering EQ
    clean_mono = fft_eq(
        clean_mono,
        SR,
        [(50, -18.0), (95, +1.5), (185, +3.0), (420, -1.6), (1200, +0.6), (3200, +2.2), (6500, +2.6), (11000, -1.2), (14500, -18.0)],
    )

    # Smooth fade-in (0.00->0.08s) and clean musical decay fade-out (4.05->4.90s)
    fi_env = smoothstep(0.0, 0.08, t)
    fo_env = 1.0 - smoothstep(4.05, 4.90, t)
    clean_mono *= fi_env * fo_env

    # True Mono-Compatible Stereo Widening + Velvet Stereo Hall Tail
    spec_m = np.fft.rfft(clean_mono)
    freqs_full = np.fft.rfftfreq(n_total, 1.0 / SR)
    width_mask = np.clip((freqs_full - 220.0) / 400.0, 0.0, 1.0) * 0.34
    side = np.fft.irfft(spec_m * 1j * (np.sin(freqs_full * 0.011) * width_mask), n=n_total).astype(np.float32)

    mix2 = np.column_stack([clean_mono + side, clean_mono - side]).astype(np.float32)
    mix2 = apply_stereo_studio_reverb(mix2, SR, wet=0.19, predelay_ms=24.0)
    mix2 *= (1.0 - smoothstep(4.78, 4.96, t))[:, None]
    mix2 = np.nan_to_num(mix2, nan=0.0)
    mix2 = mix2 / (np.max(np.abs(mix2)) + 1e-6) * 0.84

    wav_v2 = os.path.join(WORK_DIR, "audio_v2_ref_bgm_clean.wav")
    sf.write(wav_v2, mix2, SR, subtype="PCM_16")

    # ------------------------------------------------------------------
    # Track 2B (Bonus): Cleaned Sample BGM + "BM" Voiceover (Sidechain ducked!)
    # ------------------------------------------------------------------
    duck_v2 = 1.0 - 0.48 * (smoothstep(1.42, 1.56, t) * (1.0 - smoothstep(2.18, 2.52, t)))
    mix2_plus = mix2 * duck_v2[:, None] + voice_layer * 0.92
    mix2_plus *= (1.0 - smoothstep(4.78, 4.96, t))[:, None]
    pk2p = np.max(np.abs(mix2_plus)) + 1e-6
    if pk2p > 0.88:
        mix2_plus *= 0.88 / pk2p

    wav_v2_plus = os.path.join(WORK_DIR, "audio_v2_plus_voice_bm.wav")
    sf.write(wav_v2_plus, mix2_plus, SR, subtype="PCM_16")

    print(f"[Audio] Ready all 3 tracks: {wav_v1}, {wav_v2}, {wav_v2_plus}")
    return wav_v1, wav_v2, wav_v2_plus


# ==============================================================================
# 2. PREPARE CANONICAL 1920x1080 ASSETS (BM 3-PIECE LOGO + SLOGAN TYPOGRAPHY)
# ==============================================================================
def render_tracked_slogan_mask(text, w_canvas, h_canvas, center_x, center_y):
    """Renders crisp 3x supersampled Vietnamese slogan with wide modern geometric tracking."""
    scale_ss = 3
    font_candidates = [
        r"C:\Windows\Fonts\seguisb.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf",
        r"C:\Windows\Fonts\bahnschrift.ttf",
        r"C:\Windows\Fonts\arialbd.ttf",
    ]
    font_path = next((p for p in font_candidates if os.path.exists(p)), font_candidates[-1])
    font_size = 38 * scale_ss  # ~38px on 1080p canvas
    tracking = 4.6 * scale_ss  # Sleek wide architectural tracking like video_mẫu!
    fnt = ImageFont.truetype(font_path, font_size)

    dummy = Image.new("L", (64, 64), 0)
    ddraw = ImageDraw.Draw(dummy)

    # Measure per-character advances with kerning + custom tracking
    advances = []
    for i, ch in enumerate(text):
        w_ch = ddraw.textlength(ch, font=fnt)
        if i < len(text) - 1:
            pair_w = ddraw.textlength(text[i : i + 2], font=fnt)
            w_next = ddraw.textlength(text[i + 1], font=fnt)
            kern = pair_w - (w_ch + w_next)
        else:
            kern = 0.0
        advances.append(w_ch + kern + (tracking if i < len(text) - 1 else 0.0))

    total_w = sum(advances)
    strip_w = int(math.ceil(total_w + 240))
    strip_h = int(font_size * 2.4)
    strip = Image.new("L", (strip_w, strip_h), 0)
    sdraw = ImageDraw.Draw(strip)

    cur_x = (strip_w - total_w) * 0.5
    cur_y = strip_h * 0.28
    for ch, adv in zip(text, advances):
        sdraw.text((cur_x, cur_y), ch, font=fnt, fill=255)
        cur_x += adv

    strip_np = np.array(strip, dtype=np.float32) / 255.0
    # Downsample 3x with INTER_AREA for ultra-crisp anti-aliased glyphs
    ds_w = strip_w // scale_ss
    ds_h = strip_h // scale_ss
    ds = cv2.resize(strip_np, (ds_w, ds_h), interpolation=cv2.INTER_AREA)

    ys, xs = np.where(ds > 0.02)
    glyph_crop = ds[ys.min() : ys.max() + 1, xs.min() : xs.max() + 1]
    gh, gw = glyph_crop.shape

    out_mask = np.zeros((h_canvas, w_canvas), dtype=np.float32)
    x0 = int(round(center_x - gw * 0.5))
    y0 = int(round(center_y - gh * 0.5))
    out_mask[y0 : y0 + gh, x0 : x0 + gw] = glyph_crop
    print(f"[Typography] Rendered '{text}' using {os.path.basename(font_path)} -> width={gw}px, height={gh}px")
    return out_mask


def prepare_scene_assets():
    src = cv2.imread(LOGO_JPG)
    rgb = cv2.cvtColor(src, cv2.COLOR_BGR2RGB).astype(np.float32)
    interior = (rgb[:, :, 0] - rgb[:, :, 1]) > 120
    brand_rgb = np.median(rgb[interior], axis=0) / 255.0  # ~ [0.968, 0.310, 0.553]

    g_bg = 254.0
    g_fg = float(np.median(rgb[interior, 1]))
    alpha = np.clip((g_bg - rgb[:, :, 1]) / (g_bg - g_fg), 0.0, 1.0)
    alpha = np.clip((alpha - 0.04) / 0.92, 0.0, 1.0)

    h0, w0 = alpha.shape
    up_alpha = cv2.resize(alpha, (w0 * 3, h0 * 3), interpolation=cv2.INTER_CUBIC)
    up_alpha = cv2.GaussianBlur(up_alpha, (5, 5), 0.9)
    up_alpha = np.clip((up_alpha - 0.02) / 0.96, 0.0, 1.0)

    ys, xs = np.where(up_alpha > 0.02)
    logo_crop = up_alpha[ys.min() : ys.max() + 1, xs.min() : xs.max() + 1]

    # Hero BM Logo placement on 1920x1080 canvas: width = 660px, centered at (960, 448)
    logo_w = 660
    logo_h = int(round(logo_crop.shape[0] * (logo_w / logo_crop.shape[1])))
    logo_scaled = cv2.resize(logo_crop, (logo_w, logo_h), interpolation=cv2.INTER_AREA)

    cx = W // 2
    logo_cy = 448
    lx0 = cx - logo_w // 2
    ly0 = logo_cy - logo_h // 2

    logo_mask = np.zeros((H, W), dtype=np.float32)
    logo_mask[ly0 : ly0 + logo_h, lx0 : lx0 + logo_w] = logo_scaled

    # Separate 3 connected components of BM logo (B_top, B_bot, M)
    bin_m = (logo_mask > 0.15).astype(np.uint8)
    num_l, labels, stats, centroids = cv2.connectedComponentsWithStats(bin_m)
    comp_list = []
    kern = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    for lbl in range(1, num_l):
        if stats[lbl, cv2.CC_STAT_AREA] < 150:
            continue
        c_dil = cv2.dilate((labels == lbl).astype(np.uint8), kern, iterations=1)
        comp_list.append((centroids[lbl][0], centroids[lbl][1], logo_mask * c_dil.astype(np.float32)))

    comp_list.sort(key=lambda it: it[0])
    m_part = comp_list[-1][2]
    b_parts = sorted(comp_list[:-1], key=lambda it: it[1])
    b_top = b_parts[0][2]
    b_bot = b_parts[1][2] if len(b_parts) > 1 else np.zeros_like(logo_mask)

    # Render Slogan Mask centered directly below BM logo at y = 666 (harmonious gap like video_mẫu!)
    slogan_cy = ly0 + logo_h + 74
    slogan_mask = render_tracked_slogan_mask(SLOGAN_TEXT, W, H, cx, slogan_cy)

    full_union_mask = np.maximum(logo_mask, slogan_mask)

    # 3D Bevel Normals & Face RGB Shading for Logo + Slogan
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

    # Logo 3D bevel
    dist_l = cv2.distanceTransform((logo_mask > 0.35).astype(np.uint8), cv2.DIST_L2, 5)
    hf_l = cv2.GaussianBlur(np.minimum(dist_l, 18.0) / 18.0, (0, 0), 2.8)
    gxl = cv2.Sobel(hf_l, cv2.CV_32F, 1, 0, ksize=3) * 2.0
    gyl = cv2.Sobel(hf_l, cv2.CV_32F, 0, 1, ksize=3) * 2.0
    nl_len = np.sqrt(gxl * gxl + gyl * gyl + 1.0)
    key_l = np.clip((-gxl * (-0.55) - gyl * (-0.65) + 0.52) / nl_len, 0.0, 1.0)
    edge_l = np.clip(1.0 - np.abs(dist_l - 2.2) / 2.4, 0.0, 1.0) * logo_mask

    # Slogan subtle 3D bevel
    dist_s = cv2.distanceTransform((slogan_mask > 0.35).astype(np.uint8), cv2.DIST_L2, 3)
    edge_s = np.clip(1.0 - np.abs(dist_s - 1.2) / 1.5, 0.0, 1.0) * slogan_mask

    # Precompute Canonical Top-Face RGB (Logo = Vibrant BM Rose-Pink; Slogan = Executive Deep Rose-Slate)
    grad_l = np.clip((xx - lx0) / max(1.0, float(logo_w)) * 0.65 + (yy - ly0) / max(1.0, float(logo_h)) * 0.35, 0.0, 1.0)
    lr = 0.99 * (1.0 - grad_l) + 0.89 * grad_l + 0.16 * (key_l ** 2.8) + 0.18 * edge_l
    lg = 0.35 * (1.0 - grad_l) + 0.20 * grad_l + 0.15 * (key_l ** 2.8) + 0.16 * edge_l
    lb = 0.59 * (1.0 - grad_l) + 0.48 * grad_l + 0.16 * (key_l ** 2.8) + 0.18 * edge_l

    # Slogan executive rose-charcoal gradient (#5A2B46 -> #7E315B) with subtle crisp bevel highlight
    grad_s = np.clip((xx - 480.0) / 960.0, 0.0, 1.0)
    sr_col = 0.38 * (1.0 - grad_s) + 0.54 * grad_s + 0.14 * edge_s
    sg_col = 0.17 * (1.0 - grad_s) + 0.20 * grad_s + 0.08 * edge_s
    sb_col = 0.29 * (1.0 - grad_s) + 0.38 * grad_s + 0.12 * edge_s

    face_rgb = np.ones((H, W, 3), dtype=np.float32)
    w_sum = logo_mask + slogan_mask + 1e-6
    face_rgb[:, :, 0] = (lr * logo_mask + sr_col * slogan_mask) / w_sum
    face_rgb[:, :, 1] = (lg * logo_mask + sg_col * slogan_mask) / w_sum
    face_rgb[:, :, 2] = (lb * logo_mask + sb_col * slogan_mask) / w_sum
    face_rgb = np.clip(face_rgb, 0.0, 1.0)

    # Precompute Soft Studio Floor Contact + Directional Shadow Map (canonical space)
    shadow_tight = cv2.GaussianBlur(full_union_mask, (0, 0), 9.0)
    shadow_soft = cv2.GaussianBlur(full_union_mask, (0, 0), 26.0)
    floor_shadow = np.clip(shadow_tight * 0.55 + shadow_soft * 0.45, 0.0, 1.0)

    # Top-left & top-right apex coordinates of BM logo for 4-point star glint (like ref_f06!)
    apex_left = (lx0 + 38, ly0 + 14)
    apex_right = (lx0 + logo_w - 46, ly0 + 22)

    return {
        "logo_mask": logo_mask,
        "pieces": [b_top, b_bot, m_part],
        "slogan_mask": slogan_mask,
        "full_mask": full_union_mask,
        "face_rgb": face_rgb,
        "edge_l": edge_l,
        "edge_s": edge_s,
        "floor_shadow": floor_shadow,
        "pivot": (float(cx), 535.0),
        "apex_left": apex_left,
        "apex_right": apex_right,
    }


# ==============================================================================
# 3. TRUE 3D PERSPECTIVE HOMOGRAPHY + MULTI-LAYER EXTRUSION ENGINE
# ==============================================================================
def build_3d_homography(cx, cy, focal, pitch_deg, yaw_deg, roll_deg, tx, ty, tz, z_plane):
    """Exact 3x3 perspective homography mapping canonical (u,v) on depth plane z_plane -> screen (x,y)."""
    px = math.radians(pitch_deg)
    py = math.radians(yaw_deg)
    pz = math.radians(roll_deg)

    cp, sp = math.cos(px), math.sin(px)
    cy_a, sy_a = math.cos(py), math.sin(py)
    cr, sr = math.cos(pz), math.sin(pz)

    rx = np.array([[1.0, 0.0, 0.0], [0.0, cp, -sp], [0.0, sp, cp]], dtype=np.float64)
    ry = np.array([[cy_a, 0.0, sy_a], [0.0, 1.0, 0.0], [-sy_a, 0.0, cy_a]], dtype=np.float64)
    rz = np.array([[cr, -sr, 0.0], [sr, cr, 0.0], [0.0, 0.0, 1.0]], dtype=np.float64)

    rot = rz @ ry @ rx
    r1 = rot[:, 0]
    r2 = rot[:, 1]
    r3 = rot[:, 2]
    trans = np.array([tx, ty, focal + tz], dtype=np.float64)

    k_mat = np.array([[focal, 0.0, cx], [0.0, focal, cy], [0.0, 0.0, 1.0]], dtype=np.float64)
    t_unc = np.array([[1.0, 0.0, -cx], [0.0, 1.0, -cy], [0.0, 0.0, 1.0]], dtype=np.float64)

    extrinsic_plane = np.column_stack([r1, r2, r3 * z_plane + trans])
    h_mat = k_mat @ extrinsic_plane @ t_unc
    return (h_mat / h_mat[2, 2]).astype(np.float32)


def draw_4point_star_glint(img_rgb, x_pt, y_pt, radius, intensity):
    """Draws a sleek optical 4-point star gleam + soft halo (like top-left of ref_f06 in video_mẫu!)."""
    if intensity <= 0.01 or not (20 <= x_pt < W - 20 and 20 <= y_pt < H - 20):
        return
    r_int = int(round(radius))
    x0 = max(0, int(x_pt) - r_int)
    x1 = min(W, int(x_pt) + r_int + 1)
    y0 = max(0, int(y_pt) - r_int)
    y1 = min(H, int(y_pt) + r_int + 1)

    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    dx = xx - x_pt
    dy = yy - y_pt

    # Horizontal & vertical razor spikes + 45-deg minor spikes + soft radial core
    h_spike = np.exp(-0.5 * (dy / 1.6) ** 2) * np.exp(-0.5 * (dx / (radius * 0.55)) ** 2)
    v_spike = np.exp(-0.5 * (dx / 1.6) ** 2) * np.exp(-0.5 * (dy / (radius * 0.45)) ** 2)
    core = np.exp(-0.5 * ((dx * dx + dy * dy) / (7.5 ** 2)))
    glint = np.clip((h_spike * 0.85 + v_spike * 0.85 + core * 0.95) * intensity, 0.0, 1.0)

    patch = img_rgb[y0:y1, x0:x1]
    # Pure white core with subtle rose-pink outer tint
    glint_col = np.zeros_like(patch)
    glint_col[:, :, 0] = 1.0
    glint_col[:, :, 1] = 0.94 + 0.06 * core
    glint_col[:, :, 2] = 0.97 + 0.03 * core
    img_rgb[y0:y1, x0:x1] = patch * (1.0 - glint[:, :, None]) + glint_col * glint[:, :, None]


def project_point(h_mat, pt):
    vec = np.array([pt[0], pt[1], 1.0], dtype=np.float32)
    res = h_mat @ vec
    return float(res[0] / res[2]), float(res[1] / res[2])


def render_master_video_stream(assets):
    master_video = os.path.join(WORK_DIR, "master_white_slogan_video_only.mp4")
    print(f"\n[Render] Rendering 300 frames (1920x1080 @ 60fps) Pure White 3D Extruded Scene -> {master_video}")
    t0_wall = time.time()

    cx, cy = assets["pivot"]
    focal = 1650.0
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

    cmd = [
        FFMPEG,
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-pix_fmt", "bgr24",
        "-s", f"{W}x{H}",
        "-r", str(FPS),
        "-i", "-",
        "-an",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "14",
        "-pix_fmt", "yuv420p",
        master_video,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    # 3-piece kinetic convergence offsets in canonical plane during 0.04s -> 0.98s
    piece_motions = [
        (0.03, 0.92, -210.0, -45.0),  # B_top
        (0.09, 0.95, -145.0, +65.0),  # B_bot
        (0.13, 0.98, +215.0, +25.0),  # M
    ]

    preview_frames = {28, 56, 98, 122, 185, 255}

    for f in range(N_FRAMES):
        t = f / FPS

        # Pure crisp #FFFFFF white studio canvas!
        canvas = np.ones((H, W, 3), dtype=np.float32)

        # Early white fade-in (0.00s -> 0.14s) and graceful white dissolve at end (3.85s -> 4.88s)
        vis_in = float(smoothstep(0.02, 0.18, t))
        vis_out = 1.0 - float(smootherstep(3.88, 4.88, t))
        master_vis = vis_in * vis_out

        if master_vis <= 0.001:
            frame_bgr = np.full((H, W, 3), 255, dtype=np.uint8)
            proc.stdin.write(frame_bgr.tobytes())
            continue

        # ------------------------------------------------------------------
        # 3D Camera Trajectory (Matches video_mẫu: Tilted 3D Floor Sweep -> Front Hero -> Smooth Zoom-Out!)
        # ------------------------------------------------------------------
        # 0.00s -> 1.45s: Dramatic 3D floor perspective (-46° pitch, +25° yaw, -7° roll, close-up tz=-360)
        #                 gliding smoothly into clean hero front view!
        u_cam = ease_out_cubic(t / 1.55)
        # Gentle living 3D micro-drift during hero hold (1.55s -> 3.60s)
        drift_y = 2.2 * math.sin((t - 1.55) * 1.1) * float(smoothstep(1.2, 2.0, t)) * (1.0 - float(smoothstep(3.4, 4.4, t)))
        drift_p = -2.5 * (1.0 - float(smoothstep(1.4, 2.8, t)))

        pitch = -45.0 * (1.0 - u_cam) + drift_p
        yaw = +24.0 * (1.0 - u_cam) + drift_y
        roll = -6.5 * (1.0 - u_cam)
        tx = -40.0 * (1.0 - u_cam)
        ty = +55.0 * (1.0 - u_cam)

        # Camera Z distance: starts zoomed in (-360), settles near 0 at 1.55s, then smoothly pulls back (+980 by 4.9s, just like ref_f12->ref_f15!)
        tz_in = -360.0 * (1.0 - u_cam)
        tz_pullback = +1080.0 * (float(smootherstep(2.45, 4.92, t)) ** 1.15)
        tz = tz_in + tz_pullback

        # Dynamic 3D extrusion thickness: rises out of the white floor during 0.04s -> 0.95s!
        ext_depth = 26.0 * ease_out_expo((t - 0.04) / 0.85)

        # ------------------------------------------------------------------
        # Build Canonical Shape & Face RGB for Current Frame
        # ------------------------------------------------------------------
        if t < 0.99:
            # Kinetic 3-piece BM convergence + Slogan slide-up reveal
            cur_logo_m = np.zeros((H, W), dtype=np.float32)
            for p_i, (pt0, pt1, pdx0, pdy0) in enumerate(piece_motions):
                pu = ease_out_expo((t - pt0) / (pt1 - pt0))
                pop = float(smoothstep(0.0, 0.16, (t - pt0) / (pt1 - pt0)))
                dx_p = pdx0 * (1.0 - pu)
                dy_p = pdy0 * (1.0 - pu)
                mat_p = np.float32([[1.0, 0.0, dx_p], [0.0, 1.0, dy_p]])
                warped_p = cv2.warpAffine(assets["pieces"][p_i], mat_p, (W, H), flags=cv2.INTER_LINEAR) * pop
                cur_logo_m = np.maximum(cur_logo_m, warped_p)

            # Slogan rises smoothly right after logo pieces start converging (0.22s -> 0.98s)
            su_slog = ease_out_expo((t - 0.22) / 0.76)
            sop_slog = float(smoothstep(0.22, 0.52, t))
            dy_slog = 42.0 * (1.0 - su_slog)
            mat_s = np.float32([[1.0, 0.0, 0.0], [0.0, 1.0, dy_slog]])
            cur_slog_m = cv2.warpAffine(assets["slogan_mask"], mat_s, (W, H), flags=cv2.INTER_LINEAR) * sop_slog

            cur_union_m = np.maximum(cur_logo_m, cur_slog_m)
            cur_shadow_m = cv2.GaussianBlur(cur_union_m, (0, 0), 16.0)

            # Canonical face color for moving pieces
            cur_face = np.ones((H, W, 3), dtype=np.float32)
            ws = cur_logo_m + cur_slog_m + 1e-6
            cur_face[:, :, 0] = (0.965 * cur_logo_m + 0.44 * cur_slog_m) / ws
            cur_face[:, :, 1] = (0.295 * cur_logo_m + 0.18 * cur_slog_m) / ws
            cur_face[:, :, 2] = (0.545 * cur_logo_m + 0.33 * cur_slog_m) / ws
        else:
            cur_union_m = assets["full_mask"]
            cur_shadow_m = assets["floor_shadow"]
            cur_face = assets["face_rgb"].copy()

            # Diagonal Specular Liquid-Glass Light Sweep (1.42s -> 2.52s) across BM Logo + Slogan!
            sw_u = (t - 1.42) / 1.10
            if 0.0 < sw_u < 1.0:
                sw_s = ease_in_out_cubic(sw_u)
                beam_x = 440.0 + 1040.0 * sw_s
                diag = (xx - beam_x) + 0.38 * (yy - cy)
                sheen_core = np.exp(-0.5 * (diag / 42.0) ** 2)
                sheen_rim = np.exp(-0.5 * (diag / 110.0) ** 2) * (assets["edge_l"] + assets["edge_s"])
                sheen_env = math.sin(math.pi * float(np.clip(sw_u, 0.0, 1.0))) ** 0.8
                spec = np.clip((sheen_core * 0.72 + sheen_rim * 0.65) * sheen_env, 0.0, 0.92)
                cur_face = cur_face * (1.0 - spec[:, :, None]) + spec[:, :, None]

        # ------------------------------------------------------------------
        # 1) Project Soft Studio Floor Drop-Shadow onto White Floor (z_plane = +10, shifted down-right)
        # ------------------------------------------------------------------
        h_shad = build_3d_homography(cx, cy, focal, pitch, yaw, roll, tx + 18.0, ty + 22.0, tz, z_plane=+10.0)
        proj_shad = cv2.warpPerspective(cur_shadow_m, h_shad, (W, H), flags=cv2.INTER_LINEAR, borderValue=0.0)
        # Warm architectural studio shadow on pure white floor (like ref_f06 & ref_f09!)
        shad_strength = 0.23 * master_vis
        canvas[:, :, 0] -= proj_shad * shad_strength * 0.92
        canvas[:, :, 1] -= proj_shad * shad_strength * 1.02
        canvas[:, :, 2] -= proj_shad * shad_strength * 0.96

        # ------------------------------------------------------------------
        # 2) Project Multi-Layer 3D Extruded Pearl-White / Silver-Rose Side Walls!
        #    (z_plane from 0.0 up to -ext_depth)
        # ------------------------------------------------------------------
        n_slices = 10
        if ext_depth > 0.5:
            for s_idx in range(n_slices):
                frac = s_idx / float(n_slices)
                z_val = -ext_depth * frac
                h_slice = build_3d_homography(cx, cy, focal, pitch, yaw, roll, tx, ty, tz, z_plane=z_val)
                m_slice = cv2.warpPerspective(cur_union_m, h_slice, (W, H), flags=cv2.INTER_LINEAR, borderValue=0.0)
                m_slice *= master_vis

                # Architectural 3D side-wall lighting: darker ambient occlusion near floor (frac=0), crisp pearl-white near top rim (frac=1)!
                shade = 0.80 + 0.16 * frac
                wall_col = np.array([shade + 0.015, shade - 0.012, shade + 0.005], dtype=np.float32)
                canvas = canvas * (1.0 - m_slice[:, :, None]) + wall_col * m_slice[:, :, None]

        # ------------------------------------------------------------------
        # 3) Project Top 3D Beveled Face (z_plane = -ext_depth) + RGB Chromatic Shimmer on Motion!
        # ------------------------------------------------------------------
        h_top = build_3d_homography(cx, cy, focal, pitch, yaw, roll, tx, ty, tz, z_plane=-ext_depth)
        m_top = cv2.warpPerspective(cur_union_m, h_top, (W, H), flags=cv2.INTER_LINEAR, borderValue=0.0)
        rgb_top = cv2.warpPerspective(cur_face, h_top, (W, H), flags=cv2.INTER_LINEAR, borderValue=(1.0, 1.0, 1.0))

        # Subtle RGB Chromatic Aberration Edge Fringe during fast 3D rise (0.05s -> 1.15s, exactly like ref_f04!)
        chroma_amt = (1.0 - float(smoothstep(0.25, 1.25, t))) * float(smoothstep(0.04, 0.20, t))
        if chroma_amt > 0.01:
            c_shift = int(round(7.0 * chroma_amt))
            if c_shift >= 1:
                m_left = np.roll(m_top, -c_shift, axis=1)
                m_right = np.roll(m_top, +c_shift, axis=1)
                fringe_c = np.clip(m_left - m_top, 0.0, 1.0) * chroma_amt * 0.55 * master_vis
                fringe_m = np.clip(m_right - m_top, 0.0, 1.0) * chroma_amt * 0.55 * master_vis
                # Cyan fringe on leading edge, magenta-red fringe on trailing edge over white
                canvas[:, :, 0] -= fringe_c * 0.75
                canvas[:, :, 1] -= fringe_m * 0.65
                canvas[:, :, 2] -= fringe_m * 0.25

        m_top_vis = m_top * master_vis
        canvas = canvas * (1.0 - m_top_vis[:, :, None]) + rgb_top * m_top_vis[:, :, None]

        # ------------------------------------------------------------------
        # 4) Optical 4-Point Corner Star Glints (like ref_f06!) during Hero Lock & Sweep
        # ------------------------------------------------------------------
        if 1.05 < t < 1.95:
            g1 = math.sin(math.pi * clamp01((t - 1.05) / 0.90)) ** 1.4
            gx1, gy1 = project_point(h_top, assets["apex_left"])
            draw_4point_star_glint(canvas, gx1, gy1, radius=58.0, intensity=0.92 * float(g1) * master_vis)

        if 1.72 < t < 2.55:
            g2 = math.sin(math.pi * clamp01((t - 1.72) / 0.83)) ** 1.4
            gx2, gy2 = project_point(h_top, assets["apex_right"])
            draw_4point_star_glint(canvas, gx2, gy2, radius=54.0, intensity=0.88 * float(g2) * master_vis)

        # Soft dreamy focus bloom during final pull-back dissolve into pure white (4.05s -> 4.88s)
        if t > 4.05:
            blur_mix = float(smoothstep(4.05, 4.85, t)) * 0.65
            blurred = cv2.GaussianBlur(canvas, (0, 0), 5.0)
            canvas = canvas * (1.0 - blur_mix) + blurred * blur_mix

        canvas = np.clip(canvas, 0.0, 1.0)
        frame_bgr = np.clip(canvas[:, :, ::-1] * 255.0 + 0.5, 0, 255).astype(np.uint8)

        if f in preview_frames:
            cv2.imwrite(os.path.join(WORK_DIR, f"white_preview_f{f:03d}.jpg"), frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, 95])

        proc.stdin.write(frame_bgr.tobytes())
        if (f + 1) % 60 == 0 or f == N_FRAMES - 1:
            print(f"  [White 3D Master] Frame {f+1}/{N_FRAMES} ({(f+1)/N_FRAMES*100:.0f}%)", flush=True)

    proc.stdin.close()
    stderr_b = proc.stderr.read()
    ret = proc.wait()
    if ret != 0:
        raise RuntimeError(f"FFmpeg video encode failed: {stderr_b.decode('utf-8', errors='replace')}")

    print(f"[Render] Master video stream ready in {time.time() - t0_wall:.1f}s!")
    return master_video


def mux_video_with_audio(video_mp4, audio_wav, out_mp4):
    cmd = [
        FFMPEG,
        "-y",
        "-i", video_mp4,
        "-i", audio_wav,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "320k",
        "-movflags", "+faststart",
        "-shortest",
        out_mp4,
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    mb = os.path.getsize(out_mp4) / (1024 * 1024)
    print(f"[Mux] Exported: {out_mp4} ({mb:.2f} MB)")


def main():
    wav_v1, wav_v2, wav_v2_plus = build_all_audio_tracks()
    assets = prepare_scene_assets()
    master_v = render_master_video_stream(assets)

    out_1 = os.path.join(OUT_DIR, "BM_Intro_1_NenTrang_HieuUng_VoiceBM.mp4")
    out_2 = os.path.join(OUT_DIR, "BM_Intro_2_NenTrang_NhacMau_LocTapAm.mp4")
    out_2_plus = os.path.join(OUT_DIR, "BM_Intro_2_KemVoiceBM_NhacMau_LocTapAm.mp4")

    mux_video_with_audio(master_v, wav_v1, out_1)
    mux_video_with_audio(master_v, wav_v2, out_2)
    mux_video_with_audio(master_v, wav_v2_plus, out_2_plus)

    print("\n=== ALL WHITE-BACKGROUND SLOGAN INTROS COMPLETED ===")
    print("Video 1 (Voice BM + Modern SFX):", out_1)
    print("Video 2 (Cleaned Sample BGM):   ", out_2)
    print("Bonus   (Sample BGM + Voice BM):", out_2_plus)


if __name__ == "__main__":
    main()

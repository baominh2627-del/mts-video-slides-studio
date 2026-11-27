# -*- coding: utf-8 -*-
"""
BM Modern Lesson Intro Generator (1920x1080 @ 60fps)
Creates:
1. Studio Sonic Ident Audio (English "BM" /bi: em/ glide voiceover + futuristic whooshes,
   sub-bass lock-in impact, crystal harmonic chord, and stereo shimmer reverb).
2. Flagship Dark Cinematic Neon & 3D Glass Intro (BM_Intro_Modern_Dark_1080p60.mp4)
3. Clean Pearl-White Studio Intro (BM_Intro_Modern_Light_1080p60.mp4)
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

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

BASE_DIR = r"C:\Users\DELL\Documents\CODE\DU_AN"
WORK_DIR = os.path.join(BASE_DIR, "video_build", "bm_intro_work")
OUT_DIR = os.path.join(BASE_DIR, "02_San_Pham_Hoan_Chinh", "Video_Intro_BM")
ASSET_DIR = os.path.join(BASE_DIR, "03_Tai_Nguyen_Goc", "Logo_Va_Font")
UPLOADED_LOGO = r"C:/Users/DELL/.gemini/antigravity/brain/fc42d3cf-3a2f-4081-bebf-02ad4d23944a/.user_uploaded/media_1795588966074_a11371d4.jpg"

os.makedirs(WORK_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(ASSET_DIR, exist_ok=True)

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

W, H = 1920, 1080
FPS = 60
DURATION = 4.60
N_FRAMES = int(round(DURATION * FPS))  # 276 frames
SR = 48000


# ==============================================================================
# Easing & Math Helpers
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


def ease_out_quint(t):
    t = float(np.clip(t, 0.0, 1.0))
    return 1.0 - math.pow(1.0 - t, 5.0)


def ease_in_out_cubic(t):
    t = float(np.clip(t, 0.0, 1.0))
    return 4.0 * t * t * t if t < 0.5 else 1.0 - math.pow(-2.0 * t + 2.0, 3.0) / 2.0


# ==============================================================================
# 1. STUDIO AUDIO ENGINE (Voice "BM" /bi: em/ + Modern Sonic Ident)
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
    """Smooth zero-phase parametric spectral shaping in pure NumPy."""
    n = len(signal)
    spec = np.fft.rfft(signal)
    freqs = np.fft.rfftfreq(n, d=1.0 / sr)
    log_f = np.log10(np.maximum(freqs, 10.0))
    pts_f = np.log10([p[0] for p in gains_db_points])
    pts_g = [p[1] for p in gains_db_points]
    db_curve = np.interp(log_f, pts_f, pts_g)
    # High-pass below 80 Hz
    hp = np.clip((freqs - 45.0) / 45.0, 0.0, 1.0) ** 2
    gain = (10.0 ** (db_curve / 20.0)) * hp
    return np.fft.irfft(spec * gain, n=n).astype(np.float32)


def make_swept_whoosh(n_samples, sr, t_start, t_end, f_start, f_peak, f_end, pan_start, pan_end, amp=0.25):
    """Synthesizes a silky cinema air/energy whoosh with time-varying STFT bandpass & stereo glide."""
    out = np.zeros((n_samples, 2), dtype=np.float32)
    i0 = max(0, int(t_start * sr))
    i1 = min(n_samples, int(t_end * sr))
    length = i1 - i0
    if length <= 1024:
        return out

    rng = np.random.default_rng(int(t_start * 10000) + 42)
    # Velvet-pink base noise
    white = rng.standard_normal(length).astype(np.float32)
    spec = np.fft.rfft(white)
    freqs = np.fft.rfftfreq(length, 1.0 / sr)
    pink_weight = 1.0 / np.sqrt(np.maximum(freqs, 40.0) / 200.0)
    pink = np.fft.irfft(spec * pink_weight, n=length).astype(np.float32)

    # Overlap-add STFT time-varying resonant filter
    win_size = 1024
    hop = 256
    window = np.hanning(win_size).astype(np.float32)
    y = np.zeros(length + win_size, dtype=np.float32)
    f_bins = np.fft.rfftfreq(win_size, 1.0 / sr)

    n_hops = (length - win_size) // hop
    for h in range(max(1, n_hops)):
        pos = h * hop
        prog = h / max(1, n_hops - 1)
        # Smooth frequency trajectory: f_start -> f_peak -> f_end
        if prog < 0.45:
            p2 = smoothstep(0.0, 0.45, prog)
            fc = f_start * ((f_peak / f_start) ** p2)
        else:
            p2 = smoothstep(0.45, 1.0, prog)
            fc = f_peak * ((f_end / f_peak) ** p2)

        frame = pink[pos : pos + win_size] * window
        fspec = np.fft.rfft(frame)
        # Log-Gaussian bandpass around fc
        log_dist = np.log2(np.maximum(f_bins, 20.0) / fc)
        bp = np.exp(-0.5 * (log_dist / 0.65) ** 2)
        filtered = np.fft.irfft(fspec * bp, n=win_size) * window
        y[pos : pos + win_size] += filtered

    y = y[:length]
    # Normalize & shape amplitude envelope
    mx = np.max(np.abs(y)) + 1e-6
    y = (y / mx) * amp
    t_norm = np.linspace(0.0, 1.0, length, dtype=np.float32)
    env = np.maximum(0.0, np.sin(np.pi * (t_norm ** 0.85))) ** 1.6
    y *= env

    # Stereo panning + micro Haas delay
    pan = pan_start + (pan_end - pan_start) * smoothstep(0.0, 1.0, np.linspace(0, 1, length))
    theta = (pan + 1.0) * (np.pi / 4.0)
    left = y * np.cos(theta)
    right = y * np.sin(theta)
    out[i0:i1, 0] += left.astype(np.float32)
    out[i0:i1, 1] += right.astype(np.float32)
    return out


def apply_stereo_studio_reverb(stereo_in, sr, wet=0.24, predelay_ms=26.0):
    """Lush velvet multi-tap stereo studio reverb with high-frequency damping."""
    n = len(stereo_in)
    mono = 0.5 * (stereo_in[:, 0] + stereo_in[:, 1])
    # Damp harsh highs entering reverb tank
    tank_in = fft_eq(mono, sr, [(60, -12), (180, -2), (1200, 0), (4500, -4), (9000, -14), (16000, -24)])

    predelay = int(predelay_ms * 0.001 * sr)
    rev_L = np.zeros(n, dtype=np.float32)
    rev_R = np.zeros(n, dtype=np.float32)

    # Rich prime-spaced early + late diffuse reflections
    taps_L = [
        (31, 0.42), (47, 0.34), (73, 0.28), (109, 0.23), (157, 0.19),
        (223, 0.15), (307, 0.115), (401, 0.085), (521, 0.06), (659, 0.04), (811, 0.025)
    ]
    taps_R = [
        (37, 0.42), (53, 0.34), (83, 0.28), (127, 0.23), (173, 0.19),
        (241, 0.15), (331, 0.115), (433, 0.085), (557, 0.06), (691, 0.04), (853, 0.025)
    ]

    for delay_ms, gain in taps_L:
        d = predelay + int(delay_ms * 0.001 * sr)
        if d < n:
            rev_L[d:] += tank_in[: n - d] * gain
    for delay_ms, gain in taps_R:
        d = predelay + int(delay_ms * 0.001 * sr)
        if d < n:
            rev_R[d:] += tank_in[: n - d] * gain

    # Extra soft diffusion pass via short allpass-like smear
    smear_d = int(0.013 * sr)
    if smear_d < n:
        rev_L[smear_d:] = 0.72 * rev_L[smear_d:] + 0.28 * rev_R[: n - smear_d]
        rev_R[smear_d:] = 0.72 * rev_R[smear_d:] + 0.28 * rev_L[: n - smear_d]

    out = stereo_in.copy()
    out[:, 0] += wet * rev_L
    out[:, 1] += wet * rev_R
    return out


def build_master_audio():
    raw_voice_wav = os.path.join(WORK_DIR, "v_christopher_bm_space.wav")
    asyncio.run(ensure_voice_raw(raw_voice_wav))

    n_total = int(round(DURATION * SR))
    t = np.arange(n_total, dtype=np.float32) / SR
    mix = np.zeros((n_total, 2), dtype=np.float32)

    # 1. Three Kinetic Fly-in Stereo Whooshes (0.04s -> 0.92s)
    mix += make_swept_whoosh(n_total, SR, 0.04, 0.76, 180, 1950, 420, -0.85, -0.05, amp=0.17)
    mix += make_swept_whoosh(n_total, SR, 0.14, 0.84, 150, 1500, 380, -0.60, 0.00, amp=0.13)
    mix += make_swept_whoosh(n_total, SR, 0.18, 0.93, 220, 2400, 520, +0.85, +0.05, amp=0.18)

    # 2. Subtle Futuristic Laser Contour Riser (0.08s -> 0.90s)
    riser_mask = (t >= 0.08) & (t <= 0.92)
    tr = (t[riser_mask] - 0.08) / 0.84
    phase_r = 2.0 * np.pi * SR * np.cumsum((260.0 + 980.0 * (tr ** 2.1)) / SR)
    riser_sig = (0.032 * np.sin(phase_r) + 0.016 * np.sin(2.0 * phase_r)) * (np.maximum(0.0, np.sin(np.pi * tr)) ** 1.3)
    mix[riser_mask, 0] += riser_sig * (0.6 + 0.4 * np.cos(6.0 * tr))
    mix[riser_mask, 1] += riser_sig * (0.6 + 0.4 * np.sin(6.0 * tr))

    # 3. Lock-In Sub-Bass Impact + Crystalline Transient (t = 0.90s)
    imp_t0 = 0.895
    imp_mask = (t >= imp_t0) & (t <= 1.85)
    ti = t[imp_mask] - imp_t0
    # Pitch-envelope tight studio sub punch (135Hz -> 48Hz)
    inst_freq = 48.0 + 92.0 * np.exp(-ti / 0.038)
    sub_phase = 2.0 * np.pi * np.cumsum(inst_freq / SR)
    sub_env = (1.0 - np.exp(-ti / 0.004)) * np.exp(-ti / 0.24)
    sub_wave = np.tanh(1.35 * np.sin(sub_phase)) * sub_env * 0.42
    # Crisp glassy impact shimmer transient
    glass_click = (
        0.09 * np.sin(2 * np.pi * 2793.8 * ti) * np.exp(-ti / 0.045)
        + 0.06 * np.sin(2 * np.pi * 4186.0 * ti) * np.exp(-ti / 0.028)
    ) * (1.0 - np.exp(-ti / 0.002))
    mix[imp_mask, 0] += sub_wave + glass_click * 0.95
    mix[imp_mask, 1] += sub_wave + glass_click * 1.05

    # 4. Warm Modern Crystalline Chord Ident (Dbmaj9: Db3, Ab3, F4, C5, Eb5) from 0.90s -> 4.45s
    chord_mask = (t >= 0.90) & (t <= 4.50)
    tc = t[chord_mask] - 0.90
    notes = [
        (138.59, 0.075, 0.0),    # Db3 warm bass root
        (207.65, 0.060, -0.25),  # Ab3 fifth
        (349.23, 0.052, +0.25),  # F4 major third
        (523.25, 0.042, -0.45),  # C5 major seventh
        (622.25, 0.035, +0.45),  # Eb5 ninth (modern airy color!)
        (1108.73, 0.015, +0.15), # Db6 subtle crystal bell harmonic
    ]
    pad_L = np.zeros_like(tc)
    pad_R = np.zeros_like(tc)
    attack = 1.0 - np.exp(-tc / 0.06)
    decay = np.exp(-tc / 1.65)
    tail_fade = 1.0 - np.array([smoothstep(2.95, 3.55, x) for x in tc], dtype=np.float32)

    # Sidechain pocket during "BM" voiceover (t = 1.48s -> 2.32s => tc = 0.58s -> 1.42s)
    duck = np.ones_like(tc)
    for idx_c, x in enumerate(tc):
        d_in = smoothstep(0.50, 0.64, x)
        d_out = smoothstep(1.30, 1.62, x)
        duck[idx_c] = 1.0 - 0.52 * (d_in * (1.0 - d_out))

    pad_env = attack * decay * tail_fade * duck
    for freq, amp, pan in notes:
        # Gentle chorus detune (+/- 0.35 Hz) for lush studio width
        s1 = np.sin(2.0 * np.pi * (freq - 0.32) * tc)
        s2 = np.sin(2.0 * np.pi * (freq + 0.32) * tc + 0.7)
        tone = 0.5 * (s1 + s2) + 0.14 * np.sin(4.0 * np.pi * freq * tc) * np.exp(-tc / 0.55)
        th = (pan + 1.0) * (np.pi / 4.0)
        pad_L += tone * amp * math.cos(th)
        pad_R += tone * amp * math.sin(th)

    mix[chord_mask, 0] += pad_L * pad_env
    mix[chord_mask, 1] += pad_R * pad_env

    # 5. The Signature "BM" ("bi em") Light-Sweep Air Glide + Studio Voiceover (1.46s -> 2.55s)
    # Silky Left-to-Right airy sheen sweep synchronized to light beam crossing B -> M
    mix += make_swept_whoosh(n_total, SR, 1.46, 2.42, 650, 4200, 1100, -0.65, +0.65, amp=0.115)

    # Delicate high crystal sparkle during specular light sweep
    sp_mask = (t >= 1.52) & (t <= 2.38)
    tsp = t[sp_mask] - 1.52
    sparkle = (
        0.016 * np.sin(2 * np.pi * 2489.0 * tsp) * np.exp(-tsp / 0.35)
        + 0.012 * np.sin(2 * np.pi * 3322.4 * tsp + 1.1) * np.exp(-np.maximum(0, tsp - 0.18) / 0.32) * (tsp > 0.18)
    ) * np.sin(np.pi * np.clip(tsp / 0.86, 0, 1))
    mix[sp_mask, 0] += sparkle * np.linspace(0.9, 0.3, len(tsp))
    mix[sp_mask, 1] += sparkle * np.linspace(0.3, 0.9, len(tsp))

    # Load, trim, EQ, stereo-glide, and reverb the English "BM" ("bi em") voiceover
    v_data, v_sr = sf.read(raw_voice_wav)
    if v_data.ndim > 1:
        v_data = v_data[:, 0]
    v_data = v_data.astype(np.float32)

    nz = np.where(np.abs(v_data) > 0.008)[0]
    pad_pre = int(0.018 * SR)
    pad_post = int(0.085 * SR)
    v0 = max(0, nz[0] - pad_pre)
    v1 = min(len(v_data), nz[-1] + pad_post)
    voice = v_data[v0:v1].copy()

    # Smooth micro-fades to guarantee zero clicks
    fi = int(0.012 * SR)
    fo = int(0.055 * SR)
    voice[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32) ** 1.5
    voice[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32) ** 1.5

    # Studio Broadcast Vocal EQ: warm chest (165Hz), clean low-mids, silky air (6.5kHz+)
    voice = fft_eq(
        voice,
        SR,
        [
            (60, -10.0),
            (110, +1.5),
            (170, +3.2),
            (360, -2.2),
            (1200, +0.5),
            (3400, +2.6),
            (6800, +4.2),
            (11500, +4.5),
            (16500, +1.0),
        ],
    )
    # Gentle studio tube warmth + peak normalization
    voice = voice / (np.max(np.abs(voice)) + 1e-6)
    voice = np.tanh(1.25 * voice) / np.tanh(1.25) * 0.84

    # Place voice at t = 1.53s so "B" hits at ~1.56s-1.80s and "M" hits at ~1.84s-2.18s
    voice_start_t = 1.53
    vs0 = int(voice_start_t * SR)
    vs1 = min(n_total, vs0 + len(voice))
    v_len = vs1 - vs0
    voice = voice[:v_len]

    # Smooth Stereo Glide ("lướt qua chuyên nghiệp"): gently glides from Left (-0.20 on "B") -> Right (+0.20 on "M")
    v_prog = np.linspace(0.0, 1.0, v_len, dtype=np.float32)
    v_pan = -0.20 + 0.40 * smoothstep(0.08, 0.88, v_prog)
    v_theta = (v_pan + 1.0) * (np.pi / 4.0)

    voice_track = np.zeros((n_total, 2), dtype=np.float32)
    voice_track[vs0:vs1, 0] = voice * np.cos(v_theta)
    # Subtle 0.35ms Haas stereo enrichment on R channel for wide studio presence
    haas_samples = int(0.00035 * SR)
    r_sig = voice * np.sin(v_theta)
    voice_track[vs0 + haas_samples : min(n_total, vs1 + haas_samples), 1] = r_sig[: min(v_len, n_total - (vs0 + haas_samples))]

    # Apply lush velvet studio stereo reverb + glide tail to the voice!
    voice_with_reverb = apply_stereo_studio_reverb(voice_track, SR, wet=0.25, predelay_ms=28.0)
    mix += voice_with_reverb

    # Final Master Bus: Clean fade-out at end (4.05s -> 4.56s) and true-peak limiter (-1.0 dBFS)
    master_fade = np.ones(n_total, dtype=np.float32)
    for i in range(n_total):
        ti_val = i / SR
        if ti_val < 0.02:
            master_fade[i] = ti_val / 0.02
        elif ti_val > 4.05:
            master_fade[i] = 1.0 - smoothstep(4.05, 4.56, ti_val)
    mix *= master_fade[:, None]

    mix = np.nan_to_num(mix, nan=0.0, posinf=0.0, neginf=0.0)
    peak = np.max(np.abs(mix)) + 1e-6
    if peak > 0.89:
        mix = mix * (0.89 / peak)

    out_wav = os.path.join(WORK_DIR, "bm_intro_master_audio.wav")
    sf.write(out_wav, mix, SR, subtype="PCM_16")
    print(f"[Audio] Saved master sonic ident: {out_wav} ({DURATION:.2f}s, peak={np.max(np.abs(mix)):.2f})")
    return out_wav


# ==============================================================================
# 2. LOGO GEOMETRY, 3-PIECE EXTRACTION, CONTOURS & 3D BEVEL MAPS
# ==============================================================================
def prepare_logo_assets():
    src = cv2.imread(UPLOADED_LOGO)
    rgb = cv2.cvtColor(src, cv2.COLOR_BGR2RGB).astype(np.float32)

    interior = (rgb[:, :, 0] - rgb[:, :, 1]) > 120
    brand_rgb = np.median(rgb[interior], axis=0) / 255.0  # ~ [0.968, 0.310, 0.553]

    g_bg = 254.0
    g_fg = float(np.median(rgb[interior, 1]))
    alpha = np.clip((g_bg - rgb[:, :, 1]) / (g_bg - g_fg), 0.0, 1.0)
    alpha = np.clip((alpha - 0.04) / 0.92, 0.0, 1.0)

    # Upscale 3x for smooth contours
    h0, w0 = alpha.shape
    up_alpha = cv2.resize(alpha, (w0 * 3, h0 * 3), interpolation=cv2.INTER_CUBIC)
    up_alpha = cv2.GaussianBlur(up_alpha, (5, 5), 0.9)
    up_alpha = np.clip((up_alpha - 0.02) / 0.96, 0.0, 1.0)

    # Crop tight around BM logo
    ys, xs = np.where(up_alpha > 0.02)
    x0, x1 = xs.min(), xs.max()
    y0, y1 = ys.min(), ys.max()
    logo_crop = up_alpha[y0 : y1 + 1, x0 : x1 + 1]

    # Scale logo nicely onto 1920x1080 canvas: target width = 760px
    target_w = 760
    target_h = int(round(logo_crop.shape[0] * (target_w / logo_crop.shape[1])))
    logo_scaled = cv2.resize(logo_crop, (target_w, target_h), interpolation=cv2.INTER_AREA)

    full_mask = np.zeros((H, W), dtype=np.float32)
    cx, cy = W // 2, H // 2 - 12  # Slightly above geometric center (528) for balanced cinema framing
    lx0 = cx - target_w // 2
    ly0 = cy - target_h // 2
    full_mask[ly0 : ly0 + target_h, lx0 : lx0 + target_w] = logo_scaled

    # Connected components to separate B_top, B_bottom, and M!
    bin_mask = (full_mask > 0.15).astype(np.uint8)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(bin_mask)

    # Dilate each label slightly so anti-aliased edge pixels belong cleanly to their component
    comp_list = []
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    for lbl in range(1, num_labels):
        area = stats[lbl, cv2.CC_STAT_AREA]
        if area < 200:
            continue
        c_bin = (labels == lbl).astype(np.uint8)
        c_dil = cv2.dilate(c_bin, kernel, iterations=1)
        c_alpha = full_mask * c_dil.astype(np.float32)
        comp_list.append((centroids[lbl][0], centroids[lbl][1], area, c_alpha))

    # Classify components: M has largest x centroid; between remaining B parts, smaller y is B_top, larger y is B_bot
    comp_list.sort(key=lambda item: item[0])
    b_parts = comp_list[:-1]
    m_part = comp_list[-1][3]
    b_parts.sort(key=lambda item: item[1])
    b_top = b_parts[0][3]
    b_bot = b_parts[1][3] if len(b_parts) > 1 else np.zeros_like(full_mask)

    pieces = [b_top, b_bot, m_part]

    # Extract arc-length resampled contours for laser rim tracing
    contours_resampled = []
    for p_mask in pieces:
        p_u8 = (p_mask * 255).astype(np.uint8)
        cnts, _ = cv2.findContours(p_u8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if not cnts:
            continue
        cnt = max(cnts, key=cv2.contourArea)[:, 0, :].astype(np.float32)  # (N, 2)
        # Close loop and resample uniformly to 900 points
        cnt_closed = np.vstack([cnt, cnt[0:1]])
        diffs = np.diff(cnt_closed, axis=0)
        seg_lens = np.hypot(diffs[:, 0], diffs[:, 1])
        cum_len = np.concatenate([[0.0], np.cumsum(seg_lens)])
        total_len = cum_len[-1]
        u = np.linspace(0.0, total_len, 900, endpoint=False)
        rx = np.interp(u, cum_len, cnt_closed[:, 0])
        ry = np.interp(u, cum_len, cnt_closed[:, 1])
        contours_resampled.append(np.column_stack([rx, ry]).astype(np.float32))

    # Compute 3D Glass / Satin Bevel Lighting Maps from Distance Transform Heightfield
    dist = cv2.distanceTransform((full_mask > 0.35).astype(np.uint8), cv2.DIST_L2, 5)
    height_field = np.minimum(dist, 22.0) / 22.0
    height_smooth = cv2.GaussianBlur(height_field, (0, 0), 3.2)

    gx = cv2.Sobel(height_smooth, cv2.CV_32F, 1, 0, ksize=3) * 2.2
    gy = cv2.Sobel(height_smooth, cv2.CV_32F, 0, 1, ksize=3) * 2.2
    nx = -gx
    ny = -gy
    nz = np.ones_like(nx)
    norm_len = np.sqrt(nx * nx + ny * ny + nz * nz) + 1e-6
    nx /= norm_len
    ny /= norm_len
    nz /= norm_len

    # Top-left studio key light + bottom-right rim highlight
    key_dot = np.clip(nx * (-0.55) + ny * (-0.65) + nz * 0.52, 0.0, 1.0)
    rim_dot = np.clip(nx * 0.62 + ny * 0.55 + nz * 0.56, 0.0, 1.0)
    edge_band = np.clip(1.0 - np.abs(dist - 2.5) / 2.8, 0.0, 1.0) * full_mask

    # Multi-scale HDR Neon Glows for assembled logo
    glow_tight = cv2.GaussianBlur(full_mask, (0, 0), 7.0)
    glow_mid = cv2.GaussianBlur(full_mask, (0, 0), 24.0)
    glow_wide = cv2.GaussianBlur(full_mask, (0, 0), 68.0)

    return {
        "brand_rgb": brand_rgb,
        "full_mask": full_mask,
        "pieces": pieces,
        "contours": contours_resampled,
        "key_dot": key_dot,
        "rim_dot": rim_dot,
        "edge_band": edge_band,
        "nx": nx,
        "ny": ny,
        "glow_tight": glow_tight,
        "glow_mid": glow_mid,
        "glow_wide": glow_wide,
        "bbox": (lx0, ly0, lx0 + target_w, ly0 + target_h),
        "center": (cx, cy),
    }


# ==============================================================================
# 3. 60FPS HDR FLOAT32 MOTION-GRAPHICS COMPOSITOR
# ==============================================================================
def aces_tonemap_to_bgr8(hdr_rgb):
    """Smooth filmic HDR -> sRGB 8-bit BGR with subtle dither to eliminate banding."""
    x = np.maximum(hdr_rgb, 0.0)
    # Soft shoulder filmic curve (preserves exact brand colors below 0.8 while gracefully rolling highlights > 1.0)
    mapped = x / (1.0 + 0.18 * (x ** 2.2))
    mapped = np.clip(mapped, 0.0, 1.0)
    # Gamma / sRGB curve approximation (input already authored in perceptual space, apply gentle contrast polish)
    bgr = mapped[:, :, ::-1] * 255.0
    return np.clip(bgr, 0, 255).astype(np.uint8)


def warp_mask_similarity(mask, dx, dy, scale, cx, cy):
    """Fast affine transform around (cx, cy) with translation (dx, dy) and scale."""
    if abs(dx) < 0.05 and abs(dy) < 0.05 and abs(scale - 1.0) < 0.0003:
        return mask
    m = np.float32([
        [scale, 0.0, cx * (1.0 - scale) + dx],
        [0.0, scale, cy * (1.0 - scale) + dy],
    ])
    return cv2.warpAffine(mask, m, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0.0)


def render_intro_video(assets, audio_wav, theme="dark"):
    out_name = (
        "BM_Intro_Modern_Dark_1080p60.mp4"
        if theme == "dark"
        else "BM_Intro_Modern_Light_1080p60.mp4"
    )
    out_mp4 = os.path.join(OUT_DIR, out_name)
    print(f"\n[Render] Starting {theme.upper()} 60fps HDR render -> {out_mp4}")
    t_start_wall = time.time()

    cx, cy = assets["center"]
    brand_r, brand_g, brand_b = assets["brand_rgb"]  # ~0.968, 0.310, 0.553

    # Precompute normalized screen coordinate grids (H, W)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    nx_grid = (xx - cx) / (W * 0.5)
    ny_grid = (yy - cy) / (H * 0.5)
    rad2 = nx_grid * nx_grid + (ny_grid * (H / W) * 1.65) ** 2
    rad = np.sqrt(np.maximum(rad2, 1e-6))

    # Precompute static micro-dither noise to prevent 8-bit gradient banding
    rng = np.random.default_rng(2026)
    dither = rng.uniform(-0.45, 0.45, (H, W, 1)).astype(np.float32) / 255.0

    # Precompute subtle tech dot-grid pattern
    grid_spacing = 48
    gx_mod = np.abs(((xx - cx + grid_spacing // 2) % grid_spacing) - grid_spacing // 2)
    gy_mod = np.abs(((yy - cy + grid_spacing // 2) % grid_spacing) - grid_spacing // 2)
    dot_dist = np.hypot(gx_mod, gy_mod)
    dot_grid = np.clip(1.5 - dot_dist, 0.0, 1.0) * np.exp(-rad2 * 1.4)

    # Precompute 3D floating bokeh particles & impact micro-sparks
    n_bokeh = 56
    bokeh_x0 = rng.uniform(80, W - 80, n_bokeh)
    bokeh_y0 = rng.uniform(70, H - 70, n_bokeh)
    bokeh_vx = rng.uniform(-28, 28, n_bokeh)
    bokeh_vy = rng.uniform(-38, -10, n_bokeh)
    bokeh_r = rng.uniform(2.2, 6.5, n_bokeh)
    bokeh_phase = rng.uniform(0, 2 * np.pi, n_bokeh)
    bokeh_is_cyan = rng.random(n_bokeh) > 0.68

    n_sparks = 48
    sp_angles = np.linspace(0, 2 * np.pi, n_sparks, endpoint=False) + rng.uniform(-0.08, 0.08, n_sparks)
    sp_speeds = rng.uniform(240, 620, n_sparks)
    sp_sizes = rng.uniform(1.8, 3.8, n_sparks)

    # Precompute base shaded 3D BM logo RGB (before dynamic light sweep)
    full_m = assets["full_mask"]
    grad_t = np.clip((xx - 560.0) / 800.0 * 0.65 + (yy - 360.0) / 340.0 * 0.35, 0.0, 1.0)
    # Rich signature BM Pink gradient (#FF5C97 top-left -> #F74F8D core -> #E02B72 deep rose)
    base_r = (1.00 * (1.0 - grad_t) + 0.91 * grad_t)
    base_g = (0.37 * (1.0 - grad_t) + 0.19 * grad_t)
    base_b = (0.61 * (1.0 - grad_t) + 0.47 * grad_t)

    # Add 3D glass bevel shading & satin rim
    bevel_boost = 0.20 * (assets["key_dot"] ** 2.6) + 0.26 * assets["edge_band"] * (0.5 + 0.5 * assets["key_dot"])
    rim_cyan = 0.16 * (assets["rim_dot"] ** 3.2) * assets["edge_band"]

    shaded_logo_rgb = np.zeros((H, W, 3), dtype=np.float32)
    shaded_logo_rgb[:, :, 0] = base_r + bevel_boost * 0.85 + rim_cyan * 0.25
    shaded_logo_rgb[:, :, 1] = base_g + bevel_boost * 0.80 + rim_cyan * 0.75
    shaded_logo_rgb[:, :, 2] = base_b + bevel_boost * 0.90 + rim_cyan * 1.00

    # Launch FFmpeg stdin pipe for ultra-fast lossless-grade H.264 + AAC muxing
    cmd = [
        FFMPEG,
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-pix_fmt", "bgr24",
        "-s", f"{W}x{H}",
        "-r", str(FPS),
        "-i", "-",
        "-i", audio_wav,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "15",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "320k",
        "-movflags", "+faststart",
        "-shortest",
        out_mp4,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    piece_configs = [
        # (start_t, end_t, init_dx, init_dy, init_scale)
        (0.03, 0.89, -540.0, -90.0, 1.30),   # B upper ribbon
        (0.11, 0.90, -390.0, +165.0, 1.24),  # B lower loop
        (0.15, 0.91, +550.0, +40.0, 1.30),   # M wing
    ]

    sample_frames_to_save = {36, 58, 98, 116, 175} if theme == "dark" else {58, 108}

    for f in range(N_FRAMES):
        t = f / FPS

        # ------------------------------------------------------------------
        # A. Animated Studio Backdrop (Dark Space Aurora vs Pearl Light Studio)
        # ------------------------------------------------------------------
        if theme == "dark":
            # Deep obsidian midnight gradient + breathing magenta/violet/cyan volumetric aurora
            aurora_shift = 0.18 * math.sin(t * 1.1)
            a_pink = np.exp(-((nx_grid + 0.18 - aurora_shift) ** 2 + (ny_grid * 1.3 + 0.06) ** 2) * 2.1)
            a_violet = np.exp(-((nx_grid - 0.24 + aurora_shift) ** 2 + (ny_grid * 1.3 - 0.10) ** 2) * 2.3)
            ambient_pulse = 0.72 + 0.28 * smoothstep(0.75, 1.15, t)

            canvas = np.zeros((H, W, 3), dtype=np.float32)
            # Base midnight tone (#06070F -> #0D0F1E center)
            vignette = np.exp(-rad2 * 0.85)
            canvas[:, :, 0] = 0.022 + 0.032 * vignette + (0.095 * a_pink + 0.042 * a_violet) * ambient_pulse
            canvas[:, :, 1] = 0.024 + 0.028 * vignette + (0.022 * a_pink + 0.028 * a_violet) * ambient_pulse
            canvas[:, :, 2] = 0.048 + 0.055 * vignette + (0.065 * a_pink + 0.095 * a_violet) * ambient_pulse

            # Subtle cyber dot-grid
            grid_alpha = 0.045 * smoothstep(0.0, 0.6, t)
            canvas += dot_grid[:, :, None] * np.array([0.55, 0.35, 0.75], dtype=np.float32) * grid_alpha
        else:
            # Clean Apple-style Pearl-White Luxury Studio Backdrop
            vignette = np.exp(-rad2 * 0.65)
            a_pink = np.exp(-((nx_grid + 0.16) ** 2 + (ny_grid * 1.3) ** 2) * 2.0)
            a_blue = np.exp(-((nx_grid - 0.22) ** 2 + (ny_grid * 1.3) ** 2) * 2.2)
            canvas = np.zeros((H, W, 3), dtype=np.float32)
            canvas[:, :, 0] = 0.935 + 0.055 * vignette + 0.015 * a_pink
            canvas[:, :, 1] = 0.938 + 0.052 * vignette - 0.012 * a_pink + 0.006 * a_blue
            canvas[:, :, 2] = 0.952 + 0.042 * vignette + 0.005 * a_pink + 0.015 * a_blue
            canvas -= dot_grid[:, :, None] * 0.035

        # Floating 3D Bokeh Dust Layer
        bokeh_layer = np.zeros((H, W, 3), dtype=np.float32)
        b_fade = smoothstep(0.05, 0.65, t)
        for bi in range(n_bokeh):
            bx = (bokeh_x0[bi] + bokeh_vx[bi] * t) % W
            by = (bokeh_y0[bi] + bokeh_vy[bi] * t) % H
            twinkle = 0.45 + 0.55 * math.sin(t * 2.8 + bokeh_phase[bi])
            br = int(round(bokeh_r[bi]))
            if theme == "dark":
                col = (0.35, 0.82, 1.0) if bokeh_is_cyan[bi] else (1.0, 0.38, 0.68)
                strength = 0.16 * twinkle * b_fade
            else:
                col = (0.95, 0.35, 0.60)
                strength = 0.10 * twinkle * b_fade
            cv2.circle(
                bokeh_layer,
                (int(bx), int(by)),
                br,
                (col[0] * strength, col[1] * strength, col[2] * strength),
                -1,
                lineType=cv2.LINE_AA,
            )
        bokeh_layer = cv2.GaussianBlur(bokeh_layer, (9, 9), 2.2)
        if theme == "dark":
            canvas += bokeh_layer
        else:
            canvas = canvas * (1.0 - np.max(bokeh_layer, axis=2, keepdims=True) * 0.5) + bokeh_layer * 0.6

        # ------------------------------------------------------------------
        # B. Phase 1 (t < 0.91s): 3-Piece Kinetic Fly-In + Laser Perimeter Comet
        #    Phase 2-4 (t >= 0.91s): Locked 3D Logo + Slow Push-In + Elastic Pop
        # ------------------------------------------------------------------
        if t < 0.91:
            combined_mask = np.zeros((H, W), dtype=np.float32)
            chroma_r_acc = np.zeros((H, W), dtype=np.float32)
            chroma_b_acc = np.zeros((H, W), dtype=np.float32)
            laser_overlay = np.zeros((H, W, 3), dtype=np.float32)

            for p_idx, (t0_p, t1_p, idx0, idy0, isc0) in enumerate(piece_configs):
                raw_u = (t - t0_p) / (t1_p - t0_p)
                if raw_u <= 0.0:
                    continue
                u = ease_out_expo(raw_u)
                op = smoothstep(0.0, 0.18, raw_u)
                dx = idx0 * (1.0 - u)
                dy = idy0 * (1.0 - u)
                sc = 1.0 + (isc0 - 1.0) * (1.0 - u)

                w_mask = warp_mask_similarity(assets["pieces"][p_idx], dx, dy, sc, cx, cy) * op
                combined_mask = np.maximum(combined_mask, w_mask)

                # Velocity-proportional RGB chromatic dispersion during fast fly-in
                vel_factor = (1.0 - u) * op
                if vel_factor > 0.015:
                    shift_x = np.clip(dx * 0.032, -12.0, 12.0)
                    shift_y = np.clip(dy * 0.032, -8.0, 8.0)
                    chroma_r_acc = np.maximum(
                        chroma_r_acc,
                        warp_mask_similarity(w_mask, +shift_x, +shift_y, 1.0, cx, cy) * vel_factor,
                    )
                    chroma_b_acc = np.maximum(
                        chroma_b_acc,
                        warp_mask_similarity(w_mask, -shift_x, -shift_y, 1.0, cx, cy) * vel_factor,
                    )

                # Traveling Neon Laser Comet along each component's contour!
                if p_idx < len(assets["contours"]):
                    cnt = assets["contours"][p_idx]
                    # Transform contour points identically to piece
                    pts = (cnt - np.array([cx, cy], dtype=np.float32)) * sc + np.array([cx + dx, cy + dy], dtype=np.float32)
                    c_prog = clamp01((t - t0_p) / (t1_p - t0_p))
                    head_idx = int(c_prog * len(pts))
                    tail_len = 240
                    laser_fade = 1.0 - smoothstep(0.82, 1.0, c_prog)
                    if head_idx > 4 and laser_fade > 0.01:
                        s_idx = max(0, head_idx - tail_len)
                        seg = pts[s_idx:head_idx].astype(np.int32)
                        if len(seg) > 2:
                            # Outer pink-violet laser core
                            cv2.polylines(
                                laser_overlay,
                                [seg],
                                False,
                                (1.25 * laser_fade, 0.32 * laser_fade, 0.85 * laser_fade),
                                thickness=4,
                                lineType=cv2.LINE_AA,
                            )
                            # White-hot comet tip
                            tip_seg = pts[max(0, head_idx - 45) : head_idx].astype(np.int32)
                            if len(tip_seg) > 1:
                                cv2.polylines(
                                    laser_overlay,
                                    [tip_seg],
                                    False,
                                    (1.8 * laser_fade, 1.6 * laser_fade, 1.9 * laser_fade),
                                    thickness=2,
                                    lineType=cv2.LINE_AA,
                                )

            # Composite dynamic fly-in glow + chromatic trails + body
            dyn_glow = cv2.GaussianBlur(combined_mask, (0, 0), 18.0)
            if theme == "dark":
                canvas[:, :, 0] += dyn_glow * 0.65 + chroma_r_acc * 0.55
                canvas[:, :, 1] += dyn_glow * 0.16
                canvas[:, :, 2] += dyn_glow * 0.42 + chroma_b_acc * 0.65

            # Composite piece bodies
            piece_rgb = np.zeros((H, W, 3), dtype=np.float32)
            piece_rgb[:, :, 0] = brand_r * 1.03
            piece_rgb[:, :, 1] = brand_g * 1.02
            piece_rgb[:, :, 2] = brand_b * 1.03
            canvas = canvas * (1.0 - combined_mask[:, :, None]) + piece_rgb * combined_mask[:, :, None]

            if theme == "dark":
                laser_glow = cv2.GaussianBlur(laser_overlay, (0, 0), 6.0)
                canvas += laser_overlay * 0.85 + laser_glow * 1.15
            else:
                canvas = np.clip(canvas + laser_overlay * 0.35, 0.0, 1.2)

        else:
            # t >= 0.91s: Assembled 3D Beveled BM Logo + Elastic Lock-In + Slow Push-In!
            dt_lock = t - 0.91
            # Subtle damped elastic pop on impact + continuous majestic cinema push-in (1.00 -> 1.046)
            elastic = 0.036 * math.exp(-7.5 * dt_lock) * math.cos(18.0 * dt_lock)
            slow_push = 0.046 * smootherstep(0.91, DURATION, t)
            cur_scale = 1.0 + elastic + slow_push

            # Impact flash decay
            impact_flash = math.exp(-dt_lock / 0.16)

            # Build assembled logo layer at canonical coords, then apply smooth cur_scale zoom!
            logo_hdr = shaded_logo_rgb.copy()

            # --------------------------------------------------------------
            # C. Phase 3 (1.46s -> 2.52s): Signature "BM" Specular Light-Sweep!
            #    Synchronized to "B" (~1.56s-1.80s) and "M" (~1.84s-2.20s)
            # --------------------------------------------------------------
            sweep_u = (t - 1.46) / (2.46 - 1.46)
            anamorphic_flare = np.zeros((H, W, 3), dtype=np.float32)
            if 0.0 < sweep_u < 1.0:
                su_smooth = ease_in_out_cubic(sweep_u)
                # Diagonal plane sweeping from x=460 across B and M to x=1460
                beam_x = 460.0 + 1000.0 * su_smooth
                diag_coord = (xx - beam_x) + 0.42 * (yy - cy)
                sheen_core = np.exp(-0.5 * (diag_coord / 38.0) ** 2)
                sheen_wide = np.exp(-0.5 * (diag_coord / 115.0) ** 2)
                sheen_env = math.sin(math.pi * clamp01(sweep_u)) ** 0.75

                # Liquid-glass specular highlight across 3D normal surface + bright rim!
                spec_intensity = (sheen_core * 0.95 + sheen_wide * 0.32 * (0.4 + 0.6 * assets["edge_band"])) * sheen_env
                logo_hdr[:, :, 0] += spec_intensity * 1.05
                logo_hdr[:, :, 1] += spec_intensity * 0.96
                logo_hdr[:, :, 2] += spec_intensity * 1.08

                # Cinema Horizontal Anamorphic Lens Streak gliding from B -> M
                flare_x = 580.0 + 760.0 * su_smooth
                flare_y = cy - 18.0 + 36.0 * su_smooth
                fx_dist = (xx - flare_x) / 290.0
                fy_core = (yy - flare_y) / 2.6
                fy_halo = (yy - flare_y) / 16.0
                streak = (
                    np.exp(-0.5 * (fx_dist ** 2 + fy_core ** 2)) * 0.75
                    + np.exp(-0.5 * ((fx_dist * 1.3) ** 2 + fy_halo ** 2)) * 0.28
                ) * sheen_env
                anamorphic_flare[:, :, 0] = streak * 1.15
                anamorphic_flare[:, :, 1] = streak * 0.72
                anamorphic_flare[:, :, 2] = streak * 1.05

            # Impact flash brightening at t=0.91s
            if impact_flash > 0.005:
                logo_hdr += impact_flash * np.array([0.55, 0.42, 0.52], dtype=np.float32)

            # Warp mask, glows, and shaded RGB together by cur_scale for butter-smooth push-in
            m_cur = warp_mask_similarity(full_m, 0.0, 0.0, cur_scale, cx, cy)
            gt_cur = warp_mask_similarity(assets["glow_tight"], 0.0, 0.0, cur_scale, cx, cy)
            gm_cur = warp_mask_similarity(assets["glow_mid"], 0.0, 0.0, cur_scale, cx, cy)
            gw_cur = warp_mask_similarity(assets["glow_wide"], 0.0, 0.0, cur_scale, cx, cy)

            if abs(cur_scale - 1.0) > 0.0003:
                mat = np.float32([
                    [cur_scale, 0.0, cx * (1.0 - cur_scale)],
                    [0.0, cur_scale, cy * (1.0 - cur_scale)],
                ])
                logo_cur_rgb = cv2.warpAffine(logo_hdr, mat, (W, H), flags=cv2.INTER_LINEAR)
            else:
                logo_cur_rgb = logo_hdr

            # --------------------------------------------------------------
            # Shockwave Ring & Luminous Spark Burst (0.91s -> 1.75s)
            # --------------------------------------------------------------
            if dt_lock < 0.88:
                sw_p = dt_lock / 0.88
                sw_rad = 60.0 + 680.0 * ease_out_quint(sw_p)
                sw_alpha = (1.0 - sw_p) ** 1.85
                pixel_r = np.hypot(xx - cx, (yy - cy) * 1.18)
                ring = np.exp(-0.5 * ((pixel_r - sw_rad) / (14.0 + 18.0 * sw_p)) ** 2) * sw_alpha
                if theme == "dark":
                    canvas[:, :, 0] += ring * 0.62
                    canvas[:, :, 1] += ring * 0.28
                    canvas[:, :, 2] += ring * 0.55
                else:
                    canvas[:, :, 0] += ring * 0.18
                    canvas[:, :, 1] -= ring * 0.08
                    canvas[:, :, 2] += ring * 0.06

            if dt_lock < 1.35:
                sp_layer = np.zeros((H, W, 3), dtype=np.float32)
                sp_fade = (1.0 - dt_lock / 1.35) ** 1.7
                # Decelerating drag physics: dist = v0 * (1 - exp(-k*t)) / k
                drag_k = 3.2
                dist_factor = (1.0 - math.exp(-drag_k * dt_lock)) / drag_k
                for si in range(n_sparks):
                    r_dist = 95.0 + sp_speeds[si] * dist_factor
                    sx = cx + math.cos(sp_angles[si]) * r_dist * 1.25
                    sy = cy + math.sin(sp_angles[si]) * r_dist * 0.78
                    if 0 <= sx < W and 0 <= sy < H:
                        scol = (1.1 * sp_fade, 0.55 * sp_fade, 0.88 * sp_fade) if si % 3 != 0 else (0.55 * sp_fade, 0.92 * sp_fade, 1.15 * sp_fade)
                        cv2.circle(sp_layer, (int(sx), int(sy)), int(round(sp_sizes[si])), scol, -1, lineType=cv2.LINE_AA)
                sp_blur = cv2.GaussianBlur(sp_layer, (7, 7), 1.6)
                if theme == "dark":
                    canvas += sp_layer * 0.9 + sp_blur * 0.8
                else:
                    canvas = canvas * (1.0 - np.max(sp_blur, axis=2, keepdims=True) * 0.4) + sp_layer * 0.5

            # Composite Ambient Neon Glow / Studio Drop-Shadow underneath BM Logo
            breath = 0.92 + 0.08 * math.sin(dt_lock * 2.6)
            if theme == "dark":
                glow_energy = (gt_cur * 0.42 + gm_cur * 0.34 + gw_cur * 0.24) * breath + gm_cur * impact_flash * 0.65
                canvas[:, :, 0] += glow_energy * 0.98
                canvas[:, :, 1] += glow_energy * 0.22
                canvas[:, :, 2] += glow_energy * 0.58
            else:
                # Soft luxury rose-tinted studio shadow + subtle halo on pearl white
                shadow = warp_mask_similarity(assets["glow_mid"], 0.0, 18.0, cur_scale, cx, cy)
                canvas[:, :, 0] -= shadow * 0.09
                canvas[:, :, 1] -= shadow * 0.16
                canvas[:, :, 2] -= shadow * 0.11

            # Alpha-composite crisp 3D Beveled BM Logo
            canvas = canvas * (1.0 - m_cur[:, :, None]) + logo_cur_rgb * m_cur[:, :, None]

            # Add Anamorphic Specular Flare on top
            if theme == "dark":
                canvas += anamorphic_flare
            else:
                canvas += anamorphic_flare * 0.45

            # Minimalist Horizon Accent Line underneath BM Logo (expands during "BM" glide 1.50s -> 4.00s)
            if t > 1.48:
                line_in = ease_out_expo((t - 1.48) / 0.65)
                half_w = int(195 * line_in)
                ly = cy + 206
                if half_w > 2:
                    line_env = 0.78 * smoothstep(1.48, 1.72, t)
                    x_line = np.abs(xx[ly - 8 : ly + 9, :] - cx)
                    y_line = np.abs(yy[ly - 8 : ly + 9, :] - ly)
                    horiz_mask = np.clip(1.0 - x_line / max(1.0, float(half_w)), 0.0, 1.0) ** 1.4
                    vert_core = np.exp(-0.5 * (y_line / 1.1) ** 2)
                    vert_glow = np.exp(-0.5 * (y_line / 4.2) ** 2) * 0.38
                    bar = (vert_core + vert_glow) * horiz_mask * line_env
                    if theme == "dark":
                        canvas[ly - 8 : ly + 9, :, 0] += bar * 0.98
                        canvas[ly - 8 : ly + 9, :, 1] += bar * 0.36
                        canvas[ly - 8 : ly + 9, :, 2] += bar * 0.68
                    else:
                        canvas[ly - 8 : ly + 9, :, 0] = canvas[ly - 8 : ly + 9, :, 0] * (1.0 - bar * 0.5) + bar * 0.95 * 0.5
                        canvas[ly - 8 : ly + 9, :, 1] = canvas[ly - 8 : ly + 9, :, 1] * (1.0 - bar * 0.5) + bar * 0.28 * 0.5
                        canvas[ly - 8 : ly + 9, :, 2] = canvas[ly - 8 : ly + 9, :, 2] * (1.0 - bar * 0.5) + bar * 0.55 * 0.5

        # ------------------------------------------------------------------
        # D. Cinematic Intro Fade-In (0.00-0.18s) & Fade-Out (3.95-4.56s)
        # ------------------------------------------------------------------
        fade_in = smoothstep(0.0, 0.16, t)
        fade_out = 1.0 - smootherstep(3.96, 4.56, t)
        if theme == "dark":
            canvas *= (fade_in * fade_out)
        else:
            # Light edition fades in from white and fades cleanly to white/black?
            # Fading cleanly to pure white (#FFFFFF) on Light edition matches white slides!
            bg_end = 1.0
            alpha_vis = fade_in * fade_out
            canvas = canvas * alpha_vis + bg_end * (1.0 - alpha_vis)

        canvas += dither
        frame_bgr = aces_tonemap_to_bgr8(canvas)

        if f in sample_frames_to_save:
            preview_jpg = os.path.join(WORK_DIR, f"preview_{theme}_f{f:03d}.jpg")
            cv2.imwrite(preview_jpg, frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, 94])

        proc.stdin.write(frame_bgr.tobytes())

        if (f + 1) % 60 == 0 or f == N_FRAMES - 1:
            print(f"  [{theme}] Frame {f+1}/{N_FRAMES} ({(f+1)/N_FRAMES*100:.0f}%)", flush=True)

    proc.stdin.close()
    stderr_bytes = proc.stderr.read()
    ret = proc.wait()
    if ret != 0:
        raise RuntimeError(f"FFmpeg failed ({ret}): {stderr_bytes.decode('utf-8', errors='replace')}")

    elapsed = time.time() - t_start_wall
    mb = os.path.getsize(out_mp4) / (1024 * 1024)
    print(f"[Render] Completed {out_mp4} in {elapsed:.1f}s ({mb:.2f} MB)!")
    return out_mp4


def main():
    audio_wav = build_master_audio()
    print("[Assets] Preparing 3-piece BM geometry, contours & 3D bevel maps...")
    assets = prepare_logo_assets()
    dark_mp4 = render_intro_video(assets, audio_wav, theme="dark")
    light_mp4 = render_intro_video(assets, audio_wav, theme="light")
    print("\n=== ALL BM INTRO DELIVERABLES READY ===")
    print("1.", dark_mp4)
    print("2.", light_mp4)


if __name__ == "__main__":
    main()

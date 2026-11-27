# -*- coding: utf-8 -*-
"""
BM Original 100% Copyright-Free Intro Music Composer & Muxer (5.00s, 48kHz Stereo)
Style: Warm Modern Educational Studio Ident (Soft Felt Grand Piano + Delicate Glass Bell + Velvet Ambient Pad)
Key & Progression: G Major (Cmaj9 -> Dadd11 -> Gmaj9) — 100% original composition, zero copyright risk.
Muxes cleanly with the 1080p60 White-Studio + Slogan 3D video into ONE single final MP4.
"""

import os
import sys
import math
import subprocess
import numpy as np
import soundfile as sf
import imageio_ffmpeg

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

BASE_DIR = r"C:\Users\DELL\Documents\CODE\DU_AN"
OUT_DIR = os.path.join(BASE_DIR, "02_San_Pham_Hoan_Chinh", "Video_Intro_BM")
WORK_DIR = os.path.join(BASE_DIR, "video_build", "bm_orig_music")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(WORK_DIR, exist_ok=True)

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
SR = 48000
DURATION = 5.00
N_SAMPLES = int(round(DURATION * SR))


def midi_to_freq(midi_note):
    return 440.0 * (2.0 ** ((midi_note - 69.0) / 12.0))


def note_to_midi(name):
    notes = {
        "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5,
        "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11,
    }
    if len(name) == 3:
        pitch, octave = name[:2], int(name[2])
    else:
        pitch, octave = name[:1], int(name[1])
    return 12 * (octave + 1) + notes[pitch]


def fft_eq(signal, sr, gains_db_points, lp_cutoff=15500.0):
    n = len(signal)
    spec = np.fft.rfft(signal)
    freqs = np.fft.rfftfreq(n, d=1.0 / sr)
    log_f = np.log10(np.maximum(freqs, 15.0))
    pts_f = np.log10([p[0] for p in gains_db_points])
    pts_g = [p[1] for p in gains_db_points]
    db_curve = np.interp(log_f, pts_f, pts_g)
    hp = np.clip((freqs - 34.0) / 28.0, 0.0, 1.0) ** 2
    lp = 1.0 / (1.0 + (freqs / lp_cutoff) ** 6)
    gain = (10.0 ** (db_curve / 20.0)) * hp * lp
    return np.fft.irfft(spec * gain, n=n).astype(np.float32)


def add_stereo_pan(mix, start_idx, mono_sig, pan):
    end_idx = min(len(mix), start_idx + len(mono_sig))
    seg_len = end_idx - start_idx
    if seg_len <= 0:
        return
    sig = mono_sig[:seg_len]
    theta = (pan + 1.0) * (math.pi / 4.0)
    gain_l = math.cos(theta)
    gain_r = math.sin(theta)

    delay_smp = int(abs(pan) * 0.00035 * SR)
    if pan < 0 and delay_smp > 0:
        mix[start_idx:end_idx, 0] += sig * gain_l
        r_end = min(len(mix), end_idx + delay_smp)
        mix[start_idx + delay_smp : r_end, 1] += sig[: r_end - (start_idx + delay_smp)] * gain_r
    elif pan > 0 and delay_smp > 0:
        mix[start_idx:end_idx, 1] += sig * gain_r
        l_end = min(len(mix), end_idx + delay_smp)
        mix[start_idx + delay_smp : l_end, 0] += sig[: l_end - (start_idx + delay_smp)] * gain_l
    else:
        mix[start_idx:end_idx, 0] += sig * gain_l
        mix[start_idx:end_idx, 1] += sig * gain_r


def synth_felt_grand_piano(note_name, dur_s, velocity=0.75, seed=1):
    """
    Warm Studio Felt Grand Piano:
    - Steep natural felt-hammer spectral rolloff (1 / k^2.75) — zero buzzy harpsichord harmonics!
    - Rapid transient brightness decay on upper partials (hammer strike melts into pure warm singing tone)
    - Trichord unison string beating + subtle warm wooden felt key thump
    """
    midi = note_to_midi(note_name)
    f0 = midi_to_freq(midi)
    n = int(round(dur_s * SR))
    t = np.arange(n, dtype=np.float32) / SR
    rng = np.random.default_rng(seed + midi * 31)

    B = float(np.clip(0.00010 * (2.0 ** ((midi - 60.0) / 28.0)), 0.00004, 0.00045))
    tau_main = float(np.clip(1.95 * (0.5 ** ((midi - 58.0) / 24.0)), 0.55, 2.85))

    detunes_cents = [-0.48, 0.0, +0.52] if midi >= 50 else [-0.28, +0.28]
    out = np.zeros(n, dtype=np.float32)

    # Acoustic grand piano harmonic weights + crisp initial 85ms hammer-bridge crest ("plink" -> warm singing sustain!)
    partial_weights = [1.00, 0.56, 0.28, 0.14, 0.075, 0.038, 0.019, 0.009, 0.004]
    for k, w_k in enumerate(partial_weights, start=1):
        fk_c = k * f0 * math.sqrt(1.0 + B * k * k)
        if fk_c >= 12000.0:
            break
        # Three-stage real piano bridge envelope: crisp 75ms hammer ping + medium body + warm pedal sustain
        if k == 1:
            env_k = (
                0.48 * np.exp(-t / 0.095)
                + 0.34 * np.exp(-t / (tau_main * 0.45))
                + 0.18 * np.exp(-t / (tau_main * 1.45))
            )
        elif k == 2:
            env_k = (
                0.58 * np.exp(-t / 0.075)
                + 0.28 * np.exp(-t / (tau_main * 0.32))
                + 0.14 * np.exp(-t / (tau_main * 0.95))
            )
        else:
            tau_ping = 0.065 / ((k - 1) ** 0.85)
            tau_body = (tau_main * 0.24) / (k ** 1.55)
            env_k = 0.78 * np.exp(-t / max(0.012, tau_ping)) + 0.22 * np.exp(-t / max(0.035, tau_body))

        p_wave = np.zeros(n, dtype=np.float32)
        for c_det in detunes_cents:
            fk = fk_c * (2.0 ** (c_det / 1200.0))
            ph0 = rng.uniform(0.0, 0.18)
            p_wave += np.sin(2.0 * np.pi * fk * t + ph0)
        p_wave /= len(detunes_cents)

        vel_scale = velocity ** (0.55 + 0.18 * (k - 1))
        out += w_k * vel_scale * env_k * p_wave

    # Crisp natural acoustic piano hammer attack (1.6ms)
    attack_env = 1.0 - np.exp(-t / 0.0016)
    out *= attack_env

    # Subtle warm felt-hammer woody thud (140Hz-380Hz, 20ms)
    th_len = min(n, int(0.024 * SR))
    tt = t[:th_len]
    w_noise = rng.standard_normal(th_len).astype(np.float32)
    sp = np.fft.rfft(w_noise)
    fr = np.fft.rfftfreq(th_len, 1.0 / SR)
    bp = np.exp(-0.5 * (np.log2(np.maximum(fr, 25.0) / 210.0) / 0.70) ** 2)
    thud = np.fft.irfft(sp * bp, n=th_len).astype(np.float32)
    thud = thud / (np.max(np.abs(thud)) + 1e-6) * (0.055 * velocity) * np.exp(-tt / 0.006) * np.sin(np.pi * tt / 0.024)
    out[:th_len] += thud

    rel = min(n, int(0.09 * SR))
    out[-rel:] *= np.linspace(1.0, 0.0, rel, dtype=np.float32) ** 1.5

    out = out / (np.max(np.abs(out)) + 1e-6) * (velocity * 0.36)
    return out


def synth_delicate_glass_droplet(note_name, dur_s, amp=0.045):
    """Soft, round glass celeste droplet (like video_mẫu's warm crystal sparkle)."""
    midi = note_to_midi(note_name)
    f0 = midi_to_freq(midi)
    n = int(round(dur_s * SR))
    t = np.arange(n, dtype=np.float32) / SR

    # Pure sine + gentle fast-decaying octave chime (zero harsh metallicclang)
    wave = (
        1.00 * np.sin(2.0 * np.pi * f0 * t) * np.exp(-t / 0.52)
        + 0.22 * np.sin(2.0 * np.pi * (2.0 * f0) * t + 0.5) * np.exp(-t / 0.16)
        + 0.07 * np.sin(2.0 * np.pi * (3.0 * f0) * t + 1.2) * np.exp(-t / 0.055)
    )
    attack = 1.0 - np.exp(-t / 0.0028)
    rel = np.ones(n, dtype=np.float32)
    rl = min(n, int(0.08 * SR))
    rel[-rl:] = np.linspace(1.0, 0.0, rl, dtype=np.float32)
    wave = wave * attack * rel
    return (wave / (np.max(np.abs(wave)) + 1e-6) * amp).astype(np.float32)


def synth_velvet_ambient_pad(note_names, t_start, t_end, amp=0.11):
    """Deeply warm, low-passed (<820Hz) cinema ambient synth pad + sub-bass pillow."""
    n = int(round((t_end - t_start) * SR))
    t = np.arange(n, dtype=np.float32) / SR
    dur = t_end - t_start
    pad_L = np.zeros(n, dtype=np.float32)
    pad_R = np.zeros(n, dtype=np.float32)

    rng = np.random.default_rng(int(t_start * 1000) + 77)
    for idx, nm in enumerate(note_names):
        f0 = midi_to_freq(note_to_midi(nm))
        vL = np.zeros(n, dtype=np.float32)
        vR = np.zeros(n, dtype=np.float32)
        for det_hz in [-0.45, -0.15, +0.17, +0.48]:
            ph1 = rng.uniform(0, 2 * np.pi)
            ph2 = rng.uniform(0, 2 * np.pi)
            vL += (np.sin(2 * np.pi * (f0 + det_hz) * t + ph1) + 0.16 * np.sin(4 * np.pi * (f0 + det_hz) * t + ph2)) * 0.25
            vR += (np.sin(2 * np.pi * (f0 - det_hz * 0.9) * t + ph2) + 0.16 * np.sin(4 * np.pi * (f0 - det_hz * 0.9) * t + ph1)) * 0.25

        pan = -0.42 + 0.84 * (idx / max(1, len(note_names) - 1))
        th = (pan + 1.0) * (math.pi / 4.0)
        pad_L += vL * math.cos(th)
        pad_R += vR * math.sin(th)

    # Low-pass at 820 Hz so the pad is pure warm velvet air, zero organ buzz!
    pad_L = fft_eq(pad_L, SR, [(40, +1.0), (140, +2.5), (400, 0.0), (800, -3.0), (1600, -18.0)], lp_cutoff=880.0)
    pad_R = fft_eq(pad_R, SR, [(40, +1.0), (140, +2.5), (400, 0.0), (800, -3.0), (1600, -18.0)], lp_cutoff=880.0)

    attack = (1.0 - np.exp(-t / 0.28)) ** 1.3
    decay = np.exp(-np.maximum(0.0, t - dur * 0.30) / (dur * 0.55))
    fade_end = 1.0 - np.clip((t - (dur - 0.45)) / 0.45, 0.0, 1.0) ** 1.6
    env = attack * decay * fade_end

    stereo = np.column_stack([pad_L * env, pad_R * env]).astype(np.float32)
    stereo = stereo / (np.max(np.abs(stereo)) + 1e-6) * amp
    return stereo


def make_soft_air_swell(n_samples, t0, t1, amp=0.055):
    """Gentle breathy studio air swell (like the soft cinematic whoosh in video_mẫu)."""
    out = np.zeros((n_samples, 2), dtype=np.float32)
    i0, i1 = int(t0 * SR), int(t1 * SR)
    ln = i1 - i0
    rng = np.random.default_rng(1234)
    for ch in range(2):
        w = rng.standard_normal(ln).astype(np.float32)
        sp = np.fft.rfft(w)
        fr = np.fft.rfftfreq(ln, 1.0 / SR)
        bp = np.exp(-0.5 * (np.log2(np.maximum(fr, 40.0) / 680.0) / 0.95) ** 2)
        air = np.fft.irfft(sp * bp, n=ln).astype(np.float32)
        air = air / (np.max(np.abs(air)) + 1e-6) * amp
        tn = np.linspace(0.0, 1.0, ln, dtype=np.float32)
        env = np.maximum(0.0, np.sin(np.pi * (tn ** 0.9))) ** 2.0
        out[i0:i1, ch] = air * env
    return out


def apply_lush_scoring_stage_reverb(stereo_in, sr, wet=0.34, predelay_ms=22.0):
    """Warm cinema scoring-stage reverb with velvet high-damping."""
    n = len(stereo_in)
    in_L = fft_eq(stereo_in[:, 0], sr, [(60, -8), (220, +1.0), (1000, 0), (3200, -4.0), (7000, -16.0)], lp_cutoff=5200.0)
    in_R = fft_eq(stereo_in[:, 1], sr, [(60, -8), (220, +1.0), (1000, 0), (3200, -4.0), (7000, -16.0)], lp_cutoff=5200.0)

    pre = int(predelay_ms * 0.001 * sr)
    rev_L = np.zeros(n, dtype=np.float32)
    rev_R = np.zeros(n, dtype=np.float32)

    taps_L = [(29, 0.40), (53, 0.34), (89, 0.28), (137, 0.23), (193, 0.19), (269, 0.15), (359, 0.115), (467, 0.085), (593, 0.060), (739, 0.040), (907, 0.024)]
    taps_R = [(37, 0.40), (61, 0.34), (97, 0.28), (149, 0.23), (211, 0.19), (283, 0.15), (379, 0.115), (491, 0.085), (619, 0.060), (773, 0.040), (941, 0.024)]

    for idx, (d_ms, g) in enumerate(taps_L):
        d = pre + int(d_ms * 0.001 * sr)
        if d < n:
            src = in_L if idx % 2 == 0 else in_R
            rev_L[d:] += src[: n - d] * g

    for idx, (d_ms, g) in enumerate(taps_R):
        d = pre + int(d_ms * 0.001 * sr)
        if d < n:
            src = in_R if idx % 2 == 0 else in_L
            rev_R[d:] += src[: n - d] * g

    for sm_ms in [13, 21, 31]:
        sd = int(sm_ms * 0.001 * sr)
        tmp_L = rev_L.copy()
        rev_L[sd:] = 0.70 * rev_L[sd:] + 0.30 * rev_R[: n - sd]
        rev_R[sd:] = 0.70 * rev_R[sd:] + 0.30 * tmp_L[: n - sd]

    out = stereo_in.copy()
    out[:, 0] += wet * rev_L
    out[:, 1] += wet * rev_R
    return out


def compose_original_bm_intro_music():
    mix = np.zeros((N_SAMPLES, 2), dtype=np.float32)
    t = np.arange(N_SAMPLES, dtype=np.float32) / SR

    # 1. Gentle breathy studio air swell (0.04s -> 1.15s) as 3D logo rises from white floor
    mix += make_soft_air_swell(N_SAMPLES, 0.04, 1.15, amp=0.038)

    # 2. Warm Velvet Ambient Pad Cushion (Cmaj9 -> Dadd11 -> Gmaj9)
    p1 = synth_velvet_ambient_pad(["C2", "G2", "D3", "E3", "B3"], 0.08, 1.95, amp=0.125)
    mix[int(0.08 * SR) : int(0.08 * SR) + len(p1)] += p1[: N_SAMPLES - int(0.08 * SR)]

    p2 = synth_velvet_ambient_pad(["D2", "A2", "E3", "F#3", "C4"], 1.45, 2.75, amp=0.130)
    mix[int(1.45 * SR) : int(1.45 * SR) + len(p2)] += p2[: N_SAMPLES - int(1.45 * SR)]

    p3 = synth_velvet_ambient_pad(["G2", "D3", "A3", "B3", "F#4"], 2.32, 4.88, amp=0.150)
    mix[int(2.32 * SR) : int(2.32 * SR) + len(p3)] += p3[: N_SAMPLES - int(2.32 * SR)]

    # 3. Spacious, Expressive Felt Grand Piano + Delicate Glass Droplets (G Major: Cmaj9 -> Dadd11 -> Gmaj9)
    #    Lives in the warm, singing mid-register (G3 - G5) just like real Modern Educational Brand Idents!
    score = [
        # (time_s, note, dur_s, velocity, pan, droplet_amp)
        # Phrase 1: Warm Cmaj9 opening arpeggio (0.12s -> 1.45s)
        (0.12, "C3",  1.85, 0.72, -0.28, 0.000),
        (0.14, "G3",  1.80, 0.64, -0.14, 0.000),
        (0.16, "E4",  1.65, 0.74, +0.05, 0.022),
        (0.44, "G4",  1.50, 0.76, +0.14, 0.026),
        (0.72, "B4",  1.40, 0.80, +0.22, 0.032),
        (1.00, "D5",  1.35, 0.84, +0.28, 0.038),  # 3-piece BM lock-in!

        # Phrase 2: Hopeful Dadd11 turn & Specular Light-Sweep (1.46s -> 2.35s)
        (1.46, "D3",  1.30, 0.74, -0.24, 0.000),
        (1.48, "A3",  1.25, 0.65, -0.10, 0.000),
        (1.50, "F#5", 1.25, 0.86, +0.32, 0.044),  # 1st star glint (1.50s)!
        (1.80, "E5",  1.15, 0.78, +0.24, 0.032),
        (2.08, "D5",  1.10, 0.76, +0.18, 0.030),  # 2nd star glint (2.13s)!

        # Phrase 3: Radiant, Warm Gmaj9 Resolution Chord & Gentle Final Bell (2.38s -> 4.85s)
        (2.38, "G2",  2.45, 0.78, -0.32, 0.000),
        (2.40, "D3",  2.42, 0.68, -0.18, 0.000),
        (2.42, "B3",  2.38, 0.66, -0.04, 0.000),
        (2.44, "D4",  2.35, 0.68, +0.06, 0.000),
        (2.46, "A4",  2.32, 0.78, +0.18, 0.028),  # Warm 9th color
        (2.48, "B4",  2.30, 0.82, +0.26, 0.035),
        # Soft lingering upper droplet notes as camera gently pulls back
        (2.86, "D5",  1.95, 0.68, +0.30, 0.032),
        (3.26, "G5",  1.60, 0.64, +0.36, 0.036),
    ]

    for idx, (t0_n, note_nm, dur_n, vel, pan, drop_a) in enumerate(score):
        s_idx = int(round(t0_n * SR))
        p_wave = synth_felt_grand_piano(note_nm, dur_n, velocity=vel, seed=idx + 50)
        add_stereo_pan(mix, s_idx, p_wave, pan)

        if drop_a > 0.001:
            d_wave = synth_delicate_glass_droplet(note_nm, min(dur_n, 1.35), amp=drop_a)
            add_stereo_pan(mix, s_idx, d_wave, min(0.60, pan * 1.3))

    # 4. Lush Scoring-Stage Reverb + Warm Studio Mastering
    mix = apply_lush_scoring_stage_reverb(mix, SR, wet=0.35, predelay_ms=22.0)

    for ch in range(2):
        mix[:, ch] = fft_eq(
            mix[:, ch],
            SR,
            [(40, -8.0), (85, +2.0), (180, +2.2), (420, -1.2), (1200, +0.2), (3200, +1.2), (6500, +1.5), (11000, -2.0)],
            lp_cutoff=13500.0,
        )

    # Clean fade-in & silky fade-out into pure silence by 4.90s
    env_master = np.ones(N_SAMPLES, dtype=np.float32)
    env_master[: int(0.03 * SR)] = np.linspace(0.0, 1.0, int(0.03 * SR))
    tail_m = t >= 3.92
    tt_tail = np.clip((t[tail_m] - 3.92) / (4.90 - 3.92), 0.0, 1.0)
    env_master[tail_m] = (1.0 - (tt_tail * tt_tail * (3.0 - 2.0 * tt_tail))) ** 1.35
    env_master[t >= 4.90] = 0.0
    mix *= env_master[:, None]

    mix = np.nan_to_num(mix, nan=0.0)
    mix = mix / (np.max(np.abs(mix)) + 1e-6) * 0.90
    mix = np.tanh(1.10 * mix) / np.tanh(1.10) * 0.85

    out_wav = os.path.join(WORK_DIR, "bm_original_copyright_free_intro.wav")
    sf.write(out_wav, mix, SR, subtype="PCM_16")
    print(f"[Composer] Saved Felt Grand Piano & Ambient Pad intro: {out_wav} (peak={np.max(np.abs(mix)):.2f})")
    return out_wav


def main():
    wav_path = compose_original_bm_intro_music()

    # Source 1080p60 White-Studio + Slogan video stream
    src_video = os.path.join(OUT_DIR, "BM_Intro_1_NenTrang_HieuUng_VoiceBM.mp4")
    if not os.path.exists(src_video):
        raise FileNotFoundError(f"Missing master video stream: {src_video}")

    final_mp4 = os.path.join(OUT_DIR, "BM_Intro_ChinhThuc_NhacRieng_1080p60.mp4")
    cmd = [
        FFMPEG,
        "-y",
        "-i", src_video,
        "-i", wav_path,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "320k",
        "-movflags", "+faststart",
        "-shortest",
        final_mp4,
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    mb = os.path.getsize(final_mp4) / (1024 * 1024)
    print(f"[Done] Exported single official MP4: {final_mp4} ({mb:.2f} MB)")


if __name__ == "__main__":
    main()

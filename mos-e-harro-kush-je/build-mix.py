#!/usr/bin/env python3
"""V5 sound mix of « Mos e harro kush je »: the ElevenLabs voice montage over « Porsi fleta e diellit të Zotit ».

Music: the last 30.3 s of the song (from MUSIC_IN), chosen so that its sections land on the film:
  film 11.6 s  a new, louder section starts under « Edhe kur jeta na çon larg »
  film 24.9 s  the last phrase of the song starts on the cut to the eagle
  film 28.8 s  the final cadence, which dies away by itself at 30 s (no fade-out needed, no hard cut)
Voice: high-pass, gentle 2:1 compression, a short room reverb so it sits in the same space as the music.
Mix: act-by-act music level (restrained under the memory, open from the transmission onward), ducking driven by the
voice envelope with an extra dip of the 1.2-4 kHz band of the music (where the words live), then loudness to
TARGET_LUFS with a true-peak ceiling.

Usage: python3 build-mix.py  ->  assets/audio/mix.wav (48 kHz stereo, 30 s)
"""
import json
import os
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
TOTAL = 30.0
N = int(TOTAL * SR)
VOICE = os.path.join(HERE, "assets/audio/voix-montage.wav")
MUSIC = os.path.join(HERE, "assets/music/source/porsi-fleta-e-diellit.mp3")
OUT = os.path.join(HERE, "assets/audio/mix.wav")
MUSIC_IN = 92.2
TARGET_LUFS, CEILING_DBTP = -14.0, -1.5
# music level (dB) before ducking, by film time: restrained under the memory, open from the transmission onward
MUSIC_LEVEL = [(0.0, -10.0), (11.4, -10.0), (11.8, -8.0), (18.0, -8.0), (18.8, -4.5), (24.0, -4.5), (24.9, 0.0), (26.2, 0.0),
               (26.5, -5.0), (28.0, -5.0), (28.5, 0.0), (30.0, 0.0)]
DUCK_DB, DUCK_LAST_DB = 13.0, 13.0      # ducking depth under the voice; lighter under the last line
CARVE_DB = 4.0                        # extra dip of the 1.2-4 kHz band of the music while the voice speaks


def load(path, start=0.0, dur=TOTAL):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(start), "-t", str(dur), "-i", path, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, dtype="<f4").reshape(-1, 2).astype(np.float64)
    return np.pad(x, ((0, max(0, N - len(x))), (0, 0)))[:N]


def fft_filter(x, gain_fn):
    """Zero-phase filter of the whole signal: gain_fn(freqs) -> linear gain."""
    n = len(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    g = gain_fn(f)
    return np.stack([np.fft.irfft(np.fft.rfft(x[:, c]) * g, n) for c in range(x.shape[1])], 1)


def envelope(mono, attack, release, hop=0.005):
    h = int(hop * SR)
    rms = np.sqrt(np.convolve(mono ** 2, np.ones(h) / h, "same"))[::h]
    out = np.zeros_like(rms)
    a, r = np.exp(-hop / attack), np.exp(-hop / release)
    for i, v in enumerate(rms):
        prev = out[i - 1] if i else 0.0
        out[i] = a * prev + (1 - a) * v if v > prev else r * prev + (1 - r) * v
    return np.interp(np.arange(len(mono)) / SR, np.arange(len(out)) * hop, out)


def db(x):
    return 20 * np.log10(np.maximum(x, 1e-9))


# ---- voice ------------------------------------------------------------------------------------------------------
v = load(VOICE)
v = fft_filter(v, lambda f: 1 / np.sqrt(1 + (80 / np.maximum(f, 1)) ** 8))          # 4th-order high-pass at 80 Hz
env = envelope(v.mean(1), 0.010, 0.120)
lvl = db(env)
thr, ratio = -26.0, 2.0
gr = np.where(lvl > thr, (lvl - thr) * (1 - 1 / ratio), 0.0)                       # gain reduction in dB
v *= 10 ** (-gr / 20)[:, None]
# short room: decaying noise, 18 ms pre-delay, RT60 ~0.8 s, darkened; mixed 22 dB below the dry voice
rng = np.random.default_rng(7)
ir_len = int(0.9 * SR)
t = np.arange(ir_len) / SR
ir = rng.standard_normal((ir_len, 2)) * np.exp(-6.9 * t / 0.8)[:, None]
ir = fft_filter(ir, lambda f: 1 / np.sqrt(1 + (f / 3500) ** 4))
ir = np.pad(ir, ((int(0.018 * SR), 0), (0, 0)))
wet = np.stack([np.fft.irfft(np.fft.rfft(v[:, c], N + len(ir)) * np.fft.rfft(ir[:, c], N + len(ir)), N + len(ir))[:N] for c in range(2)], 1)
wet *= np.sqrt(np.mean(v ** 2)) / max(1e-9, np.sqrt(np.mean(wet ** 2))) * 10 ** (-22 / 20)
v = v + wet

# ---- music ------------------------------------------------------------------------------------------------------
m = load(MUSIC, MUSIC_IN)
fade = int(0.9 * SR)                                       # the song enters mid-phrase: a short swell, not a jump
m[:fade] *= (np.linspace(0, 1, fade) ** 2)[:, None]
times = np.arange(N) / SR
level = np.interp(times, [p[0] for p in MUSIC_LEVEL], [p[1] for p in MUSIC_LEVEL])
# ducking key: the voice envelope, normalised to 0..1, slow enough to breathe between words
key = envelope(v.mean(1), 0.060, 0.350)
key = np.clip((db(key) + 56) / 18, 0, 1)
depth = np.where(times >= 26.4, DUCK_LAST_DB, DUCK_DB)
level = level - key * depth
band = fft_filter(m, lambda f: ((f > 1200) & (f < 4000)).astype(float))
m = m * (10 ** (level / 20))[:, None] - band * ((1 - 10 ** (-CARVE_DB * key / 20)) * 10 ** (level / 20))[:, None]

# ---- master -----------------------------------------------------------------------------------------------------
mix = v + m
tmp = OUT + ".f32"
mix.astype("<f4").tofile(tmp)


def measure(path_args):
    out = subprocess.run(["ffmpeg", "-nostats", *path_args, "-af", "loudnorm=print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
    j = json.loads(out[out.rindex("{"): out.rindex("}") + 1])
    return float(j["input_i"]), float(j["input_tp"])


raw_args = ["-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", tmp]
li, _ = measure(raw_args)
gain = TARGET_LUFS - li
# gain to target, then a look-ahead limiter on 4x oversampled audio for the true-peak ceiling
lim = 10 ** (CEILING_DBTP / 20)
af = f"volume={gain:.2f}dB,aresample=192000,alimiter=limit={lim:.4f}:attack=2:release=60:level=false,aresample={SR}"
subprocess.run(["ffmpeg", "-v", "error", "-y", *raw_args, "-af", af, "-c:a", "pcm_s24le", OUT], check=True)
os.remove(tmp)
li2, tp2 = measure(["-i", OUT])
speech = db(envelope(v.mean(1), 0.01, 0.05)) > -38
vm = 10 * np.log10(np.mean(v[speech] ** 2) / np.mean(m[speech] ** 2))
print(f"voice over music while speaking: {vm:+.1f} dB (RMS)")
print(f"wrote assets/audio/mix.wav: {li2:.1f} LUFS, true peak {tp2:.1f} dBTP (pre-gain {li:.1f} LUFS, gain {gain:+.1f} dB)")
